# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bios.c

## Purpose
`intel_bios.c` parses Intel VBT/BDB firmware data into sanitized i915 display configuration. It discovers the VBT from firmware override, ACPI OpRegion, SPI flash, or PCI ROM, caches selected BDB blocks, extracts child display device data, panel timing/backlight/power/eDP/PSR/MIPI/DSC settings, maps VBT ports/AUX/DDC pins to driver enums, and exposes query helpers for connector/encoder initialization.

## Important APIs, Types, and Functions
- `struct intel_bios_encoder_data` wraps a parsed `child_device_config`, optional DSC parameters, and list linkage.
- BDB block helpers include `find_raw_section()`, `bdb_find_section()`, `init_bdb_blocks()`, LFP pointer validation/fixup/generation helpers, and `get_blocksize()`.
- Panel parsing includes `get_panel_type()`, `parse_panel_options()`, `parse_generic_dtd()`, `parse_lfp_data()`, `parse_lfp_backlight()`, `parse_edp()`, `parse_psr()`, `parse_mipi_config()`, and `parse_mipi_sequence()`.
- Device parsing includes `parse_general_features()`, `parse_general_definitions()`, `parse_driver_features()`, `parse_compression_parameters()`, `parse_sdvo_device_mapping()`, and `parse_ddi_ports()`.
- Public lifecycle/query APIs include `intel_bios_init()`, early/late panel init, `intel_bios_driver_remove()`, `intel_bios_fini_panel()`, VBT validity check, TV/LVDS/port/DSI presence checks, encoder capability helpers, AUX/DDC/boost/link-rate helpers, DSC parameter lookup, encoder iteration, and debugfs registration.

## Control Flow
`intel_bios_init()` initializes VBT lists and defaults, locates a valid VBT, records BDB version, copies selected BDB blocks into `display->vbt.bdb_blocks`, parses general features and child devices, attaches DSC data to child devices, then performs SDVO/DDI parsing. If no VBT is found, it generates limited default child devices for non-Type-C DDI ports on relevant platforms.

Panel initialization is split into early and late paths. `intel_bios_init_panel_early()` selects a panel type without EDID fallback, while `intel_bios_init_panel_late()` can use EDID/PNPID and fallback. Once a panel type is known, parsing populates fixed modes, backlight data, SDVO LVDS mode, DRRS/PSR/VRR/HOBL, eDP link parameters, MIPI config/PPS/sequences, and DSI backlight ports.

## State and Persistence
Persistent parsed state lives in `display->vbt`, including default/general flags, BDB version, child device list, copied BDB block list, SDVO mappings, and CRT DDC pin. Per-panel persistent state lives in `panel->vbt`, including panel type, fixed modes, backlight config, eDP/PSR/DSI settings, and allocated MIPI sequence/config/PPS buffers. Cleanup frees child devices, DSC entries, BDB block entries, panel modes, and MIPI buffers.

## Dependencies and Integration Points
The file depends on VBT structure definitions from `intel_vbt_defs.h`, display core/runtime info, OpRegion, ROM helpers, GMBUS pin validation, DSC helpers, DP constants, DRM EDID/product ID helpers, firmware loading, debugfs, and display RPM for ROM access. Query helpers feed connector probing, DDI port initialization, eDP/DSI panel setup, AUX/DDC selection, HDMI/DP limits, and DSC CRTC configuration.

## Risks
VBT is firmware-provided and often malformed. The parser performs many size/version checks, but changes can still cause out-of-bounds reads if block sizes, child device sizes, or MIPI sequence sizes are mishandled. Version-gated fields must not be read on older BDB versions. Port, DDC, and AUX mappings vary by platform and PCH generation; mistakes can initialize nonexistent ports or choose wrong AUX/DDC channels. Panel type selection may differ between OpRegion, VBT, EDID PNPID, and fallback. MIPI sequence fixups intentionally compensate for broken real systems and are regression-prone.

## Test Signals
Important signals are KMS debug logs for VBT source, BDB version, block sizes, malformed LFP pointers, panel type source, mode/backlight/eDP/PSR/MIPI details, child device parsing, DDI port capabilities, and ignored invalid pins/ports. Test with valid VBT, no VBT, firmware override VBT, OpRegion VBT, PCI/SPI ROM VBT, old and new BDB versions, dual-LFP panel types, eDP/DSI panels, DSC-enabled child devices, Type-C/TBT/dedicated external ports, and `i915_vbt` debugfs reads.
