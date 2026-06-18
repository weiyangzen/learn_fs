## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll_regs.h

### Purpose

`vlv_dsi_pll_regs.h` defines BXT/GLK DSI PLL, TX escape clock, and MIPI clock-divider MMIO registers used by `vlv_dsi_pll.c`.

### Important APIs, types, and functions

The header exports MMIO macros for `MIPIO_TXESC_CLK_DIV1`, `MIPIO_TXESC_CLK_DIV2`, `BXT_MIPI_CLOCK_CTL`, `BXT_DSI_PLL_CTL`, and `BXT_DSI_PLL_ENABLE`. Field macros cover TX ESCLK dividers, RX upper/lower dividers, 8x-by-3 dividers, PLL ratio/PVD/DSIA/DSIC output selection, ratio bounds (`BXT_DSI_PLL_RATIO_MIN/MAX`, `GLK_DSI_PLL_RATIO_MIN/MAX`), `BXT_REF_CLOCK_KHZ`, enable, and lock bits.

### Control flow

There is no runtime flow. `bxt_dsi_pll_enable()` writes `BXT_DSI_PLL_CTL`, programs dividers from `BXT_MIPI_CLOCK_CTL` or GLK TXESC registers, then sets `BXT_DSI_PLL_DO_ENABLE` and polls `BXT_DSI_PLL_LOCKED`.

### State and persistence behavior

The constants describe persistent PLL and escape-clock hardware state. Divider fields remain programmed until reset or explicit cleanup by `bxt_dsi_reset_clocks()` and PLL disable paths.

### Dependencies

It includes `vlv_dsi_regs.h` for `_MIPI_PORT()` and MMIO helper definitions. Consumers depend on `intel_de_read/write/rmw()` for register access.

### Integration points

Main consumers are `vlv_dsi_pll.c`, GVT MMIO tables, and GVT handlers. This makes the header part of both physical display programming and virtualized register exposure.

### Risks

Incorrect shift/mask definitions can cause invalid dividers and possible DSI register access hangs on BXT/GLK. DSIA/DSIC fields differ by port and by platform because GLK does not have the same DSIC clock behavior as BXT.

### Test signals

Compile coverage of display and GVT, PLL lock tests, register readback during DSI modeset, and validation that clock dividers are cleared during post-disable.
