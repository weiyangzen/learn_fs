# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-pll.c

## Purpose
This file is the SG2042 PLL driver. It registers MPLL, FPLL, DPLL0, and DPLL1 clocks from SYS_CTRL registers and implements rate calculation/programming for writable PLLs.

## Important APIs, Types, And Functions
`struct sg2042_pll_clock` describes a PLL `clk_hw`, binding ID, register base, lock, control offset, status lock/updating bits, and enable bit. `struct sg2042_pll_ctrl` holds decoded frequency parameters: `fbdiv`, `postdiv1`, `postdiv2`, and `refdiv`.

Core helpers include `sg2042_pll_ctrl_encode()`, `sg2042_pll_ctrl_decode()`, `sg2042_pll_enable()`, `sg2042_pll_recalc_rate()`, `sg2042_pll_get_postdiv_1_2()`, `sg2042_get_pll_ctl_setting()`, and CCF callbacks `sg2042_clk_pll_recalc_rate()`, `sg2042_clk_pll_determine_rate()`, and `sg2042_clk_pll_set_rate()`.

## Control Flow
Probe allocates onecell data sized to the PLL table, maps the SYS_CTRL PLL resource, initializes each PLL's base and shared lock, registers the `clk_hw`, stores it by ID, and adds the OF provider. The PLL programming path disables the PLL, searches valid control settings for the target rate, writes the encoded control register, re-enables the PLL, and waits for lock/updating bits in the enable helper.

Rate search requires a 25 MHz parent and target output between 16 MHz and 3.2 GHz. It iterates REFDIV and FBDIV ranges while enforcing FREF/REFDIV and VCO constraints, then derives postdiv1/postdiv2 from a small product table.

## State And Persistence
The PLL driver stores static PLL descriptors and runtime base/lock pointers. Hardware state persists in SYS_CTRL PLL status, enable, and control registers. FPLL and DPLLs are registered read-only; MPLL is writable.

## Dependencies And Integration Points
It depends on dt-binding IDs from `sophgo,sg2042-pll.h`, the shared SG2042 data structure, CCF, MMIO, polling, and 64-bit division helpers. Downstream SG2042 clock-generator nodes consume firmware-named PLL outputs.

## Risks
`sg2042_get_pll_ctl_setting()` requires `parent_rate == 25 MHz`; alternate oscillator descriptions fail. The post-divider search rounds by selecting the first product not less than the computed value, so rate accuracy depends on the table. Set-rate always re-enables the PLL even after search failure, but returns the error. Poll timeouts warn but do not abort enabling.

## Test Signals
Validate MPLL set-rate across the supported range, read-only behavior for FPLL/DPLLs, and measured output rates. Confirm parent rate from Device Tree is exactly 25 MHz or gracefully rejected. Boot tests should verify SG2042 CLKGEN can resolve `mpll`, `fpll`, `dpll0`, and `dpll1`.
