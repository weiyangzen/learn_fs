# sources/distributed-fs/ceph-client/drivers/iio/multiplexer/Kconfig

## Purpose
Kconfig menu and option for the IIO multiplexer driver.

## Important APIs, Types, And Functions
Defines `CONFIG_IIO_MUX` as a tristate option labeled "IIO multiplexer driver" and selects `MULTIPLEXER`.

## Control Flow
When enabled as built-in or module, the Makefile builds `iio-mux.o`. The help text documents the module name as `iio-mux`.

## State And Persistence
No runtime state; this controls compilation.

## Dependencies And Integration Points
Integrates the IIO mux driver with the kernel multiplexer framework through `select MULTIPLEXER`.

## Risks And Test Signals
Build tests should ensure enabling `IIO_MUX=m/y` pulls in mux consumer support and produces `iio-mux`.
