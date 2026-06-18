<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mode.h

## Purpose

`radeon_mode.h` is the central private display-mode contract for the Radeon DRM driver. It defines display constants, GPIO/I2C bus records, PLL data, connector/encoder/CRTC state structures, TV/backlight/DisplayPort/AtomBIOS helper structures, scanout-position flags, and a large set of cross-file declarations for connector discovery, encoder programming, CRTC modesetting, I2C, DP AUX, BIOS parsing, PLL computation, fbdev, hotplug, and flip handling.

## Important APIs, Types, and Definitions

- Conversion macros `to_radeon_crtc`, `to_radeon_connector`, and `to_radeon_encoder` map DRM base objects to Radeon wrappers.
- Limits: `RADEON_MAX_HPD_PINS`, `RADEON_MAX_CRTCS`, `RADEON_MAX_AFMT_BLOCKS`, `RADEON_MAX_I2C_BUS`, `RADEON_MAX_BL_LEVEL`, and TV timing array lengths.
- Enums for RMX scaling, TV standards, underscan policy, HPD IDs, output CSC, connector audio, connector dithering, DVO chips, and page-flip status.
- `struct radeon_i2c_bus_rec` and `struct radeon_i2c_chan`: describe GPIO/hardware/AUX I2C buses and live Linux I2C adapters.
- `struct radeon_pll`, `struct atom_clock_dividers`, `struct atom_mpll_param`, and memory/voltage table structs: carry PLL and firmware-table values across AtomBIOS/display/power code.
- `struct radeon_mode_info`: persistent display subsystem state, connector table kind, CRTC/AFMT arrays, DRM properties, hardcoded EDID, firmware flags, active encoders, and backlight encoder.
- `struct radeon_crtc`: wraps `drm_crtc` with legacy offset, cursor state, RMX/native mode, PLL sharing, page flip work/status, DPM watermarks, current encoder/connector, output CSC, and scanout mode.
- Encoder-private structs for primary DAC, LVDS, TV DAC, internal/external TMDS, Atom DIG, and Atom DAC.
- `struct radeon_encoder`, `struct radeon_connector_atom_dig`, `struct radeon_hpd`, `struct radeon_router`, and `struct radeon_connector`: persistent routing, HPD, DDC, router, EDID, audio/dither, and encoder metadata.
- Function declarations cover Atom and legacy connector/encoder discovery, I2C/DDC, DP, PLL computation, CRTC base/mode/cursor handling, BIOS scratch registers, framebuffer init, fbdev, TV adjustment, FMT blocks, vblank/flip handling, and DIG encoder allocation.

## Control Flow

The header has no executable flow, but it defines the object model used by the display stack. BIOS discovery fills `radeon_mode_info`, creates connectors/encoders using the declared add/link functions, and populates I2C/HPD/router records. Modeset paths use `radeon_crtc`, `radeon_encoder`, and `radeon_connector` fields to choose PLLs, route sources, program encoders, validate scaling, and handle DP link training. Hotplug, DDC, and AUX flows use the connector's HPD/router/I2C state. Page flip and vblank handling use CRTC flip status/work and scanout helpers.

## State and Persistence Behavior

Almost every structure here is persistent for at least a DRM object lifetime. Mode info persists for the device, connectors and encoders persist through modeset teardown, CRTC state tracks current scanout/cursor/flip/PLL information, and encoder-private data stores BIOS-derived panel/DAC/TV/TMDS parameters. Some fields cache user properties such as underscan, dither, audio, TV standard, and output CSC. Firmware table structs are parsed snapshots of AtomBIOS data used by display and power management.

## Dependencies and Integration Points

This header depends on DRM CRTC/encoder/modeset helper types, DP helper definitions, Linux I2C and bit-bang I2C, fixed-point math, Radeon BO forward declarations, AtomBIOS object IDs and encoder modes through included Radeon headers, and many implementation files under `drivers/gpu/drm/radeon`. It is included by legacy and Atom display files, connector code, DP/AUX code, framebuffer code, IRQ/KMS vblank code, and BIOS parser code.

## Risks and Edge Cases

- This is a high-coupling private ABI: changing struct fields, enum values, or prototypes can ripple across many Radeon display files.
- `void *enc_priv` and connector private pointers require correct type discipline by encoder/connector kind.
- Several structs mix persistent state, cached hardware values, and user properties; stale values can cause incorrect resume, hotplug, or modeset behavior.
- Bitfield layouts in Atom divider structs are endian-sensitive and must match firmware expectations.
- Limit constants must match hardware and array sizes used in IRQ, CRTC, AFMT, I2C, and timing code.

## Test Signals

Build coverage across the Radeon display subsystem is mandatory. Runtime signals include connector discovery on AtomBIOS and COMBIOS boards, DP/DVI/VGA/LVDS/TV modesets, I2C/DDC/AUX probing, HPD routing, page flips, vblank accounting, cursor operations, backlight properties, TV/underscan/audio/dither/output-CSC properties, suspend/resume, and 32-bit/big-endian builds for bitfield layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mode.h -->
