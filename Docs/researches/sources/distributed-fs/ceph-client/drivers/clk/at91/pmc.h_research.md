# sources/distributed-fs/ceph-client/drivers/clk/at91/pmc.h

Purpose: private interface for AT91 PMC clock drivers. It defines shared data structures, layout/characteristic descriptors, PM snapshot structure, table helpers, external layout constants, and registration prototypes.

Important APIs and data: key structs are `pmc_data`, `clk_range`, `clk_master_layout`, `clk_master_characteristics`, `clk_pll_layout`, `clk_pll_characteristics`, `clk_programmable_layout`, `clk_pcr_layout`, and `at91_clk_pms`. Macros `nck()` and `ndck()` size clock arrays from sorted ID tables, and `PMC_INIT_TABLE`/`PMC_FILL_TABLE` build mux tables.

Control flow: the header has no executable flow, but it establishes the construction contract used by SoC files: allocate `pmc_data`, register providers, store handles in typed arrays, then expose `of_clk_hw_pmc_get()`. It also declares all helper registration functions for oscillator, PLL, master, peripheral, generated, USB, UTMI, audio, and misc clocks.

State and persistence: `at91_clk_pms` standardizes saved rate, parent rate, enable status, and parent index for backup suspend. Layout structs describe hardware register masks that provider implementations persist in their allocated clock objects.

Dependencies and integration: included by every file in this subset. It depends on Linux regmap, spinlock, I/O, IRQ domain includes, and AT91 DT clock binding constants.

Risks: `nck()` assumes tables are sorted by ascending `id` and non-empty; wrong layout masks cause provider register corruption; prototypes allow both parent names and parent hardware pointers, so callers must pass consistent combinations. Test signals are compile-time: all providers agree on prototypes, layout constants link, and SoC setup tables allocate enough entries for their highest IDs.
