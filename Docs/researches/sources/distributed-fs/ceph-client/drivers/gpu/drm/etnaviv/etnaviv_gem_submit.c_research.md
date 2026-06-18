## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem_submit.c

### Purpose
`etnaviv_gem_submit.c` implements the userspace command-stream submission ioctl for the Etnaviv DRM driver. It copies submit arguments from userspace, validates buffer objects, relocations, softpin addresses, sync fences, and performance-monitor requests, then creates a `drm_sched_job` for GPU execution.

### Important APIs, Types, And Functions
The central type is `struct etnaviv_gem_submit`, allocated by `submit_create()` and reference-counted through `etnaviv_submit_put()`. `etnaviv_ioctl_gem_submit()` is the UAPI entry point. Helper paths include `submit_lookup_objects()`, `submit_lock_objects()`, `submit_pin_objects()`, `submit_reloc()`, `submit_perfmon_validate()`, `submit_fence_sync()`, and `submit_attach_object_fences()`.

### Control Flow
The ioctl validates pipe, stream alignment, exec state, flags, MMU compatibility for softpin, and argument limits. It copies BO, relocation, PMR, and command stream arrays outside locks, reserves an output fence fd when requested, initializes a command buffer and scheduler job, looks up GEM handles under `file->table_lock`, optionally validates the command stream, imports an input sync file, pins objects into the submit MMU context, patches relocations, validates perfmon writes, locks reservations with wound/wait retry handling, adds implicit dependencies, pushes the job to the scheduler, and attaches the output fence to every BO reservation.

### State, Persistence, And Dependencies
State persists only through kernel objects: pinned `etnaviv_vram_mapping`s, GEM references, reservation fences, scheduler job state, xarray user fence id, and command-buffer storage. Cleanup unpins mappings, drops MMU contexts, removes user-fence xarray entries, wakes fence waiters, and releases copied PMR storage. Dependencies include GEM object lookup, dma-resv locking/fencing, sync_file, `drm_gpu_scheduler`, Etnaviv command buffers, MMU contexts, and perfmon validation.

### Integration Points
The ioctl feeds `etnaviv_sched_push_job()` and ultimately `etnaviv_gpu_submit()`. BO mapping is provided by `etnaviv_gem_mapping_get()`, relocation addresses by `mapping->iova`, and PMRs are consumed later by sync-point callbacks in `etnaviv_gpu.c`.

### Risks
Late output-fence allocation failure happens after the job has been handed to the scheduler, so cleanup must avoid `drm_sched_job_cleanup()` on that path. Softpin forbids relocations and requires MMUv2. Reservation locking must handle duplicate BOs and `-EDEADLK` correctly. PMR offsets are in mapped CPU memory and must not overwrite userspace sequence word zero. Any missing cleanup leaks GEM refs, active counts, or user fence ids.

### Test Signals
Useful signals include invalid handles, duplicate BO handles, invalid flags, unaligned stream and relocation offsets, softpin on MMUv1, softpin address mismatch, relocation outside object, input and output sync-fd behavior, `ETNA_SUBMIT_NO_IMPLICIT`, PMR validation failures, scheduler push failure, and fault injection around allocation and copy-from-user paths.
