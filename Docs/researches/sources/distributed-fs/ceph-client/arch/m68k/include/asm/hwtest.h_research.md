<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hwtest.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/hwtest.h

## Purpose
`hwtest.h` declares tiny hardware-presence probes for m68k memory-mapped registers.

## Important APIs, Types, and Functions
`hwreg_present(volatile void *regp)` tests whether a register can be safely read. `hwreg_write(volatile void *regp, unsigned short val)` tests whether a register accepts a write. Implementations live in `arch/m68k/mm/hwtest.c`.

## Control Flow, State, and Persistence
The header has no state. The implementation is expected to trap or recover from bus errors while probing volatile addresses.

## Dependencies and Integration Points
It is used by board/platform detection and optional hardware drivers that need to avoid touching absent registers directly.

## Risks
Hardware probing can have side effects on real devices. Callers must pass correctly aligned register addresses and choose harmless values for write tests. The declarations are deliberately available to modules.

## Test Signals
Signals are successful boot probes on machines with and without optional devices, plus fault-path testing on unmapped addresses where practical. Compile coverage for modular users is also relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hwtest.h -->
