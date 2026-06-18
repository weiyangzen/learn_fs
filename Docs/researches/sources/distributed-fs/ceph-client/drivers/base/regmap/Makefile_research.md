# sources/distributed-fs/ceph-client/drivers/base/regmap/Makefile

## Purpose
This Makefile maps regmap Kconfig symbols to compiled objects for the core, cache implementations, debugfs, KUnit, RAM test backend, and bus-specific adapters.

## Important APIs, Types, And Functions
The key build rules compile `regmap.o`, `regcache.o`, `regcache-rbtree.o`, `regcache-flat.o`, `regcache-maple.o`, `regmap-debugfs.o`, `regmap-kunit.o`, and transport objects such as `regmap-ac97.o`, `regmap-i2c.o`, `regmap-spi.o`, `regmap-mmio.o`, `regmap-irq.o`, `regmap-sdw.o`, `regmap-sccb.o`, `regmap-i3c.o`, `regmap-mdio.o`, and `regmap-fsi.o`.

## Control Flow And State
The file is declarative. `CFLAGS_regmap.o := -I$(src)` ensures `include/trace/define_trace.h` can include the local `trace.h`. Core cache backends are built whenever `CONFIG_REGMAP` is enabled, while adapters follow their specific Kconfig symbol.

## Dependencies And Integration Points
It must remain synchronized with `Kconfig`, source files in this directory, and trace include layout. Debugfs and KUnit objects are guarded by their respective config symbols.

## Risks And Test Signals
Risks include adding a backend in Kconfig without adding its object here, stale object names after renames, and trace include path breakage. Test signals include `make drivers/base/regmap/`, config matrix builds for each backend, and KUnit regmap builds with `CONFIG_REGMAP_KUNIT`.
