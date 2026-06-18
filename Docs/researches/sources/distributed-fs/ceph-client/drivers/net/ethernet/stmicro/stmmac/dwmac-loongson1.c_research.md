<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson1.c

## Purpose
`dwmac-loongson1.c` provides OF platform glue for Loongson-1B GMAC and Loongson-1C EMAC instances. It programs Loongson syscon bits for MAC shutdown release, pin muxing, and PHY interface selection before handing the device to the generic stmmac platform driver.

## Important APIs, Types, and Functions
- `struct ls1x_dwmac` stores stmmac platform data, syscon regmap, and Loongson-1B MAC id.
- `struct ls1x_data` selects SoC-specific `setup` and `init` callbacks from OF match data.
- `ls1b_dwmac_setup()` infers GMAC0/GMAC1 from the MMIO base address.
- `ls1b_dwmac_syscon_init()` programs LS1B syscon bits for RGMII_ID or MII and releases GMAC shutdown.
- `ls1c_dwmac_syscon_init()` maps stmmac PHY interface selectors into the LS1C `PHY_INTF_SELI` field.
- `ls1x_dwmac_probe()` builds platform data and calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe gathers stmmac resources, obtains the `loongson,ls1-syscon` regmap, loads match data, allocates private state, parses stmmac DT configuration, stores `bsp_priv`, and runs optional setup. The stmmac core later invokes the SoC-specific `init` callback to write syscon mode bits and deassert shutdown before normal MAC operation.

## State and Persistence
State is limited to devm private data and syscon register settings. The syscon writes persist until reset or later firmware/kernel changes. The driver has no dynamic runtime state beyond stmmac-owned netdev state.

## Dependencies and Integration Points
It uses syscon/regmap, platform resources, OF match data, stmmac DT parsing, and `stmmac_get_phy_intf_sel()`. Compatible strings are `loongson,ls1b-gmac` and `loongson,ls1c-emac`.

## Risks and Edge Cases
- LS1B id detection is hard-coded to two physical base addresses; unexpected address maps fail probe.
- LS1B supports only `RGMII_ID` and `MII`; LS1C accepts only GMII/MII and RMII selector results.
- GMAC1 shares pins with UART/PWM functions, so syscon mux writes can affect board-level pin use.
- Missing syscon phandle prevents all mode programming.

## Test Signals
Bring-up should verify both LS1B MAC base addresses, LS1C RMII/MII mode selection, syscon shutdown bit clearing, and negative tests for unsupported PHY modes. Network traffic at expected speeds plus scope or register inspection of pin mode bits are useful hardware signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson1.c -->
