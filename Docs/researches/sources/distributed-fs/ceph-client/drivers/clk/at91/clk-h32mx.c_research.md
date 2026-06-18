# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-h32mx.c

Purpose: provider for SAMA5D4/SAMA5D2 H32MX clock divider, a master-clock derivative that can pass through the parent or divide by two to keep the H32 matrix clock within limits.

Important APIs and data: `at91_clk_register_h32mx()` registers a single-output clock with `h32mx_ops`. The private struct stores `clk_hw` and PMC regmap. `H32MX_MAX_FREQ` is 90 MHz.

Control flow: `recalc_rate` reads `AT91_PMC_MCKR`; if `AT91_PMC_H32MXDIV` is set, it returns parent/2, otherwise parent and warns when above max. `determine_rate` chooses the closer of parent or parent/2. `set_rate` validates exact parent or parent/2 and updates `H32MXDIV`.

State and persistence: no explicit save/restore state; the selected divider is only in `AT91_PMC_MCKR`. The registered clock object persists with its regmap pointer.

Dependencies and integration: used by SAMA5D2 setup for `h32mxck`, which then parents 32-bit peripheral clocks. It depends on regmap and common clock rate-gate behavior.

Risks: unsupported rates return `-EINVAL`; no automatic cap is enforced on recalc beyond a warning, so bootloader-provided overclocking can persist until consumers set a rate. Test signals include `h32mxck` at or below 90 MHz, peripheral32 clocks parented by `h32mxck`, and MCKR bit transitions during rate changes.
