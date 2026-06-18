# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4m_irq.c

Purpose: implements sun4m interrupt register support, IRQ mask mapping, NMI/error reporting, timer registration, and `sparc_config` IRQ callbacks.

Important APIs/types/functions: globals `sun4m_irq_percpu[]` and `sun4m_irq_global` are consumed by entry/SMP code. Key routines are `sun4m_mask_irq()`, `sun4m_unmask_irq()`, `sun4m_build_device_irq()`, `sun4m_clear_clock_irq()`, `sun4m_nmi()`, `sun4m_unmask_profile_irq()`, `sun4m_clear_profile_irq()`, `sun4m_load_profile_irq()`, `sun4m_init_timers()`, and `sun4m_init_IRQ()`.

Control flow: initialization maps interrupt registers from the OF `interrupt` node, masks global sources, clears per-CPU masks, optionally programs interrupt target, then sets `sparc_config` callbacks. Timer init maps per-CPU/global counter addresses from the OF `counter` node, configures timer mode, selects L10 clocksource and L10/L14 event features, registers the timer IRQ, clears per-CPU profile timers, and patches the level-14 trap table under SMP. IRQ build converts OBP priority values into PILs and mask bits from `sun4m_imask`, then attaches a level IRQ chip.

State and persistence: stores MMIO register pointers and per-IRQ handler mask/percpu data. Hardware mask/timer registers are runtime state.

Dependencies and integration points: depends on OF `interrupt`/`counter` properties, SBUS MMIO helpers, generic IRQ buckets, timer/clockevent code, sun4m SMP IPIs, and trap-table patching.

Risks: sun4m IRQ priority encodings are ambiguous without `intr` property class bits. Wrong mask bit enables/disables unrelated devices. NMI path halts after reporting asynchronous errors.

Test signals: device IRQ allocation for onboard/SBUS/VME priorities, masking/unmasking, L10 timer interrupt, L14 profile timer on SMP, NMI error log, and boot on systems with two or four CPU interrupt registers.
