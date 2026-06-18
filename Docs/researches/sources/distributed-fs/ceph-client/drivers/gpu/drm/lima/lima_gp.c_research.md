<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.c

## Purpose
Implements the Mali GP (geometry processor) IP block, including IRQ handling, reset, task validation/run/recovery, version detection, and scheduler-pipe callback setup.

## Important APIs, types, and functions
Lifecycle functions are `lima_gp_init()`, `lima_gp_fini()`, `lima_gp_resume()`, and `lima_gp_suspend()`. Pipe setup is `lima_gp_pipe_init()` and `lima_gp_pipe_fini()`. Internal callbacks include `lima_gp_task_validate()`, `lima_gp_task_run()`, `lima_gp_task_fini()`, `lima_gp_task_error()`, `lima_gp_task_mmu_error()`, `lima_gp_task_recover()`, and reset helpers.

## Control flow
IRQ handling distinguishes shared IRQ false positives, recoverable PLBU out-of-memory, other errors, and normal VS/PLBU completion. Task validation checks command-list and heap address ranges. Task run identifies heap BOs by matching VA to PLBU allocation start, updates heap end, marks recoverability, waits for any prior async reset, writes GP frame registers, updates PLBU allocation, and starts VS and/or PLBU. Recoverable PLBU OOM grows the heap if the fail size reached current heap size, then updates allocation registers and resumes. Error handling masks interrupts and hard-resets after bus stop.

## State and persistence
`ip->data.async_reset` tracks deferred soft resets. `pipe->current_task`, `pipe->error`, task heap pointers, and recoverable flags coordinate with the scheduler. Hardware GP registers persist frame addresses, command bits, interrupt masks, and performance-counter reset probes.

## Dependencies and integration points
Depends on Lima scheduler, VM, GEM heap allocation, DRM UAPI GP frame layout, MMU error callbacks, and register constants. Device init installs this as the GP pipe processor.

## Risks
Heap recovery depends on exact PLBU allocation VA matching. Interrupt completion considers active bits and command-list end bits; wrong interpretation can complete early or hang. Reset polling has short timeouts. Task slab lifetime is global refcounted and must be balanced.

## Test signals
Run GP-only and GP+PP submissions, invalid frame ranges, PLBU heap OOM recovery, nonrecoverable GP errors, MMU fault completion, IRQ sharing, reset timeout injection, and version logging on Mali400/450.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gp.c -->
