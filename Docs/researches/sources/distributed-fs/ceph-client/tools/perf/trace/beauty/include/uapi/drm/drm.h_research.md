# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/drm/drm.h

## Purpose
This vendored Direct Rendering Manager UAPI header defines the generic DRM userspace ABI: core structs, flags, capabilities, ioctl numbers, private ioctl ranges, and event layouts. In this perf tree it is primarily input for DRM ioctl beautifier generation.

## Important APIs, Types, And Functions
Major type groups include legacy DRM core handles (`drm_context_t`, `drm_drawable_t`, `drm_magic_t`), lock/map/buffer/DMA structs, vblank structs, AGP and scatter-gather structs, GEM handle structs, capability structs, PRIME sharing structs, syncobj structs, CRTC sequence structs, client naming, and DRM event structs. Key macros include `DRM_IOCTL_BASE`, `DRM_IO*`, all `DRM_IOCTL_*` command definitions, `DRM_COMMAND_BASE`, `DRM_COMMAND_END`, `DRM_EVENT_*`, `DRM_CAP_*`, `DRM_CLIENT_CAP_*`, syncobj flags, PRIME flags, and legacy lock/stat/map flags.

## Control Flow
There is no runtime control flow; this is an ABI declaration header. Preprocessor flow selects Linux/kernel/BSD type includes, preserves C++ linkage, includes `drm_mode.h`, and exposes userspace typedef aliases outside `__KERNEL__`.

## State, Dependencies, And Integration
The header defines stable binary layouts shared between kernel and userspace. `trace/beauty/drm_ioctl.sh` parses its `DRM_IOCTL_* DRM_IO*` macros and `DRM_COMMAND_BASE` to generate the generic DRM ioctl name array used by `trace/beauty/ioctl.c`. It also relies on companion `i915_drm.h` for i915 private commands.

## Risks And Test Signals
This file is large and ABI-sensitive; local edits can break ioctl numbering or struct layout assumptions. For perf, the main risk is stale or unparsable macros causing missing ioctl names. Tests should regenerate the ioctl table, compile `ioctl.c`, and verify representative generic commands such as `DRM_IOCTL_VERSION`, KMS mode ioctls, GEM/PRIME, syncobj, and recent client/name commands are decoded.
