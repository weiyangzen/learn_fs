# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc.c

Purpose: legacy ColdFire interrupt-controller support for older parts using a single IMR and optional autovector register.

Important APIs and data: global `mcf_irq2imr[NR_IRQS]` maps Linux IRQs to IMR bit indexes. `mcf_setimr()`, `mcf_clrimr()`, `mcf_maskimr()`, `mcf_autovector()`, `intc_irq_mask()`, `intc_irq_unmask()`, and `init_IRQ()` are the core functions.

Control flow and state: build-time selection handles 16-bit versus 32-bit IMR access. `init_IRQ()` masks all interrupt sources and installs a simple level-high `CF-INTC` chip for every IRQ. Board/SoC setup code later calls `mcf_mapirq2imr()` elsewhere to populate `mcf_irq2imr`; mask/unmask are no-ops for unmapped IRQs. `mcf_autovector()` enables autovectoring for external IRQ levels in `MCFSIM_AVR` when available.

Dependencies and integration: Linux IRQ core, legacy SIM registers, board files such as `m5206.c`, `m5307.c`, `m5407.c`, and drivers that need autovector behavior.

Risks and test signals: missing `mcf_irq2imr` mappings leave interrupts unmaskable. IMR width selection must match silicon. The set-type callback returns success but programs nothing. Test with timer/UART/I2C/external IRQ mappings, autovectored devices, and mask/unmask register reads.
