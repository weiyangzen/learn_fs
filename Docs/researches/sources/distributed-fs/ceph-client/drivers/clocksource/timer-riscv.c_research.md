# sources/distributed-fs/ceph-client/drivers/clocksource/timer-riscv.c

Purpose: generic RISC-V timer driver for per-hart clockevents and global clocksource/sched_clock using the architectural time counter, SBI timer calls, or Sstc supervisor timer compare CSRs.

Important APIs/types/functions: static key `riscv_sstc_available` selects CSR compare programming versus `sbi_set_timer()`. Per-CPU `riscv_clock_event`; `riscv_clocksource`; `riscv_cs_get_mult_shift()` exports conversion parameters. `riscv_timer_init_common()` registers source, percpu IRQ, detects Sstc, and installs hotplug.

Control flow: DT init validates hartid/cpuid and only initializes common path on the boot CPU’s CPU node, also reading `riscv,timer-cannot-wake-cpu`. ACPI init reads RHCT wake flag. Common init maps `RV_IRQ_TIMER` through the interrupt controller domain, registers 64-bit clocksource and sched_clock, requests percpu IRQ, enables Sstc static branch if ISA extension exists, then sets CPU hotplug callbacks. CPU startup stops pending timer, sets features/rating, registers event, and enables IRQ. Interrupt stops timer and dispatches.

State/persistence: static clocksource and per-CPU event structures, global IRQ, static key, and wake capability flag.

Dependencies/integration: RISC-V arch timebase, IRQ domains, SBI, Sstc CSRs, DT/ACPI, CPU hotplug, VDSO clock mode.

Risks: relies on synchronized hart timers; 32-bit Sstc write ordering is critical; init is gated to one CPU node; cannot-wake flag affects deep idle. Tests include DT and ACPI boot, Sstc and SBI paths, CPU hotplug, exported mult/shift users, and timer interrupt after idle.
