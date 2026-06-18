# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/Kconfig

## Purpose
Provides the top-level Kconfig gate for Digital Equipment Corporation Ethernet drivers and includes the Tulip-family Kconfig when the vendor group is enabled.

## Important APIs, Types, and Functions
Defines `NET_VENDOR_DEC` as a boolean vendor menu option, defaults it to `y`, constrains it to PCI/EISA/CardBus-capable builds, and sources `drivers/net/ethernet/dec/tulip/Kconfig` inside `if NET_VENDOR_DEC`.

## Control Flow and State
There is no runtime flow. Build-time state is whether DEC vendor questions are visible. Disabling this option hides subordinate DEC/Tulip driver choices without directly compiling code itself.

## Dependencies and Integration Points
Integrated into the kernel networking Kconfig tree. It depends on bus families that can host DEC Ethernet devices and delegates all actual driver symbols to the tulip subdirectory Kconfig.

## Risks and Test Signals
Risks are build visibility regressions: too-strict dependencies can hide drivers, while too-loose defaults expose irrelevant menus. Test signals are `menuconfig` visibility for PCI/EISA/CardBus targets, absence on unsupported bus configs, and correct inclusion of Tulip-family symbols when `NET_VENDOR_DEC=y`.
