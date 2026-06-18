# sources/distributed-fs/ceph-client/include/uapi/drm/rocket_accel.h

## Purpose
This header defines an MIT-licensed DRM accelerator UAPI for Rocket NPU devices. The ABI is intentionally small: create NPU-addressable BOs, prepare/finalize BO CPU ownership, and submit jobs made of sequential NPU tasks with explicit input/output BO handle arrays.

## Important APIs and types
The ioctl set is `DRM_IOCTL_ROCKET_CREATE_BO`, `SUBMIT`, `PREP_BO`, and `FINI_BO`. `drm_rocket_create_bo` returns a GEM handle, an NPU DMA address valid for the DRM file and GEM lifetime, and an mmap offset. `drm_rocket_prep_bo` waits for outstanding NPU usage and synchronizes caches before CPU access, bounded by `timeout_ns`. `drm_rocket_fini_bo` synchronizes caches for NPU access after CPU writes. `drm_rocket_task` points at a register-command buffer by NPU DMA address and command count. `drm_rocket_job` carries task arrays plus input and output BO handle arrays. `drm_rocket_submit` submits an array of jobs and includes struct-size fields for extensibility.

## Control flow and state
Userspace creates BOs, mmaps them through the returned offset if needed, uses prep/fini to transfer ownership between NPU and CPU, builds register-command buffers in BOs, groups tasks into jobs, lists BO dependencies by read/write direction, and submits all jobs. The kernel scheduler is expected to order jobs by dependencies, while tasks inside a job execute sequentially on the same core.

## State and persistence behavior
The returned DMA address is private to the DRM fd and valid only for the lifetime of the GEM handle. BO ownership and cache state transition through prep/fini calls rather than implicit coherency. Job and task arrays are transient submission records, while GEM handles and DMA mappings are persistent resources. Reserved fields must be zero.

## Dependencies and integration points
The header depends on `drm.h`, DRM GEM, DRM mmap offsets, kernel accelerator scheduling, NPU DMA address space, and cache-maintenance semantics. The `*_struct_size` fields indicate intended forward compatibility for task/job records.

## Risks and test signals
Risks include stale DMA addresses after handle close, missing cache synchronization, invalid timeout handling, dependency under-declaration in input/output BO arrays, and struct-size mismatches. Tests should cover BO create/mmap, prep timeout and busy paths, fini cache transitions, single and multi-task jobs, dependency ordering between jobs, invalid reserved fields, zero counts, and forward-compatible struct-size validation.
