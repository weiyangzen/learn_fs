<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-r4k.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-r4k.c

### Purpose
`cevt-r4k.c` implements the standard MIPS CP0 Count/Compare clockevent device and compare interrupt handling.

### Important APIs, Types, And Functions
Important functions include `mips_next_event()`, `calculate_min_delta()`, `handle_perf_irq()`, `c0_compare_interrupt()`, `mips_event_handler()`, `c0_compare_int_usable()`, `r4k_clockevent_init()`, `r4k_register_clockevent()`, and CPU notifier hooks when enabled. It defines per-CPU `mips_clockevent_device` and `cp0_timer_irq_installed`.

### Control Flow
Next-event programming writes Compare to Count plus delta and detects already-expired events. Initialization verifies usable compare interrupt behavior, computes a virtualization-tolerant minimum delta, configures per-CPU clockevent attributes, and registers the device. The interrupt handler arbitrates shared perf-counter interrupts before acknowledging timer interrupts and calling the event handler.

### State, Persistence, And Dependencies
State is CP0 Count/Compare/Cause, per-CPU clockevents, global IRQ installation flag, CPU frequency notifier state, and perf IRQ sharing state. Dependencies include clockchips, perf IRQ hooks, CPU feature flags, and MIPS time globals.

### Integration Points
This is the common timer for many MIPS CPUs. It feeds Linux tick/nohz, works with perf counter overflow sharing, and is paired with `csrc-r4k.c` for clocksource.

### Risks
Virtualized Count/Compare access can make small deltas unreliable. Pre-R2 CPUs cannot reliably distinguish perf and timer interrupts. CPU frequency changes can invalidate timer assumptions.

### Test Signals
Run clockevent selftests under native and virtual MIPS, perf interrupt sharing tests, CPU frequency transition tests, nohz/oneshot tick tests, and compare-interrupt usability probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-r4k.c -->
