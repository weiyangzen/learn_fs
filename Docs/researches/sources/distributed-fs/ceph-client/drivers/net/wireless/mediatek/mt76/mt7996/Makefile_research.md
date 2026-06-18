# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/Makefile

## Purpose
This Makefile defines the object composition for the MT7996E driver module.

## Important APIs, Types, And Functions
It builds `mt7996e.o` when `CONFIG_MT7996E` is enabled. The base object list includes `pci.o`, `init.o`, `dma.o`, `eeprom.o`, `main.o`, `mcu.o`, `mac.o`, `debugfs.o`, and `mmio.o`. `npu.o` is conditional on `CONFIG_MT7996_NPU`, and `coredump.o` is conditional on `CONFIG_DEV_COREDUMP`.

## Control Flow
No runtime logic exists. Kbuild aggregates the listed objects into one module or built-in object.

## State And Persistence
Build state is determined by Kconfig symbols. Runtime coredump and NPU features appear only when their objects are linked.

## Dependencies And Integration Points
It integrates with the kernel Kbuild system and the surrounding mt76 directory build. It must stay synchronized with source files and Kconfig options.

## Risks
Missing an object can produce unresolved symbols or silently drop features. Adding coredump only under `CONFIG_DEV_COREDUMP` must match stubs in `coredump.h`.

## Test Signals
Incremental and clean builds with MT7996E built-in/module, DEV_COREDUMP on/off, and MT7996_NPU on/off validate this file.
