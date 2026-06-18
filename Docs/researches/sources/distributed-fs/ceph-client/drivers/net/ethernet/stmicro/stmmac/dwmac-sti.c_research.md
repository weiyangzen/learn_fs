<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sti.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sti.c

## Purpose
`dwmac-sti.c` is the STMicroelectronics STiH407/STiH410 stmmac glue layer. It programs syscfg PHY interface bits, enables the GMAC glue block, selects MII enable polarity, and retimes TX clocks based on PHY mode, link speed, and clock-source DT properties.

## Important APIs, Types, and Functions
- `struct sti_dwmac` stores interface mode, external PHY clock flag, retime source, PHY clock, syscfg register offset, regmap, enable flag, current speed, and retime callback.
- `stih4xx_fix_retime_src()` chooses TXCLK, CLK_125, PHYCLK, or clock generator and may set `sti-ethclk` rate.
- `sti_set_phy_intf_sel()` writes GMAC enable, PHY selector, ENMII, and then retime source.
- `sti_dwmac_parse_data()` reads `st,syscon`, `st,gmac_en`, `st,ext-phyclk`, `st,tx-retime-src`, optional `sti-clkconf`, and `sti-ethclk`.
- `sti_dwmac_init/exit()` prepare and disable the PHY clock.
- `sti_dwmac_probe()` installs stmmac callbacks and probes.

## Control Flow
Probe selects match data, obtains stmmac resources and DT config, allocates private state, parses syscfg and clock settings, assigns the retime callback, installs `set_phy_intf_sel`, `fix_mac_speed`, init, and exit callbacks, then calls `devm_stmmac_pltfr_probe()`. Interface selection and link-speed changes both feed retime source programming.

## State and Persistence
Driver state is per-device. Hardware state is stored in syscfg control bits and the optional PHY clock rate/enable count. The private `speed` default is used for initial retiming before real link speed updates.

## Dependencies and Integration Points
It depends on syscon/regmap, clk APIs, stmmac platform probing, OF properties, and generic PHY selectors. Compatible string: `st,stih407-dwmac`.

## Risks and Edge Cases
- Unsupported selector values are silently coerced to GMII/MII in `sti_set_phy_intf_sel()`.
- Missing `sti-ethclk` only warns; clock-generator retiming may later call `clk_set_rate()` on NULL.
- Retiming choices are tightly coupled to board clock topology and `st,tx-retime-src`.
- The optional `sti-clkconf` resource is parsed but not otherwise used in this file.

## Test Signals
Test MII, GMII/RGMII, and RMII modes with external and internal clock sources; verify 10/100/1000 retime source transitions; inspect syscfg bits; exercise missing optional clock behavior; and run suspend/resume to confirm init/exit clock balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sti.c -->
