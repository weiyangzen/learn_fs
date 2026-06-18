# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-frac.c

Purpose: implements the MMP fractional M/N clock type used for UART and I2S synthesizer clocks.

Important APIs/functions: `mmp_clk_register_factor` allocates and registers `struct mmp_clk_factor`. The `clk_factor_ops` callbacks are `clk_factor_recalc_rate`, `clk_factor_determine_rate`, `clk_factor_set_rate`, and `clk_factor_init`.

Control flow: `determine_rate` scans a caller-provided `u32_fract` table and picks the nearest output derived from `parent * denominator / (numerator * factor)`. `set_rate` chooses the nearest not-greater table entry, masks numerator/denominator fields, and writes the MMIO register under an optional spinlock. `init` validates the current hardware fraction against the table and enables or normalizes the synthesizer.

State and persistence: state is in the hardware register at `base`; the allocated `mmp_clk_factor` stores masks, table pointer, count, and lock. No suspend state is kept here.

Dependencies and integration: included by MMP SoC clock files through `clk.h`. It uses Linux CCF, `do_div`, `u32_fract`, relaxed MMIO access, and optional SoC-provided locks.

Risks: `determine_rate` assumes the table is ordered by increasing effective rate. A zero denominator in hardware returns zero rate. `set_rate` silently falls back to the first entry for very low rates and always returns success after programming an approximate value.

Test signals: unit-level checks of table ordering and rounding, UART/I2S baud/audio sample-rate validation, and boot logs for synthesized clocks after `clk_factor_init`.
