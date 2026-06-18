<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/irq_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/irq_helpers.c

Purpose: framework helper for regulator drivers that report fault or warning events through IRQs, including retry, cached error, notification, and fatal recovery handling.

Important APIs/types/functions: `struct regulator_irq` stores descriptor, IRQ, retry count, event data, and delayed work. Public APIs are `regulator_irq_helper()`, `regulator_irq_helper_cancel()`, and `regulator_irq_map_event_simple()`. Internal helpers update `rdev->cached_err` under `err_lock`.

Control flow: the threaded IRQ maps a hardware event to one or more regulator states, optionally skips events when relevant regulators are off, disables asserted IRQ lines, emits notifier events, records cached errors, and schedules delayed re-enable/status polling. Workqueue logic calls optional `renable()` until clear or fatal count is exceeded, then calls `die()` or `hw_protection_trigger()`.

State and persistence: per-helper retry count and cached regulator error bits persist during driver lifetime. There is no disk state.

Dependencies and integration: integrates with genirq, delayed workqueues, regulator notifier chains, cached-error reporting, and system hardware-protection shutdown.

Risks and test signals: `regulator_irq_helper_cancel()` sets only a local `h = NULL`, not `*handle`, so callers do not get a nulled handle despite the comment. `skip_off` assumes `is_enabled` exists. Test status-map failures, persistent asserted IRQs, fatal recovery, high-priority work, cached-error clearing, and cancellation races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/irq_helpers.c -->
