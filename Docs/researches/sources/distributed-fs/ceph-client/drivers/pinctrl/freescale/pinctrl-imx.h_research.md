# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx.h

Purpose: Defines the shared data contract for common i.MX pinctrl SoC drivers and the common `pinctrl-imx.c` implementation.

Important APIs and types: Defines `struct imx_pin_mmio`, `struct imx_pin_scu`, `struct imx_pin`, `struct imx_pin_reg`, `struct imx_pinctrl`, and `struct imx_pinctrl_soc_info`. Exports `imx_pinctrl_probe()`, `imx_pmx_ops`, `imx_pinctrl_pm_ops`, SCU helper prototypes, and macros such as `SHARE_MUX_CONF_REG`, `ZERO_OFFSET_VALID`, `IMX_USE_SCU`, `IMX_MUX_MASK`, and `IOMUXC_CONFIG_SION`.

Control flow: SoC data files fill `imx_pinctrl_soc_info` and call `imx_pinctrl_probe()`. The common driver uses flags and callbacks to decide whether to parse/apply MMIO cells or SCU firmware cells.

State and persistence: The header defines runtime state containers but owns no storage. `struct imx_pinctrl` persists per controller; register offsets and parsed pin configs persist for driver lifetime; hardware state is persisted by MMIO or SCU writes.

Dependencies and integration points: Includes public pinmux definitions and is used by all common i.MX pinctrl SoC files plus SCU support. Its flags encode binding and register-layout differences across SoCs.

Risks: `imx_pin_reg` uses signed 16-bit offsets with `-1` sentinel, so large register maps or zero-offset semantics depend on flags. Callback pointers must be present when `IMX_USE_SCU` is set. Macros such as `PAD_CTL_MASK()` assume modest bit widths.

Test signals: Build every `PINCTRL_IMX` SoC, compile SCU and non-SCU paths, parse representative DT bindings, and validate register offsets for SoCs with shared mux/config registers and zero-valid offsets.
