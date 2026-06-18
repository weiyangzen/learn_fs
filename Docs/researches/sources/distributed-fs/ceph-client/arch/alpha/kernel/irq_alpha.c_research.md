# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_alpha.c

**Purpose:** Implements the Alpha PAL interrupt entry C dispatcher and machine-check support glue. It routes interrupt types to IPI, RTC, machine-check, device, and performance handlers, initializes architecture IRQ handling, resets ISA DMA, reports generic machine-check info, and installs the RTC IRQ.

**Important APIs/types/functions:** Exposes optional `__min_ipl`, `perf_irq`, `do_entInt()`, `common_init_isa_dma()`, `init_IRQ()`, `process_mcheck_info()`, and `init_rtc_irq()`. It uses `alpha_mv.machine_check`, `alpha_mv.device_interrupt`, and `alpha_mv.init_irq` from the machine vector.

**Control flow:** Assembly `entInt` calls `do_entInt(type, vector, la_ptr, regs)`. The dispatcher disables local interrupts, switches on PAL interrupt type, and calls `handle_ipi()`, `handle_irq(RTC_IRQ)`, `alpha_mv.machine_check()`, `alpha_mv.device_interrupt()`, or `perf_irq()`, with `set_irq_regs()` around handlers that need current register context. `init_IRQ()` writes the interrupt entry vector through `wrent()` before invoking platform IRQ init. `process_mcheck_info()` suppresses expected machine checks used by probing, otherwise prints vector/PC/code, decodes common PAL reason codes, dumps registers, and optionally dumps logout memory.

**State and persistence behavior:** Mutates per-CPU expected/taken machine-check flags, global `perf_irq`, ISA DMA controllers, IRQ register context, and PAL interrupt entry state. No persistent data.

**Dependencies and integration points:** Entry assembly, machine vectors, SMP IPI handlers, Alpha PAL operations, DMA register constants, `rtc_timer_interrupt`, and generic IRQ functions all meet here.

**Risks:** Interrupts intentionally remain disabled until PAL return because some PALcode has RTI/IPL issues. Expected machine-check state is delicate for probing paths. A module can override `perf_irq`, so it must preserve interrupt-context constraints. Incorrect vector type routing can turn machine checks into device IRQs or vice versa.

**Test signals:** Boot and verify `wrent(entInt)`, RTC timer IRQ registration, device IRQ dispatch through current machine vector, machine-check probe suppression, real machine-check reporting, performance interrupt override modules, and ISA DMA reset behavior on legacy systems.
