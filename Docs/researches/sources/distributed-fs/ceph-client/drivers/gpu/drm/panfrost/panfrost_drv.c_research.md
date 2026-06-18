# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_drv.c

## Purpose
This is the Panfrost platform and DRM driver entry point. It defines the DRM UAPI ioctl handlers, file open/close lifecycle, fdinfo/debugfs reporting, probe/remove, sysfs profiling control, compatible data, and module registration.

## Important APIs, Types, and Functions
Important ioctls include get-param, create/mmap/wait/get-offset/madvise/set-label/sync/query BO, submit, and JM context create/destroy. Important lifecycle functions are `panfrost_open`, `panfrost_postclose`, `panfrost_probe`, and `panfrost_remove`. It also defines `panfrost_drm_driver`, compatible data tables, and the `unstable_ioctls` and `transparent_hugepage` module parameters.

## Control Flow
Probe allocates `struct panfrost_device` as a DRM device, reads compatible data and coherency, initializes shrinker state, calls device init, enables runtime PM/autosuspend, registers DRM, and registers the GEM shrinker. Open allocates per-file state, creates an MMU context, and opens job-manager contexts. Submit validates inputs, resolves output syncobj, JM context, incoming syncobjs, BO handles and mappings, initializes a scheduler job, pushes it, and attaches the output fence. Remove unregisters DRM, frees shrinker, disables runtime PM, and tears down the device.

## State and Persistence Behavior
Per-device state includes DRM registration, PM state, compatible policy, shrinker, profiling flag, and module parameters. Per-file state owns MMU and JM contexts plus engine usage counters. BO ioctls mutate GEM objects, labels, mappings, purgeability, and cache state.

## Dependencies and Integration Points
It integrates with DRM core ioctls, syncobjs, GEM handles, dma-resv, runtime PM, device tree, sysfs attributes, debugfs, Panfrost GEM/MMU/job/perfcnt subsystems, and the platform driver bus.

## Risks
UAPI validation is security-sensitive: padding, flags, handles, sync object counts, user pointers, and priority permissions must remain strict. Submit cleanup relies on reference ownership across scheduler jobs, BO mappings, syncobjs, and JM contexts. MADVISE only supports single-owner purgeable BOs. Compatible data drives PM behavior and platform quirks.

## Test Signals
Run userspace submit/create/wait/mmap/get-param paths, invalid ioctl fuzzing, syncobj dependency tests, PRIME/import query tests, JM context priority permission checks, fd close with in-flight jobs, runtime PM autosuspend, sysfs profiling toggles, and debugfs/fdinfo reads.
