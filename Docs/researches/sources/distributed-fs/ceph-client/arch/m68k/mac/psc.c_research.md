# sources/distributed-fs/ceph-client/arch/m68k/mac/psc.c

## Purpose
Initializes and dispatches interrupts for the Apple Peripheral System Controller used on AV Macs.

## APIs, Flow, And State
The exported global is `volatile __u8 *psc`. `psc_init()` detects Centris 660AV and Quadra 840AV, assigns `PSC_BASE`, kills DMA channels with `psc_dma_die_die_die()`, optionally dumps registers, and masks/clears PSC interrupt groups 3 through 6. `psc_register_interrupts()` chains autovectors 3-6 to `psc_irq()` with group offsets. `psc_irq()` reads enabled pending bits from PSC IFR/IER registers, clears the bit, and dispatches `generic_handle_irq()` for `irq << 3 | index`. `psc_irq_enable()` and `psc_irq_disable()` set or clear individual IER bits.

## Dependencies And Integration
Depends on `asm/mac_psc.h`, Mac IRQ encodings, AV model detection, and generic IRQ chained handlers. It serves MACE Ethernet, SCC, DMA, and other AV-specific interrupt sources routed through `macints.c`.

## Risks And Test Signals
DMA shutdown and some PSC IFR groups are explicitly uncertain. A persistent interrupt condition on unused levels can cause storms if accidentally enabled. Test signals include AV Mac boot logs, MACE/SCC interrupt delivery, no unexpected PSC level 5/6 storms, and successful platform device probing for AV Ethernet/SCC.
