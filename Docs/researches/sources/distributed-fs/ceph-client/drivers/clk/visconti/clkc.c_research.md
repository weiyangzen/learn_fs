<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.c

## Purpose

`clkc.c` implements common Visconti gate-clock registration and provider allocation.

## Important APIs, Types, And Functions

`struct visconti_clk_gate` is operated by `visconti_clk_gate_ops`. Enable writes the gate bit to `ckon_offset`; disable writes it to `ckoff_offset` after checking status; `is_enabled` reads `ckon_offset`. `visconti_clk_register_gates()` creates a fixed-factor divider for each table entry, registers the gate with parent data and reset metadata, and stores it at the binding ID. `visconti_init_clk()` allocates a flexible onecell provider initialized to `ERR_PTR(-ENOENT)`.

## Control Flow

SoC code calls `visconti_init_clk()`, then one or more `visconti_clk_register_gates()` calls. Each table row yields a `name_div` fixed factor and a gate clock parented by it.

## State And Persistence Behavior

Hardware gate state persists in syscon registers. The gate struct stores reset offsets/bit but this file does not actively couple reset toggling to clock enable/disable. Provider state is devm-managed.

## Dependencies And Integration Points

It depends on CCF, regmap, spinlocks, and table definitions from `clkc.h`. TMPV770x data is the direct consumer.

## Risks And Test Signals

Risks include using `u8` for flags, storing `-1` into unsigned reset fields for `NO_RESET`, and reading enable from the set register rather than an explicit status register if hardware distinguishes them. Test gate enable/disable bit writes, divider rates, and failed registration cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.c -->
