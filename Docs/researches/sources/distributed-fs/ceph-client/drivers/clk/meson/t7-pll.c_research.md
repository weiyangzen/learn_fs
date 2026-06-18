# sources/distributed-fs/ceph-client/drivers/clk/meson/t7-pll.c

Purpose: This file registers Amlogic T7 PLL blocks. Unlike S4's single PLL controller node, it provides separate compatible entries for GP0, GP1, HIFI, PCIe, MPLL, HDMI, and MCLK PLL register regions.

Important APIs, types, and functions: It defines PLL DCO/divider chains for `t7_gp0_pll`, `t7_gp1_pll`, `t7_hifi_pll`, `t7_pcie_pll`, `t7_mpll0-3`, `t7_hdmi_pll`, and `t7_mclk_*`. It uses `meson_clk_pll_ops`, `meson_clk_pcie_pll_ops`, `meson_clk_mpll_ops`, regmap divider/gate ops, fixed-factor ops, `struct reg_sequence` init arrays, and multiple `struct meson_clkc_data` instances selected by OF match data.

Control flow: Platform probe is handled by `meson_clkc_mmio_probe`. The selected compatible determines which `hw_clks` array and init registers are registered for that MMIO region. GP/HIFI/HDMI/MCLK PLLs use standard Meson PLL ops with multiplier ranges and optional fractional or lock-detect fields. PCIe uses a strict init sequence with delays and the PCIe-specific PLL ops before exposing fixed/divided 100 MHz style outputs.

State and persistence behavior: Clock state is held in hardware PLL control/status registers and CCF registrations. MPLL has a controller init register. MCLK has muxes that can select the local MCLK PLL or firmware-provided `in1`/`in2`, then divides and gates two MCLK outputs.

Dependencies and integration points: It depends on Meson PLL/MPLL/regmap helpers, `meson-clkc-utils`, and dt-binding IDs from `amlogic,t7-pll-clkc.h`. Parent firmware names are `in0`, `in1`, and `in2`; consumers are T7 peripheral clocks and device-tree clock references.

Risks and edge cases: The T7 file is especially sensitive to per-compatible array sizing and ID offsets because each node exports only a subset of binding IDs. PLL lock/status register selection differs across PLL families. PCIe requires exact sequencing and delays for a precise reference clock. Test signals include probing each compatible node, checking expected PLL rates and locks, PCIe link bring-up, HDMI/display clocks, audio MPLL rates, and dt-binding index checks for sparse per-node providers.
