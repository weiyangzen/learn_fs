# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/Kconfig

Purpose: Defines build-time configuration for Freescale/NXP pinctrl drivers spanning common i.MX MMIO controllers, i.MX SCMI firmware-backed controllers, i.MX SCU controllers, legacy i.MX1/i.MX27 controllers, MXS i.MX23/i.MX28 controllers, Vybrid, i.MX8/9, and i.MXRT variants.

Important APIs and symbols: Core symbols include `PINCTRL_IMX`, `PINCTRL_IMX_SCMI`, `PINCTRL_IMX_SCU`, `PINCTRL_IMX1_CORE`, and `PINCTRL_MXS`. SoC symbols select the appropriate core, for example `PINCTRL_IMX25` and `PINCTRL_IMX35` select `PINCTRL_IMX`, `PINCTRL_IMX1`/`PINCTRL_IMX27` select `PINCTRL_IMX1_CORE`, and `PINCTRL_IMX23`/`PINCTRL_IMX28` select `PINCTRL_MXS`.

Control flow: Kconfig selection determines which common objects and SoC data files are compiled. Defaults are tied to matching SoC architecture symbols, with `COMPILE_TEST` enabling broader build coverage.

State and persistence: No runtime state. The file controls whether driver objects exist as built-in or modules and which generic pinctrl facilities are selected.

Dependencies and integration points: Integrates with architecture symbols such as `ARCH_MXC`, `SOC_IMX*`, `IMX_SCU`, `ARM_SCMI_PROTOCOL`, generic pinctrl group/function helpers, `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, and `REGMAP`.

Risks: Missing `select` lines cause link failures or runtime feature gaps in shared core files. Built-in-only legacy symbols affect init ordering; tristate newer symbols must align with exported symbols from common cores. The SCMI driver is platform-allowlisted, so Kconfig enablement alone is not enough for runtime probe.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, SoC defconfigs, and module/built-in combinations for common core plus individual SoC drivers validate this file.
