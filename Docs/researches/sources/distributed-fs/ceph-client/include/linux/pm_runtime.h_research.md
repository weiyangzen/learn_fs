# sources/distributed-fs/ceph-client/include/linux/pm_runtime.h

Purpose: provides the inline runtime PM API used by drivers to manage per-device active/suspended state, usage counts, autosuspend, PM workqueue dispatch, supplier links, and system-sleep handoff.

Important APIs and types: flag bits `RPM_ASYNC`, `RPM_NOWAIT`, `RPM_GET_PUT`, `RPM_AUTO`, and `RPM_TRANSPARENT` parameterize core `__pm_runtime_idle/suspend/resume()`. Public helpers include synchronous and asynchronous idle/suspend/resume calls, `pm_runtime_get*()` and `pm_runtime_put*()` usage-count wrappers, autosuspend helpers, status setters, enable/disable/block/unblock, no-callback/irq-safe markers, autosuspend-delay control, memalloc-noio, supplier get/put, link lifecycle hooks, device-managed enable/get helpers, and scoped guards such as `PM_RUNTIME_ACQUIRE()`.

Control flow: drivers enable runtime PM, initialize status while disabled, increment usage before accessing hardware, resume the device if needed, mark last busy, then drop usage using idle/autosuspend/suspend variants. The inline wrappers translate common patterns into core calls with the right flags; some variants intentionally leave usage counts incremented on errors while `pm_runtime_resume_and_get()` unwinds failures. Force suspend/resume bridges runtime PM callbacks into system sleep via `DEFINE_RUNTIME_DEV_PM_OPS()`.

State and persistence: state lives in `dev->power`: runtime status, usage count, disable depth, child dependencies, autosuspend delay/last busy, irq-safe/no-callback flags, supplier links, and blocked status. No persistent data is stored, but incorrect counters or status can permanently pin devices on/off until reprobe.

Dependencies and integration points: integrates with the device core, PM workqueue `pm_wq`, system sleep callbacks, devres, device links/suppliers, PM domains, PM QoS resume constraints, jiffies/ktime, and cleanup guard macros. With `CONFIG_PM` disabled, most operations are no-ops or return fixed values; with sleep disabled, force-resume returns `-ENXIO`.

Risks and test signals: risks include unbalanced get/put, using `pm_runtime_get_sync()` without unwinding errors, changing status while PM is enabled, autosuspend not disabled on manual teardown, IRQ-safe callbacks that sleep, supplier link ordering bugs, and guard misuse without checking `PM_RUNTIME_ACQUIRE_ERR()`. Test runtime suspend/resume callback paths, error unwinding, autosuspend expiration, system sleep force suspend/resume, devm cleanup, supplier dependency behavior, IRQ-safe devices, and builds with PM disabled.
