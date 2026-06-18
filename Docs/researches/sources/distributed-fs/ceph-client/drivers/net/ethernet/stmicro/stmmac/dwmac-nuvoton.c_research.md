<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-nuvoton.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-nuvoton.c

## Purpose
`dwmac-nuvoton.c` is the Nuvoton MA35D1 DWMAC glue layer. It programs a syscon MISCR register for MAC0 or MAC1 to select RGMII/RMII mode and optional internal TX/RX delays.

## Important APIs, Types, and Functions
- `struct nvt_priv_data` stores device, syscon regmap, and MAC id.
- `nvt_gmac_get_delay()` reads delay properties in picoseconds and converts 0..2000 ps into a 4-bit register code.
- `nvt_set_phy_intf_sel()` writes RGMII delay fields or the RMII enable bit based on stmmac's PHY selector.
- `nvt_gmac_probe()` parses stmmac resources, resolves `nuvoton,sys` phandle arguments, validates MAC id, installs `set_phy_intf_sel`, and probes stmmac.

## Control Flow
Probe gets platform resources and stmmac DT data, allocates private state, looks up a syscon phandle with one argument for the MAC id, rejects ids above 1, stores the private state in `bsp_priv`, and calls `stmmac_pltfr_probe()`. The interface callback later programs `NVT_REG_SYS_GMAC0MISCR` or `NVT_REG_SYS_GMAC1MISCR`.

## State and Persistence
The driver persists mode and delay state only in Nuvoton syscon registers. Private data is devm-allocated per device. It has no runtime worker state or storage.

## Dependencies and Integration Points
It depends on syscon/regmap phandle arguments, stmmac platform probing, OF delay properties, and generic PHY interface selectors. Compatible string: `nuvoton,ma35d1-dwmac`.

## Risks and Edge Cases
- Delay inputs above 2000 ps are rejected; other values are rounded down by integer division except exactly 2000 ps mapping to 15.
- Only RGMII and RMII selector values are valid.
- Incorrect `nuvoton,sys` MAC id writes the wrong MISCR register.

## Test Signals
Validate MAC0 and MAC1 DT instances, RGMII delay codes for 0, intermediate, and 2000 ps, RMII mode bit setting, invalid delay rejection, invalid MAC id rejection, and successful traffic in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-nuvoton.c -->
