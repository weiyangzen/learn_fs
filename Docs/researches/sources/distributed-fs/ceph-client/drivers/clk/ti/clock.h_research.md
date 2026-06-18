# sources/distributed-fs/ceph-client/drivers/clk/ti/clock.h

Purpose: internal header for TI clock drivers. It defines shared clock wrapper structures, table schemas, flag bits, macros, extern data declarations, and cross-file helper prototypes.

Important APIs/types/functions: structures include `clk_omap_divider`, `clk_omap_mux`, `ti_clk`, `ti_clk_mux`, `ti_clk_divider`, `ti_clk_gate`, `ti_dt_clk`, `omap_clkctrl_div_data`, `omap_clkctrl_bit_data`, `omap_clkctrl_reg_data`, and `omap_clkctrl_data`. It declares ops such as `ti_clk_divider_ops`, `ti_clk_mux_ops`, `omap_gate_clk_ops`, and helpers across registration, clockdomain, DPLL, divider, mux, gate, and clkctrl paths.

Control flow: no executable code, but the flag definitions determine behavior in setup and runtime paths. Global flags describe legacy index schemes and rate-parent behavior; gate flags select waits, inverted enables, and clockdomain handling; DPLL flags select modes; clkctrl flags select module supervision and SoC masks.

State and persistence: wrapper structs hold runtime context such as divider register context, mux saved parent, DPLL cached values through referenced public TI structures, and clkctrl table metadata. The header also exposes global `ti_clk_features` and `ti_clk_ll_ops`.

Dependencies/integration: this header is the internal contract among all files in `drivers/clk/ti`. Public pieces from `<linux/clk/ti.h>` and CCF types are assumed.

Risks: bit values are reused across flag domains, so callers must pass the right flag namespace. Structure layout is relied on by `container_of()` macros. Any signature change affects many clock setup files.

Test signals: compile coverage across enabled SoC configs is the primary signal; runtime coverage comes from exercising each declared ops structure and table type.
