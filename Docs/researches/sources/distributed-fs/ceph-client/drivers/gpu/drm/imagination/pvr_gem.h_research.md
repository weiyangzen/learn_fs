# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_gem.h

## Purpose
Defines PowerVR GEM object flags, the PowerVR shmem GEM wrapper, conversion helpers, and public GEM utility APIs.

## Important APIs, types, and functions
- Kernel-only flags `PVR_BO_CPU_CACHED` and `PVR_BO_FW_NO_CLEAR_ON_RESET` occupy high reserved bits; `PVR_BO_KERNEL_FLAGS_MASK` and `PVR_BO_UNDEFINED_MASK` support validation.
- Firmware mapping presets `PVR_BO_FW_FLAGS_DEVICE_CACHED` and `PVR_BO_FW_FLAGS_DEVICE_UNCACHED` describe device-cache policy.
- `struct pvr_gem_object` embeds `drm_gem_shmem_object` at offset 0 and stores immutable `flags`.
- Conversion macros bridge PowerVR, shmem, and base GEM objects.
- Declares object creation, handle conversion, page sg-table access, vmap/vunmap, DMA-address lookup, refcount get/put, and size helper APIs.

## Control flow
Only small inline helpers exist: sg-table retrieval delegates to shmem, references delegate to DRM GEM get/put, and size reads the base GEM object size.

## State and persistence
The header defines the persistent per-buffer flag state used for CPU caching, firmware reset preservation, PM/FW protection, device cache bypass, and userspace CPU access. The embedded layout assertion makes generic GEM/shmem conversion safe.

## Dependencies and integration points
Depends on DRM GEM/shmem/MM headers, UAPI BO flags, Rogue heap/meta constants, Linux scatterlist/types, and PVR device/file forward declarations. Used by almost every memory, VM, firmware, free-list, context, and job subsystem.

## Risks
Flag namespace mistakes can expose kernel-only flags to userspace or break validation. Since `flags` is const, behavior that needs mutable cache policy would require new object creation rather than modification. The comment contains a typo in "shem_gem" but the macro names are correct.

## Test signals
Build assertions for object layout, flag validation through create ioctl tests, and runtime GEM object creation/mapping/export/mmap tests are the main signals.
