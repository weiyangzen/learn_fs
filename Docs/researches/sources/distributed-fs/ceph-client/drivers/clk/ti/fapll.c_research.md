# sources/distributed-fs/ceph-client/drivers/clk/ti/fapll.c

Purpose: DM816 Flying Adder PLL and synthesizer clock driver. It registers a parent FAPLL with two parents and up to seven output clocks, including fractional synthesizers and fixed/hardwired special cases.

Important APIs/types/functions: `ti_fapll_setup()` for `ti,dm816-fapll-clock`, `ti_fapll_ops`, `ti_fapll_synt_ops`, `ti_fapll_synth_setup()`, and structures `fapll_data` and `fapll_synth`.

Control flow: setup maps the FAPLL base, obtains reference and bypass parents, detects inverted bypass behavior for DDR PLL, registers the main PLL, then iterates `clock-output-names` and optional `clock-indices` to register synthesizer outputs. Runtime main PLL ops enable/disable PLLEN, calculate bypass or `parent / P * N`, choose parent by bypass bit, and set rate by entering bypass, writing P/N, waiting for lock, and clearing bypass. Synth ops power outputs via PWD bits, compute fractional/post-divider rates, and program frequency/divider load bits.

State and persistence: `fapll_data` owns base MMIO, parent clocks, onecell output array, and bypass polarity. `fapll_synth` owns per-output register pointers and index. Hardware PLL, PWD, synth frequency, and divider registers persist.

Dependencies/integration: uses raw MMIO, CCF onecell providers, clkdev for synthesizer names, OF address/clock properties, and DM816 TRM-specific register layouts.

Risks: address-based special cases (`fapll_is_ddr_pll`, `is_audio_pll_clk1`) depend on mapped virtual address low bits matching hardware offsets, which is fragile. `ti_fapll_determine_rate()` stores an error code in `req->rate` but returns success. Main divider rates below parent are unsupported.

Test signals: DM816 boot with FAPLL nodes, lock timeout behavior, main PLL set-rate and bypass parent changes, fixed audio 32.768 kHz output, fractional synth rate programming, and onecell index holes.
