# sources/distributed-fs/ceph-client/drivers/clocksource/timer-rtl-otto.c

Purpose: Realtek Otto timer driver using the first N timers as per-CPU clockevents and the next timer as a stable 28-bit clocksource/sched_clock.

Important APIs/types/functions: per-CPU `timer_of rttm_to` requests base/clock/IRQ; `struct rttm_cs` wraps source `timer_of` and clocksource. Register helpers set period, mode, divisor, IRQ bits. `rttm_bounce_timer()` works around a late-stop/start hardware window. `rttm_probe()` initializes all timers and hotplug.

Control flow: probe loops possible CPUs, assigning base/IRQ index equal to CPU and initializing each event timer, then initializes clocksource at index `num_possible_cpus()`. It enables source in timer mode, registers clocksource/sched_clock, and installs CPU hotplug. CPU startup forces IRQ affinity, registers event at fixed 3.125 MHz, and enables IRQ. Event callbacks bounce/stop/program/restart in counter or timer mode; ISR acks and dispatches.

State/persistence: per-CPU static timer_of objects, global `rttm_cs`, fixed target tick rate, and hardware divisor derived from input clock. No dynamic teardown except rollback on early per-CPU init failure.

Dependencies/integration: compatible `realtek,otto-timer`, `timer-of`, CPU hotplug, per-CPU IRQs, IRQ affinity, CCF clock.

Risks: requires at least `num_possible_cpus()+1` timer resources; source init failure only logs and still installs hotplug; divisor calculation assumes clock rate supports 3.125 MHz; hardware workaround is timing-sensitive. Tests include resource-count DT validation, CPU hotplug/affinity, one-shot near min delta, source timer index, and monotonic 28-bit source.
