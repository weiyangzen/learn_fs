# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_drv.h

Purpose: declares the per-file private state for the Ethos-U DRM accel driver.

Important type: `struct ethosu_file_priv` stores the `ethosu_device` pointer and a DRM scheduler entity for jobs submitted by that file.

Control flow: `ethosu_open()` allocates this structure and calls `ethosu_job_open()` to initialize the scheduler entity; `ethosu_postclose()` destroys it through `ethosu_job_close()`.

State and persistence: per-open runtime state only. It persists until DRM postclose.

Dependencies: DRM GPU scheduler and forward declaration of `ethosu_device`.

Risks: job submission assumes `file->driver_priv` is a valid initialized `ethosu_file_priv`; open failure paths must not publish partial state.

Test signals: open/postclose lifecycle, scheduler entity cleanup with queued jobs, and invalid file-private handling in submit paths.
