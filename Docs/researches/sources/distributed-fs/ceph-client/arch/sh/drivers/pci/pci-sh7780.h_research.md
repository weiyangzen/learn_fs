# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7780.h



Source read size: 43 lines, 1652 bytes.



Purpose: SH7780-specific PCI host-controller register and resource constants.

Important APIs/types/functions: vendor/device IDs, config-space base/size, memory and I/O window base/size, PCIC register base, config register offsets, memory-controller register addresses, and BAR/window mask constants.

Control flow: no runtime flow; included by `pci-sh4.h` and controller init code.

State and persistence: constants describe controller and memory-controller MMIO state programmed during PCI initialization.

Dependencies and integration points: used by `SH7780` low-level setup, SH4 config ops, and board fixup code.

Risks and test signals: address constants and masks define the PCI resource ABI for the board. Test against datasheet values, resource registration, and config access on matching CPU subtypes.
