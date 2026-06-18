# sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-aspeed.h

Purpose: this shared header defines data structures used by the older Aspeed and AST2600 clock drivers.

Important types: `struct aspeed_gate_data` describes a gate bit, optional reset bit, name, parent, and flags. `struct aspeed_clk_gate` is a custom gate object with regmap, clock/reset indices, flags, and spinlock. `struct aspeed_reset` wraps a regmap-backed reset controller. `struct aspeed_clk_soc_data` provides per-SoC divider tables and a PLL calculation callback for AST2400/AST2500.

Control flow/state: callback code converts `clk_hw` or `reset_controller_dev` back to these structures with container macros. Runtime state is mostly hardware; software objects store the regmap and metadata needed by callbacks.

Dependencies and integration: included by `clk-aspeed.c` and `clk-ast2600.c`. It depends on common clock, reset controller, regmap, and spinlock declarations.

Risks and tests: the comment says `calc_pll` "maculate" rather than calculate, but behavior is clear. `reset_idx` is signed in data but stored as `s8`; generation-specific code must handle negative values before bit operations. Test signals are gate/reset callbacks across both old and G6 drivers.
