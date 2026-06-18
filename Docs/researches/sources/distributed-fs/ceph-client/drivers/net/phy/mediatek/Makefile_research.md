# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/Makefile

## Purpose
`mediatek/Makefile` maps the MediaTek PHY Kconfig symbols to kernel objects. It is the build glue for the driver sources and the shared helper library in this directory.

## Important APIs, Types, And Targets
- `obj-$(CONFIG_MEDIATEK_2P5GE_PHY) += mtk-2p5ge.o` builds the 2.5GbE SoC PHY driver.
- `obj-$(CONFIG_MEDIATEK_GE_PHY) += mtk-ge.o` builds the non-built-in gigabit PHY driver.
- `obj-$(CONFIG_MEDIATEK_GE_SOC_PHY) += mtk-ge-soc.o` builds the SoC gigabit PHY/Airoha driver.
- `obj-$(CONFIG_MTK_NET_PHYLIB) += mtk-phy-lib.o` builds the shared MediaTek PHY helper library.

## Control Flow And State Behavior
There is no runtime state or control flow. Kbuild evaluates each `obj-$()` expression from `.config` and includes the corresponding object either built-in, as a module, or not at all. The shared helper object is controlled by the hidden `MTK_NET_PHYLIB` symbol selected by the driver Kconfig entries.

## Dependencies And Integration Points
The Makefile integrates directly with the Kconfig file in the same directory and with the broader `drivers/net/phy` build. It also codifies that both `mtk-2p5ge.c` and `mtk-ge-soc.c` depend on helper routines supplied by `mtk-phy-lib.o`.

## Risks And Edge Cases
- If a driver uses shared helper symbols without selecting `MTK_NET_PHYLIB`, module or vmlinux linking will fail.
- Object names must match source files; adding a new driver requires corresponding Kconfig and Makefile updates.
- Built-in versus module combinations need consistent symbol visibility for shared helpers.

## Test Signals
Build all four symbols as modules, all as built-ins, and individual driver combinations to confirm `mtk-phy-lib.o` is included exactly when needed and no unresolved symbols are emitted.
