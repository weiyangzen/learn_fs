<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.c

## Purpose

`radeon_legacy_encoders.c` implements legacy output encoder handling for LVDS, primary DAC, internal TMDS, external DVO/TMDS, and TV DAC encoders. It wires DRM encoder helper callbacks, performs DPMS and mode routing through direct register programming, registers legacy LVDS backlight devices, performs analog/TV load detection, retrieves BIOS encoder private data, and creates/merges legacy encoder objects.

## Important APIs, Types, and Functions

- `radeon_add_legacy_encoder()`: creates or updates a `struct radeon_encoder`, sets possible CRTCs/devices, chooses encoder funcs/helper funcs by Atom object ID, and loads encoder-private BIOS data.
- `radeon_legacy_encoder_disable()`: calls the encoder's DPMS-off helper and clears `active_device`.
- LVDS path: `radeon_legacy_lvds_update()`, `*_dpms`, `*_prepare`, `*_commit`, `*_mode_set`, `radeon_legacy_get_backlight_level()`, `radeon_legacy_set_backlight_level()`, `radeon_legacy_backlight_init()`, and destroy helpers.
- Primary DAC path: `radeon_legacy_primary_dac_dpms()`, `*_mode_set()`, and `radeon_legacy_primary_dac_detect()`.
- Internal TMDS path: `radeon_legacy_tmds_int_dpms()` and `*_mode_set()` program `FP_GEN_CNTL`, TMDS PLL, and transmitter registers.
- External TMDS/DVO path: `radeon_legacy_tmds_ext_*()` programs `FP2_GEN_CNTL` and calls Atom/COMBIOS/external DVO setup helpers.
- TV DAC path: `radeon_legacy_tv_dac_*()`, `radeon_legacy_tv_detect()`, `r300_legacy_tv_detect()`, `radeon_legacy_ext_dac_detect()`, and `radeon_legacy_tv_dac_detect()`.
- Private-data loaders `radeon_legacy_get_tmds_info()` and `radeon_legacy_get_ext_tmds_info()` combine AtomBIOS, COMBIOS, and fallback table sources.

## Control Flow

Connector discovery calls `radeon_add_legacy_encoder()` with an encoder enum and supported device mask. If the encoder already exists, its device mask is extended; otherwise a new DRM encoder is initialized with helper functions matching the encoder ID. LVDS is limited to CRTC0 and defaults to full RMX scaling; other legacy encoders can generally drive either CRTC unless the device is single-CRTC.

During modeset, the common fixup path sets `active_device`, computes adjusted CRTC info, and applies panel mode fixup for LCDs. Prepare locks the output through AtomBIOS or COMBIOS scratch mechanisms and powers the encoder down. Mode-set functions select source CRTC/RMX, program output-specific PLL/routing/DAC registers, and update BIOS scratch CRTC routing. Commit powers the encoder on and releases the output lock for most paths.

Detection paths save the registers they need, force known DAC/TV/DVO test patterns, wait for comparator/GPIO results, then restore the saved state. TV and secondary DAC detection have separate R300, R200 external DAC, single-CRTC, and connector-type branches.

Backlight registration allocates private data, respects platform native-backlight policy, detects positive/negative brightness sense, stores the backlight device in Atom or legacy LVDS private data, initializes brightness from hardware, and updates mode-info `bl_encoder`.

## State and Persistence Behavior

Persistent state includes DRM encoder objects, `radeon_encoder` fields (`devices`, `active_device`, `rmx_type`, `enc_priv`, output CSC/audio fields), BIOS-derived private structs for LVDS/DAC/TMDS/TV, LVDS backlight device and brightness, connector routing scratch registers, and direct hardware output registers. Detection routines temporarily perturb registers and must restore them exactly.

## Dependencies and Integration Points

The file integrates with DRM encoder helpers, Linux backlight and ACPI video policy, Radeon BIOS parsers, AtomBIOS/COMBIOS output locks and scratch registers, legacy CRTC code, legacy TV mode programming, external TMDS/DVO helpers, I2C bus records for DVO chips, PMac backlight support, and connector detection flows.

## Risks and Edge Cases

- Several commit functions for internal TMDS and TV DAC call output lock with `true` after enabling, unlike other paths that unlock with `false`; this may be intentional for legacy hardware but is a high-risk semantic trap.
- Load detection temporarily rewrites many display registers. Missing restore on new early returns would corrupt active displays.
- Backlight polarity detection uses heuristics and platform exceptions; incorrect polarity inverts brightness.
- `enc_priv` is a `void *` whose concrete type depends on encoder ID and BIOS type, so wrong casts can silently corrupt behavior.
- External TMDS setup falls through multiple data sources; absent or invalid BIOS data may still create an encoder with limited private state.
- Some detection paths refuse probing while CRTC2 is in use, which can produce connector-status differences depending on active modes.

## Test Signals

Test LVDS panel power sequencing and backlight on AtomBIOS and COMBIOS systems, primary/secondary DAC load detection, TV S-video/composite detection, internal and external DVI modes, CRTC0/CRTC1 routing, RMX with LVDS/TMDS, output lock/scratch register updates, backlight registration skip under ACPI native policy, PMac backlight cases, suspend/resume encoder restore, and repeated detect while displays are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.c -->
