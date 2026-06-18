<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-tegra.c

## Purpose
NVIDIA Tegra234 MGBE glue for the XGMAC/STMMAC driver. It manages wrapper register mappings, clock/reset sequencing, IOMMU stream ID programming, XPCS/UPHY SERDES bring-up, and suspend/resume.

## Important APIs, Types, And Functions
`struct tegra_mgbe` persists device, bulk clocks, MAC/PCS resets, IOMMU SID, mapped hypervisor/MAC/XPCS register bases, and MDIO bus pointer. `tegra_mgbe_probe` is the main setup path. `mgbe_uphy_lane_bringup_serdes_up/down` are STMMAC SERDES callbacks. `tegra_mgbe_suspend` and `tegra_mgbe_resume` wrap core suspend/resume with clocks, reset, interrupt, SID, and TX lane handling.

## Control Flow
Probe maps named resources (`hypervisor`, `mac`, `xpcs`), reads the interrupt and IOMMU SID, obtains and enables all clocks, asserts/deasserts MAC and PCS resets, parses STMMAC DT config, sets `DWMAC_CORE_XGMAC`, TSO and PMT flags, ensures MDIO bus data, enables the TX UPHY lane if not powered, waits for hardware clear, installs SERDES callbacks, programs FIFO sizes, enables wrapper interrupts, writes SID, and calls `stmmac_dvr_probe`. SERDES up sequences RX override, IDDQ/sleep/calibration/data/CDR/PCS-ready bits and polls link status; down reverses RX data/sleep/IDDQ.

## State And Persistence
State lives in mapped wrapper registers, clock/reset state, `iommu_sid`, and STMMAC platform data. No disk persistence exists. Resume must reconstruct wrapper interrupt/SID and TX lane state after clock/reset cycling.

## Dependencies And Integration Points
Uses STMMAC direct DVR probe, Tegra IOMMU stream-ID helper, bulk clocks, reset framework, OF clock-name compatibility for `ptp-ref`, and XPCS/UPHY wrapper registers. It signals SERDES should power up after PHY link-up through `STMMAC_FLAG_SERDES_UP_AFTER_PHY_LINKUP`.

## Risks
The clock name table contains `mac` twice, making DT clock order/name correctness critical. Poll timeouts during TX lane or RX calibration/link can fail probe or resume. Error unwinding mostly disables clocks, so partial reset states rely on devm cleanup. Incorrect SID programming can break DMA behind IOMMU.

## Test Signals
Probe on Tegra234 DT, legacy `ptp-ref` clock fallback warning, suspend/resume with link recovery, SERDES up/down cycles, IOMMU SID write validation, XPCS timeout paths, and high-throughput XGMAC/TSO traffic are key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-tegra.c -->
