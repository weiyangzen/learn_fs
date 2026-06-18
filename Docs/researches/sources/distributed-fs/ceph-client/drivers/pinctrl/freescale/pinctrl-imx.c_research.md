# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx.c

Purpose: Provides the shared MMIO/SCU-aware i.MX pinctrl implementation used by many NXP/Freescale SoC data files. It parses i.MX `fsl,pins`/`pinmux` bindings, registers generic groups/functions, applies muxes and pad configs, and supplies PM state forcing.

Important APIs and functions: Exported API is `imx_pinctrl_probe()` plus `imx_pmx_ops` and `imx_pinctrl_pm_ops`. Important internals include `imx_dt_node_to_map()`, `imx_pmx_set_one_pin_mmio()`, `imx_pinconf_get_mmio()`, `imx_pinconf_set_mmio()`, `imx_pinctrl_parse_pin_mmio()`, `imx_pinctrl_parse_groups()`, `imx_pinctrl_parse_functions()`, and `imx_pinctrl_probe_dt()`.

Control flow: SoC drivers pass `imx_pinctrl_soc_info` to `imx_pinctrl_probe()`. Probe maps registers, optionally maps an input-select block, registers the pinctrl device, parses DT into generic functions/groups, then enables hogs. State selection calls `imx_dt_node_to_map()` to create mux and config maps; mux setting writes mux registers and select-input registers, while config setting writes pad-control registers or delegates to SCU callbacks.

State and persistence: `struct imx_pinctrl` stores MMIO bases, parsed `pin_regs`, group index, and SoC info. Parsed group data is devm allocated. Hardware mux, select input, SION, and pad config values persist in IOMUXC registers or SCU firmware until reprogrammed.

Dependencies and integration points: Uses generic pinctrl group/function helpers, pinmux/pinconf core, OF parsing, syscon/regmap for optional GPR attachment, platform MMIO mapping, and SoC-specific data in files such as `pinctrl-imx25.c` and `pinctrl-imx35.c`.

Risks: DT cell-size handling differs for default, shared mux/conf, SCU, and generic `pinmux` formats; malformed bindings can misparse register offsets. `imx_pmx_ops.gpio_set_direction` is a global ops struct field overwritten during probe, which is risky with multiple controller variants. Shared mux/config registers require read-modify-write masking to preserve mux bits. Quirky select-input encoding uses packed width/shift/select fields.

Test signals: Probe on MMIO and SCU i.MX variants, DT parsing for flat and nested function layouts, pin state changes for mux/config/select-input/SION, GPIO direction callbacks, debugfs pinconf output, suspend/resume default/sleep states, and invalid `fsl,pins` sizes.
