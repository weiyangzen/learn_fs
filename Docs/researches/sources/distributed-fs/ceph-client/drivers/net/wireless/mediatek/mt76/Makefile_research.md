# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/Makefile

Purpose: defines kbuild composition for the mt76 common module, transport modules, shared chipset libraries, and per-chip subdirectories.

Important APIs/types/functions: builds `mt76.o`, `mt76-usb.o`, `mt76-sdio.o`, `mt76x02-lib.o`, `mt76x02-usb.o`, `mt76-connac-lib.o`, `mt792x-lib.o`, and `mt792x-usb.o` from symbol-dependent object lists. The core `mt76-y` list includes `mmio.o`, `util.o`, `trace.o`, `dma.o`, `mac80211.o`, `debugfs.o`, `eeprom.o`, `tx.o`, `agg-rx.o`, `mcu.o`, `wed.o`, `scan.o`, and `channel.o`. Optional objects include `npu.o`, `pci.o`, and `testmode.o`. Trace CFLAGS add `-I$(src)`.

Control flow: kbuild expands object lists based on enabled Kconfig symbols, compiles shared objects into their module archives, and descends into chip subdirectories for enabled chip families. Transport and library modules can be selected independently by chipset drivers.

State and persistence: no runtime state. Build outputs are object files/modules shaped by this file.

Dependencies and integration: depends on the Kconfig symbols defined in `mt76/Kconfig` and child Kconfigs. Integrates with Linux kbuild syntax for composite modules and conditional object inclusion.

Risks: object list order matters for link-time symbol resolution and initialization dependencies. Missing a shared source file from `mt76-y` can produce unresolved symbols in chip drivers; including optional code without the matching config can break builds. Trace include flags must track generated trace headers.

Test signals: allmodconfig and representative built-in/module builds should verify each composite module links, trace sources find headers, optional NPU/PCI/testmode objects are included only when intended, and all child subdirectories build under their symbols.
