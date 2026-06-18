# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-pci.c

## Purpose
`xgbe-pci.c` is the PCI bus binding for newer AMD XGBE devices. It maps PCI BARs, configures XPCS indirect addressing, reads port property registers, assigns MAC address/clock/DMA settings, configures MSI/MSI-X or single IRQs, registers the netdev, and handles PCI suspend/resume.

## Important APIs, Types, And Functions
- `xgbe_config_multi_msi` and `xgbe_config_irqs` allocate IRQ vectors and assign device, ECC, I2C, AN, and channel IRQs.
- `xgbe_pci_probe` performs the full PCI discovery and netdev enable path.
- `xgbe_pci_remove` deconfigures the netdev, frees IRQ vectors, disables hardware interrupts, and frees private data.
- `xgbe_pci_synchronize_irqs` drains IRQ handlers before suspend.
- `xgbe_pci_suspend` and `xgbe_pci_resume` handle power state transitions and PHY low-power mode.
- Version data instances `xgbe_v2a`, `xgbe_v2b`, and `xgbe_v3` select PHY v2 callbacks, XPCS access style, FIFO limits, timestamp behavior, ECC/I2C support, and workarounds.
- `xgbe_pci_init`/`xgbe_pci_exit` register and unregister the `pci_driver`.

## Control Flow
Probe allocates `pdata`, stores version data from the PCI ID table, enables the device, maps BARs, sets XGMAC/XPCS/property/I2C register pointers, determines XPCS window registers from the root AMD device ID, reads XPCS window definitions via SMN for v3 or MMIO for v2, enables PCI bus mastering and device interrupts, reads a valid MAC address, sets fixed PCI clock rates and DMA coherency values, reads port properties, computes counts and FIFO limits, configures IRQs, and calls `xgbe_config_netdev`. Suspend powers down the running netdev, disables interrupts, synchronizes IRQs, puts PCS in low power, disables bus mastering, saves config, and enters D3hot. Resume restores D0/config, re-enables the device and interrupts, clears low-power mode, powers up, and schedules restart if needed.

## State And Persistence
PCI probe populates runtime fields in `pdata`: BAR pointers, `pcidev`, property registers, XPCS window metadata, IRQ numbers/counts, clocks, DMA coherency settings, FIFO/channel limits, MAC address, and version-data workarounds. Suspend stores `lpm_ctrl`. PCI configuration state is saved/restored through the kernel PCI APIs.

## Dependencies And Integration Points
This file depends on Linux PCI APIs, SMN access from `xgbe-smn.h`, XPCS/window register macros, root AMD device IDs, and common netdev setup in `xgbe-main.c`. It uses PHY v2 implementation through version data. It also depends on power-management callbacks and the driver-wide `xgbe_powerdown`/`xgbe_powerup` paths.

## Risks
XPCS indirect window setup varies by platform and can fail if SMN access is unavailable on v3 hardware. The code mutates version-data workaround flags based on root device ID; because version data objects are static, this can affect later devices using the same object. IRQ allocation falls back from multi-vector to single-vector, changing ISR execution mode and channel capacity. Suspend must avoid IRQ handlers touching disabled hardware, hence explicit synchronization.

## Test Signals
Probe on all listed PCI IDs, MSI-X/MSI/single-IRQ fallback, valid/invalid MAC handling, SMN read failures, suspend/resume under traffic, and link restart after resume should be tested. Logs around XPCS window values, property registers, IRQ assignment, and "net device enabled" are key signals.
