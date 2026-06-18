# sources/distributed-fs/ceph-client/include/uapi/drm/drm.h

## Purpose
Defines the common Direct Rendering Manager UAPI foundation: base types, legacy DRM ioctls, GEM, PRIME dma-buf sharing, client and device capabilities, sync objects, CRTC sequence events, mode-setting ioctl numbers, command ranges, and event formats.

## Important APIs, Types, And Functions
Exports base DRM types, legacy map/lock/DMA/context/auth/AGP structs, `drm_version`, GEM close/flink/open/change-handle structs, capability constants, client capability constants, PRIME handle conversion, syncobj binary/timeline/eventfd structs, CRTC sequence structs, ioctl construction macros, generic `DRM_IOCTL_*` numbers, `DRM_COMMAND_BASE`/`END`, and event structs `drm_event`, `drm_event_vblank`, `drm_event_crtc_sequence`.

## Control Flow
No executable logic. The header encodes ioctl flows for version/capability negotiation, GEM handle lifetime, PRIME import/export, syncobj create/wait/signal/timeline operations, KMS mode ioctls imported from `drm_mode.h`, and event reads from DRM fds.

## State, Persistence, And Dependencies
Kernel state includes DRM file clients, master/auth state, GEM handles, dma-buf FDs, syncobjs and timeline points, KMS objects, vblank counters, leases, and queued events. It depends on Linux or BSD integer/ioctl headers and includes `drm_mode.h`.

## Integration Points
Included by nearly every DRM driver UAPI header, including amdgpu, amdxdna, armada, and asahi. Used by libdrm, Mesa, compositors, display servers, games, compute runtimes, PRIME/dma-buf sharing, and KMS tools.

## Risks
This is core ABI. Legacy structs contain native `long`, pointers, and historical layouts, so compat handling is fragile. GEM handles are not refcounted per handle and duplicate imports can return the same handle. Event reads must be complete-event aligned. Device-specific ioctls must stay inside `0x40..0x9f`.

## Test Signals
libdrm test suite, KMS/modetest coverage, GEM handle lifetime and duplicate-import tests, PRIME import/export tests, syncobj binary/timeline/eventfd tests, vblank and CRTC sequence event tests, 32-bit compat ioctl tests, and ABI size checks for every exported struct.
