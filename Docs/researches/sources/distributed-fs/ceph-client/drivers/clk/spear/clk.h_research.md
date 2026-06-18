# sources/distributed-fs/ceph-client/drivers/clk/spear/clk.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk.h

Purpose: defines the local SPEAr clock framework data structures, register bit masks, registration prototypes, and shared table-rounding callback type.

Important APIs and control flow: the header describes auxiliary synthesizer masks and `struct clk_aux`, fractional synthesizers through `struct clk_frac`, GPT synthesizers through `struct clk_gpt`, VCO/PLL pairs through `struct clk_vco` and `struct clk_pll`, plus rate table types for each. It declares `clk_register_aux()`, `clk_register_frac()`, `clk_register_gpt()`, `clk_register_vco_pll()`, and `clk_round_rate_index()`.

State and persistence behavior: no runtime state is defined directly. The structures encode heap-allocated clock wrapper layout and the masks used to interpret persistent hardware registers.

Dependencies and integration points: depends on CCF types, spinlock type declarations, and Linux integer types. SPEAr platform files include it to register complex clocks, while helper implementation files include it for shared structures and prototypes.

Risks and test signals: risks include legacy CCF API use with `parent_names`, manually managed allocation, u8 table counts limiting table size, and local masks needing to match multiple SPEAr register variants. Test signals are compile coverage across all SPEAr platform configurations, registration of every declared helper, and correct field extraction for custom aux masks in I2S paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk.h -->
