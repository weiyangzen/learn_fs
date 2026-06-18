# sources/distributed-fs/ceph-client/include/trace/events/power.h

Purpose: Defines broad power-management tracepoints covering CPU idle/frequency, PSCI domain idle, wakeup sources, power domains, device PM callbacks, suspend/resume phases, PM QoS, device PM QoS, pstate samples, CPU frequency limits, idle misses, and guest halt polling.

Important APIs/types/functions: Event classes include `cpu`, `psci_domain_idle`, `wakeup_source`, `power_domain`, `cpu_latency_qos_request`, `pm_qos_update`, and `dev_pm_qos_request`. Standalone events include `cpu_idle_miss`, `pstate_sample`, `cpu_frequency_limits`, `device_pm_callback_start`, `device_pm_callback_end`, `suspend_resume`, and `guest_halt_poll_ns`.

Control flow: CPU idle/frequency governors, PSCI, PM domains, wakeup-source accounting, driver-core PM callbacks, suspend/resume core code, PM QoS updates, and virtualization halt-poll code emit events as state changes or callbacks start/end. Trace entries snapshot device names, callback pointers, event names, states, request values, timestamps, and CPU IDs.

State and persistence: No state is owned. It observes runtime PM state in devices, domains, QoS constraints, CPU policy, and suspend/resume sequencing. Trace records are transient.

Dependencies and integration points: Depends on cpufreq, ktime, PM QoS, trace events, and tracepoints. It integrates with driver core, CPU idle/freq, PM domains, wakeup-source infrastructure, suspend/hibernate, and KVM halt-poll tuning.

Risks and test signals: Risks include tracing during fragile suspend/noirq windows, callback pointer symbol drift, inconsistent CPU state naming, and event storms. Test suspend-to-idle/RAM, hibernation, runtime PM, cpufreq transitions, wakeup-source leaks, PM QoS add/update/remove, PSCI idle domains, and guest halt polling changes.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/power.h` completely for this pass (531 lines, 11479 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/power.h_research.md`.
