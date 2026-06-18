# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-aux-synth.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-aux-synth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-aux-synth.c

Purpose: implements SPEAr auxiliary synthesizer clocks, which generate rates from table-selected X/Y scale values and one of two equations, with optional gate registration on the same register.

Important APIs and control flow: `aux_calc_rate()` computes table-derived rates using equation selection, `clk_aux_determine_rate()` chooses the nearest table entry via `clk_round_rate_index()`, `clk_aux_recalc_rate()` reads equation, X, and Y fields from MMIO and computes the live rate, and `clk_aux_set_rate()` rewrites those fields from the chosen table row. `clk_register_aux()` validates arguments, allocates `struct clk_aux`, applies default or custom masks, registers the synthesizer clock, and optionally registers a gate named by `gate_name` with `CLK_SET_RATE_PARENT`.

State and persistence behavior: software state is heap-allocated `struct clk_aux` containing the MMIO register pointer, masks, rate table, count, and optional shared spinlock. Hardware state persists in the synthesizer fields and optional enable bit. The object is not devm-managed and has no explicit unregister path in this file.

Dependencies and integration points: depends on CCF, raw MMIO access, spinlocks supplied by platform clock init code, `struct aux_rate_tbl`, `struct aux_clk_masks`, and the shared rounding helper from `clk.c`. SPEAr1310/1340 use it for UART, SDHCI, CFXD, C3, GMAC PHY, I2S, ADC, and similar synthesized clocks.

Risks and test signals: risks include returning NULL rather than `ERR_PTR()` on registration failure after allocation, leaking a separately registered gate if later steps fail, 10 kHz granularity/truncation from scaled arithmetic, invalid table ordering breaking nearest-rate selection, and no divide-by-zero protection in table-based calculations. Test signals include expected rates from X/Y/eq tables, live recalc matching register fields, gate enable bit behavior, safe concurrent reads/writes under the shared lock, and working device clocks for UART, SDHCI, GMAC, I2S, and ADC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-aux-synth.c -->
