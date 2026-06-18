# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.h

## Purpose
`amdgpu_dm.h` is the central private Display Manager contract between the AMDGPU DRM/KMS driver and AMD Display Core. It defines the main `amdgpu_display_manager` device state, connector/plane/CRTC state wrappers, color-management enums and limits, DMUB/IRQ/workqueue structures, and exported helper prototypes used by connector, CRTC, color, AUX, memory, and detection code.

## Important APIs, Types, And Functions
Important types include `struct amdgpu_display_manager`, `struct amdgpu_dm_connector`, `struct dm_plane_state`, `struct dm_crtc_state`, `struct dm_atomic_state`, and `struct dm_connector_state`. The display manager owns DC/DMUB pointers, firmware buffers, atomic private object state, DC/audio locks, IRQ handler tables, vblank/vupdate/pageflip parameters, backlight caches, secure-display context, HPD offload queues, MST encoders, DMUB completions, and boot-time CRC buffers. Plane and CRTC state wrappers carry DC objects plus AMD color properties such as degamma/shaper/blend LUT blobs, transfer functions, HDR multiplier, 3x4 CTM, 3D LUT, regamma TF, VRR state, ABM level, CRC skip count, active plane count, and cursor mode.

## Control Flow
This header does not execute logic directly except for small container/status helpers, but it establishes the flow used by the implementation: DRM atomic state is extended into DM-specific state, commit code builds or retains DC streams and planes, color and CRC code mutate DC stream/plane transfer functions and IRQ parameters, and asynchronous work structures defer HPD/vblank/vupdate/idle work outside hard interrupt paths.

## State And Persistence
State is runtime kernel state, not on-disk persistence. Several fields are long-lived caches across hotplug, suspend/resume, and atomic commits: cached DRM/DC state, backlight brightness, MST status, FreeSync/ABM settings, secure-display ROI mapping, DMUB firmware buffer addresses, and connector EDID/sink pointers. DC stream and plane pointers require explicit retain/release discipline in users.

## Dependencies And Integration Points
The file depends on DRM atomic/connector/CRTC/plane/writeback APIs, DP MST helpers, AMD DC link/signal/IRQ types, DM CRC declarations, info packets, and broader AMDGPU mode structures. It is included by most `amdgpu_dm` implementation files and is the shared ABI for CRTC, connector, color, CRC, debugfs, DMUB, MST, PSR, Replay, backlight, and audio integration.

## Risks
The header is a high-blast-radius ownership contract. Risks include stale `dc_stream_state`/`dc_plane_state` references, lock-order bugs between `dc_lock`, `audio_lock`, event locks, and mode-config locks, build-configuration drift around `AMD_PRIVATE_COLOR` and `CONFIG_DRM_AMD_SECURE_DISPLAY`, array size mismatches for CRTC/EDP/DMUB notification limits, and connector sink/MST pointers becoming stale during hotplug.

## Test Signals
Useful signals are successful DRM device initialization, atomic modesets with suspend/resume, MST hotplug and payload changes, eDP backlight and PSR/Replay transitions, DMUB AUX/config transactions, CRC debugfs enable/disable, secure-display ROI creation when enabled, and IGT/KMS coverage for color properties, VRR, writeback exclusion, connector state duplication, and plane/CRTC atomic validation.
