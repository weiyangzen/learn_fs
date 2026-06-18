<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_baboon.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_baboon.h

## Purpose
`mac_baboon.h` describes the Baboon custom IC on the PowerBook 190, particularly media-bay control and interrupts.

## Important APIs, Types, and Functions
It defines `BABOON_BASE`, `struct baboon` with media-bay control, status, and interrupt flag registers, `baboon_present`, and interrupt helpers `baboon_register_interrupts()`, `baboon_irq_enable()`, and `baboon_irq_disable()`.

## Control Flow, State, and Persistence
The header has no code. Runtime state includes hardware media-bay register bits and the global `baboon_present` flag.

## Dependencies and Integration Points
Mac interrupt code cascades Baboon interrupts from NuBus slot C, and IDE/media-bay code interprets status bits for device presence and IDE interrupt state.

## Risks
Several status/control bits are undocumented. The base address overlaps the IDE controller area, so careless struct access can affect IDE registers. Presence detection must guard all Baboon accesses.

## Test Signals
Signals include PowerBook 190 media-bay insertion/removal interrupts, IDE interrupt delivery through Baboon, slot power control behavior, and no Baboon access on non-Baboon Macs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_baboon.h -->
