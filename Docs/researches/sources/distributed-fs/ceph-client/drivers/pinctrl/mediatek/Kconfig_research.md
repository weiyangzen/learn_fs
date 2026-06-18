# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/Kconfig

Purpose: Defines the MediaTek, Airoha, and legacy Ralink pinctrl Kconfig menu. It selects the correct common pinctrl framework layers, GPIO support, external interrupt support, and SoC-specific drivers.

Important APIs/types/functions: Key symbols include `EINT_MTK`, `PINCTRL_MTK`, `PINCTRL_MTK_V2`, `PINCTRL_MTK_MTMIPS`, `PINCTRL_MTK_MOORE`, `PINCTRL_MTK_PARIS`, `PINCTRL_AIROHA`, many SoC options such as `PINCTRL_MT2701`, `PINCTRL_MT2712`, `PINCTRL_MT7988`, `PINCTRL_MT8196`, and PMIC `PINCTRL_MT6397`. `select` lines wire shared support such as `PINMUX`, `GENERIC_PINCONF`, `GPIOLIB`, `IRQ_DOMAIN`, `GPIOLIB_IRQCHIP`, and `REGMAP_MMIO`.

Control flow: Kconfig resolution determines which objects the Makefile builds. Older ARMv7/PMIC drivers select `PINCTRL_MTK`; Moore binding drivers select `PINCTRL_MTK_MOORE`; newer Paris binding drivers select `PINCTRL_MTK_PARIS`; MIPS/Ralink drivers select `PINCTRL_MTK_MTMIPS`; Airoha builds a standalone tristate driver.

State and persistence: No runtime state. It persists build-time dependency policy and default enablement, such as defaulting many ARM64 MediaTek SoC drivers when `ARCH_MEDIATEK` is enabled and defaulting PMIC pinctrl with `MFD_MT6397`.

Dependencies and integration points: Sourced by the parent pinctrl Kconfig. It must remain synchronized with `drivers/pinctrl/mediatek/Makefile`, SoC driver filenames, and common helper availability.

Risks: Incorrect `select` relationships cause build failures or missing runtime capabilities such as GPIO-to-IRQ translation. Broad `COMPILE_TEST` paths must still select all helper libraries. `EINT_MTK` defaults differ for `PINCTRL_MTK_PARIS` versus older bool symbols; regressions here can silently remove debounce/wake IRQ support.

Test signals: `allyesconfig`, `allmodconfig`, MediaTek ARM/ARM64 defconfigs, Ralink configs, PMIC configs, and targeted `COMPILE_TEST` builds for each family. Validate generated `.config` includes expected common helpers when a SoC driver is selected.
