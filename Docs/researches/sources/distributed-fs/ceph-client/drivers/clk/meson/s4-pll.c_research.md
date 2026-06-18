# sources/distributed-fs/ceph-client/drivers/clk/meson/s4-pll.c

Purpose: This file registers the Amlogic S4 PLL clock controller. It exposes fixed PLL derived clocks, GP0 PLL, HIFI PLL, HDMI PLL, a 50 MHz MPLL selector, and MPLL0 through MPLL3 outputs for downstream S4 peripheral clocks.

Important APIs, types, and functions: Important objects are `s4_fixed_pll_dco`, `s4_fixed_pll`, fixed-factor `fclk_div*` clocks, `s4_gp0_pll_dco`, `s4_hifi_pll_dco`, `s4_hdmi_pll_dco`, MPLL divider/gate pairs, `s4_pll_hw_clks[]`, `s4_pll_init_regs[]`, and `s4_pll_clkc_data`. It uses `meson_clk_pll_ops`, `meson_clk_pll_ro_ops`, `meson_clk_mpll_ops`, regmap divider/gate ops, and `meson_clkc_mmio_probe`.

Control flow: On platform probe for `amlogic,s4-pll-clkc`, the generic Meson MMIO probe applies controller-level init registers, registers each clock hardware object, and publishes the OF clock provider. Runtime rate operations are delegated to generic Meson PLL/MPLL and divider/gate implementations. GP0 and HIFI PLLs include init register sequences. Fixed PLL and fclk outputs are read-only because firmware/ROM owns them.

State and persistence behavior: Runtime state is almost entirely hardware register state plus CCF registrations. The file explicitly documents that fixed PLL registers are not writable in the kernel phase and writing them may crash the system, so fixed PLL DCO/dividers/gates use read-only ops and have no runtime persistence outside hardware.

Dependencies and integration points: It depends on Meson PLL/MPLL/regmap helpers, `meson-clkc-utils`, and dt-binding IDs from `amlogic,s4-pll-clkc.h`. Parent input is `xtal`; exported PLL and fclk names are consumed by S4 peripheral clock definitions, especially system, video, audio, storage, GPU, and demod clocks.

Risks and edge cases: PLL programming risks include wrong multiplier ranges, missing init sequences, lock-bit handling, and accidental writes to protected fixed PLL registers. MPLL outputs share a common control block and require correct SDM/N2/enable fields. Test signals include successful boot without PLL write faults, expected fixed PLL and fclk rates in clk summary, GP0/HIFI/HDMI rate changes with lock, MPLL audio-rate tests, and dt-binding index validation for all exported `CLKID_*` entries.
