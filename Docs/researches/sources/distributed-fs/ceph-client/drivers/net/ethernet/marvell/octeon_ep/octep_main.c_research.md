# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_main.c

## Purpose
This is the primary PCI and netdev implementation for the OCTEON endpoint Physical Function driver. It registers the `octeon_ep` PCI driver, probes supported CN9K/CNXK PF devices, maps BARs through `octep_device_setup()`, initializes firmware control and PF/VF mailbox state, exposes a Linux Ethernet netdev, and owns open/stop, transmit, NAPI, interrupts, SR-IOV enablement, heartbeat monitoring, and remove cleanup.

## Important APIs, Types, And Functions
- PCI/module surface: `octep_pci_id_tbl`, `octep_driver`, `octep_probe()`, `octep_remove()`, `octep_sriov_configure()`, `octep_init_module()`, and `octep_exit_module()`.
- Netdev surface: `octep_netdev_ops` wires `octep_open()`, `octep_stop()`, `octep_start_xmit()`, `octep_get_stats64()`, `octep_tx_timeout()`, `octep_set_mac()`, `octep_change_mtu()`, `octep_set_features()`, `octep_get_vf_config()`, and `octep_set_vf_mac()`.
- Interrupt setup: `octep_alloc_ioq_vectors()`, `octep_enable_msix_range()`, `octep_request_irqs()`, `octep_setup_irqs()`, and `octep_clean_irqs()` allocate per-queue vector context, enable MSI-X, bind non-IOQ interrupt names to hardware-specific handlers, and register IOQ handlers.
- NAPI and queue accounting: `octep_napi_poll()` calls `octep_iq_process_completions()` and `octep_oq_process_rx()`, then `octep_update_pkt()` acknowledges completed Tx/Rx counts before `octep_enable_ioq_irq()` resends interrupts.
- Work items: `octep_tx_timeout_task()` restarts a running netdev under RTNL, `octep_intr_poll_task()` polls non-IOQ interrupts when the interface is down, `octep_ctrl_mbox_task()` drains firmware control messages, and `octep_hb_timeout_task()` closes the netdev after repeated firmware heartbeat misses.

## Control Flow
Probe enables PCI, sets a 64-bit DMA mask, requests BARs, verifies firmware readiness via a vendor extended capability, allocates `alloc_etherdev_mq()`, sets driver data, calls `octep_device_setup()`, sets up PF/VF mailbox structures, queries firmware info, configures netdev features and MTU/MAC limits, and registers the netdev. `octep_device_setup()` maps BAR0/BAR2/BAR4, selects CN93-compatible or CNXK PF hardware ops by device ID, initializes control mailbox support, and starts delayed non-IOQ polling until the interface is opened.

Open resets hardware queues, allocates IQs and OQs, sets up MSI-X and IRQs, sets real queue counts, adds/enables NAPI, advertises admin/rx/link state through control mailbox, enables hardware queues and interrupts, credits all OQs, and turns carrier on if firmware reports link up. Stop reverses the data path: it sets PF link/Rx down, stops carrier and Tx queues, disables interrupts, disables/deletes NAPI, frees IRQs, completes and frees Tx/Rx queue resources, disables/resets hardware queues, and restarts non-IOQ polling.

Transmit pads short frames, selects the queue from `skb_get_queue_mapping()`, maps the linear skb or gather list, fills `octep_tx_desc_hw`, applies checksum/TSO metadata when firmware supports it, advances the ring write index, stops the subqueue if descriptor space is low, and rings the IQ doorbell when batching should flush. DMA mapping failures free the skb and return `NETDEV_TX_OK`, effectively dropping the frame without retry.

## State And Persistence
State is in memory and hardware registers only. `struct octep_device` stores BAR mappings, hardware ops, firmware capabilities, queue arrays, per-queue stats, PF/VF mailbox state, link info, work structs, control mailbox wait lists, heartbeat miss counter, and delayed work flags. Persistent configuration is not written by this file. Hardware-visible state includes ring base/size registers, interrupt masks, queue doorbells, packet counters, mailbox registers, SR-IOV VF enablement, and firmware-maintained link/MAC/MTU/offload state reached through control mailbox commands.

## Dependencies And Integration Points
The file depends on Linux PCI, netdevice, MSI-X, NAPI, DMA mapping, workqueue, rtnl, SR-IOV, and ethtool integration. It delegates ring allocation to `octep_tx.c` and `octep_rx.c`, hardware register programming to `octep_cn9k_pf.c`/`octep_cnxk_pf.c` via `octep_hw_ops`, firmware control to `octep_ctrl_net.*`, VF mailbox servicing to `octep_pfvf_mbox.*`, and ethtool registration to `octep_ethtool.c`.

## Risks And Edge Cases
- IRQ, workqueue, and netdev teardown ordering is critical because interrupt handlers and delayed work dereference `octep_device`.
- Queue indices and packet counters are intentionally lockless and rely on `READ_ONCE()`, `WRITE_ONCE()`, barriers, NAPI serialization, and hardware counter semantics.
- `octep_start_xmit()` drops frames on DMA mapping failure while returning `NETDEV_TX_OK`; monitoring must use driver stats or kernel logs rather than stack retry behavior.
- Probe deferral depends on a vendor-specific firmware-ready capability; missing or late firmware blocks binding.
- SR-IOV disable refuses assigned VFs, and PF-maintained VF MAC policy blocks VF override only after the PF flag is set.
- `octep_device_cleanup()` frees mailbox slots before `octep_delete_pfvf_mbox()`, so changes around mailbox allocation/freeing need careful double-free review.

## Test Signals
Useful signals are successful `pci_register_driver()`, probe logs, `register_netdev()` success, carrier transitions on open/stop, MSI-X allocation count, IRQ request/free logs, NAPI traffic under Tx/Rx load, ethtool feature negotiation, MTU/MAC changes through control mailbox, SR-IOV VF count changes, VF MAC policy behavior, heartbeat-miss device close, and remove/unload with no use-after-free, DMA leak, or stuck workqueue warnings.
