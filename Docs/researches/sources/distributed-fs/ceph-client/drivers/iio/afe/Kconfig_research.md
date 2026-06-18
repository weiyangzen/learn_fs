# sources/distributed-fs/ceph-client/drivers/iio/afe/Kconfig

## Purpose
This Kconfig file defines the IIO Analog Front Ends submenu and the `CONFIG_IIO_RESCALE` option for the rescale virtual front-end driver.

## Important APIs, Types, And Functions
The single symbol, `IIO_RESCALE`, is a tristate option named "IIO rescale". It enables support for IIO rescaling helpers that model voltage dividers, current sense shunts, current sense amplifiers, RTD temperature sensing, and temperature transducers. The help text documents that the module is named `iio-rescale`.

## Control Flow
Kconfig decides whether `iio-rescale.o` is omitted, built in, or built as a module. There are no explicit dependencies in this file, so the C file's included framework dependencies must be available through the IIO subsystem and selected kernel configuration.

## State And Persistence
The file persists build-time selection only. It has no runtime state.

## Dependencies And Integration Points
It integrates with `drivers/iio/afe/Makefile`, the IIO subsystem, and devicetree compatible strings handled by `iio-rescale.c`.

## Risks And Test Signals
Risks are missing dependency declarations if the implementation gains hard dependencies or help text drifting from module naming. Test signals are `CONFIG_IIO_RESCALE=y/m` builds, DT compatible probe tests for all variants, and module artifact checks.
