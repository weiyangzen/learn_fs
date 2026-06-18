<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/irq.c

Purpose: Provides common first-level interrupt setup and Bonito interrupt dispatch for Loongson2EF boards.

Important APIs/types/functions: `bonito_irqdispatch()` handles pending Bonito sources. `plat_irq_dispatch()` passes MIPS pending bits to board-specific `mach_irq_dispatch()`. `arch_init_irq()` clears MIPS interrupt state and delegates board controller setup.

Control flow: Bonito dispatch first waits while DMA-related bit 10 is set, then masks pending sources with `LOONGSON_INTEN`, selects the lowest pending bit with `__ffs`, and calls `do_IRQ(LOONGSON_IRQ_BASE + i)`.

State and persistence: Programs interrupt steer/enable registers and relies on board code to initialize cascades.

Dependencies and integration: Board-specific Fuloong and Lemote interrupt files supply `mach_irq_dispatch()` and `mach_init_irq()`.

Risks: The DMA wait loop can stall if bit 10 never clears. Only one Bonito interrupt is dispatched per entry. Board-specific cascade wiring must match pending bit routing.

Test signals: Boot should clear stale interrupts; Bonito device IRQs should map to `LOONGSON_IRQ_BASE`; spurious IRQ logs should remain rare under device load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/irq.c -->
