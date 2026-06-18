# sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc32xx.c

Purpose: Implements the LPC32xx clock tree, including system clocks, PLLs, bus muxes/dividers, many peripheral gates, composite UART/PWM/SD/LCD clocks, DDRAM clock handling, and a separate USB clock provider.

Important APIs, types, and functions: `clk_proto[]` defines CCF-visible names, parents, and flags. `clk_hw_proto[]` defines fixed, mux, divider, gate, PLL, USB, and composite hardware descriptors. Custom ops include `clk_mask_ops`, PLL ops for `pll_397x`, `hclk_pll`, and `usb_pll`, DDRAM ops, UART divider recalc, USB enable/disable ops, and local mux/divider/gate ops over regmap. `lpc32xx_clk_register()` materializes a descriptor into a CCF clock.

Control flow: `lpc32xx_clk_init()` validates external `xtal_32k` and `xtal`, maps the system control block, creates a regmap, applies divider quirks to avoid zero values for PWM/MS clocks, registers clocks 1 through `LPC32XX_CLK_MAX - 1`, adds the main one-cell provider, sets USB PLL to 48 MHz, enables ARM/HCLK/VFP, and disables default NAND flash clocks. `lpc32xx_usb_clk_init()` maps USB clock registers, registers USB subclocks from offset IDs, and adds the USB provider.

State and persistence: Global `clk_regmap`, `usb_clk_vbase`, `clk[]`, and `usb_clk[]` persist after early init. Hardware registers hold clock state. PLL objects store most recently calculated divider mode parameters for subsequent `set_rate()`.

Dependencies and integration points: Depends on `dt-bindings/clock/lpc32xx-clock.h`, external oscillator DT clocks, regmap MMIO, and CCF one-cell providers for both main and USB clock nodes. USB clocks mix system-control and USB-controller register apertures.

Risks: PLL `set_rate()` depends on `determine_rate()` having populated in-memory `m_div`, `n_div`, `p_div`, and `mode`; direct set-rate without prior negotiation can fail. USB PLL only supports 48 MHz. Several muxes share one control bit but are registered as separate read-only muxes, so parent interpretations must stay synchronized. `lpc32xx_clk_register()` composite paths reuse union members carefully; changes to descriptor layout are high-risk.

Test signals: Boot should validate oscillator rates, register providers without errors, and show ARM/HCLK/VFP enabled. Rate tests should cover HCLK PLL closest-rate search and USB PLL 48 MHz setup. USB device/host enable paths should report `-EBUSY` when the opposite busy bit is set and should restore control state on timeout.
