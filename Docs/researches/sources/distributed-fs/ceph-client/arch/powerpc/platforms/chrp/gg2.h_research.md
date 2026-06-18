# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/gg2.h

Purpose: defines VLSI VAS96011/12 Golden Gate 2 chipset memory-map and PCI configuration register constants used by CHRP PCI/setup code.

Important definitions: base addresses for PCI memory, ISA memory/IO, PCI config, interrupt acknowledge/special cycles, and ROM banks; external `gg2_pci_config_base`; register offsets for bus numbers, control registers, ROM timing, cache controller, DRAM banks/timing/control, and error control/status.

Integration: consumed by CHRP PCI code that maps and accesses Golden Gate 2 configuration space. Constants encode CHRP-mode physical addresses and register offsets, not runtime-discovered resources.

Risks and test signals: hardcoded chipset addresses can be wrong for non-GG2 CHRP variants and require correct ioremap usage by callers. The error-status register being cleared on read is a side-effect risk for diagnostics. Test signals include PCI config access on GG2 hardware/emulation, bridge enumeration, and no accidental reads of clear-on-read error status.
