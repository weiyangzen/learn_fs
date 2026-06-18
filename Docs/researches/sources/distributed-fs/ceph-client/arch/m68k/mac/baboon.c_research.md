# sources/distributed-fs/ceph-client/arch/m68k/mac/baboon.c

## Purpose
Manages the Baboon custom IC used on the PowerBook 190 for IDE, PCMCIA, and media-bay interrupt fan-out behind NuBus slot C.

## APIs, Flow, And State
Exports runtime state through `int baboon_present` and keeps the MMIO pointer `static volatile struct baboon *baboon`. `baboon_init()` enables the driver only when `macintosh_config->ident == MAC_MODEL_PB190`; otherwise it clears state. `baboon_register_interrupts()` installs `baboon_irq()` as the chained handler for `IRQ_NUBUS_C`. The handler reads `mb_ifr & 0x07` and calls `generic_handle_irq()` for `IRQ_BABOON_0..2`. `baboon_irq_enable()` and `baboon_irq_disable()` proxy to the parent NuBus C IRQ because individual Baboon masks are undocumented.

## Dependencies And Integration
Depends on `asm/macintosh.h`, `asm/macints.h`, `asm/mac_baboon.h`, and the global `macintosh_config`. It integrates with `macints.c` through IRQ chip dispatch and with `config.c` through model feature selection, especially the Baboon IDE platform IRQ.

## Risks And Test Signals
The code documents an unresolved risk: clearing pending Baboon IRQs and per-source masking are unknown. Enabling/disabling the parent IRQ can affect all Baboon children. Test signals are PowerBook 190 IDE interrupts, `baboon_present` detection logs, and absence of stuck NuBus C interrupt storms.
