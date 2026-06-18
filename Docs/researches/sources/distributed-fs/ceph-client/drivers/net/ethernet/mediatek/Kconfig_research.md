# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/Kconfig

## Purpose
This Kconfig file exposes MediaTek Ethernet support under the kernel networking vendor menu. It gates three symbols: the vendor visibility symbol `NET_VENDOR_MEDIATEK`, the optional wireless Ethernet dispatcher support `NET_MEDIATEK_SOC_WED`, the main SoC frame-engine Ethernet driver `NET_MEDIATEK_SOC`, and the separate STAR EMAC driver `NET_MEDIATEK_STAR_EMAC`.

## Important APIs, Types, and Functions
Kconfig symbols are the API. `NET_VENDOR_MEDIATEK` is a bool selected for MediaTek, Airoha, MT7621, MT7620, or `COMPILE_TEST` builds. `NET_MEDIATEK_SOC_WED` defaults to enabled when `NET_MEDIATEK_SOC` is not disabled and depends on `ARCH_MEDIATEK || COMPILE_TEST`. `NET_MEDIATEK_SOC` is tristate and selects its required kernel subsystems: `PINCTRL`, `PHYLINK`, `DIMLIB`, `GENERIC_ALLOCATOR`, `PAGE_POOL`, `PAGE_POOL_STATS`, `PCS_MTK_LYNXI`, and `REGMAP_MMIO`. `NET_MEDIATEK_STAR_EMAC` is a separate tristate selecting `PHYLIB` and `REGMAP_MMIO`.

## Control Flow
The file has a simple menu flow: show `NET_VENDOR_MEDIATEK`, enter the vendor block only when it is enabled, then expose WED, SoC Gigabit Ethernet, and STAR EMAC options. The `NET_MEDIATEK_SOC` dependency `NET_DSA || !NET_DSA` is the common Kconfig idiom that tracks the tristate state of DSA, preventing impossible built-in/module combinations when DSA is modular.

## State and Persistence
Build configuration is persisted in the kernel `.config`. Runtime state is not managed here, but these choices determine which object files can be built and which APIs the C code may assume are available.

## Dependencies and Integration Points
This file integrates with `drivers/net/ethernet/Kconfig`, the MediaTek Makefile in the same directory, phylink/PHY infrastructure, page-pool/XDP-adjacent receive allocation support, Dynamic Interrupt Moderation, LynxI PCS, regmap-backed syscon access, and optional DSA. The WED symbol controls compilation of `mtk_wed*` files and `mtk_wed_ops.o`.

## Risks
The main risk is dependency drift. If `mtk_eth_soc.c` starts using new APIs without selecting or depending on their providers, build failures appear only on some architecture or module combinations. `NET_MEDIATEK_SOC_WED` being `def_bool NET_MEDIATEK_SOC != n` makes WED compile broadly, so WED code must stay guarded for platforms without matching device tree resources.

## Test Signals
Run representative `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, MediaTek/Airoha defconfig, and DSA-as-module builds. Check that `NET_MEDIATEK_SOC=y` with `NET_DSA=m` is not allowed, that WED objects are included only when expected, and that STAR EMAC remains independently selectable.
