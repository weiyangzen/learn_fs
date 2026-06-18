# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/Makefile

## Purpose
`Makefile` defines the object composition for the carl9170 kernel module. It lists the core compilation units and conditionally adds debugfs support.

## Important APIs, types, and targets
`carl9170-objs` includes `main.o`, `usb.o`, `cmd.o`, `mac.o`, `phy.o`, `led.o`, `fw.o`, `tx.o`, and `rx.o`. `carl9170-$(CONFIG_CARL9170_DEBUGFS)` adds `debug.o`. `obj-$(CONFIG_CARL9170)` emits `carl9170.o`.

## Control flow and integration
There is no runtime control flow. Kbuild combines the listed objects into the module or built-in object based on `CONFIG_CARL9170`, with debug object inclusion controlled by the Kconfig symbol.

## State and persistence behavior
The file encodes build graph state only. It does not affect runtime state except by including or excluding compiled objects.

## Dependencies
It depends on Kbuild conventions and symbol values produced by `Kconfig`. The object list must match source files and exported prototypes in `carl9170.h`.

## Risks
Risks include stale object lists after source moves, unconditional inclusion of feature-specific code that should be conditional, and missing object inclusion causing unresolved symbols. `led.o` is always compiled, so the LED source must guard optional LED subsystem use internally.

## Test signals
Signals include allmodconfig/allyesconfig builds, `CONFIG_CARL9170=m/y/n` behavior, `CONFIG_CARL9170_DEBUGFS` toggling `debug.o`, and no missing symbol or dead object references.
