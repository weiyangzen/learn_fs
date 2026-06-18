# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pci.h

## Purpose
Defines PCI constants, device IDs, queue IDs, descriptor layouts, ring structures, PCI private state, MMIO accessors, and public PCI operations for rtlwifi.

## Important APIs, Types, And Functions
Queue IDs cover BK/BE/VI/VO, beacon, TX command, management, high, and H2C queues. Device IDs cover RTL8192SE/CE/DE, RTL8188EE, RTL8723AE/BE, RTL8192EE, RTL8821/12AE, and RTL8822BE. Main structs are descriptor types, `rtl8192_tx_ring`, `rtl8192_rx_ring`, `rtl_pci`, `mp_adapter`, and `rtl_pci_priv`.

## Control Flow
`RTL_PCI_DEVICE()` builds ID-table entries. `rtl_pci_probe()`/disconnect own lifecycle, while `rtl_pci_ops` is called by shared core for start/stop/TX/flush/ring reset/wait queue/ASPM.

## State And Persistence
Defines DMA addresses, descriptors, SKB queues, RX buffers, indices, IRQ masks, ASPM policy, bridge identity, retry limits, MSI state, BT state, and LED state.

## Dependencies And Integration Points
Depends on Linux PCI, rtlwifi core private state, BT coexistence, LED control, and queue/acm definitions. Inline MMIO helpers bind `io.pci_mem_start` to register access.

## Risks
Packed descriptors and queue numbers are hardware ABI. Private layout affects `ieee80211_alloc_hw()` private allocation. `calc_fifo_space()` assumes one reserved ring slot.

## Test Signals
Compile all PCI chip drivers, verify MMIO callbacks, descriptor alignment, queue selection, ring reset, ASPM toggles, and probe/disconnect casts.
