# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_sched.c

Purpose: implements Lima's DRM GPU scheduler backend, per-pipe fences, runtime PM bracketing, VM switching, timeout/error recovery, and error-task capture.

Important APIs/types/functions: `lima_sched_slab_init/fini`, `lima_sched_task_init/fini`, `lima_sched_context_init/fini`, `lima_sched_context_queue_task`, `lima_sched_pipe_init/fini`, and `lima_sched_pipe_task_done`. Internal anchors are `struct lima_fence`, `lima_sched_run_job`, `lima_sched_timedout_job`, `lima_sched_build_error_task_list`, and `lima_sched_recover_work`.

Control flow: userspace submission creates a `lima_sched_task`, arms a `drm_sched_job`, pushes it to the scheduler, and receives the finished fence. `run_job` resumes runtime PM, creates a pipe fence, records `current_task`, flushes L2 caches, switches MMU(s) to the task VM, traces the run, and calls pipe-specific `task_run`. IRQ completion calls `lima_sched_pipe_task_done`, which either signals the fence and idles PM or schedules recovery/fault handling. Timeout handling masks processor IRQs, stops the scheduler, records blame, optionally dumps task buffers, resumes page faults, clears current state, idles PM, resubmits jobs, and restarts the scheduler.

State and persistence: pipe state includes current task/VM, fence context/sequence, error flag, work item, and callback table. Task state holds BO references, VM ref, frame, heap, recoverability, and pipe fence. Error dumps persist in `ldev->error_task_list` until consumed elsewhere.

Dependencies and integration points: depends on DRM scheduler/fence APIs, Lima PM/devfreq, MMU, L2 cache, GEM/BO, tracepoints, and pipe-specific GP/PP callbacks. It is the bridge between submit ioctls and hardware engines.

Risks and test signals: race windows around IRQ latency, timeout versus fence completion, and RCU fence release are critical. BO/VM reference leaks or missing `lima_vm_bo_del` can leak VA mappings. Test with normal submits, forced hangs, MMU faults, reset recovery, runtime suspend/resume, and debug dump retrieval.
