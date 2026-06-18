# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_job.c

## Purpose
This file implements the Panfrost job manager: DRM scheduler integration, hardware job submission, job IRQ handling, fences, reset recovery, profiling/accounting, and per-file JM context management.

## Important APIs, Types, and Functions
Key public functions are `panfrost_jm_init/fini/open/close`, `panfrost_jm_ctx_create/destroy/get/put/from_handle`, `panfrost_job_get_slot`, `panfrost_job_push`, `panfrost_job_put`, IRQ suspend/reset helpers, and `panfrost_jm_is_idle`. Internal pieces include Panfrost fences, scheduler ops, hardware submit, IRQ handlers, timeout handling, and reset work.

## Control Flow
Userspace submit creates a scheduler job elsewhere, then `panfrost_job_push` locks BO reservations, arms the scheduler job, adds implicit dependencies, queues it, and attaches write fences. Scheduler `run_job` creates a Panfrost fence and submits to hardware. Hardware submit resumes runtime PM, gets an MMU AS, records devfreq busy, writes job chain address/config/affinity/flush-id, enqueues in one of two hardware subslots, starts cycle counting if needed, and issues START. IRQ handling dequeues done or failed jobs, signals fences, releases AS/runtime PM/devfreq, requeues second-slot jobs when safe, or schedules reset. Timeouts produce devcoredumps and reset the GPU.

## State and Persistence Behavior
State includes per-slot schedulers, fence contexts/seqnos, `pfdev->jobs[slot][subslot]`, scheduled jobs list, reset work/pending flag, per-file JM context xarray, job refcounts, BO mapping refs, done/render fences, profiling timestamps, and engine usage counters.

## Dependencies and Integration Points
It integrates DRM GPU scheduler, DMA fences, dma-resv, runtime PM, Panfrost MMU AS allocation, devfreq, GPU counters, GEM mappings, devcoredump, reset code, UAPI JM context priority, and fdinfo accounting.

## Risks
Reset and IRQ paths are concurrency-heavy and must balance runtime PM, devfreq, MMU AS refs, cycle counter refs, job refs, and fences. Jobchain disambiguation controls whether two hardware slots can be used. Destroying JM contexts must hard-stop in-flight jobs without touching freed file state. Timeout handling must distinguish interrupt latency from real hangs.

## Test Signals
Run parallel fragment/vertex submissions, syncobj and implicit-fence tests, context destroy with in-flight jobs, high-priority permission checks, GPU timeout/reset, devfreq/cycle counter balance, fd close races, IRQ storm/fault injection, and scheduler debugfs inspection.
