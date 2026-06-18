<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sunxi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sunxi.c

## Purpose
Legacy Allwinner sun7i A20 GMAC glue for the standard DWMAC GMAC core. It mainly programs the external TX clock and optional PHY regulator around generic STMMAC platform probing.

## Important APIs, Types, And Functions
`struct sunxi_priv_data` stores the PHY interface, TX clock enable state, TX clock handle, and optional regulator. `sun7i_gmac_init` and `sun7i_gmac_exit` are platform callbacks. `sun7i_set_clk_tx_rate` is the STMMAC speed-change callback for GMII. `sun7i_gmac_probe` wires these into `plat_stmmacenet_data`.

## Control Flow
Probe obtains STMMAC resources and DT platform config, allocates private data, gets `allwinner_gmac_tx`, handles optional `phy` regulator, sets DWMAC GMAC core type and FIFO sizes, and delegates to `devm_stmmac_pltfr_probe`. Init enables the regulator, sets clock rate to 125 MHz for RGMII/GMII or 25 MHz for MII, and prepares/enables as required. Speed changes in GMII disable/unprepare before selecting 125 MHz for 1000 Mbps or 25 MHz otherwise.

## State And Persistence
The only persistent state is the device lifetime clock/regulator state and `clk_enabled` guard. No hardware state survives beyond registers programmed by the clock framework and STMMAC core.

## Dependencies And Integration Points
Integrates with STMMAC platform callbacks, CCF clocks, regulator framework, OF match `allwinner,sun7i-a20-gmac`, and generic DWMAC GMAC support via `DWMAC_CORE_GMAC`.

## Risks
Clock prepare/enable bookkeeping is manual; mismatched `clk_enabled` paths can leak an enabled clock or unprepare incorrectly. `clk_set_rate` return values are ignored. Missing regulator is allowed except `-EPROBE_DEFER`, so board power descriptions must be correct.

## Test Signals
Probe with and without PHY regulator, link speed transitions in GMII, RGMII init rate, MII prepare-only behavior, module remove/devm cleanup, and clock rate checks are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sunxi.c -->
