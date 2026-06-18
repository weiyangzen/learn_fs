# sources/distributed-fs/ceph-client/drivers/misc/cardreader/Kconfig

## Purpose
`cardreader/Kconfig` declares misc-driver options for Alcor PCIe card readers, Realtek PCIe card readers, and Realtek USB card readers.

## Important APIs, Types, and Functions
`MISC_ALCOR_PCI` depends on PCI and selects MFD core for AU6601/AU6621/AU6625-style devices. `MISC_RTSX_PCI` depends on PCI and selects MFD core for Realtek PCIe readers including RTS5209, RTS5227/5228/5229, RTS5249/524A, RTS525A, RTL8411, RTS5260/5261/5264. `MISC_RTSX_USB` depends on USB and selects MFD core for USB Realtek readers.

## Control Flow
Enabling these symbols causes Kbuild to compile parent cardreader MFD drivers that create child devices for SD/MMC and MemoryStick functions.

## State and Persistence
The file stores build-time configuration only. Runtime state belongs to the selected PCI/USB parent drivers and their child function drivers.

## Dependencies and Integration Points
It integrates with the Linux config system, PCI/USB subsystems, and MFD core. Help text describes card formats supported by the resulting drivers.

## Risks and Edge Cases
The Alcor help text says "This supports for", and its list omits AU6625 despite the PCI driver including it. Enabling these parent drivers still requires relevant child drivers for card protocols.

## Test Signals
Kconfig tests should confirm dependency visibility, `select MFD_CORE`, module builds, and that help text/device lists stay synchronized with PCI/USB ID tables.
