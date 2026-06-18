# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-pseries.c

Purpose: registers pSeries PowerPC guest cpuidle states for shared and dedicated SPLPAR partitions, using snooze polling and hypervisor cede operations.

Important APIs and functions: `snooze_loop()` polls with low SMT priority until reschedule or timeout. `check_and_cede_processor()` prepares IRQ state and calls `cede_processor()`. `dedicated_cede_loop()` sets `donate_dedicated_cpu` and a cede latency hint in the LPPACA before ceding; `shared_cede_loop()` simply cedes. Extended cede parsing uses RTAS `ibm,get-system-parameter` token 45 to inspect firmware latency records, and `fixup_cede0_latency()` uses the minimum nonzero extended latency as a proxy for CEDE(0). Probe selects shared or dedicated state tables by firmware feature and partition type, then registers cpuidle and hotplug enable/disable callbacks.

Control flow and state: global state includes the selected state table, max state count, snooze timeout, extended cede records, and cede latency hints. Dedicated tables contain snooze and CEDE; shared tables contain snooze and Shared Cede. Snooze timeout is derived from the next state's target residency.

Dependencies and integration points: depends on pSeries firmware SPLPAR, LPPACA fields, RTAS, hypervisor cede wrappers, timebase conversions, runlatch/SMT priority helpers, and CPU hotplug.

Risks and test signals: risks include RTAS payload fixed to 16 records, cede latency fixup only on POWER10/arch 3.1 paths, IRQ state subtleties around H_CEDE returning with interrupts enabled, polling overhead in snooze, and no registration outside SPLPAR. Test signals include correct shared/dedicated table selection, RTAS latency parsing logs, CEDE exit latency adjusted when firmware data exists, LPPACA donate flag restored after idle, and hotplug disabling cpuidle devices for dead CPUs.
