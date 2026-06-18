# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-fixed-factor.h

Purpose: this header provides a small OWL-local macro wrapper around the common clock fixed-factor implementation.

Important API: `OWL_FIX_FACT()` declares a `struct clk_fixed_factor` with `mult`, `div`, and a `CLK_HW_INIT()` using `clk_fixed_factor_ops`. The header also declares `extern const struct clk_ops clk_fixed_factor_ops`.

Control flow/state: fixed-factor clocks have no mutable hardware state. Runtime behavior is delegated entirely to the core fixed-factor clock ops, which calculate child rate from parent rate.

Dependencies and integration: standalone use is minimal in the listed SoC files because composite fixed-factor clocks are usually declared through `OWL_COMP_FIXED_FACTOR`. The header is included by composite and SoC descriptors for consistent naming and availability.

Risks and tests: division by zero would be a macro caller bug. The macro instantiates a concrete object, so duplicate `_struct` names or wrong parent names are compile or DT clock-tree issues. Test signals are clock registration and rate propagation in `clk_summary`.
