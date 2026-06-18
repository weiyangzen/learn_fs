<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.c

### Purpose
`ivpu_pm.c` implements ivpu power management, runtime suspend/resume, cold/warm boot preparation, reset/recovery, job timeout detection, and DCT duty-cycle control.

### Important APIs, Types, And Functions
PM callbacks are `ivpu_pm_suspend_cb()`, `ivpu_pm_resume_cb()`, `ivpu_pm_runtime_suspend_cb()`, and `ivpu_pm_runtime_resume_cb()`. Reset callbacks are `ivpu_pm_reset_prepare_cb()` and `ivpu_pm_reset_done_cb()`. Runtime helpers are `ivpu_rpm_get()`, `ivpu_rpm_put()`, `ivpu_pm_init()`, `ivpu_pm_enable()`, `ivpu_pm_disable()`, and `ivpu_pm_disable_recovery()`. Recovery/timeout APIs include `ivpu_pm_trigger_recovery()`, `ivpu_start_job_timeout_detection()`, and `ivpu_stop_job_timeout_detection()`. DCT APIs include init/enable/disable and IRQ work handling.

### Control Flow
Suspend prepares for reset, shuts down hardware, and prepares warm boot when possible. Resume restores PCI D0/state, powers hardware, enables MMU, boots firmware, and falls back to cold boot if warm boot fails. Recovery work disables runtime PM, optionally dumps firmware state and coredump, suspends, prepares cold boot, aborts jobs, cleans metric streams, resumes, updates runtime PM state, clears reset pending, and emits a uevent. Job timeout work queries heartbeat; if it does not progress, or if inference retry limits are exceeded, it triggers full recovery for OS scheduling or state dump/coredump plus context abort work for HWS scheduling.

### State, Persistence, And Dependencies
State lives in `vdev->pm`: reset lock, recovery work, delayed timeout work, reset counters, engine reset counter, reset-pending flag, and DCT active percent. Firmware boot state is updated through `vdev->fw->next_boot_mode`, warm boot entry point, and last heartbeat. Dependencies include PCI power state, runtime PM, hardware power/reset/idle helpers, MMU enable/disable, firmware load/boot/shutdown, IPC reset, fw log reset, job abort, metric cleanup, coredump, and JSM power/debug calls.

### Integration Points
Job submission takes `reset_lock` for read, and reset/recovery takes it for write. MMU is disabled before runtime suspend and enabled during resume. Job completion starts/stops timeout detection. Sysfs exposes reset/engine counters indirectly through driver state. Hardware BTRS DCT requests are serviced by `ivpu_pm_irq_dct_work_fn()`.

### Risks
Reset and runtime PM sequencing is high risk: stale jobs, active metric streams, or queued recovery work during suspend can break assumptions. `pm_runtime_get_if_active()` in abort work and sysfs frequency reads must be balanced. Recovery can be disabled by debug parameter, which leaves hangs unrecovered. Heartbeat-based timeout detection must coordinate with firmware scheduling mode and non-progress inference limits. DCT state is stored before firmware command success, so failure leaves requested state in `dct_active_percent`.

### Test Signals
System suspend/resume, runtime autosuspend/resume, warm-boot fallback to cold boot, PCI FLR/reset callbacks, job timeout in OS and HWS modes, recovery uevent emission, coredump on timeout/recovery, active job abort after reset, active metric stream cleanup, DCT enable/disable from IRQ request, and module parameters for timeout/recovery behavior are high-signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.c -->
