<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.c

## Purpose
Implements Mali PP (pixel processor) IP blocks, including IRQ handling, reset, task dispatch for Mali400 and Mali450 broadcast/DLBU modes, error handling, version detection, and PP scheduler-pipe callback setup.

## Important APIs, types, and functions
Lifecycle APIs are `lima_pp_init()`, `lima_pp_fini()`, `lima_pp_resume()`, `lima_pp_suspend()`, plus broadcast pseudo-IP functions `lima_pp_bcast_*()`. Pipe APIs are `lima_pp_pipe_init()` and `lima_pp_pipe_fini()`. Internal callbacks include `lima_pp_task_validate()`, `lima_pp_task_run()`, `lima_pp_task_fini()`, `lima_pp_task_error()`, `lima_pp_task_mmu_error()`, and `lima_pp_task_mask_irq()`.

## Control flow
Per-PP IRQs handle error bits, clear interrupts, decrement the outstanding PP task count, and complete the scheduler task when all processors finish. Broadcast IRQ handling loops over participating PP cores, reads status before interrupt state to avoid races, records done bits, and completes when the atomic task count reaches zero. Task validation checks requested PP count and Mali450 padding. Mali450 task run optionally enables DLBU, programs DLBU registers, enables broadcast, waits for reset, writes shared frame/writeback registers, writes per-PP stack/frame data, and starts rendering through broadcast. Mali400 task run programs each PP individually. Error handling hard-resets every PP and resets broadcast masks.

## State and persistence
`ip->data.async_reset` tracks deferred soft resets. `pipe->task` counts active PP cores, `pipe->done` tracks broadcast completions, and `pipe->error` records error state. Hardware PP registers persist frame, writeback, stack, control, interrupt mask/status, and reset probes.

## Dependencies and integration points
Depends on DRM UAPI PP frame layouts, Lima scheduler, DLBU and broadcast modules, VM constants, and register definitions. Device init wires present PP/MMU/L2 triplets into the PP pipe.

## Risks
Broadcast completion races are subtle; status/state ordering is intentional. PP count must not exceed discovered processors. DLBU and broadcast programming are Mali450-specific. Reset timeouts or missed interrupts can hang the scheduler. Task slab lifetime is global refcounted.

## Test signals
Mali400 single/multi-PP rendering, Mali450 broadcast rendering, DLBU and non-DLBU tasks, invalid PP count/padding, PP error IRQs, MMU errors, reset recovery, shared IRQs, and version logging validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_pp.c -->
