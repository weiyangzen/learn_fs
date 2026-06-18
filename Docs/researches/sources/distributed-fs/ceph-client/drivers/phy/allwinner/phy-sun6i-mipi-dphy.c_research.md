# sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun6i-mipi-dphy.c

Purpose: Allwinner MIPI D-PHY driver for A31-style and A100-style PHY blocks. It supports TX mode for display and RX mode only on variants that mark RX support.

Important APIs, types, and functions: `struct sun6i_dphy_variant` supplies variant analog TX power-on callback and RX capability. `struct sun6i_dphy` stores reset, module clock, regmap, generic PHY, MIPI D-PHY configuration, variant, and direction. PHY ops include `configure`, `power_on`, `power_off`, `init`, and `exit`. Timing validation uses `phy_mipi_dphy_config_validate`.

Control flow: probe maps MMIO through `devm_regmap_init_mmio_clk`, gets shared reset and `mod` clock, creates a PHY, defaults direction to TX, optionally switches to RX if DT property `allwinner,direction = "rx"` and variant supports it, then registers a simple provider. Init deasserts reset, enables the module clock, and exclusively sets it to 150 MHz. Configure validates and copies MIPI timing options. TX power-on programs digital timing registers, then calls variant-specific analog setup: A31 hardcodes analog lane masks, A100 computes PLL divider/N from `hs_clk_rate` and enables combo PHY bits. RX power-on programs BSP-derived receive timing from module clock and symbol rate, enables forced RX lanes, and enables global control. Power-off clears global and analog registers; exit releases exclusive clock rate, disables clock, and asserts reset.

State and persistence: runtime state is copied `phy_configure_opts_mipi_dphy`, selected direction, register state, reset and clock state. No disk persistence.

Dependencies and integration: generic PHY, generic MIPI D-PHY helpers, regmap MMIO, clock/reset, DT compatibles `allwinner,sun6i-a31-mipi-dphy` and `allwinner,sun50i-a100-mipi-dphy`, and display/camera consumers.

Risks: many timing and analog values are hardcoded or BSP-derived; invalid `hs_clk_rate` can cause divide behavior problems. A100 RX is unsupported by variant data. Exclusive clock rate must be released on exit. Test signals include DSI panel bring-up, RX rejection on unsupported variant, configure validation failures, power cycle register cleanup, and scope/link validation across lane counts and symbol rates.
