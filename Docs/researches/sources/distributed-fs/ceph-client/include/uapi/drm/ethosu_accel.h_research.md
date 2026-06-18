# sources/distributed-fs/ceph-client/include/uapi/drm/ethosu_accel.h

## Purpose

`ethosu_accel.h` defines the DRM accelerator UAPI for Arm Ethos-U NPUs. It provides ioctls for device queries, GEM buffer creation, command-stream buffer creation, buffer waits, mmap offset lookup, and NPU job submission.

## Important APIs, Types, And Constants

`enum drm_ethosu_ioctl_id` allocates append-only IDs for `DEV_QUERY`, `BO_CREATE`, `BO_WAIT`, `BO_MMAP_OFFSET`, `CMDSTREAM_BO_CREATE`, and `SUBMIT`. `DRM_ETHOSU_DEV_QUERY_NPU_INFO` returns `struct drm_ethosu_npu_info`, whose `id`, `config`, and `sram_size` describe the NPU and whose helper macros decode architecture/product/version fields.

`struct drm_ethosu_dev_query` uses the common extensible query pattern: NULL pointer returns required size, while non-NULL copies `min(size, actual_size)`. Buffer structures cover BO create flags such as `DRM_ETHOSU_BO_NO_MMAP`, mmap fake offsets, and absolute-timeout BO waits. `struct drm_ethosu_cmdstream_bo_create` creates command-stream BOs from user data. `struct drm_ethosu_job` references one command-stream BO plus up to eight region BO handles, and `struct drm_ethosu_submit` submits an array of jobs. `DRM_IOCTL_ETHOSU()` builds concrete ioctl numbers over `DRM_COMMAND_BASE`.

## Control Flow

Typical userspace flow is query NPU info, create tensor/region BOs, create a command-stream BO, request mmap offsets when needed, submit one or more jobs, and wait for BO completion. Jobs in a submit are scheduled by the kernel with dependency awareness; tasks within a job execute sequentially on the same core to benefit from SRAM residency.

## State And Persistence

GEM BO handles and command-stream BO handles persist for the DRM file lifetime or until closed. Submissions create scheduled work and fences associated with BOs. `BO_WAIT` observes completion of the last submit affecting a BO. SRAM use is per job and scheduler-managed.

## Dependencies And Integration Points

The file includes `drm.h` and depends on DRM ioctl macros, GEM, mmap fake offsets, fences, and the Ethos-U driver scheduler. Consumers are ML runtimes, inference delegates, and low-level Ethos-U userspace libraries.

## Risks

Ioctl IDs are append-only ABI and must not be reordered. Query extensibility depends on userspace honoring the size/pointer protocol. `timeout_ns` is absolute. `DRM_ETHOSU_BO_NO_MMAP` must prevent invalid mmap flows. `ETHOSU_MAX_REGIONS` is fixed at eight, and user pointers for jobs/data require strict kernel validation.

## Test Signals

Tests should cover ioctl numbering, query size negotiation, BO creation page alignment and flag validation, mmap offset success/failure, command-stream BO creation from valid and invalid pointers, submit with zero/one/multiple jobs, invalid region handles, SRAM limit validation, BO wait timeout behavior, and 32-bit pointer compatibility.
