# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_job.h

Purpose: declares Rocket job/task structures and scheduler-facing functions.

Important APIs and types: `struct rocket_task` stores command-buffer DMA address and register-command count. `struct rocket_job` embeds `drm_sched_job`, tracks input/output BO arrays, task array/progress, scheduler and hardware fences, IOMMU domain, parent device, and refcount. Declares submit and scheduler lifecycle APIs.

Control flow: UAPI submit data is copied into `rocket_job`; scheduler code advances `next_task_idx`; IRQ code signals `done_fence`; cleanup releases all refs through `kref`.

State and persistence: job objects live from ioctl submission until scheduler and hardware references are dropped. Per-file scheduler entity setup is declared here but stored in `rocket_file_priv`.

Dependencies and integration: includes DRM driver/scheduler headers plus Rocket core and driver-private state.

Risks and test signals: verify refcount ownership between ioctl, scheduler free, and IRQ completion; ensure task_count and BO arrays are validated before hardware submission.
