# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crc.h

## Purpose
`amdgpu_dm_crc.h` declares the Display Manager CRC source enum, secure-display CRC data structures, validity helper, and debugfs/secure-display CRC entry points used by CRTC and IRQ code.

## Important APIs, Types, And Functions
`enum amdgpu_dm_pipe_crc_source` models no CRC, CRTC CRC, CRTC CRC with dither, DPRX CRC, DPRX CRC with dither, max, and invalid. Under `CONFIG_DRM_AMD_SECURE_DISPLAY`, it defines `enum secure_display_mode`, `struct phy_id_mapping`, `struct crc_data`, `struct crc_info`, `struct crc_window_param`, `struct secure_display_crtc_context`, and `struct secure_display_context`. `amdgpu_dm_is_valid_crc_source` checks enabled non-`none` sources.

## Control Flow
The header defines the compile-time control surface: debugfs builds wire CRTC funcs to CRC set/verify/source/get/IRQ handlers, while non-debugfs builds replace them with NULL or empty macros. Secure-display builds add ROI activation, window IRQ, and context creation; other builds compile those uses out.

## State And Persistence
Secure-display structures store per-CRTC work items, ROI rectangles, per-window RGB CRC values, frame counts, readiness flags, and PHY mapping metadata for connected SST/MST displays. This is runtime kernel state only.

## Dependencies And Integration Points
It forward declares DRM CRTC and DM CRTC state and expects surrounding AMDGPU/DC headers to provide `MAX_CRC_WINDOW_NUM`, `struct crc_window`, workqueue, spinlock, and device types when secure display is enabled. It is included by `amdgpu_dm.h` and consumed by CRTC functions and CRC implementation.

## Risks
Macro fallbacks must match function-pointer expectations; `amdgpu_dm_crc_window_is_activated(x)` expands to no value when secure display is disabled, so callers must keep uses under matching `#ifdef`s. Secure-display array sizes (`MAX_CRTC`, `MAX_CRC_WINDOW_NUM`) must match hardware and mode-info limits. Structs shared with IRQ code require careful locking around `crc_info` and window parameters.

## Test Signals
Compile matrix coverage for `CONFIG_DEBUG_FS` and `CONFIG_DRM_AMD_SECURE_DISPLAY` on/off combinations is essential. Runtime signals are CRC source callbacks present in DRM CRTC funcs when expected, no unresolved references in disabled builds, secure-display context allocation for every CRTC, and valid per-window CRC data under ROI tests.
