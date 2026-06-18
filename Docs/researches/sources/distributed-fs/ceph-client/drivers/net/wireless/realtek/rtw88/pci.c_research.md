# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/pci.c

## Purpose
`pci.c` implements the PCIe HCI backend for `rtw88`. It maps device registers, allocates and programs DMA descriptor rings, implements register and packet I/O hooks for core/HCI, handles TX completion and RX NAPI, controls PCI interrupts, manages PCIe link power saving and deep power-save entry/exit, applies PCI PHY/DBI/MDIO configuration, handles suspend/resume quirks, registers PCI error handlers, and provides probe/remove/shutdown entry points.

## Important APIs, Types, and Functions
- Module parameters: `disable_msi` and `disable_aspm`; DMI quirks can also disable ASPM and deep LPS.
- MMIO hooks: `rtw_pci_read8/16/32()` and `rtw_pci_write8/16/32()` back `rtw_hci_ops`.
- Ring setup/teardown: `rtw_pci_init_trx_ring()`, `rtw_pci_init_tx_ring()`, `rtw_pci_init_rx_ring()`, `rtw_pci_free_trx_ring()`, and reset helpers.
- HCI lifecycle: `rtw_pci_setup()`, `rtw_pci_start()`, `rtw_pci_stop()`, `rtw_pci_deep_ps()`, `rtw_pci_link_ps()`, `rtw_pci_interface_cfg()`, and `rtw_pci_ops`.
- TX path: `rtw_pci_tx_write_data()`, `rtw_pci_tx_write()`, `rtw_pci_tx_kick_off_queue()`, `rtw_pci_tx_kick_off()`, reserved-page and H2C writers, queue flush helpers, and `rtw_pci_tx_isr()`.
- RX path: `rtw_pci_rx_isr()`, `rtw_pci_get_hw_rx_ring_nr()`, `rtw_pci_rx_napi()`, and `rtw_pci_napi_poll()`.
- IRQ path: `rtw_pci_request_irq()`, `rtw_pci_interrupt_handler()`, `rtw_pci_interrupt_threadfn()`, interrupt mask/recognition helpers.
- PCI configuration: `rtw_dbi_read8()`, `rtw_dbi_write8()`, `rtw_mdio_write()`, `rtw_pci_link_cfg()`, `rtw_pci_phy_cfg()`, `rtw_pci_claim()`, and resource mapping/destruction.
- Top-level exports: `rtw_pci_probe()`, `rtw_pci_remove()`, `rtw_pci_shutdown()`, `rtw_pm_ops`, and `rtw_pci_err_handler`.

## Control Flow
`rtw_pci_probe()` allocates `ieee80211_hw` with appended `rtw_dev` and `rtw_pci`, assigns the chip info and PCI HCI ops, checks DMI quirks, initializes core firmware/work state, enables and claims the PCI device, maps BAR 2, allocates rings, initializes NAPI, reads chip/efuse/board info, optionally marks `rx_no_aspm`, programs PCI PHY/link settings, registers mac80211 hardware, and requests a threaded IRQ. Error paths unwind NAPI, PCI resources, core state, and hardware allocation.

During HCI setup, `rtw_pci_reset_buf_desc()` writes DMA base addresses and descriptor counts for BCN, H2C, BK/BE/VO/VI/MGMT/HI0 TX rings and the MPDU RX ring, then clears read/write pointers. Start enables NAPI, marks the backend running, and enables interrupts under `irq_lock`. Stop disables interrupts, synchronizes IRQ, stops NAPI, resets rings, and frees queued TX SKBs.

TX prepares an SKB by pushing the chip TX descriptor, filling it with `rtw_tx_fill_tx_desc()`, mapping it for DMA, writing two PCI buffer descriptors for descriptor and payload, queueing the SKB, setting a pending queue bit, and later kicking hardware by writing the queue write pointer. If a ring runs low on descriptors, the corresponding mac80211 queue is stopped; TX ISR drains completed descriptors, unmaps DMA, wakes queues when space returns, forwards requested TX status to the TX report path, and otherwise reports ACK/NOACK to mac80211.

RX interrupt handling schedules NAPI. NAPI reads the hardware write pointer, syncs each RX buffer for CPU, parses the RX descriptor, copies the frame into a fresh SKB, routes C2H packets to firmware command handling, strips RX descriptors from data frames, updates invalid-channel frequency if needed, updates RX stats, passes packets to `ieee80211_rx_napi()`, then resyncs the original DMA buffer and advances ring indices. Interrupts are reenabled when NAPI completes; a race check reschedules NAPI if data appeared before completion.

## State and Persistence Behavior
`struct rtw_pci` persists the PCI device pointer, MMIO base, IRQ masks/enabled/running state, two spinlocks, NAPI netdev, RX tag counter, TX queued bitmap, TX/RX rings, PCIe link control, link power-save usage count, ASPM workaround flag, and NAPI-running bit. Descriptor rings and RX buffers are DMA allocations held from probe until remove. TX SKBs are queued until completion or stop; reserved-page beacon queue replaces its previous SKB. RX buffers are reused permanently and copied into fresh SKBs for upper layers.

## Dependencies and Integration Points
`pci.c` integrates Linux PCI, DMI, MSI/INTx vector allocation, threaded IRQs, DMA mapping, NAPI, and mac80211 TX/RX reporting. It depends on local core/HCI abstractions (`main.h`, `pci.h`, `tx.h`, `rx.h`, `fw.h`, `ps.h`, `debug.h`, `mac.h`). It exposes `rtw_hci_ops` to core and consumes chip descriptors sizes, WCPU type, interface PHY tables, firmware features, and power-save callbacks.

## Risks
- DMA descriptor ownership and ring indices are sensitive to ordering. A bad write pointer, descriptor size, or unmap length can corrupt TX/RX or leak DMA mappings.
- RX path copies from reusable DMA buffers; allocation failure drops frames and must still resync descriptors.
- Interrupt masking is deliberately split between hard handler, threaded handler, and NAPI. Incorrect reenable behavior can cause interrupt storms, missed RX, or MSI edge loss.
- Deep power save requires TX rings to be empty unless firmware supports TX wake; entering too early can strand DMA.
- ASPM/CLKREQ behavior is hardware/platform sensitive. DMI quirks, bridge vendor checks, and module parameters are required to avoid device loss on known systems.
- Probe/remove unwind order is nontrivial; IRQ freeing after resource teardown or NAPI cleanup out of order can race live handlers.

## Test Signals
- PCI probe/remove/reprobe with MSI enabled and disabled.
- High-throughput TX/RX with queue stop/wake behavior and no DMA API warnings.
- RX NAPI budget exhaustion and interrupt-race scenarios.
- H2C and reserved-page/beacon queue writes.
- Suspend/resume on affected 8822C RFE and 8821C/Intel bridge systems, with ASPM toggling.
- Firmware recovery through PCI AER slot reset.
- Deep LPS entry under idle TX rings and forced TX while leaving deep PS.
