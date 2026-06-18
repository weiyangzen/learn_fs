# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/Kconfig

## Purpose
This Kconfig file defines the Wangxun Ethernet vendor menu and the build symbols for the shared Wangxun library plus physical-function and virtual-function drivers for GbE and 10/25/40GbE PCIe adapters.

## Important APIs, types, and functions
There are no C APIs. `NET_VENDOR_WANGXUN` gates the submenu. `LIBWX` is a hidden tristate common library symbol depending on `PTP_1588_CLOCK_OPTIONAL` and selecting `PAGE_POOL`, `DIMLIB`, and `PHYLINK`. Device options are `NGBE`, `TXGBE`, `TXGBEVF`, and `NGBEVF`. PF drivers depend on PCI and select `LIBWX`; VF drivers depend on PCI MSI and select `LIBWX`. `TXGBE` also selects support libraries for clocks, I2C DesignWare platform, Marvell 10G PHY, regmap, SFP, GPIO, IRQ chips, XPCS, and optional hwmon when built-in.

## Control flow and integration
Selecting a device driver causes the top-level Makefile to descend into the matching subdirectory and, through `select LIBWX`, build the shared `libwx` library. Help text points users to driver documentation under `Documentation/networking/device_drivers/ethernet/wangxun/`.

## State and persistence behavior
Kconfig choices persist in `.config` and determine which Wangxun modules or built-in objects are produced. No runtime state exists here.

## Dependencies and integration points
The file integrates Wangxun drivers with kernel PCI, MSI, PTP, page-pool, DIM, PHYLINK, SFP, XPCS, GPIO, regmap, hwmon, and documentation systems. The hidden `LIBWX` symbol centralizes common dependencies.

## Risks and edge cases
Because `LIBWX` is selected by multiple drivers, dependency mistakes can break broad Wangxun builds. `TXGBE` has many transitive dependencies; configuration combinations around built-in vs module and `HWMON if TXGBE=y` need coverage. VF drivers require MSI-X functionality per help text, represented by `PCI_MSI`.

## Test signals
Build each driver as module and, where supported, built-in. Verify `LIBWX` is selected automatically, `txgbe` pulls the required PHY/SFP/XPCS/GPIO dependencies, and docs referenced by help text remain valid.
