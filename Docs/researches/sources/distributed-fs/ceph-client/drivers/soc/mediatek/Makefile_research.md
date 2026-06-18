# sources/distributed-fs/ceph-client/drivers/soc/mediatek/Makefile

## Purpose
This Makefile maps the Kconfig symbols in the same directory to concrete driver objects. It is the build bridge between configuration selections and the MediaTek SoC support code.

## Important APIs, Types, and Functions
There are no runtime APIs. The important entries are one-object mappings such as `obj-$(CONFIG_MTK_CMDQ) += mtk-cmdq-helper.o`, plus two objects under `CONFIG_MTK_MMSYS`: `mtk-mmsys.o` and `mtk-mutex.o`.

## Control Flow and State
The only control flow is kbuild object inclusion. It creates no persistent state, but determines whether exported symbols from drivers such as CMDQ, MMSYS, infracfg, and DVFSRC are present for other kernel subsystems.

## Dependencies and Integration Points
The file relies on Kconfig to enforce prerequisites. It integrates with the kernel module build and may produce separate modules for tristate selections or built-in objects for bool selections.

## Risks and Test Signals
The main risk is Kconfig/Makefile skew, such as a new Kconfig symbol lacking an object or an object compiled without its dependencies. Test signals are successful kernel builds across `m`, `y`, and disabled symbol combinations.
