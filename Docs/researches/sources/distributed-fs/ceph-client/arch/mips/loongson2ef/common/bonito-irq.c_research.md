# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/bonito-irq.c

Purpose: implements IRQ chip support for the Bonito/Loongson interrupt block.

Important APIs/functions: `bonito_irq_enable`, `bonito_irq_disable`, `bonito_irq_type`, and `bonito_irq_init`.

Control flow: init assigns `bonito_irq_type` and `handle_level_irq` to 32 IRQs starting at `LOONGSON_IRQ_BASE`; Loongson2E additionally requests the DMA timeout IRQ with `no_action`. Enable/disable write bit masks to `LOONGSON_INTENSET`/`LOONGSON_INTENCLR` and flush with `mmiowb()`.

State and persistence: hardware interrupt enable registers hold state.

Dependencies and integration: used by Loongson common IRQ init; depends on `loongson.h` register macros and generic IRQ APIs.

Risks: IRQ arithmetic uses `d->irq - LOONGSON_IRQ_BASE`; wrong IRQ numbering writes wrong bits. The DMA timeout IRQ is reserved only by a no-op handler.

Test signals: interrupt enable/disable tests, DMA timeout reservation log, and level IRQ handling on Loongson2E/2F.
