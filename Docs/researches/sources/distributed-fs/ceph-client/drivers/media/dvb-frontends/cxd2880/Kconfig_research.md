# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/Kconfig

## Purpose
Declares the `DVB_CXD2880` tristate option for the Sony CXD2880 DVB-T2/T tuner plus demodulator frontend driver.

## Important APIs, Types, and Functions
The key Kconfig symbol is `DVB_CXD2880`. It depends on `DVB_CORE` and `SPI`, defaults to module when media subdriver autoselection is disabled, and exposes help text for frontend support.

## Control Flow
Kconfig visibility and selection determine whether the CXD2880 object list in the Makefile is built into the kernel, emitted as a module, or omitted.

## State and Persistence
The selected tristate value persists in the kernel `.config`. Runtime demodulator state is not handled here.

## Dependencies and Integration Points
The SPI dependency matches the driver's `struct spi_device` transport. `DVB_CORE` provides frontend registration and media subsystem integration. The symbol controls the `IS_REACHABLE()` branch in `cxd2880.h`.

## Risks and Edge Cases
Missing dependencies could expose build failures; overly strict dependencies could hide compile-test coverage. The default `m` behavior changes module composition when autoselection is disabled.

## Test Signals
Run `olddefconfig`, `allmodconfig`, and builds with `DVB_CORE` or `SPI` disabled. Confirm `CONFIG_DVB_CXD2880=m` produces the expected `cxd2880` module and disabled builds use the attach stub.
