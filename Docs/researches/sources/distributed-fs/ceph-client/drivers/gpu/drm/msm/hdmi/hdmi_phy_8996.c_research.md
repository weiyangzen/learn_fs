# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8996.c

## Purpose
Implements the MSM8996 HDMI QSERDES PHY PLL clock provider and PHY configuration data.

## Important APIs, types, and functions
- `struct hdmi_pll_8996` stores platform device, `clk_hw`, QSERDES common MMIO, and four TX lane MMIO bases.
- `struct hdmi_8996_phy_pll_reg_cfg` holds computed PLL, lane, drive, emphasis, mode, and comparator register values.
- `pll_get_post_div()` and `pll_calculate()` derive VCO, dividers, lock comparator, and lane programming from pixel clock and reference clock.
- `hdmi_8996_pll_set_clk_rate()`, `prepare()`, `unprepare()`, `determine_rate()`, `recalc_rate()`, and `is_enabled()` implement `clk_ops`.
- `msm_hdmi_pll_8996_init()` maps common/TX register windows and registers the `hdmipll` provider.

## Control flow
Rate setting computes bit clock as 10x pixel clock, chooses post dividers producing an 8-12 GHz VCO, calculates fractional PLL fields and thresholds, powers the PHY down/up, writes QSERDES common PLL registers, writes all TX lane drive and band settings, sets PHY mode, powers PHY blocks, and uses `wmb()` before PLL enable. `prepare()` toggles PHY config, polls QSERDES C_READY lock, enables TX transceivers, disables SSC, polls PHY ready, and restarts retiming. Rate requests are clamped to 25-600 MHz.

## State and persistence
The PLL object is devm-managed and registered as a clock provider. Hardware state lives in QSERDES common, TX lane, and HDMI PHY registers. Recalc reconstructs a rate from lock comparator registers instead of storing the requested value.

## Dependencies and integration points
Depends on common clock framework, OF clock provider registration, HDMI PHY drvdata from `hdmi_phy.c`, QSERDES register definitions, and `msm_ioremap()`. The HDMI modeset path drives it through the clock framework.

## Risks
PLL math and register values are mode-sensitive; incorrect divider selection can fail lock or produce wrong TMDS clocks. Poll helpers return boolean-like success rather than Linux error codes, so callers treat zero as failure. TX lane arrays assume exactly four channels. Recalc gives an approximate `fdata/10` result based on comparator state.

## Test signals
Check PLL lock/PHY ready debug logs, successful 25-600 MHz clock requests, high/mid/low TMDS modes, HDMI analyzer pixel clock, and mode changes across threshold boundaries.
