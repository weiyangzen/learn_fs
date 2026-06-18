# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-audio-pll.c

Purpose: common-clock providers for SAMA5D2 audio PLL outputs: fractional core (`FRAC`), PAD output, and PMC output. It converts requested audio rates into PLL multiplier/fraction and divider register fields.

Important APIs and data: exported registration helpers are `at91_clk_register_audio_pll_frac()`, `at91_clk_register_audio_pll_pad()`, and `at91_clk_register_audio_pll_pmc()`. Internal structs track `fracr`/`nd`, PAD `qdaudio`/`div`, and PMC `qdpmc`. Ops implement enable/disable, recalc, determine, and set-rate.

Control flow: FRAC enable resets the PLL, writes fractional register `AUDIO_PLL1`, then enables PLL and ND in `AUDIO_PLL0`. PAD/PMC enables write their divider fields and enable output bits. Determine-rate for FRAC clamps to 620-700 MHz and computes `nd`/`fracr`; PAD searches qd/div combinations and asks the parent PLL to round; PMC searches qd divisors against parent-rounded rates.

State and persistence: selected rate parameters are held in allocated clock structs until enable programs registers. This file does not implement save/restore ops; suspend correctness depends on normal clock framework re-enablement or parent PMC backup handling.

Dependencies and integration: used by SAMA5D2 SoC setup and legacy DT compat code. It depends on `AT91_PMC_AUDIO_PLL*` masks and common-clock parent rate propagation (`CLK_SET_RATE_PARENT` for PAD/PMC).

Risks: PAD set-rate does not independently verify exact divisibility or qd bounds after determine-rate; zero rate is rejected except PMC determine returns success for zero. Test signals include exact audio sample-clock derivation, parent rate lock behavior when multiple audio consumers share FRAC, and register dumps around enable/disable.
