# sources/distributed-fs/ceph-client/drivers/misc/cardreader/Makefile

## Purpose
`cardreader/Makefile` maps cardreader Kconfig symbols to build objects and assembles the Realtek PCIe parent driver from common and chip-specific sources.

## Important APIs, Types, and Functions
`obj-$(CONFIG_MISC_ALCOR_PCI) += alcor_pci.o`; `obj-$(CONFIG_MISC_RTSX_USB) += rtsx_usb.o`; `obj-$(CONFIG_MISC_RTSX_PCI) += rtsx_pci.o`. `rtsx_pci-objs` includes `rtsx_pcr.o` plus chip files `rts5209.o`, `rts5229.o`, `rtl8411.o`, `rts5227.o`, `rts5249.o`, `rts5260.o`, `rts5261.o`, `rts5228.o`, and `rts5264.o`.

## Control Flow
Kbuild links the chip parameter files into one `rtsx_pci` module/object so the common PCI core can select chip-specific init routines by PCI ID.

## State and Persistence
The file has no runtime state.

## Dependencies and Integration Points
It integrates the common Realtek PCI code with per-chip operation tables and ensures the MFD parent can support all configured PCI IDs.

## Risks and Edge Cases
Adding a new Realtek chip requires updating this object list as well as IDs and init dispatch in the common code. Missing a chip object would produce unresolved symbols or unsupported IDs.

## Test Signals
Build tests should verify `MISC_RTSX_PCI=m/y` links every listed chip file and that disabling the symbol excludes the aggregate object.
