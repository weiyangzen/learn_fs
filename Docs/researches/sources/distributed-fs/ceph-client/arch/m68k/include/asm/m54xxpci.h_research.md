<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxpci.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxpci.h

## Purpose
`m54xxpci.h` maps ColdFire 547x/548x PCI controller registers and helper bitfields.

## Important APIs, Types, and Functions
It defines PCI configuration, global status/control, target/initiator window, configuration address, TX/RX FIFO/packet registers, arbiter registers, `PCIGSCR_*`, `PCICAR_*`, `WXBTAR(hostaddr,pciaddr,size)`, initiator window flags, target enable bits, arbiter flags, and `PCICR1_CL()`/`PCICR1_LT()`.

## Control Flow, State, and Persistence
There is no local control flow. PCI bridge state persists in MBAR-mapped controller registers programmed during PCI host setup and transaction handling.

## Dependencies and Integration Points
It depends on `CONFIG_MBAR` and integrates with m54xx PCI host-controller setup, config-space access, address-window programming, and arbiter control.

## Risks
Window macros operate on high address bits and size masks; wrong values expose incorrect host memory or PCI ranges. Reset, parity, and system-error bits have controller-wide effects. FIFO register programming is hardware-specific.

## Test Signals
Signals include PCI bus enumeration, config reads/writes through `PCICAR`, memory and I/O BAR access through initiator windows, interrupt/error reporting, and arbiter behavior with multiple masters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxpci.h -->
