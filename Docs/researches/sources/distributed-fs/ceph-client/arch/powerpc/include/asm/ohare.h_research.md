<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ohare.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ohare.h

## Purpose
This header defines register offsets and feature-control bits for Apple's O'Hare I/O controller used in older PowerMac systems.

## Important APIs, Types, And Functions
It defines `OHARE_MBCR`, `OHARE_FCR`, feature bits such as `OH_SCC_RESET`, media-bay power/PCI/IDE/floppy enables, IDE reset/enables, SCC/MESH/floppy/VIA bits, `PBOOK_FEATURES`, and `STARMAX_FEATURES`.

## Control Flow
There are no functions. Platform feature code reads or writes O'Hare feature-control registers using these masks to enable, reset, or power hardware blocks.

## State And Persistence Behavior
State resides in O'Hare hardware registers. Writes persist until reset or later feature-management calls and directly affect device availability.

## Dependencies And Integration Points
It integrates with PowerMac feature management, media bay, IDE, serial SCC, MESH SCSI, floppy, and board-specific initialization.

## Risks And Edge Cases
Several bits are documented as guesses or experimentally derived. Incorrect masks can power off devices, hold reset lines, or break media-bay detection on specific machines.

## Test Signals
Boot affected PowerBook/Starmax/O'Hare systems, test IDE CD, media bay, serial, MESH SCSI, floppy, and suspend/resume feature restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ohare.h -->
