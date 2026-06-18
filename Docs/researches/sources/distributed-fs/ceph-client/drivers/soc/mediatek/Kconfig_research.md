# sources/distributed-fs/ceph-client/drivers/soc/mediatek/Kconfig

## Purpose
This Kconfig menu exposes build-time selections for MediaTek SoC support drivers. It gates the helper, bus, multimedia, power-management, PMIC wrapper, regulator coupling, smart-voltage-scaling, and SoC identification modules under `ARCH_MEDIATEK` or `COMPILE_TEST` where appropriate.

## Important APIs, Types, and Functions
The file defines configuration symbols rather than C APIs. Important symbols are `MTK_CMDQ`, `MTK_DEVAPC`, `MTK_DVFSRC`, `MTK_INFRACFG`, `MTK_PMIC_WRAP`, `MTK_REGULATOR_COUPLER`, `MTK_MMSYS`, `MTK_SVS`, and `MTK_SOCINFO`. The dependency graph is meaningful: `MTK_CMDQ` selects mailbox and infracfg support, `MTK_PMIC_WRAP` depends on reset controller and OF, `MTK_MMSYS` tolerates `MTK_CMDQ=n` but depends on `HAS_IOMEM`, and `MTK_SOCINFO` selects `SOC_BUS`.

## Control Flow and State
There is no runtime control flow. Its persistent effect is the kernel build configuration that determines which objects in the sibling Makefile are compiled and whether code paths using mailbox, regmap, reset, nvmem, regulator, or SoC bus APIs are reachable.

## Dependencies and Integration Points
The menu integrates with the Linux Kconfig system and downstream Makefile object selection. Several options are tristate modules, while `MTK_INFRACFG` and `MTK_REGULATOR_COUPLER` are bools because they provide low-level helper behavior used by other drivers.

## Risks and Test Signals
Risk is mostly dependency drift: missing `select` or `depends on` clauses can allow compile failures in non-MediaTek builds. Test signals are `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, and targeted builds with each symbol enabled as module or built-in.
