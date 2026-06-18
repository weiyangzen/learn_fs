# sources/distributed-fs/ceph-client/drivers/clk/clk-composite.c


### Purpose
`clk-composite.c` implements the reusable CCF composite clock wrapper that combines optional mux, rate, and gate subclocks into one logical clock.

### Important APIs, Types, And Functions
Public registration APIs are `clk_hw_register_composite()`, `clk_hw_register_composite_pdata()`, `clk_register_composite()`, `clk_register_composite_pdata()`, `clk_hw_unregister_composite()`, and `devm_clk_hw_register_composite_pdata()`. Internal callbacks forward parent selection, rate calculation, rate setting, gate state, and enable/disable to the subclock ops after setting each sub-HW's `clk` context.

### Control Flow, State, And Persistence
Registration allocates `struct clk_composite`, validates required sub-ops, builds a synthetic `clk_ops` table based on supplied subcomponents, registers the composite hardware, then points each child `clk_hw` at the composite's `struct clk`. `determine_rate()` either evaluates all mux parents and picks the closest rate through the rate component, honors `CLK_SET_RATE_NO_REPARENT`, or delegates to the rate or mux component alone. `set_rate_and_parent()` orders parent and rate changes based on temporary rate to reduce overshoot.

### Dependencies, Integration Points, Risks, And Test Signals
The file is a central integration point for SoC drivers that compose generic mux/divider/gate blocks. Risks include accepting inconsistent sub-op sets, ownership ambiguity because unregistering the composite only frees the wrapper and not caller-owned sub-HW allocations, and subtle rate-selection behavior when parents return errors. Test signals include mux-only, rate-only, gate-only, and full composite clocks; `CLK_SET_RATE_NO_REPARENT`; exact and closest parent selection; invalid ops rejection; devm release; and unregister paths not freeing caller-owned subcomponents unexpectedly.
