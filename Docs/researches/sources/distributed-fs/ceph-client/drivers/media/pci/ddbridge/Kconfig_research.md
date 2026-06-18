# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/Kconfig

## Purpose
`ddbridge/Kconfig` exposes Digital Devices PCIe bridge support to the kernel media configuration system. It defines the main `DVB_DDBRIDGE` tristate and an optional MSI default-setting knob.

## Important APIs, Types, And Functions
The primary symbol is `DVB_DDBRIDGE`, which depends on `DVB_CORE`, `PCI`, and `I2C`. With `MEDIA_SUBDRV_AUTOSELECT`, it selects many frontend/tuner/CAM helpers: LNBP21, STV6110x, STV090x, DRXK, TDA18271C2DD, STV0367, CXD2841ER, STV0910, STV6111, LNBH25, TDA18212, MXL5XX, and CXD2099. `DVB_DDBRIDGE_MSIENABLE` is a bool depending on `DVB_DDBRIDGE` and `PCI_MSI`.

## Control Flow
There is no runtime control flow. Kconfig selection determines which objects and dependent modules are built and whether MSI is enabled by default in the driver.

## State, Persistence, And Dependencies
The persistent state is build configuration. The help text documents supported Digital Devices bridge products and warns that default MSI may cause I2C errors with some SATA controllers, while module option `msi=0` can still disable it.

## Integration Points
The Makefile consumes `CONFIG_DVB_DDBRIDGE` to build `ddbridge.o` and `ddbridge-dummy-fe.o`. The selected subdrivers line up with frontend/CAM attach paths in the ddbridge source, including CXD2099 CI support in `ddbridge-ci.c`.

## Risks
Overselecting subdrivers can increase module footprint but avoids missing dependencies for automatic board support. Enabling MSI by default is explicitly experimental and may trade interrupt performance for I2C stability issues on some systems. Missing `MEDIA_SUBDRV_AUTOSELECT` requires users to configure needed demod/tuner drivers manually.

## Test Signals
Check `allyesconfig`/`allmodconfig` and minimal configs, module autoload with common Digital Devices cards, build behavior with/without `MEDIA_SUBDRV_AUTOSELECT`, and runtime interrupt/I2C stability with `DVB_DDBRIDGE_MSIENABLE` enabled and overridden by `msi=0`.
