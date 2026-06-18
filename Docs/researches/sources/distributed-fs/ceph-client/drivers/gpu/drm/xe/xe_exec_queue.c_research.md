<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.c

## Purpose
`xe_exec_queue.c` implements execution queue allocation, initialization, ioctl creation/destruction/property handling, multi-queue grouping, LRC management, runtime accounting, kill/fini ordering, and last-fence tracking.

## Important APIs, types, and functions
Core APIs include `xe_exec_queue_create()`, `xe_exec_queue_create_class()`, `xe_exec_queue_create_bind()`, `xe_exec_queue_destroy()`, `xe_exec_queue_fini()`, `xe_exec_queue_lookup()`, `xe_exec_queue_create_ioctl()`, property get/set ioctls, `xe_exec_queue_is_lr()`, `xe_exec_queue_is_idle()`, `xe_exec_queue_update_run_ticks()`, `xe_exec_queue_kill()`, and last-fence/TLB-invalidation fence helpers. Internal helpers allocate dependency schedulers, parse user extensions, validate logical engine masks, initialize multi-queue groups, and add secondary queues.

## Control flow and integration points
Creation allocates a flex-array queue, initializes defaults from the hardware engine class, optionally parses user extensions before LRC creation, initializes backend ops, then creates LRCs while coordinating with SR-IOV VF GGTT migration fixups. User create ioctl validates placements, handles VM-bind queues per tile, validates regular engine masks and multi-LRC constraints, creates queues, attaches multi-queue state, registers LR compute queues and hardware-engine-group membership, then allocates the user xarray id last to avoid UAF. Destroy ioctl erases the xarray id, increments pending-removal for fdinfo synchronization, removes engine-group membership, kills backend execution, traces close, and drops the reference.

## State and persistence behavior
Queues hold VM/file refs, LRC refs, backend state, DRM sched entity, PXP linkage, multi-GT child queues, multi-queue group BO/LRC refs, last fences, TLB invalidation fences, dependency schedulers, run-tick accounting, and optional replay state. Locking contracts vary by queue type: migrate job lock, VM lock, or hardware-engine-group mode semaphore protect last-fence access.

## Dependencies, risks, and test signals
Dependencies include Xe VM, LRC, GuC/execlist backend ops, hw engine groups, migration, dep scheduler, syncobj, PXP, SR-IOV PF/VF, xarrays, and UAPI properties. Risks include multi-queue reference leaks, id allocation ordering, stale LRC GGTT addresses after VF migration, property permission mistakes, lockdep contract violations for fences, and partial creation cleanup. Test signals include queue create/destroy ioctl stress, VM-bind multi-tile queues, multi-LRC validation, multi-queue group add/delete, property limits and CAP_SYS_NICE behavior, LR compute queues, PXP queue lists, fdinfo pending-removal waits, and error-injection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec_queue.c -->
