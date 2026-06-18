# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_job.h

Purpose: declares Ethos-U job state and job-management entry points used by the driver and ioctl layer.

Important APIs/types: `struct ethosu_job` embeds a DRM scheduler job, device pointer, command BO, up to eight region BOs and their region numbers, region count, requested SRAM size, inference-done scheduler fence, hardware done fence, and kref. Public functions initialize/finalize device scheduler state, initialize/destroy per-file scheduler entity state, and handle the submit ioctl.

Control flow: open initializes per-file scheduler entity; submit allocates `ethosu_job` and pushes it; scheduler backend runs and frees jobs; IRQ/timeout paths signal or reset.

State and persistence: per-job runtime state persists from ioctl submission until scheduler cleanup and kref release. No disk state.

Dependencies: Linux kref, DRM scheduler, Ethos-U region constants from device header.

Risks: fixed region array size must match hardware `NPU_BASEP_REGION_MAX`. Fence ownership is split between scheduler and IRQ completion, so cleanup must drop both.

Test signals: scheduler init/fini, per-file open/close, job kref lifetime, region array bounds, and submit ioctl ABI validation.
