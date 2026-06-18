# sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos-pinctrl.h

Purpose: this Samsung binding header defines symbolic pinctrl constants for Exynos DTS files.

Important API surface: it exports pull mode constants (`EXYNOS_PIN_PULL_NONE`, DOWN, UP), power-down function constants (`EXYNOS_PIN_PDN_*`), drive strength encodings for Exynos4/3250/5250, Exynos5260, and Exynos5420/542x/5800/850-style blocks, and pin function constants from input/output through function 6 plus external interrupt function `0xf` (`EXYNOS_PIN_FUNC_EINT`/`F`).

Control flow: none. DTS files include the header to express pin configuration values symbolically; dtc emits the numbers that Samsung pinctrl drivers apply.

State and persistence: constants only. The values persist in DTBs as pull, drive, power-down, and mux settings.

Dependencies and integration: integrated with Exynos pinctrl binding properties and Exynos board DTS files selected by the Samsung Makefile. The different drive-strength macro families reflect SoC-specific register encodings.

Risks and test signals: changing a value can misconfigure every board using that SoC family. A key risk is using the wrong drive-strength family for a DTS node. Test with dt-schema for Samsung pinctrl nodes and boot/peripheral checks for GPIO, eMMC, SDIO, I2C, and sleep/resume pin states.
