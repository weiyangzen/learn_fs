<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-lpc18xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-lpc18xx.c

## Purpose
`dwmac-lpc18xx.c` is the NXP LPC18xx/LPC43xx Ethernet glue layer. Its only platform-specific job is to program the CREG syscon Ethernet mode field for MII/GMII or RMII before delegating to stmmac.

## Important APIs, Types, and Functions
- `lpc18xx_set_phy_intf_sel()` validates stmmac's abstract PHY selector and writes `LPC18XX_CREG_CREG6_ETHMODE_MASK`.
- `lpc18xx_dwmac_probe()` parses stmmac DT resources, finds the `nxp,lpc1850-creg` syscon, sets `DWMAC_CORE_GMAC`, and installs `set_phy_intf_sel`.

## Control Flow
Probe gets stmmac resources and DT config, looks up the global CREG syscon by compatible string, stores the regmap as `bsp_priv`, and calls `stmmac_dvr_probe()`. The stmmac core calls back to `lpc18xx_set_phy_intf_sel()` when applying the selected PHY interface.

## State and Persistence
The only driver-owned state is a regmap pointer in `bsp_priv`. Hardware state is a small CREG mode field that survives until SoC reset or later syscon writes.

## Dependencies and Integration Points
The file depends on syscon/regmap, OF platform probing, stmmac platform helpers, and the generic stmmac PHY interface selector. Compatible string: `nxp,lpc1850-dwmac`.

## Risks and Edge Cases
- Syscon lookup is by compatible string, so boards must expose the CREG node correctly.
- Only GMII/MII and RMII selector values are accepted.
- Shared syscon access requires the field mask to stay accurate to avoid corrupting adjacent CREG settings.

## Test Signals
Probe tests should cover valid MII and RMII DT modes, missing CREG syscon, and unsupported interface rejection. Runtime signals are successful link-up in each mode and inspection of CREG6 mode bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-lpc18xx.c -->
