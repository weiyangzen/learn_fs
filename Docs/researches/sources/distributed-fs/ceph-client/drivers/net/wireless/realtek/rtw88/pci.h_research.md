# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/pci.h

## Purpose
`pci.h` defines the PCIe backend contract for `rtw88`: descriptor counts and buffer sizes, PCI register offsets and bit fields, interrupt masks, ring structures, PCI-private device state, exported PCI entry points, and small helpers for descriptor availability, queue sizing, SKB-private TX data access, and TX buffer descriptor lookup.

## Important APIs, Types, and Functions
- Ring sizes and buffers: `RTK_DEFAULT_TX_DESC_NUM`, `RTK_BEQ_TX_DESC_NUM`, `RTK_MAX_RX_DESC_NUM`, and `RTK_PCI_RX_BUF_SIZE`.
- PCI register definitions: control, DBI, MDIO, link config, descriptor base/count/index registers, read/write pointer clear, H2C CSR, interrupt mask/status registers, and interrupt bit definitions.
- Descriptor/ring types: `struct rtw_pci_tx_buffer_desc`, `struct rtw_pci_rx_buffer_desc`, `struct rtw_pci_tx_data`, `struct rtw_pci_ring`, `struct rtw_pci_tx_ring`, and `struct rtw_pci_rx_ring`.
- PCI-private state: `struct rtw_pci` with PCI device, locks, masks, running/IRQ state, NAPI netdev, RX tag, queued TX bitmap, ring arrays, link state, ASPM workaround flag, flags bitmap, and MMIO pointer.
- Exports: `rtw_pm_ops`, `rtw_pci_err_handler`, `rtw_pci_probe()`, `rtw_pci_remove()`, and `rtw_pci_shutdown()`.
- Helpers: `avail_desc()`, `max_num_of_tx_queue()`, `rtw_pci_get_tx_data()`, and `get_tx_buffer_desc()`.

## Control Flow
This header provides compile-time data consumed by `pci.c`. `max_num_of_tx_queue()` gives BE a larger ring and BCN a single descriptor. `avail_desc()` reserves one descriptor slot so full and empty ring states are distinguishable. `rtw_pci_get_tx_data()` stores PCI DMA metadata in mac80211 SKB status driver data, guarded by a `BUILD_BUG_ON()`. `get_tx_buffer_desc()` computes the current write-pointer descriptor address from ring head and descriptor size.

## State and Persistence Behavior
The declared `struct rtw_pci` state lives in `rtw_dev->priv` for the lifetime of the PCI device. Ring heads point to coherent DMA memory; RX ring `buf[]` entries point to long-lived SKBs; TX rings maintain software SKB queues matching hardware descriptors. `link_usage` persists nested link-power requests, while `flags` records NAPI state. Register constants encode persistent hardware programming addresses rather than mutable state.

## Dependencies and Integration Points
The header includes `main.h`, so it inherits core driver state and queue enums. It integrates with Linux PCI through `struct pci_dev`, DMA types, NAPI/netdev types, and mac80211 SKB control blocks. Its register definitions must match the chip families supported by the PCI backend and are used by interrupt, DMA, ASPM, DBI, and MDIO code.

## Risks
- Descriptor counts must stay within `TRX_BD_IDX_MASK`; `pci.c` validates TX lengths, but changing constants can break hardware index fields.
- `struct rtw_pci_tx_data` must fit inside mac80211 `status_driver_data`; the build assertion catches size growth only at compile time.
- RX/TX descriptor layouts use little-endian fields and exact sizes expected by hardware.
- Register definitions are shared across chip generations with conditional handling in `pci.c`; accidental reuse for unsupported chips can cause silent hardware misconfiguration.

## Test Signals
- Compile-time assertions for SKB private data size.
- Ring wrap tests for `avail_desc()` and queue stop/wake behavior.
- Probe tests validating BE/BCN/default queue descriptor counts.
- DMA and interrupt tests confirming register constants program the expected hardware queues.
