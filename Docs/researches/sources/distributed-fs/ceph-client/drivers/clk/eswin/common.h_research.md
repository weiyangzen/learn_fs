# sources/distributed-fs/ceph-client/drivers/clk/eswin/common.h

Purpose: defines ESWIN clock descriptor structures, frequency limits, private divider flags, registration prototypes, and table-building macros.

Important APIs/types/functions: central types include `eswin_clock_data`, `eswin_divider_clock`, `eswin_fixed_rate_clock`, `eswin_fixed_factor_clock`, `eswin_gate_clock`, `eswin_mux_clock`, `eswin_pll_clock`, `eswin_clk_pll`, and generic `eswin_clk_info`. Macros such as `ESWIN_FIXED`, `ESWIN_PLL`, `ESWIN_DIV`, `ESWIN_GATE`, `ESWIN_MUX`, and `*_TYPE` forms initialize descriptor tables.

Control flow: no executable code; it defines the data contracts consumed by `clk.c` and SoC files.

State and persistence: no direct state. Struct fields point to MMIO offsets, parents, flags, and IDs that determine registered clock state.

Dependencies and integration points: used by all ESWIN clock providers and relies on common clock types, `clk_parent_data`, `clk_hw_onecell_data`, `notifier_block`, and spinlocks from included kernel headers via C files.

Risks: descriptor macros hide field ownership differences between direct arrays and typed `eswin_clk_info` arrays; `_pid` and `_pdata` usage must match the registration path. `ESWIN_PRIV_DIV_MIN_2` changes hardware divider interpretation and must only be used where the register encoding really forbids 0/1.

Test signals: compile descriptor arrays with sparse IDs, validate onecell lookups for all exported binding IDs, and check that macro-produced parent relationships match clock tree documentation.
