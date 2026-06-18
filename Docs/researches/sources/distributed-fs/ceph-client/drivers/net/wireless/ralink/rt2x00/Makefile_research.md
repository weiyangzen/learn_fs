## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/Makefile

### Purpose
`rt2x00/Makefile` maps rt2x00 Kconfig symbols to shared library objects and concrete Ralink driver modules.

### Important APIs, Types, And Functions
It builds `rt2x00lib-y` from core library objects and conditionally adds debugfs, crypto, firmware, and LED helpers. It maps symbols to objects such as `rt2x00lib.o`, `rt2x00mmio.o`, `rt2x00pci.o`, `rt2x00usb.o`, `rt2800lib.o`, `rt2800mmio.o`, `rt2400pci.o`, `rt2500pci.o`, `rt61pci.o`, `rt2800pci.o`, USB drivers, and `rt2800soc.o`.

### Control Flow
Kbuild combines the `rt2x00lib-y` components into the library object when `CONFIG_RT2X00_LIB` is enabled, and builds bus helpers or device drivers according to their config symbols.

### State, Persistence, And Dependencies
There is no runtime state. Build state follows `.config` and Kbuild's object graph. It depends on object files existing with names matching symbol intent.

### Integration Points
This file is the final build selection layer for the entire rt2x00 family, connecting Kconfig choices to modules used by PCI/USB/SoC probe paths.

### Risks
Missing object entries or symbol mismatches create link or missing-driver failures. Conditional helper objects must stay aligned with code guarded by corresponding `CONFIG_RT2X00_LIB_*` symbols.

### Test Signals
Module builds for each individual driver, combined allmodconfig builds, and link checks with debugfs/crypto/firmware/LED toggles validate this file.
