# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pci.c

## Purpose
PCI bus implementation for rtlwifi. It owns MMIO setup, probe/disconnect, DMA rings, descriptor handling, interrupts, beacon tasklets, ASPM/CLKREQ policy, MSI/legacy IRQ selection, suspend/resume, and exported `rtl_pci_ops`.

## Important APIs, Types, And Functions
Public entry points are `rtl_pci_probe()`, `rtl_pci_disconnect()`, `rtl_pci_suspend()`, `rtl_pci_resume()`, `rtl_pci_reset_trx_ring()`, and `rtl_pci_ops`. Key internals include `_rtl_mac_to_hwqueue()`, `rtl_pci_enable_aspm()`, `rtl_pci_disable_aspm()`, ring init/free helpers, `_rtl_pci_interrupt()`, `_rtl_pci_rx_interrupt()`, `_rtl_pci_tx_isr()`, `_rtl_pci_prepare_bcn_tasklet()`, `rtl_pci_tx()`, `rtl_pci_flush()`, `rtl_pci_start()`, `rtl_pci_stop()`, and `_rtl_pci_find_adapter()`.

## Control Flow
Probe enables PCI, selects DMA mask, allocates mac80211 hw, maps BAR MMIO, identifies chip type, installs IO handlers, reads efuse, initializes chip/core/PCI state, registers hardware, adds debugfs/rfkill, and requests IRQ. Start resets rings, initializes BT coexistence, calls chip `hw_init`, enables interrupts, configures RX, and marks HAL started. Interrupt handling demuxes beacon/TX/RX/FW/HSISR events, schedules tasklets, and reenables interrupts.

## State And Persistence
`struct rtl_pci` stores `pdev`, IRQ flags, TX/RX rings, descriptor counts, RX buffer size, IRQ masks, ASPM constants, retry limits, MSI state, and unload/init flags. Rings own DMA coherent descriptors and queued SKBs while active.

## Dependencies And Integration Points
Uses Linux PCI/DMA/IRQ APIs, mac80211, shared rtlwifi core/base/ps/efuse/debug/rfkill helpers, chip descriptor ops, BT coexistence, and register maps.

## Risks
DMA ownership, descriptor lifetime, old-vs-new TRX flow index handling, IRQ lock latency, probe error unwinds, ASPM quirks, and `rtl_pci_tx()` descriptor-pressure behavior are high-risk areas.

## Test Signals
Probe/remove PCI IDs, MSI fallback, DMA32/DMA64, start/stop, heavy TX/RX queue stop/wake, C2H RX commands, beacon refresh, early mode, suspend/resume, ASPM under IPS/LPS, and DMA/lockdep checks.
