# sources/distributed-fs/ceph-client/arch/s390/kernel/idle.c

Purpose: provides s390 CPU idle entry and idle accounting. It loads an enabled-wait PSW and accounts time spent waiting when an interrupt exits idle.

Important APIs and state: `DEFINE_PER_CPU(struct s390_idle_data, s390_idle)` stores `clock_idle_enter`, `timer_idle_enter`, optional MT diagnostic cycles, `idle_time`, and `idle_count`. `arch_cpu_idle()` enters wait state; `account_idle_time_irq()` is called by interrupt entry code when `CIF_ENABLED_WAIT` was set. Sysfs device attributes expose `idle_count` and `idle_time_us`.

Control flow: `arch_cpu_idle()` clears delayed nohz, marks enabled-wait, optionally stores MT diagnostic counters with `stcctm()`, snapshots TOD and CPU timer values, enables branch prediction with `bpon()`, then loads a PSW accepting external, I/O, and machine-check interrupts. `do_io_irq()` and `do_ext_irq()` clear `CIF_ENABLED_WAIT`, update idle timers, call `account_idle_time_irq()`, and strip wait/enabled interrupt bits from the resumed PSW.

Dependencies and integration: depends on lowcore interrupt clocks, CPU timer helpers, CPU-MF MT diagnostics, power trace headers, s390 idle flags, and generic `account_idle_time()`. `arch_cpu_idle_dead()` delegates CPU death to `cpu_die()`.

Risks and test signals: incorrect flag handling can resume in wait state or double-account idle time. Validate with CPU idle stats, `/sys/devices/system/cpu/cpu*/idle_*`, interrupt wakeups from idle, NOHZ behavior, and CPU hotplug/offline paths.
