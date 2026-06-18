# sources/distributed-fs/ceph-client/drivers/clocksource/timer-probe.c

Purpose: central early boot dispatcher for clocksource timer drivers registered in the `__timer_of_table` linker section and ACPI timer table.

Important APIs/types/functions: `timer_probe()` iterates `for_each_matching_node_and_match()` over `__timer_of_table`; `__timer_of_table_sentinel` marks section end. It treats `match->data` as `of_init_fn_1_ret` and also calls `acpi_probe_device_table(timer)`.

Control flow: for every matching DT node, skip unavailable nodes, call the registered init function, log failures except `-EPROBE_DEFER`, and count successful timers. Then add successful ACPI probes. If no timers were initialized, emit a critical log.

State/persistence: no driver-owned persistent state besides local count. It consumes linker-section registrations created by `TIMER_OF_DECLARE()` macros elsewhere.

Dependencies/integration: OF core, ACPI probe tables, clocksource header declarations, and architecture boot calling `timer_probe()`.

Risks: init functions must be idempotent or self-filter when multiple compatible nodes match; deferred probe is only skipped/log-suppressed here and not retried by this function itself; critical no-timer log is fatal for platform bring-up diagnosis. Test signals include correct linker table population, disabled DT nodes being skipped, ACPI timer discovery, and expected logs for missing/misconfigured timers.
