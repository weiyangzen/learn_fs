# sources/distributed-fs/ceph-client/drivers/phy/cadence/cdns-dphy.c

Purpose: Implements the Cadence MIPI D-PHY transmitter driver. It computes PLL dividers from requested MIPI D-PHY options, configures PSM and PLL registers for reference or TI J721E integrations, selects the TX band, starts the TX state machine, and exposes a generic PHY provider.

Important APIs and types: `struct cdns_dphy_cfg` caches PLL input/output/fb dividers, actual HS clock, and lane count. `struct cdns_dphy_ops` abstracts integration-specific hooks for probe/remove, PSM divider, clock-lane routing, PLL programming, wakeup time, PLL lock, and common-ready polling. `ref_dphy_ops` uses the reference register layout; `j721e_dphy_ops` programs TI WIZ registers. PHY callbacks are `cdns_dphy_configure()`, `cdns_dphy_validate()`, `cdns_dphy_power_on()`, and `cdns_dphy_power_off()`.

Control flow: Probe selects ops by compatible, maps MMIO, obtains `psm` and `pll_ref` clocks, runs optional integration probe, creates the PHY, and registers the OF provider. Validate/configure require MIPI D-PHY mode, run generic option validation, derive PLL divisors from the reference clock and requested HS bit clock, update the requested `hs_clk_rate` to the achievable rate, and set `wakeup` in microseconds. Power-on requires a configured and not already powered PHY, enables clocks, derives a roughly 1 MHz PSM divider, selects the left clock lane to drive left lanes, writes PLL configuration, maps actual HS rate to a TX band, writes band config, enables TX state machine bits, then waits for optional PLL lock and common-ready hooks. Power-off disables clocks, clears state-machine enable, and clears `is_powered`.

State and persistence: `is_configured` and `is_powered` enforce call ordering. `cfg` persists the last accepted configuration. Hardware PLL, PSM, band, PWM, WIZ, and state-machine registers persist until power-off, reset, or reconfiguration.

Dependencies and integration points: Uses common clock APIs, OF platform probing, reset headers, generic PHY, MIPI D-PHY helpers, and Linux polling helpers. Binds `cdns,dphy` and `ti,j721e-dphy`. Display or DSI consumers drive it through standard PHY configure/power calls.

Risks: `clk_prepare_enable()` return values are not checked individually before later setup. Error handling after clocks are enabled unwinds both clocks but does not clear partially written registers. PLL math rejects reference clocks outside 9.6 MHz to below 150 MHz and HS rates outside 80 Mbps to 2.5 Gbps; consumers must handle exact-rate adjustment. The generic clock-lane hook is optional and unimplemented for current ops, so integrations that need lane routing must add it.

Test signals: MIPI DSI/display bring-up, validation of invalid rates and modes, actual `hs_clk_rate` negotiation, PLL lock/common-ready timeout handling on J721E, repeated configure/power cycles, and build tests for both compatibles.
