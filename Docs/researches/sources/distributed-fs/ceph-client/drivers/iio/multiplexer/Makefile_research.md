# sources/distributed-fs/ceph-client/drivers/iio/multiplexer/Makefile

## Purpose
Build rule for IIO multiplexer drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_IIO_MUX` to `iio-mux.o`.

## Control Flow
Kbuild includes the object only when the Kconfig option is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Tied directly to `drivers/iio/multiplexer/Kconfig`.

## Risks And Test Signals
Compile with `CONFIG_IIO_MUX=m` and `=y` to confirm object inclusion and module naming.
