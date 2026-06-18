<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_no.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_no.h

## Purpose
`io_no.h` implements I/O access for non-MMU m68k and ColdFire systems, where physical and I/O virtual addresses are usually identity-mapped.

## Important APIs, Types, and Functions
It defines `iomem(a)`, raw volatile `__raw_readb/w/l` and `__raw_writeb/w/l`, default `readb/w/l` and `writeb/w/l`, ColdFire internal-I/O detection helpers `__cf_internalio()` and `cf_internalio()`, and PCI window constants when `CONFIG_PCI` is enabled.

## Control Flow, State, and Persistence
For ColdFire systems with `IOMEMBASE`, `readw/readl/writew/writel` branch at runtime: internal peripherals use native big-endian order, while bus ranges such as PCI are byte-swapped to little-endian. There is no persistent software state.

## Dependencies and Integration Points
It integrates with ColdFire platform register definitions from `coldfire.h` and `mcfsim.h`, byte-swap helpers, generic I/O, kmap, and virtual-address conversion code. PCI users consume `PCI_IOBASE` and address masks.

## Risks
The internal-I/O range check is central; wrong `IOMEMBASE` or `IOMEMSIZE` corrupts endian handling. Direct volatile dereferences require correctly mapped addresses and do not impose higher-level locking.

## Test Signals
Signals include correct access to native-endian ColdFire peripherals, byte-swapped PCI device configuration/MMIO, non-MMU boot probes, and compile coverage with and without `IOMEMBASE` and `CONFIG_PCI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_no.h -->
