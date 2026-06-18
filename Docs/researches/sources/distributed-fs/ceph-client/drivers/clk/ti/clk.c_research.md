# sources/distributed-fs/ceph-client/drivers/clk/ti/clk.c

Purpose: shared TI clock infrastructure. It provides low-level register access indirection, DT clock alias registration, retry initialization, provider memory-map indexing, feature setup, common alias helpers, and tracking for registered `clk_hw_omap` clocks.

Important APIs/types/functions: `ti_clk_setup_ll_ops()`, `ti_dt_clocks_register()`, `ti_clk_retry_init()`, `ti_clk_get_reg_addr()`, `ti_clk_latch()`, `omap2_clk_provider_init()`, `omap2_clk_legacy_provider_init()`, `ti_dt_clk_init_retry_clks()`, `ti_clk_add_aliases()`, `ti_clk_setup_features()`, `omap2_clk_enable_init_clocks()`, `of_ti_clk_register()`, `of_ti_clk_register_omap_hw()`, `omap2_clk_for_each()`, and `omap2_clk_is_hw_omap()`.

Control flow: platform code first installs `ti_clk_ll_ops`, which is augmented with this file's read/write/rmw callbacks. Provider init maps clock DT parent nodes to `clk_memmaps[]`. Individual clock setup code then calls `ti_clk_get_reg_addr()` to encode provider index, offset, and bit. Alias registration resolves legacy `DT_CLK` names by `clock-output-names`, node names, or clkctrl phandle arguments and adds `clkdev` lookups.

State and persistence: persistent globals include `ti_clk_ll_ops`, `ti_clk_features`, `clocks_node_ptr[]`, `clk_memmaps[]`, `clk_hw_omap_clocks`, and `retry_list`. Legacy provider data may be allocated from memblock. Retry entries are consumed and freed by `ti_dt_clk_init_retry_clks()`.

Dependencies/integration: integrates Linux CCF, clkdev, OF, regmap/syscon or MMIO, and platform-specific low-level clockdomain/CM callbacks. It is the hub used by TI gate/divider/mux/DPLL/composite/clkctrl files.

Risks: memory-map indexes must match provider setup or register access goes to the wrong region. `ti_dt_clocks_register()` has compatibility behavior for old clkctrl layouts and can suppress repeated warnings after missing clkctrl nodes. Retry processing has a bounded retry count but does not verify that callbacks succeeded.

Test signals: unit-style coverage is mostly boot-time: verify provider init order, alias lookup for old and new DT naming, regmap and MMIO access paths, retry list draining, and `clk_summary` consistency after clock registration.
