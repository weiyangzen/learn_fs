# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_kernel.c

Purpose: Implements LEON platform IRQ, extended IRQ, timer, clockevent, and clocksource initialization for SPARC32 LEON systems.

Important APIs/types/functions: Global register pointers `leon3_irqctrl_regs` and `leon3_gptimer_regs` point to IRQMP and GPTIMER MMIO maps. `leon_get_irqmask()`, `leon_build_device_irq()`, `leon_update_virq_handling()`, `leon_unmask_irq()`, `leon_mask_irq()`, `leon_eoi_irq()`, and `leon_set_affinity()` define the LEON IRQ chip. `leon_eirq_setup()` registers an extended IRQ demux. `leon_cycles_offset()`, `leon_init_timers()`, `leon_clear_clock_irq()`, and SMP `leon_percpu_timer_ce_interrupt()` drive timers. `leon_init_IRQ()` installs LEON callbacks into `sparc_config`.

Control flow: Boot scans `/ambapp0` for system ID, IRQMP, and GPTIMER nodes, honors AMP timer ownership, selects timer index and IRQ, detects whether the timer pending bit is write-clearable, adjusts IRQ controller selection, masks boot CPU IRQs, optionally registers extended IRQ demuxing, patches SMP trap behavior, and requests the timer IRQ. The IRQ chip masks/unmasks bits in per-CPU IRQMP mask registers according to affinity.

State and persistence: Runtime state is MMIO register state, selected timer index, ACK mask, GPTIMER IRQ number, extended IRQ number, debug globals, and `sparc_config` function pointers. No disk persistence exists.

Dependencies and integration points: It integrates Open Firmware device nodes, LEON AMBA definitions, IRQ core descriptors, SPARC timer framework, SMP clockevents, cache patching through `local_ops`, and low-level IRQ mapping from `irq_map`.

Risks and test signals: Incorrect device-tree parsing or IRQMP register selection breaks all interrupts. AMP timer skipping and shared GPTIMER IRQs are board-sensitive. Tests include LEON boot, timer ticks, extended IRQ dispatch, IRQ affinity changes on SMP, level-triggered EOI handling, AMP configurations, and missing-node failure paths.
