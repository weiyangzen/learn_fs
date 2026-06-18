# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_job.c

Purpose: implements Ethos-U job submission, DRM scheduler integration, hardware register programming, IRQ completion, timeout/reset handling, per-file scheduler entities, and submit ioctl validation.

Important APIs/functions: `ethosu_ioctl_submit()` copies an array of jobs and submits each. `ethosu_ioctl_submit_job()` validates SRAM/region handles against command metadata, rejects command BOs as region BOs, checks region size <= BO size, allocates fences, initializes a DRM scheduler job, and pushes it. `ethosu_job_push()` locks reservations, adds implicit dependencies, resumes runtime PM, arms and queues the scheduler job, and attaches output fences. `ethosu_job_run()` initializes the hardware completion fence, sets `in_flight_job`, and calls `ethosu_job_hw_submit()` to program base pointers, SRAM pointer, queue base/size, and run command. IRQ handlers clear IRQ and signal the done fence. Timeout stops scheduler, force-suspends/resumes hardware, and restarts scheduler.

Control flow: per-file scheduler entity queues jobs into a single-credit scheduler. Hardware has one in-flight job tracked under `job_lock`.

State and persistence: `ethosu_job` holds references to command and region BOs, region numbers, SRAM size, scheduler and IRQ fences, and kref. Device stores scheduler, in-flight job, fence context, and sequence.

Dependencies: DRM scheduler/fences/reservations, DRM GEM DMA, PM runtime, MMIO registers, gen_pool SRAM, IRQ.

Risks: timeout reset must clear `in_flight_job` and restart scheduler safely. Reservation/fence ordering must protect output BOs. Multiple jobs are submitted sequentially; failure stops later jobs without rolling back earlier queued jobs.

Test signals: submit valid/invalid jobs, missing/extra region handles, SRAM region conflict, implicit fence dependencies, IRQ completion, timeout progress/no-progress branches, reset recovery, and close with queued jobs.
