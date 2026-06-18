<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/Kconfig

## Purpose
This Kconfig file exposes build-time configuration for the mwifiex core and its SDIO, PCIe, and USB transport modules.

## Important APIs, Types, And Functions
`CONFIG_MWIFIEX` is a tristate core option depending on `CFG80211`. `CONFIG_MWIFIEX_SDIO` depends on `MWIFIEX && MMC` and selects firmware loader plus device coredump support. `CONFIG_MWIFIEX_PCIE` depends on `MWIFIEX && PCI` and also selects firmware loader and coredump support. `CONFIG_MWIFIEX_USB` depends on `MWIFIEX && USB` and selects firmware loader.

## Control Flow
Kconfig controls whether the core `mwifiex` object and transport modules are built in, built as modules, or omitted. Transport choices require the core and their bus subsystem.

## State And Persistence
No runtime state exists. User/kernel configuration persists in the kernel build configuration and determines compiled artifacts.

## Dependencies And Integration Points
The file integrates with Linux wireless configuration (`CFG80211`), bus subsystems (`MMC`, `PCI`, `USB`), firmware loading, device coredump support, and the adjacent Makefile's `obj-$(CONFIG_*)` rules.

## Risks
Incorrect dependencies could allow a transport to build without required core or bus APIs. Missing `FW_LOADER` selection would break firmware-based devices at runtime. USB lacks `WANT_DEV_COREDUMP` selection unlike SDIO/PCIe, which may be intentional but affects diagnostics.

## Test Signals
Build matrix checks should cover core disabled, core built-in/module, each transport built-in/module, missing bus dependencies, firmware loader availability, and module names `mwifiex`, `mwifiex_sdio`, `mwifiex_pcie`, and `mwifiex_usb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/Kconfig -->
