# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_pll_8960.c

## Purpose
Registers and programs the MSM8960 HDMI PLL as a common-clock provider using a fixed table of supported pixel-clock configurations.

## Important APIs, types, and functions
- `struct hdmi_pll_8960` stores platform device, `clk_hw`, MMIO base, and current pixel clock.
- `struct pll_rate` and `freqtbl[]` map target pixel clocks to ordered register writes.
- `find_rate()` chooses the closest table entry at or above the requested rate according to descending table order.
- `hdmi_pll_enable()`, `disable()`, `determine_rate()`, `set_rate()`, and `recalc_rate()` implement `clk_ops`.
- `msm_hdmi_pll_8960_init()` maps the PLL, sanity-checks table order, registers `hdmi_pll`, and adds the OF clock provider.

## Control flow
`set_rate()` finds a table row and writes all configured PLL registers, then stores the requested rate in `pixclk`. `determine_rate()` snaps requests to a table-supported rate. Enable asserts/deasserts PLL software reset, toggles PHY reset/power bits, powers the PLL, then polls the lock bit with retries and software-reset attempts. Disable clears PHY global power and PLL power bits.

## State and persistence
Software state is the stored `pixclk`. Hardware state is the PLL register table and power/lock bits. The clock provider remains registered for the device lifetime.

## Dependencies and integration points
Depends on common clock framework, OF provider helpers, MSM8960 HDMI PHY register access via `pll_get_phy()`, and `msm_ioremap()`. Used by HDMI modeset through clock APIs.

## Risks
Only table-supported rates are accurate; `pixclk` stores the requested rate rather than the snapped table rate. `hdmi_pll_enable()` returns success even if lock polling never observes lock. Table order validation only checks descending rates at init.

## Test signals
Validate `determine_rate()` snapping, PLL lock bit behavior, 25.2/27/74.176/74.25/148.5 MHz modes, clock provider registration, and behavior after failed lock retries.
