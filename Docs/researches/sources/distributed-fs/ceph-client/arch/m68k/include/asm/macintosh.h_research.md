<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/macintosh.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/macintosh.h

## Purpose
`macintosh.h` defines core Macintosh platform APIs, model descriptors, hardware-type enums, and bootloader-provided data.

## Important APIs, Types, and Functions
It declares reset/poweroff/IRQ functions, IRQ enable/disable hooks, PRAM read/write/size APIs, `struct mac_model`, hardware type constants for ADB, VIA, SCSI, IDE, SCC, Ethernet, expansion, and floppy, `macintosh_config`, `struct mac_booter_data`, and `mac_bi_data`.

## Control Flow, State, and Persistence
Machine setup fills `macintosh_config` and `mac_bi_data` from bootinfo. PRAM functions persist small values in battery-backed storage. IRQ functions control runtime interrupt state.

## Dependencies and Integration Points
It includes Mac bootinfo plus Linux seq/interrupt/irq headers. Mac drivers branch on the model descriptor to choose ADB, SCSI, IDE, serial, Ethernet, expansion, and floppy implementations.

## Risks
Hardware type enums are compact char fields; unsupported or mismatched values send drivers down wrong paths. PRAM writes have persistent side effects. Bootloader data must be trusted but validated by setup code where possible.

## Test Signals
Signals include correct model identification, PRAM access, reset/poweroff, IRQ enable/disable, and driver selection for representative Mac II, Quadra, PowerBook, LC, and AV systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/macintosh.h -->
