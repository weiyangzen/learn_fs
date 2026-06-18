# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/Kconfig

## Purpose
`mediatek/Kconfig` defines the configuration symbols for MediaTek and Airoha PHY drivers and their shared helper library. It controls which PHY objects are built, their architecture dependencies, and the shared support selected by the individual drivers.

## Important APIs, Types, And Symbols
- `MEDIATEK_2P5GE_PHY` builds the MT7988 built-in 2.5GbE PHY driver. It depends on `ARM64 && ARCH_MEDIATEK` or `COMPILE_TEST` and selects `MTK_NET_PHYLIB`.
- `MEDIATEK_GE_PHY` builds the non-built-in gigabit PHY driver, including MT7530/MT7531-style PHYs, and selects `MTK_NET_PHYLIB`.
- `MEDIATEK_GE_SOC_PHY` builds SoC built-in gigabit PHY support for MT7981/MT7988 and Airoha variants. It depends on ARM64 or compile testing, requires Airoha or MediaTek efuse-capable platforms unless compile-testing, and selects both `MTK_NET_PHYLIB` and `PHY_PACKAGE`.
- `MTK_NET_PHYLIB` is a hidden tristate used for shared MediaTek PHY helper code.

## Control Flow And State Behavior
This file has no runtime control flow. At configuration time it determines whether the relevant drivers can be selected and whether shared helper objects are included. The selected symbols affect compilation of `mtk-2p5ge.o`, `mtk-ge.o`, `mtk-ge-soc.o`, and `mtk-phy-lib.o` through the adjacent Makefile.

## Dependencies And Integration Points
The symbols integrate with Kbuild, phylib, MediaTek/Airoha architecture symbols, NVMEM efuse support, and PHY package support. The help text documents firmware loading for 2.5GbE PHYs and efuse-driven calibration for SoC gigabit PHYs, matching the behavior in the C sources.

## Risks And Edge Cases
- `MEDIATEK_GE_SOC_PHY` has platform and NVMEM dependencies because calibration data may be required for correct analog behavior.
- `COMPILE_TEST` broadens build coverage but does not imply runtime platform support.
- The hidden `MTK_NET_PHYLIB` must be selected by every driver that uses shared `mtk.h`/helper functions; missing selection would produce link failures.
- `PHY_PACKAGE` is required for shared MT7988 package state in `mtk-ge-soc.c`.

## Test Signals
Build-test the symbols as built-in and modules, with and without `COMPILE_TEST`, and verify dependencies pull in `mtk-phy-lib.o` and `PHY_PACKAGE` where required. Confirm invalid platform combinations hide the SoC PHY option outside compile-test configurations.
