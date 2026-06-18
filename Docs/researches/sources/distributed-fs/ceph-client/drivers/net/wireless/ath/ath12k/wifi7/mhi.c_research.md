# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/mhi.c

## Purpose

`mhi.c` defines MHI controller configurations for Wi-Fi 7 PCIe ath12k devices. It provides channel and event-ring descriptions for QCN9274 and WCN7850-style devices so firmware/QMI IPC can run over MHI.

## Important APIs And Data

The file exports `ath12k_wifi7_mhi_config_qcn9274` and `ath12k_wifi7_mhi_config_wcn7850`. Each config uses two `IPCR` channels: channel 20 for host-to-device (`DMA_TO_DEVICE`) and channel 21 for device-to-host (`DMA_FROM_DEVICE`). Both use event ring 1, execution environment mask `0x4`, disabled doorbell burst mode, and no low-power/offload notifications. QCN9274 uses 32 channel elements, `max_channels = 30`, and `timeout_ms = 10000`. WCN7850 uses 64 channel elements, `max_channels = 128`, `timeout_ms = 2000`, and `buf_len = 8192`.

Event configs define a control event ring with 32 elements on IRQ 1 and a data event ring with 256 elements on IRQ 2, one millisecond moderation for the second event ring, disabled doorbell burst mode, and priority 1 on the data ring.

## Control Flow And Integration

`hw.c` references these exported configs in `ath12k_wifi7_hw_params[]`. The PCI/core MHI setup layer consumes the selected `mhi_controller_config` during device bring-up, creates MHI channels/events, and later uses MHI for firmware communication and bus power management. WCN7850 PCI bus wake/release helpers in `pci.c` call into MHI device get/put paths around bus access.

## State And Persistence Behavior

The channel and event tables are static configuration, not runtime state. Once selected, the MHI core creates runtime controller/channel/event state from these descriptors. The descriptors persist for the lifetime of the module.

## Dependencies

The file includes generic ath12k MHI definitions and its local header. It depends on Linux MHI types (`struct mhi_channel_config`, `struct mhi_event_config`, `struct mhi_controller_config`), DMA direction constants, and MHI doorbell/event enums.

## Risks And Edge Cases

Timeout and buffer-length differences between QCN9274 and WCN7850 are intentional; assigning the wrong config in `hw.c` can break firmware boot or IPC. Channel numbers are hard-coded to IPCR 20/21; firmware ABI changes would require synchronized updates. WCN7850's shorter timeout may expose slow firmware boot or resume issues more readily than QCN9274.

## Test Signals

Probe should create MHI channels/events without errors, firmware boot should complete, QMI/IPCR traffic should work in both directions, suspend/resume should not strand MHI references, and timeout logs should be absent during normal boot and recovery. Device-specific tests should confirm QCN9274 and WCN7850 select their intended config.
