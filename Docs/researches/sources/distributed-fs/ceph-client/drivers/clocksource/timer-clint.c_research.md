# sources/distributed-fs/ceph-client/drivers/clocksource/timer-clint.c

Purpose: supports RISC-V CLINT MMIO timers and software interrupts, mainly for M-mode/no-MMU systems. It registers the CLINT mtime counter as clocksource/sched_clock, per-hart mtimecmp registers as one-shot clockevents, and CLINT software interrupt registers as SMP IPIs.

Important APIs, types, and functions: global pointers include `clint_ipi_base`, `clint_timer_cmp`, and `clint_timer_val`; `clint_timer_freq` comes from `riscv_timebase`. Important routines are `clint_send_ipi()`, `clint_clear_ipi()`, `clint_ipi_interrupt()`, `clint_get_cycles64()`, `clint_clock_next_event()`, `clint_timer_starting_cpu()`, `clint_timer_dying_cpu()`, `clint_timer_interrupt()`, and `clint_timer_init_dt()`.

Control flow: DT init validates all interrupt specifiers are either timer or software interrupt, maps both IRQs through parent domains, maps CLINT registers, sets global bases, registers clocksource and sched_clock, requests the timer percpu IRQ, creates an IPI mux and chained software interrupt handler on SMP, then installs CPU hotplug callbacks. CPU startup registers the local clockevent and enables timer and IPI percpu IRQs. `set_next_event` enables timer interrupts in CSR_IE and writes current time plus delta to the hart's compare register.

State and persistence: runtime state is global MMIO pointers, percpu clockevent structs, IRQ mappings, and IPI mux state. On M-mode builds `clint_time_val` is exported for legacy access. No persistent storage exists.

Dependencies and integration points: integrates with RISC-V hart ID mapping, CSR interrupt bits, irqdomain/chained IRQ APIs, percpu IRQs, IPI mux, clocksource, clockevents, sched_clock, and OF timer declarations.

Risks: hart ID indexing must match CLINT register layout. The code assumes both timer and IPI IRQs are present. Timer ISR clears `IE_TIE`, so future events rely on `set_next_event` re-enabling it. Test signals include timer and soft IRQ validation, SMP IPIs through mux, CPU hotplug event setup, correct 32-bit lo/hi counter reads on non-64-bit builds, and clocksource registration at `riscv_timebase`.
