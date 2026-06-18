# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/Makefile

## Purpose
This Makefile maps the MediaTek Ethernet Kconfig symbols to kernel objects. It builds the main MediaTek SoC Ethernet driver as a composite `mtk_eth.o`, optional WED support and debugfs components, the exported WED ops object, and the standalone STAR EMAC driver.

## Important APIs, Types, and Functions
The key build variables are `obj-$(CONFIG_NET_MEDIATEK_SOC) += mtk_eth.o`, `mtk_eth-y := ...`, `mtk_eth-$(CONFIG_NET_MEDIATEK_SOC_WED) += ...`, `obj-$(CONFIG_NET_MEDIATEK_SOC_WED) += mtk_wed_ops.o`, and `obj-$(CONFIG_NET_MEDIATEK_STAR_EMAC) += mtk_star_emac.o`. `mtk_eth-y` always includes `mtk_eth_soc.o`, `mtk_eth_path.o`, `mtk_ppe.o`, `mtk_ppe_debugfs.o`, and `mtk_ppe_offload.o`. When WED is enabled, the composite also includes `mtk_wed.o`, `mtk_wed_mcu.o`, and `mtk_wed_wo.o`; `mtk_wed_debugfs.o` is added only when `CONFIG_DEBUG_FS` is defined.

## Control Flow
Build control is declarative. Kbuild creates `mtk_eth.o` as built-in or module according to `CONFIG_NET_MEDIATEK_SOC`, links unconditional core/offload objects into it, and conditionally augments it with WED implementation files. `mtk_wed_ops.o` is built as a separate object under the WED symbol, likely because it exposes operations across module boundaries.

## State and Persistence
No runtime state exists. The persistent output is the kernel build artifact graph, determined by `.config` and the object lists.

## Dependencies and Integration Points
This file integrates directly with `Kconfig` and the C files in the directory. Its most important coupling is that `mtk_eth_soc.c` references symbols provided by `mtk_eth_path.o`, PPE files, and WED headers/objects. The debugfs conditional keeps WED debug support out of non-debugfs builds.

## Risks
Ordering and symbol ownership matter. Moving a source file out of `mtk_eth-y` can create unresolved symbols in the composite driver. Making `mtk_wed_ops.o` part of `mtk_eth-y` instead of a separate object could break consumers that expect its current linkage. Debugfs-specific code must remain fully guarded by `CONFIG_DEBUG_FS`.

## Test Signals
Build with `CONFIG_NET_MEDIATEK_SOC=y/m/n`, `CONFIG_NET_MEDIATEK_SOC_WED=y/n`, `CONFIG_DEBUG_FS=y/n`, and `CONFIG_NET_MEDIATEK_STAR_EMAC=y/m`. Use `nm` or modpost output to verify that `mtk_eth.o`, WED objects, and STAR EMAC objects appear in the intended configurations without unresolved symbols.
