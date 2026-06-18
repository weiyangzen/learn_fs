# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4d_irq.c

Purpose: implements sun4d SS1000/SC2000 interrupt controller support, including SBUS IRQ demultiplexing, IRQ chip operations, timer setup, and SBI distribution.

Important APIs/types/functions: `sun4d_handler_irq()`, `sun4d_sbus_handler_irq()`, `sun4d_mask_irq()`, `sun4d_unmask_irq()`, `sun4d_build_device_irq()`, `sun4d_init_sbi_irq()`, `sun4d_init_IRQ()`, `sun4d_init_timers()`, `sun4d_distribute_irqs()`, and `sun4d_load_profile_irq()` use `struct sun4d_handler_data`, `board_to_cpu`, `pil_to_sbus`, `sun4d_imsk_lock`, and `sparc_config`.

Control flow: top-level IRQ handling clears the CPU interrupt latch, optionally handles IPI work, enters generic IRQ accounting, and dispatches either CPU-local IRQ buckets or SBUS interrupts. SBUS handling reads BW interrupt masks by SBUS level, acknowledges pending SBI bits, walks pending slots, maps encoded board/level/slot IRQ buckets, invokes `generic_handle_irq()`, and releases SBI bits. Initialization maps bootbus timer registers, registers the L10 timer IRQ, configures clocksource/clockevent features, clears PROM-pending SBI IRQs, and wires `sparc_config` callbacks.

State and persistence: maintains MMIO timer pointer, board-to-CPU routing, IRQ handler data allocations, and controller masks. Hardware interrupt mask state is runtime only.

Dependencies and integration points: depends on Open Firmware `sbi`/`cpu-unit` topology, BW/SBI register helpers, generic IRQ buckets, clocksource/timer code, SMP sun4d IPI code, and trap-table fixups for level-14 timers.

Risks: IRQ encoding must match board/level/slot hardware or devices misroute. SMP mask updates need `sun4d_imsk_lock`. Timer register mapping and trap-table patching happen early and halt on fatal setup failures.

Test signals: device IRQ allocation from OF nodes, SBUS slot interrupt dispatch, timer interrupt delivery, SMP IPI at `SUN4D_IPI_IRQ`, profile timers, SBI pending-IRQ cleanup, and IRQ routing to selected CPUs.
