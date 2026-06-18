# sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-ast2700.c

Purpose: this module implements AST2700 clock providers for two SCU blocks, `aspeed,ast2700-scu0` and `aspeed,ast2700-scu1`. It is descriptor-driven and also creates an auxiliary reset device for each SCU.

Important types/functions: `enum ast2700_clk_type` selects registration behavior. `struct ast2700_clk_info` describes fixed, fixed-factor, display-fixed, PLL, HPLL, UART PLL, mux, divider, gate, and misc clocks. Static descriptor arrays `ast2700_scu0_clk_info` and `ast2700_scu1_clk_info` define the whole clock tree. Register helpers calculate display clocks, HPLL strap-selected rates, PLL fixed factors, UART PLL factors, MPHY/U2PHY misc divisors, and clear-to-enable gates. `ast2700_soc_clk_probe()` maps registers, allocates onecell data, optionally configures SCU1 I3C clock, iterates descriptors in dependency order, registers each clock, adds the OF provider, and creates `reset0` or `reset1` auxiliary devices.

Control flow/state: all clocks are device-managed except the small custom gate allocation path, which frees on registration failure. Parent hardware arrays are filled during probe from previously registered IDs. Hardware state is in SCU clock selection, PLL, stop, and display parameter registers.

Risks and tests: descriptor order is critical because parent IDs must already be registered. Several calculations use integer division before fixed-factor registration, so non-integral PLL ratios may be truncated. `devm_kasprintf()` result is not checked before auxiliary device creation. Test signals are both SCU nodes probing, UART/I3C/SD/MAC/display clocks, auxiliary reset device binding, and invalid descriptor ID detection.
