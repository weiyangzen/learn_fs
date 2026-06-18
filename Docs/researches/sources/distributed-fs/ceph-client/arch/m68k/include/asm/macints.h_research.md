<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/macints.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/macints.h

## Purpose
`macints.h` defines the Macintosh m68k IRQ numbering scheme and named interrupt aliases.

## Important APIs, Types, and Functions
It defines source base offsets for VIA1, VIA2, PSC levels 3-6, NuBus, and Baboon, `NUM_MAC_SOURCES`, helpers `IRQ_SRC()` and `IRQ_IDX()`, aliases for ADB, VBlank, timers, SCSI, MACE, SCC, NuBus slots, Baboon lines, and `SLOT2IRQ()`/`IRQ2SLOT()`.

## Control Flow, State, and Persistence
There is no control flow. The macros encode a stable IRQ namespace where each source block has eight indexes.

## Dependencies and Integration Points
It includes `asm/irq.h` and is consumed by Mac VIA/PSC/OSS/Baboon/NuBus interrupt-controller code and device drivers.

## Risks
Aliases overlap where different machines route similar functions through PSC or OSS. The slot conversion assumes NuBus slot numbering offset by 47.

## Test Signals
Signals include registration and delivery for VIA timers/ADB, SCSI/SCSIDRQ, PSC MACE/SCC, OSS SCC, NuBus slots 9-F, and Baboon media-bay interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/macints.h -->
