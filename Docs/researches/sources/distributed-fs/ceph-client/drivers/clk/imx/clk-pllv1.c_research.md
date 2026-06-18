# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv1.c

## Purpose
Implements recalc-rate support for first-generation i.MX PLLs found on i.MX1/21/25/27/31/35.

## Important APIs, Types, And Functions
`struct clk_pllv1` stores base address and `enum imx_pllv1_type`. Helpers identify SoC variants and signed MFN behavior. `clk_pllv1_recalc_rate()` decodes MFI/MFN/MFD/PD fields and computes the PLL output. `imx_clk_hw_pllv1()` registers the clock.

## Control Flow
The only clock operation is recalc. It reads the PLL register, extracts fields, enforces minimum MFI of 5, handles SoC-specific MFN signedness, computes `2 * parent / (pd + 1) * (mfi +/- mfn/(mfd+1))`, and returns the result.

## State And Persistence Behavior
All PLL configuration lives in the hardware register. The driver does not support set-rate, prepare, or suspend state.

## Dependencies And Integration Points
Used by legacy i.MX clock drivers through `clk.h`. Depends on common clock framework and MMIO access.

## Risks
Variant-specific MFN interpretation is the main risk; i.MX1/i.MX21 differ from i.MX27 and later. This driver cannot change PLL settings, so platform code must not expect rate control.

## Test Signals
Compare recalc rates against bootloader-programmed PLL registers on legacy i.MX SoCs and validate signed MFN cases for i.MX27-like hardware.
