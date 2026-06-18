<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-armpll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-armpll.c

Purpose: This shared helper implements rate reporting for iProc ARM PLLs and registers them as early OF clock providers for SoC wrapper files.

Important APIs, types, and functions: `iproc_arm_pll` stores `clk_hw`, MMIO base, and cached rate. Internal helpers `__get_fid()`, `__get_mdiv()`, and `__get_ndiv()` decode active frequency policy, post divider, and integer/fractional multiplier from hardware registers. `iproc_arm_pll_recalc_rate()` computes the clock rate. Public setup is `iproc_armpll_setup()`.

Control flow: Setup allocates state, maps the DT register resource, builds a single-parent clock from the DT parent if present, registers the hardware clock, and adds a simple provider. Recalc checks bypass mode, verifies PLL lock, decodes PDIV/NDIV/MDIV according to active frequency ID, and computes `((ndiv * parent_rate) >> 20) / pdiv / mdiv`.

State and persistence behavior: The only software state is the registered clock and last rate. Hardware state includes policy, debug active frequency, PLL control, fractional offset, lock, and divider registers. `BUG_ON()` is used if decoded policy exceeds the maximum, so invalid hardware state can become fatal.

Dependencies and integration points: It depends on SoC wrapper files that call `iproc_armpll_setup()` for specific compatibles, common clock framework APIs, and OF MMIO mapping. It is selected through `COMMON_CLK_IPROC`.

Risks and test signals: Risks include fatal `BUG_ON()` on bad policy, returning 0 if unlocked or invalid divider, handling offset mode correctly, and matching hardware bitfields across SoCs. Tests should check rate reporting under each FID path, bypass mode, locked/unlocked states, and wrapper compatibles for Cygnus, HR2, and BCM63138.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-armpll.c -->
