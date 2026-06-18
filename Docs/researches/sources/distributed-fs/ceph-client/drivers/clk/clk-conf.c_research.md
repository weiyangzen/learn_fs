# sources/distributed-fs/ceph-client/drivers/clk/clk-conf.c


### Purpose
`clk-conf.c` applies standard device-tree assigned-clock defaults. It parses assigned clock parents and rates and programs them through the CCF during device/provider setup.

### Important APIs, Types, And Functions
The exported API is `of_clk_set_defaults(struct device_node *node, bool clk_supplier)`. Internals `__set_clk_parents()` and `__set_clk_rates()` parse `assigned-clock-parents`, `assigned-clocks`, `assigned-clock-rates`, and `assigned-clock-rates-u64`.

### Control Flow, State, And Persistence
`of_clk_set_defaults()` first reparents assigned clocks, then applies assigned rates. Each index resolves phandle arguments with `of_parse_phandle_with_args()`, skips empty phandles, obtains `struct clk` from providers, performs `clk_set_parent()` or `clk_set_rate()`, and drops clock references. If the node supplies one of the clocks and `clk_supplier` is false, the function exits early to avoid configuring a provider before it is ready. Persistent effects are the clock parent/rate changes in CCF and hardware provider state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF phandle parsing, provider lookup, `clk_set_parent()`, `clk_set_rate()`, and the assigned-clock DT binding. Risks include mismatched array lengths, self-supplier deferral semantics, 32-bit versus 64-bit rate property precedence, and partial application if a later entry fails. Test signals include null phandle holes, `-EPROBE_DEFER` propagation, self-supplier behavior for both `clk_supplier` values, `assigned-clock-rates-u64`, and logs for failed reparent/rate programming.
