
# sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/Kconfig

## Purpose
Defines IXP4xx SoC driver options for the queue manager and network processor engines.

## Important APIs, Types, and Functions
No runtime APIs. `IXP4XX_QMGR` is a tristate queue manager option. `IXP4XX_NPE` is a tristate NPE option selecting firmware loader and MFD syscon.

## Control Flow
Options are visible when `ARCH_IXP4XX || COMPILE_TEST` and gate corresponding Makefile objects.

## State and Persistence
Kernel configuration only.

## Dependencies and Integration Points
Ethernet and HSS drivers select/use these hardware services. NPE depends on firmware loading and syscon.

## Risks
Queue/NPE are low-level shared services; disabling them breaks dependent network/HSS drivers.

## Test Signals
Kconfig visibility, compile-test builds, module/built-in builds, and dependency selection of `FW_LOADER`/`MFD_SYSCON`.
