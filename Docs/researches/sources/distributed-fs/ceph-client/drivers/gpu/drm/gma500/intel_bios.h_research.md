<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.h

## Purpose

This header defines the packed Intel VBT/BDB layout structures, section IDs, child-device constants, eDP parameter encodings, scratch-register bit definitions, and parser API used by the GMA500 BIOS parser and output code.

## Important APIs, Types, And Macros

Important structures include `vbt_header`, `bdb_header`, `vbios_data`, `bdb_general_features`, `child_device_config`, `bdb_general_definitions`, `bdb_lvds_options`, `bdb_lvds_backlight`, LFP timing structures, `bdb_lvds_lfp_data`, AIM/VCH panel data, `bdb_sdvo_lvds_options`, `bdb_driver_features`, `edp_power_seq`, `edp_link_params`, and `bdb_edp`. Macros enumerate BDB section IDs, device types/config/wiring/ports, driver LVDS feature values, eDP color/rate/lane/preemphasis/vswing encodings, GR18 and SWF scratch bits, and Cedarview device classes such as HDMI, DP, and eDP. It declares `psb_intel_init_bios()` and `psb_intel_destroy_bios()`.

## Control Flow

The header has no executable flow. Its packed structures are cast directly over firmware bytes by `intel_bios.c`; output code also consults child-device constants to classify LVDS/eDP/DP ports.

## State And Persistence

No runtime state is stored in the header. It defines the ABI used to populate persistent fields in `drm_psb_private`, especially panel modes, child devices, and eDP settings. Scratch-register macros describe firmware/driver communication state in VGA/SWF registers.

## Dependencies And Integration Points

It is used by the BIOS parser, Cedarview LVDS detection, Cedarview DP eDP detection, backlight setup, SDVO code, and any code interpreting OpRegion or PCI ROM VBT data.

## Risks And Test Signals

Risks include packed layout drift across VBT versions, bitfield endian/compiler assumptions, unsafe direct casts over untrusted firmware data, duplicate old/new device-type constants, and scratch-bit semantics that depend on BIOS behavior. Test signals are compile coverage, parser tests with representative VBT versions, LVDS/eDP child-device matching, eDP bpp/lane/rate decoding, and malformed firmware fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.h -->
