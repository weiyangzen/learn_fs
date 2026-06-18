# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/Makefile

## Purpose
Kbuild object mapping for digital potentiometer drivers.

## Important APIs, Types, And Functions
Maps each Kconfig symbol to its `.o` file: `ad5110.o`, `ad5272.o`, `ds1803.o`, `max5432.o`, `max5481.o`, `max5487.o`, `mcp4018.o`, `mcp4131.o`, `mcp4531.o`, `mcp41010.o`, `tpl0102.o`, and `x9250.o`.

## Control Flow
Kbuild includes objects conditionally based on `obj-$(CONFIG_...)`.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Pairs with the potentiometer Kconfig file.

## Risks And Test Signals
Build tests should confirm each module is emitted under the documented module name.
