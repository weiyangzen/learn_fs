# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-platform.c

## Purpose
`xgbe-platform.c` is the platform/ACPI/Device Tree binding for first-generation AMD XGBE devices. It obtains MMIO resources, clocks/properties, PHY resources, MAC address, interrupts, DMA coherency settings, and v1 version data before delegating to common netdev setup.

## Important APIs, Types, And Functions
- `xgbe_acpi_support` reads ACPI DMA and PTP clock frequencies.
- `xgbe_of_support` obtains `dma_clk` and `ptp_clk` through the clock framework.
- `xgbe_of_get_phy_pdev` and `xgbe_get_phy_pdev` support old split XGBE/PHY DT layouts and newer grouped layouts.
- `xgbe_resource_count` counts platform resources of a given type.
- `xgbe_platform_probe` performs platform discovery and netdev enablement.
- `xgbe_platform_remove` tears down the netdev and releases the PHY platform device.
- PM callbacks put PCS into low-power mode and call `xgbe_powerdown`/`xgbe_powerup`.
- `xgbe_v1` selects PHY v1 callbacks, XPCS access v1, FIFO limits, and TX timestamp workaround.
- `xgbe_platform_init`/`xgbe_platform_exit` register and unregister the platform driver.

## Control Flow
Probe allocates `pdata`, determines ACPI versus OF, gets version data, finds the PHY platform device, decides resource indexes for old/new layouts, maps XGMAC, XPCS, RxTx, SIR0, and SIR1 MMIO resources, reads MAC address and verifies `phy-mode` is `xgmii`, detects per-channel IRQ property, obtains clock rates, sets DMA coherency register values, applies FIFO limits, calculates counts, fetches device/channel/AN IRQs, and calls `xgbe_config_netdev`. Suspend/resume power down/up the netdev if running and toggle PCS low-power mode.

## State And Persistence
Probe populates `pdata->platdev`, `adev`, `phy_platdev`, `phy_dev`, MMIO pointers, `phy_mode`, IRQ numbers, clock handles/rates, DMA coherency fields, FIFO limits, per-channel IRQ mode, and `vdata`. This state lasts for the platform device lifetime. PM stores/restores low-power control through `pdata->lpm_ctrl`.

## Dependencies And Integration Points
This file depends on ACPI, OF, platform resource APIs, clock framework, device properties, DMA attribute APIs, and common netdev setup in `xgbe-main.c`. It selects `xgbe-phy-v1.c` as the implementation backend.

## Risks
Resource index calculations differ for old split and new grouped DT layouts; incorrect firmware descriptions can map the wrong PHY resources. Per-channel IRQ setup sets `channel_irq_count` to the array maximum after the loop, even if fewer IRQs were discovered before `dma_irqend`; downstream limits depend on accurate counts. The platform PM path does not perform the PCI file's explicit IRQ synchronization before low-power writes. `phy-mode` is strict and rejects anything other than `xgmii`.

## Test Signals
Test ACPI and OF boot paths, old and new DT PHY resource layouts, missing clock/property failures, MAC address validation, per-channel IRQ resources, probe/remove unwind, and suspend/resume with link up. Verify supported modes and SerDes resources through v1 PHY behavior.
