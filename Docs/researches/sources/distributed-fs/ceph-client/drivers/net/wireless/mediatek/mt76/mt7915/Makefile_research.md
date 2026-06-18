# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/Makefile

Purpose: Object composition for the `mt7915e` driver module.

Important entries: `obj-$(CONFIG_MT7915E) += mt7915e.o`; base objects are `pci.o init.o dma.o eeprom.o main.o mcu.o mac.o debugfs.o mmio.o`; optional objects include `testmode.o` for `CONFIG_NL80211_TESTMODE`, `soc.o` for `CONFIG_MT798X_WMAC`, and `coredump.o` for `CONFIG_DEV_COREDUMP`.

Control flow: no runtime flow; the Makefile determines which translation units are linked into the driver.

State and persistence: persistent state is kernel configuration and module build output. Optional object inclusion changes available runtime features such as testmode, SoC support, and firmware coredump.

Dependencies and integration: mirrors declarations in Kconfig and header stubs. `coredump.h` provides no-op inline functions when `coredump.o` is absent, allowing callers in `init.c`/`mac.c` to compile.

Risks: adding calls to functions from optional objects requires matching stubs or Makefile updates. Missing `coredump.o` with `CONFIG_DEV_COREDUMP` would break firmware crash reporting; adding new source files without updating this list silently omits functionality.

Test signals: build matrix with `CONFIG_MT7915E=n/m/y`, `CONFIG_NL80211_TESTMODE`, `CONFIG_MT798X_WMAC`, and `CONFIG_DEV_COREDUMP`; inspect `nm`/modinfo to confirm expected optional symbols and firmware declarations elsewhere.
