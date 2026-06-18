# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-common.c

## Purpose
`pinctrl-mtk-common.c` implements the legacy MediaTek pinctrl core used by older SoC drivers such as MT8365 and MT8516. It registers Linux pinctrl, pinmux, pinconf, GPIO, and EINT services, translates device-tree `pinmux` and generic pinconf properties into register writes, and provides common helpers for special MediaTek pull, IES, and SMT layouts.

## Important APIs, Types, And Functions
- `mtk_get_regmap()` chooses `regmap1` or `regmap2` based on the SoC's `type1_start`/`type1_end` interval.
- `mtk_get_port()` calculates port register stride using `mode_shf`, `port_mask`, and `port_shf`.
- GPIO methods implement direction, get/set, GPIO-to-IRQ, and debounce configuration.
- `mtk_pconf_spec_set_ies_smt_range()` and `mtk_pctrl_spec_pull_set_samereg()` are exported helpers for SoC-provided special IES/SMT and PUPD/R1/R0 tables.
- `mtk_pconf_parse_conf()` supports bias disable, pull-up, pull-down, input enable, output level, Schmitt enable, and drive strength.
- `mtk_pctrl_dt_node_to_map()` parses child nodes containing `pinmux` arrays plus generic pinconf properties.
- `mtk_pctrl_init()` is the main registration entry point, while `mtk_pctrl_common_probe()` retrieves OF match data and calls it.

## Control Flow
SoC platform drivers call `mtk_pctrl_common_probe()` or directly `mtk_pctrl_init()`. Probe obtains a regmap from the `mediatek,pctl-regmap` phandle or caller, optionally obtains a second regmap, stores SoC devdata, builds one pinctrl group per pin, registers the pinctrl device, allocates and registers a GPIO chip, adds a GPIO-to-pin range, and initializes EINT if the SoC advertises AP EINTs. At runtime, DTS pinctrl states are parsed into maps. Mux maps validate function numbers against each pin's function list and write pinmux bits. Config maps invoke `mtk_pconf_parse_conf()`.

## State And Persistence
Runtime state is stored in devm-managed `struct mtk_pinctrl`: regmaps, pinctrl descriptor/device, GPIO chip pointer, generated groups, group names, devdata, and EINT object. GPIO chip registration is explicitly removed on post-registration probe failures. Hardware pin state persists in registers. `group->config` stores the last applied config value for group get operations but does not represent full hardware state.

## Dependencies And Integration Points
The file integrates with Linux pinctrl core, pinconf generic parser, pinmux ops, gpiolib, regmap/syscon, platform devices, OF IRQ parsing, PM sleep ops, and `mtk-eint`. SoC data files must provide `struct mtk_pinctrl_devdata` with pin descriptors, register offsets, packing fields, drive tables, optional special callbacks, and EINT hardware parameters.

## Risks
The generic IES/SMT path depends on subtle offset/port packing conventions. `mtk_gpio_get_direction()` and `mtk_gpio_get()` read from `regmap1` directly instead of `mtk_get_regmap()`, which may be wrong for SoCs where some pins use `regmap2`. `mtk_pmx_set_mode()` calls `spec_pinmux_set()` but continues with generic programming. Group config get returns cached last config, not live register state. `gpiochip_add_data()` is not devm-managed here.

## Test Signals
Build legacy MediaTek SoC drivers against this common file. Boot with valid and invalid `pinmux` states, multiple child nodes, and generic pinconf properties. Exercise GPIO request, direction input/output, get/set, GPIO-to-IRQ, debounce, special PUPD/R1/R0, special IES/SMT, MT8365 pull mode, `regmap2` SoCs, and EINT suspend/resume.
