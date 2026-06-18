# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-pll.h

Purpose: this header defines the OWL PLL descriptor, table model, and instantiation macros.

Important types/macros: `struct clk_pll_table` maps register values to fixed rates and is sentinel-terminated by `rate == 0`. `struct owl_pll_hw` stores register, base frequency, enable bit, multiplier shift/width, min/max multiplier, delay, and optional table. `OWL_PLL`, `OWL_PLL_NO_PARENT`, and `OWL_PLL_NO_PARENT_DELAY` create PLL clocks with named parent, no parent, or custom lock delay. `mul_mask()` derives the field mask from width.

Control flow/state: runtime PLL state is in hardware bits; the static descriptor supplies constraints. A width of zero means fixed-frequency behavior.

Dependencies and integration: SoC files use these macros for core, dev, DDR, NAND, display, audio, Ethernet, assist, CVBS, and EDP PLLs. `owl-pll.c` provides `owl_pll_ops`.

Risks and tests: invalid width can break `mul_mask()`. Table-backed PLLs need sorted rates for closest-rate behavior. No-parent PLLs assume firmware or external naming is enough for the clock tree. Test signals are rate constraints, lock delays, and parented EDP PLL registration on S900.
