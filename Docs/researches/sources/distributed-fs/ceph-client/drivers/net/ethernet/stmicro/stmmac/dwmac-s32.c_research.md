<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-s32.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-s32.c

## Purpose
`dwmac-s32.c` is the NXP S32G/R common chassis GMAC glue driver. It sets up TX/RX interface clocks, writes the SoC PHY interface selection register, enables GMAC4 platform features, configures FIFO sizes, and selects multi-IRQ mode when all per-queue IRQs are present.

## Important APIs, Types, and Functions
- `struct s32_priv_data` stores MAC/control MMIO, optional syscon regmap, clock handles, device pointer, and pointer to stmmac PHY mode.
- `s32_gmac_write_phy_intf_select()` writes the PHY select register or syscon offset.
- `s32_gmac_init()` enables TX/RX clocks, sets both to 125 MHz, and writes interface mode.
- `s32_gmac_exit()` disables both clocks.
- `s32_gmac_setup_multi_irq()` validates per-RX/TX queue IRQ arrays and sets `STMMAC_FLAG_MULTI_MSI_EN`.
- `s32_dwmac_probe()` parses resources, clocks, optional `nxp,phy-sel`, stmmac flags, FIFO sizes, and callbacks.

## Control Flow
Probe allocates private state, gathers resources and stmmac DT config, obtains PHY select access via syscon phandle or second MMIO resource, gets TX/RX clocks, configures GMAC4/PMT/SPH-disable platform data, selects multi-IRQ if all queue IRQs are valid, sets large FIFOs, installs init/exit and TX clock callback, and calls `stmmac_pltfr_probe()`. Init performs clock and PHY-select programming before MAC use.

## State and Persistence
State is per-device private data. Hardware state includes clock rates/enables, interface selection register, interrupt routing mode, and stmmac registers. No persistent storage is used.

## Dependencies and Integration Points
It uses clk APIs, syscon/regmap or MMIO resource fallback, stmmac GMAC4 platform helpers, queue IRQ resources, and `stmmac_set_clk_tx_rate()`. Compatible string: `nxp,s32g2-dwmac`.

## Risks and Edge Cases
- `s32_gmac_write_phy_intf_select()` currently always writes RGMII selector despite constants for other modes.
- All TX and RX queue IRQs must be present to enable multi-IRQ; one missing IRQ falls back to MAC IRQ mode.
- Clock enable error unwinding must keep TX/RX enable counts balanced.
- Missing `nxp,phy-sel` requires a valid second MMIO region.

## Test Signals
Tests should cover syscon and MMIO PHY-select access, missing queue IRQ fallback, all-queue multi-IRQ mode, clock set-rate failures, probe deferral for clocks/syscon, and traffic with per-queue interrupts enabled. Register inspection should confirm the 125 MHz clock setup and PHY select value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-s32.c -->
