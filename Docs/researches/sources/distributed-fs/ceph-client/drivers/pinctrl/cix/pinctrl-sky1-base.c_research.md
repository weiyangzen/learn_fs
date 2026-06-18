# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1-base.c

Purpose: Reusable Cix Sky1 pinctrl base driver that parses DT pinmux/config data, creates one group per pin, writes mux/pull/drive fields, and exports `sky1_base_pinctrl_probe()`.

Important APIs/types/functions: uses SoC-provided `struct sky1_pinctrl_soc_info` and `sky1_pin_desc` from `pinctrl-sky1.h`. Core callbacks are `sky1_pctrl_dt_node_to_map()`, `sky1_pmx_set_mux()`, `sky1_pconf_group_set/get()`, and `sky1_pctrl_build_state()`. Register field macros cover mux bits, pull bits, and drive-strength bits.

Control flow: exported probe validates SoC info, maps MMIO resource 0, allocates a dynamic pinctrl descriptor and pin list, builds one-pin groups, registers and enables pinctrl, and calls `pinctrl_provide_dummies()` to make default/sleep state transitions work across separate controllers. DT parsing walks child nodes, reads packed `pinmux` cells, validates pin/function numbers, adds mux maps, and optionally adds group config maps.

State and persistence: hardware state is per-pin MMIO registers at `base + pin * 4`. Group `config` stores the last config value for group get but is not a full hardware readback. Driver state is devm-managed.

Dependencies/integration: Linux OF, pinctrl, pinmux, generic pinconf, MMIO accessors, and SoC-specific Sky1 data. Functions are generic names `func0` through `func3`; valid function count is per pin.

Risks: `sky1_pconf_parse_conf()` declares the config argument as `enum pin_config_param`, though it carries a numeric argument; this is type-confusing but works as integer C. Unsupported drive strengths silently map to default table index 4 rather than erroring. No locks protect MMIO read-modify-write operations, so concurrent pinctrl changes could race.

Test signals: parse DT nodes with valid/invalid packed pinmux cells, verify one group per pin in debugfs, set pull-up/down/disable and drive strengths, confirm default/sleep dummy behavior during suspend transitions, and validate exported symbol use by the SoC driver.
