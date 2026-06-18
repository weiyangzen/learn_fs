# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/Makefile

## Purpose
Build composition for the `mt7603e` kernel object.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_MT7603E) += mt7603e.o` ties the module/object to the Kconfig option.
- `mt7603e-y` lists implementation units: `pci.o`, `soc.o`, `main.o`, `init.o`, `mcu.o`, `core.o`, `dma.o`, `mac.o`, `eeprom.o`, `beacon.o`, and `debugfs.o`.

## Control Flow
Build-time only. Kbuild compiles and links the listed objects into one driver object when `CONFIG_MT7603E` is enabled.

## State And Persistence
No runtime state. Build output is determined by Kconfig and Kbuild.

## Dependencies And Integration Points
Integrates mt7603 bus frontends (`pci.o`, `soc.o`) with shared mt7603 runtime logic and the parent mt76 build.

## Risks
Missing a new source file from `mt7603e-y` causes unresolved symbols or omitted functionality. Ordering is generally not semantic, but link-time symbol availability depends on all units being listed.

## Test Signals
Run kernel module build for `CONFIG_MT7603E=y` and `m`; inspect `modinfo` for the final module and ensure both PCI and SoC probe objects are linked.
