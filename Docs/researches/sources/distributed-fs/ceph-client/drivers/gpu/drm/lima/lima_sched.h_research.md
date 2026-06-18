# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_sched.h

Purpose: declares Lima scheduler data structures and entry points shared by submit, GP/PP, MMU, and device lifecycle code.

Important APIs/types/functions: `struct lima_sched_task`, `struct lima_sched_context`, `struct lima_sched_pipe`, and `struct lima_sched_error_task`. Public functions cover task init/fini, entity init/fini, job queueing, pipe init/fini, task completion, slab init/fini, and the inline `lima_sched_pipe_mmu_error`.

Control flow: pipe users fill callback slots (`task_validate`, `task_run`, `task_fini`, `task_error`, `task_mmu_error`, `task_recover`, `task_mask_irq`) before initializing the DRM scheduler. Running jobs update `current_task` and `current_vm`, while MMU error paths mark `pipe->error` and delegate to pipe-specific handling.

State and persistence: the header defines persistent in-memory scheduler state: fence counters, current VM ref, arrays of MMU/L2/processor IP blocks, broadcast IPs, task slab, error flag, done mask, atomic task count, and recovery work. `struct lima_sched_task` owns BO references and a VM ref across job lifetime.

Dependencies and integration points: imports `drm/gpu_scheduler.h`, Linux lists, xarray, and Lima device/VM forward declarations. It is consumed by scheduler implementation plus processor-specific modules.

Risks and test signals: callback contract mismatches can crash during timeout or completion. Array maximums must cover hardware topology. Test by initializing GP and PP pipes on all supported SoCs, exercising MMU errors, and checking fence completion/cleanup paths.
