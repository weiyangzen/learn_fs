# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/pci.c

## Purpose

`pci.c` registers the Wi-Fi 7 ath12k PCI family driver and performs device-specific PCI probe setup for QCN9274, WCN7850, and QCC2072. It selects MSI layout, window-register behavior, PCI ops, board search mode, target memory mode, hardware revision, and then hands control to common Wi-Fi 7 hardware initialization.

## Important APIs, Types, And Data

The PCI ID table matches Qualcomm device IDs `0x1109` (QCN9274), `0x1107` (WCN7850), and `0x1112` (QCC2072). `ath12k_wifi7_msi_config` allocates 16 vectors across MHI (3), CE (5), and DP (8). QCN9274 PCI ops have no wake/release callbacks, while WCN7850/QCC2072 use `ath12k_wifi7_pci_bus_wake_up()` and `ath12k_wifi7_pci_bus_release()` to call `mhi_device_get_sync()` and `mhi_device_put()`.

`ath12k_wifi7_pci_read_hw_version()` reads `TCSR_SOC_HW_VERSION` and extracts major/minor fields. `ath12k_wifi7_pci_probe()` is the main bus-specific setup function. `ath12k_wifi7_pci_init()` and `ath12k_wifi7_pci_exit()` register and unregister the driver for `ATH12K_DEVICE_FAMILY_WIFI7`.

## Control Flow

Registration passes `ath12k_wifi7_pci_driver` to shared PCI registration with arch init/deinit hooks. Probe retrieves `ath12k_base` from `pci_get_drvdata()`, validates PCI private state, switches on device ID, sets bus/hardware fields, optionally reads SoC hardware version through the configured window register, selects `ab->hw_rev`, and calls `ath12k_wifi7_hw_init()`. Unknown device IDs or unsupported hardware major versions return `-EOPNOTSUPP`; missing driver data returns `-EINVAL`.

## State And Persistence Behavior

Probe mutates `ab`, `ab_pci`, and board-identification state. Persistent settings include `ab_pci->msi_config`, `ab_pci->pci_ops`, `ab_pci->window_reg_addr`, `ab->static_window_map`, `ab->target_mem_mode`, `ab->id.bdf_search`, and `ab->hw_rev`. These settings remain active for the lifetime of the PCI device and influence later HAL/MHI/firmware setup.

## Dependencies And Integration

The file depends on Linux PCI matching, shared ath12k PCI/HIF/MHI/core/HAL layers, local Wi-Fi 7 hardware init, DP/core HAL headers, and common PCI register base definitions. It integrates with `hw.c` for revision-specific params and with `mhi.c` through bus wake/release and selected hardware MHI configs.

## Risks And Edge Cases

Hardware version reading depends on setting `window_reg_addr` before reading `TCSR_SOC_HW_VERSION`; wrong ordering would read the wrong window. QCC2072 uses a different window register address and does not read a version, assuming one current revision. WCN7850/QCC2072 call MHI get/put on bus wake/release, so missing `mhi_ctrl` or `mhi_dev` would be fatal if those paths run too early. Unsupported major versions intentionally fail probe.

## Test Signals

Tests should verify PCI ID matching, MSI vector allocation, correct hw_rev selection for QCN9274 major 1/2 and WCN7850 major 2, QCC2072 fixed revision setup, firmware board search behavior, MHI wake/release during runtime PM, and clean unregister through `ath12k_wifi7_pci_exit()`.
