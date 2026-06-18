<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun8i.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun8i.c

## Purpose
Allwinner sun8i/sun50i glue for a non-standard EMAC block that is integrated with the STMMAC core but has its own register layout and DMA/MAC operation tables. It supports multiple SoC variants, syscon/CCU clock selection, internal PHY muxing, and platform-specific delays.

## Important APIs, Types, And Functions
`struct emac_variant` records syscon field, supported PHY interfaces, internal PHY presence, and delay limits. `struct sunxi_priv_data` persists clocks, regulator, reset, regmap field, PHY state, and MDIO mux handle. `sun8i_dwmac_dma_ops` and `sun8i_dwmac_ops` are the integration contracts passed through `sun8i_dwmac_setup`. Key functions include `sun8i_dwmac_probe`, `sun8i_dwmac_set_syscon`, `sun8i_dwmac_reset`, `sun8i_dwmac_power_internal_phy`, `mdio_mux_syscon_switch_fn`, and custom DMA interrupt/start/stop/init handlers.

## Control Flow
Probe gets platform resources, allocates variant private data, resolves optional PHY regulator, locates the syscon regmap, parses STMMAC DT config, installs custom ops/capabilities, programs syscon interface/delays, calls `stmmac_pltfr_probe`, resumes the runtime-suspended MAC for reset/mux work, and either registers the MDIO mux/internal PHY path or performs a plain reset. Runtime init enables the regulator and powers the internal PHY if selected. Exit/remove unwind mux, clock, reset, regulator, STMMAC platform state, and syscon bits.

## State And Persistence
Persistent state is all kernel-managed device state: syscon register fields, EMAC register bits, regulator enable count, internal PHY clock/reset state, `internal_phy_powered`, `use_internal_phy`, and mux handle. No disk persistence exists. The syscon value carries PHY mode, clock delays, EPHY address, LED polarity, and internal/external PHY selection.

## Dependencies And Integration Points
Depends on STMMAC core/platform APIs, Linux regmap/syscon, MDIO mux, runtime PM, reset, regulator, OF/MDIO parsing, and netdev multicast/unicast list handling. It deliberately bypasses generic DWMAC1000/4 ops and supplies Allwinner-specific DMA/MAC callbacks.

## Risks
Syscon writes are sensitive to DT properties and SoC variant limits; invalid delay units or unsupported PHY modes fail probe. Internal PHY muxing requires correct `mdio-mux` child nodes, reset, and clock handles. Interrupt status maps RX timeout to `tx_hard_error`, which deserves care in debugging. Reset timing was expanded to 100 ms for boards with no cable, so regressions may be board-specific.

## Test Signals
Probe/remove on each compatible, link at MII/RMII/RGMII speeds, MDIO mux switching, internal/external PHY selection, regulator and reset unwind on failures, ethtool register dumps, multicast/unicast filter programming, RX/TX IRQ counters, checksum enable, flow control, and suspend/runtime-PM interactions are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun8i.c -->
