# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8998.c

## Purpose
Implements the MSM8998 HDMI QSERDES PHY PLL provider and resource configuration, closely related to 8996 but with 8998-specific divider search and register programming.

## Important APIs, types, and functions
- `struct hdmi_pll_8998` stores platform device, `clk_hw`, last requested rate, QSERDES common MMIO, and four TX lane bases.
- `struct hdmi_8998_phy_pll_reg_cfg` contains calculated common PLL and TX lane fields.
- `pll_get_post_div()` selects VCO ratio, TX band, half-rate mode, and HSCLK divider with extra threshold checks.
- `pll_calculate()` derives PLL fractional fields, lock comparator, and drive settings for frequency ranges.
- `hdmi_8998_pll_*` functions implement clock rate, prepare, unprepare, recalc, and enable-state operations.

## Control flow
Rate setting calculates bit clock, selects a valid 8-12 GHz VCO that also satisfies comparator threshold ranges, fills common and TX lane config, powers down/up, writes QSERDES common PLL registers, writes TX interface/buffer/driver/emphasis/pre-driver/res-code registers, sets PHY mode, initializes lane config, flushes writes, and stores the requested rate. Prepare toggles PHY CFG values, polls lock, switches lane config to `0x1f`, polls PHY ready, restarts retiming, and flushes writes.

## State and persistence
The software PLL object stores `rate` because recalc returns the last requested clock instead of decoding hardware. Hardware state persists in 8998 QSERDES and PHY registers while powered. The config advertises regulators `vddio`, `vcca` and clocks `iface`, `ref`, `xo`.

## Dependencies and integration points
Depends on common clock framework, OF clock provider registration, `hdmi_phy.c` drvdata, and 8998 register macros. HDMI modeset uses the registered `hdmipll`.

## Risks
The divider search has more constraints than 8996; unsupported frequencies return `-EINVAL`. Stored-rate recalc can be stale after hardware reset. Poll failures return zero, which is not a conventional negative errno. Frequency threshold-specific drive settings need hardware validation across modes.

## Test signals
Validate PLL lock and PHY ready across low, mid, digital, and high frequency thresholds, HDMI pixel clock accuracy, mode switches after suspend/resume, and clock provider probe with all three clocks.
