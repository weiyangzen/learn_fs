# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pm.c

Purpose: implements generic AMD XDNA runtime and system PM wrappers used by the PCI driver, delegating hardware-specific suspend/resume to `amdxdna_dev_ops`.

Important APIs/functions: `amdxdna_pm_suspend()` and `amdxdna_pm_resume()` lock `dev_lock`, call hardware `suspend`/`resume` if present, and log return status. `amdxdna_pm_resume_get()` wraps `pm_runtime_resume_and_get()` and marks the device suspended on failure. `amdxdna_pm_suspend_put()` drops an autosuspend reference. `amdxdna_pm_init()` marks runtime PM active, sets a 5s autosuspend delay, enables autosuspend, allows runtime PM, and drops the initial ref. `amdxdna_pm_fini()` gets a noresume ref and forbids runtime PM.

Control flow: hardware init calls `amdxdna_pm_init()` after successful AIE2 startup; cleanup calls fini before hardware stop. User ioctls and DPM changes resume the device around hardware access.

State and persistence: state is Linux PM core runtime state on the device plus hardware state restored by ops callbacks. No independent storage.

Dependencies: Linux PM runtime, DRM device lookup, AMD XDNA driver structs.

Risks: suspend/resume callbacks assume `dev_get_drvdata()` points at `amdxdna_dev`. Returning `-EOPNOTSUPP` if ops are absent may not be desirable for future hardware. Failure handling in `resume_get()` changes PM state.

Test signals: runtime autosuspend/resume around ioctl and submit paths, system suspend/resume, PM failure injection, remove while suspended, and lockdep for `dev_lock` interactions.
