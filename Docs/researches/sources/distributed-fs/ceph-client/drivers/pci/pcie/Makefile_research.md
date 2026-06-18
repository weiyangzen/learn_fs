<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/Makefile

## Purpose
The Makefile maps PCIe service Kconfig symbols to compiled objects. It keeps the port driver core, resource/event services, and independent support files in the expected link order.

## Important APIs, Types, and Functions
No APIs are declared here. The main object relationship is `pcieportdrv-y := portdrv.o rcec.o`, so the port bus driver includes RCEC support when `CONFIG_PCIEPORTBUS` builds `pcieportdrv.o`. The object rules include `bwctrl.o` with `PCIEPORTBUS`, always compile `aspm.o`, and gate `aer.o err.o tlp.o`, `aer_cxl_rch.o`, `aer_inject.o`, `pme.o`, `dpc.o`, `ptm.o`, and `edr.o` behind their respective options.

## Control Flow and State
Build composition determines which initialization functions can be reached from `pcie_portdrv_init()` and which stubs are active from headers. ASPM is always compiled because PCI core needs LTR/L1SS save-restore helpers even when full `CONFIG_PCIEASPM` policy control is disabled.

## Dependencies and Integration Points
The file integrates Kconfig with the PCIe service bus. `aer.o` and `err.o` are built together for `CONFIG_PCIEAER`, tying interrupt logging to generic recovery. `aer_cxl_rch.o` follows `CONFIG_CXL_RAS`, and `aer_inject.o` follows `CONFIG_PCIEAER_INJECT`. PTM, PME, DPC, EDR, and bandwidth control are separate service modules/objects that share `portdrv.h`.

## Risks and Test Signals
Risks include accidentally omitting a companion object, especially `err.o` or `tlp.o` for AER, or changing ASPM to conditional compilation and breaking unconditional PCI core callers. Test with representative configs, module/built-in permutations, and link checks for unresolved symbols around AER recovery, PTM debugfs exports, and ASPM save/restore helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/Makefile -->
