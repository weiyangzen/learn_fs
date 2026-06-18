# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pll.c

Purpose: `clk-pll.c` implements MediaTek PLL common-clock operations: power sequencing, prepare/unprepare, PCW/post-divider rate calculation, rate programming, optional tuner handling, optional fenc/set-clear enable operations, and bulk PLL registration.

Important APIs and functions: exported or externally declared operations include `mtk_pll_is_prepared()`, `mtk_pll_prepare()`, `mtk_pll_unprepare()`, `mtk_pll_recalc_rate()`, `mtk_pll_calc_values()`, `mtk_pll_set_rate()`, `mtk_pll_determine_rate()`, `mtk_clk_register_pll_ops()`, `mtk_clk_register_pll()`, `mtk_clk_unregister_pll()`, `mtk_clk_register_plls()`, `mtk_clk_unregister_plls()`, and `mtk_clk_pll_get_base()`. The main ops tables are `mtk_pll_ops` and exported `mtk_pll_fenc_clr_set_ops`.

Control flow: rate calculation clamps requested rates to `fmax`, picks a post divider from an optional divider table or from the default VCO minimum rule, and computes PCW using integer plus fractional PCW bits. `mtk_pll_set_rate_regs()` disables the tuner, writes postdiv and PCW, toggles the PCW change bit, updates the tuner register, re-enables tuning, and delays. Normal prepare powers on, deisolates, enables, optionally sets an enable mask and reset-bar bit, and waits. Unprepare reverses that sequence. Set/clear prepare variants only write enable set/clear registers and rely on fenc status for prepared state.

State and persistence: state is in PLL MMIO registers and allocated `struct mtk_clk_pll` instances. Bulk registration maps the provider base with `of_iomap()` and stores the base indirectly in each PLL object; unregister recovers one base pointer from registered clocks before `iounmap()`. There is no persistent storage.

Dependencies and integration points: the file integrates with Linux CCF `clk_hw_register()`, OF MMIO mapping, `clk_init_data`, and local PLL descriptors from `clk-pll.h`. `clk-pllfh.c` reuses most of these functions while replacing `.set_rate` with frequency-hopping control.

Risks: descriptor correctness is critical: bad register offsets, bit widths, `pcwbits`, `pd_shift`, or fmax/fmin constraints directly misprogram PLL hardware. Bulk registration does not check duplicate IDs before writing in the error unwind path, unlike some other helpers. Base unmapping relies on at least one registered clock to recover the mapping, which is fragile if descriptors or registration state are corrupted. Rate programming has no explicit locking in this file, so serialization relies on CCF and platform usage.

Test signals: boot logs should show no failed PLL registration. `clk_summary` should report expected PLL rates after `clk_set_rate()`. Tests should cover rates near `fmin`/`fmax`, fractional PCW rounding, divider-table entries, prepare/unprepare power bits, set/clear/fenc variants, and tuner enable state around rate changes.
