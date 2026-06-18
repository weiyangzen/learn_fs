# sources/distributed-fs/ceph-client/drivers/sbus/char/Makefile

Purpose: maps SBUS character-driver Kconfig symbols to object files and combines the BBC I2C/environment-control pair into one module object.

Important APIs/types/functions: `bbc-objs := bbc_i2c.o bbc_envctrl.o` creates the composite `bbc.o`. Object rules build `envctrl.o`, `display7seg.o`, `flash.o`, `openprom.o`, `uctrl.o`, `bbc.o`, and `oradax.o` from their respective config symbols.

Control flow: build-time only; no runtime code.

State and persistence: no runtime state.

Dependencies and integration: ties Kconfig symbols to the source files in this directory and ensures `bbc_i2c.c` and `bbc_envctrl.c` are linked together for `CONFIG_BBC_I2C`.

Risks and test signals: composite BBC linkage matters because `bbc_i2c.c` calls `bbc_envctrl_init()` and cleanup. Test module and built-in builds for each symbol, especially `CONFIG_BBC_I2C=m`, and verify no unresolved exported symbols.
