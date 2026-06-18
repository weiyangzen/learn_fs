## sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/Kconfig

## Purpose
Defines Kconfig options for EZchip Ethernet drivers, including the vendor menu gate and the NPS management Ethernet driver option.

## Important APIs, Types, and Functions
The declarative symbols are `NET_VENDOR_EZCHIP` and `EZCHIP_NPS_MANAGEMENT_ENET`. The vendor symbol is a boolean default-y menu selector. The NPS driver is a tristate depending on `OF_IRQ` and `HAS_IOMEM`.

## Control Flow and State
There is no runtime control flow. Build-time state controls whether EZchip-specific prompts are visible and whether `nps_enet.o` can be built in or as a module.

## Dependencies and Integration Points
Integrates with the kernel networking vendor-driver Kconfig hierarchy and the local Makefile's `obj-$(CONFIG_EZCHIP_NPS_MANAGEMENT_ENET)` rule. The help text documents the device as a simple interrupt-driven debug/management LAN device without DMA.

## Risks and Test Signals
Risks are missing dependencies rather than runtime bugs: the driver also needs OF platform and MMIO APIs, so Kconfig coverage should be checked under `allmodconfig`, `allyesconfig`, and `COMPILE_TEST`-like builds. Menu visibility and module/built-in selection should produce exactly `nps_enet.o` when enabled.
