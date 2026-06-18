# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_debugfs.c

## Purpose
`vc4_debugfs.c` centralizes VC4 debugfs setup for DRM minors and provides a small helper for exposing 32-bit hardware register sets. It does not own hardware policy; instead it connects HVS, BO, V3D, CRTC, DPI, DSI, and other module-provided `debugfs_regset32` definitions to DRM debugfs entries.

## Important APIs, Types, And Functions
- `vc4_debugfs_init()` is the DRM driver's `debugfs_init` callback. It always attempts HVS debugfs setup and conditionally adds BO/V3D debugfs when `vc4->v3d` exists.
- `vc4_debugfs_regset32()` is the seq-file show callback used for register dumps. It retrieves the `struct debugfs_regset32` from `entry->file.data`, enters the DRM device with `drm_dev_enter()`, and prints registers with `drm_print_regset32()`.
- `vc4_debugfs_add_regset32()` wraps `drm_debugfs_add_file()` so component drivers can register named register-dump files with the common show implementation.

## Control Flow
At `drm_dev_register()` time, DRM calls `vc4_debugfs_init()` for each minor. That function invokes module-specific debugfs initializers and uses `drm_WARN_ON()` to surface failures without aborting driver registration. Later, individual component late-register hooks such as CRTC, DPI, and DSI call `vc4_debugfs_add_regset32()` with their regset metadata. When users read a debugfs file, `vc4_debugfs_regset32()` prints live registers if the DRM device is still present.

## State And Persistence Behavior
This file stores no long-lived private state. Persistent debugfs entries are owned by DRM core, while the register-set metadata is owned by the component structures that pass it in. Reads are live hardware snapshots and are guarded by `drm_dev_enter()` so unplugged devices return `-ENODEV`.

## Dependencies And Integration Points
The file depends on DRM debugfs infrastructure, DRM printers, seq_file, Linux debugfs, platform-device-visible component regsets, and `vc4_drv.h` declarations. It integrates with HVS, BO cache, V3D, CRTC, DPI, and DSI modules by providing the shared register-dump plumbing.

## Risks And Edge Cases
- Debugfs reads touch MMIO through `drm_print_regset32()`; invalid regset lifetime or missing `drm_dev_enter()` would be hazardous, but this helper guards device lifetime.
- `vc4_debugfs_init()` only adds BO/V3D debugfs when `vc4->v3d` is present, so display-only VC5/VC6 devices intentionally lack those entries.
- Failures are warnings, not probe failures. Debugfs absence should not be treated as functional driver failure.

## Test Signals
- Build with and without `CONFIG_DEBUG_FS` to confirm the helper declaration and call sites compile.
- On hardware, verify expected files such as HVS, V3D, BO, CRTC, DSI, and DPI reg dumps appear only for present blocks.
- Unplug/removal or simulated `drm_dev_enter()` failure should make register reads fail cleanly rather than dereferencing removed hardware.
