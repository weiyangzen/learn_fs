<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigaints.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigaints.h

## Purpose
This header defines Amiga interrupt source numbering and register bit masks. It bridges generic m68k IRQ numbers to Amiga custom-chip and CIA interrupt sources.

## Important APIs, Types, And Functions
- `AUTO_IRQS`, `AMI_STD_IRQS`, `CIA_IRQS`, and `AMI_IRQS` define source counts.
- `IRQ_AMIGA_*` constants assign serial, disk, soft, ports, external, copper, vertical blank, blitter, audio, and CIA A/B subinterrupts.
- `IF_*` masks represent Amiga custom interrupt register bits such as `IF_INTEN`, `IF_EXTER`, `IF_RBF`, `IF_AUD*`, `IF_BLIT`, `IF_VERTB`, and `IF_TBE`.
- `CIA_ICR_*` masks represent CIA timer, alarm, serial, flag, all, and set/clear bits.
- Declared APIs include `amiga_init_IRQ()`, `cia_init_IRQ()`, `cia_set_irq()`, and `cia_able_irq()`.

## Control Flow
Initialization code calls `amiga_init_IRQ()` and `cia_init_IRQ()` to register handlers. Runtime interrupt code maps hardware INTREQ/CIA bits to the `IRQ_AMIGA_*` namespace and uses CIA helpers to set, enable, or disable subinterrupt masks.

## State And Persistence Behavior
The header stores no state, but its masks operate on persistent hardware interrupt-enable/request registers and on `ciaa_base`/`ciab_base` runtime descriptors declared here.

## Dependencies And Integration Points
It depends on `asm/irq.h` for base IRQ numbering and integrates with Amiga custom-chip interrupt code, CIA support, serial, audio, disk, input, and timer drivers.

## Risks And Edge Cases
Interrupt numbering is ABI-like inside the arch port. Off-by-one changes can route handlers to the wrong source. CIA set/clear semantics require using `CIA_ICR_SETCLR` correctly or interrupts may be disabled while appearing configured.

## Test Signals
Boot IRQ initialization, vertical blank timer events, serial RX/TX, disk block/sync, audio channel completion, blitter completion, ports/external IRQs, and individual CIA timer/alarm/flag interrupts provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigaints.h -->
