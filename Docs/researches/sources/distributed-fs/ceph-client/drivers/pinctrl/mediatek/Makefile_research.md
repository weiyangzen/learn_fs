# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/Makefile

Purpose: Maps MediaTek/Airoha/Ralink pinctrl Kconfig symbols to object files. It is the build glue between the Kconfig menu and the individual common or SoC-specific driver sources.

Important APIs/types/functions: Core objects are `mtk-eint.o`, `pinctrl-mtk-common.o`, `pinctrl-mtk-common-v2.o`, `pinctrl-mtmips.o`, `pinctrl-moore.o`, and `pinctrl-paris.o`. SoC objects include `pinctrl-airoha.o`, legacy Ralink/MT762x files, ARMv7 files such as `pinctrl-mt2701.o`, ARM64 files such as `pinctrl-mt2712.o`, `pinctrl-mt8189.o`, `pinctrl-mt8196.o`, and PMIC `pinctrl-mt6397.o`.

Control flow: Kbuild evaluates `obj-$(CONFIG_...)` assignments and links selected objects built-in or as modules according to the symbol type. Common framework objects are selected by Kconfig and built before SoC objects that reference their exported helpers.

State and persistence: No runtime state. The file persists build membership and must reflect every Kconfig option and source filename.

Dependencies and integration points: Tightly coupled to `Kconfig`, common headers, and SoC source files. If a driver selects `PINCTRL_MTK_MOORE`, both `pinctrl-moore.o` and `pinctrl-mtk-common-v2.o` must be present for symbols to resolve.

Risks: Missing or misspelled object entries cause selected drivers to disappear or fail link. Tristate/common-helper combinations are especially sensitive because helpers may need to be linked in the same module/built-in mode as users. Formatting drift, such as the spaced `PINCTRL_MT8189` line, is low risk but worth normalizing only in separate cleanup.

Test signals: `make drivers/pinctrl/mediatek/`, `modpost` symbol checks, build matrix for built-in and module variants, and comparing Kconfig symbols against Makefile object entries.
