# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_main.c

## Purpose
This is the primary PCI and netdev implementation for the OCTEON endpoint Virtual Function driver. It probes supported VF PCI IDs, maps BAR0, selects CN9K/CNXK VF hardware ops, negotiates PF/VF mailbox compatibility, registers the netdev, owns open/stop, transmit, NAPI, MSI-X queue interrupts, mailbox-backed link/Rx/MTU/MAC/offload operations, stats, timeout recovery, and remove cleanup.

## Important APIs, Types, And Functions
- PCI/module surface: `octep_vf_pci_id_tbl`, `octep_vf_driver`, `octep_vf_probe()`, `octep_vf_remove()`, `octep_vf_init_module()`, and `octep_vf_exit_module()`.
- Netdev surface: `octep_vf_netdev_ops` wires `octep_vf_open()`, `octep_vf_stop()`, `octep_vf_start_xmit()`, `octep_vf_get_stats64()`, `octep_vf_tx_timeout()`, `octep_vf_set_mac()`, `octep_vf_change_mtu()`, and `octep_vf_set_features()`.
- Interrupt and NAPI setup: `octep_vf_alloc_ioq_vectors()`, `octep_vf_enable_msix_range()`, `octep_vf_request_irqs()`, `octep_vf_setup_irqs()`, `octep_vf_napi_poll()`, and cleanup counterparts.
- PF mailbox integration: `octep_vf_get_link_status()`, `octep_vf_set_link_status()`, `octep_vf_set_rx_state()`, `octep_vf_get_if_stats()`, `octep_vf_get_link_info()`, and `octep_vf_get_mac_addr()` call mailbox helpers.
- Device setup: `octep_vf_device_setup()` maps BAR0, identifies chip, and calls `octep_vf_device_setup_cn93()` or `octep_vf_device_setup_cnxk()`.

## Control Flow
Probe enables PCI, sets 64-bit DMA mask, requests BARs, allocates a multiqueue Ethernet netdev, initializes `struct octep_vf_device`, maps BAR0 and hardware ops, initializes Tx-timeout work, installs netdev/ethtool ops, sets up the PF/VF mailbox, negotiates mailbox version, fetches firmware info, configures netdev offload features and MTU bounds, retrieves MAC address from PF, and registers the netdev.

Open resets IO queues, allocates IQ/OQ rings, sets up MSI-X and queue IRQs, sets real queue counts, adds/enables NAPI, marks admin up, asks PF to enable Rx, ensures link status is up if needed, enables hardware queues and interrupts, credits OQs, and turns carrier on if PF reports link up. Stop disables carrier and Tx, asks PF to set link/Rx down, disables interrupts and NAPI, frees IRQs and queue resources, disables/resets hardware queues, and returns the device to a closed state.

Transmit is the VF equivalent of the PF path: pad short skb, select queue, build single-buffer or SGL descriptor, add firmware-provided PKIND/front-size and optional checksum/TSO metadata, advance ring indices, maybe stop the subqueue, batch doorbell writes, and free dropped skbs on DMA mapping errors. Tx timeout holds a netdev reference, schedules work, and the work restarts the running netdev under RTNL.

## State And Persistence
State is volatile and stored in `struct octep_vf_device`: config, BAR mapping, firmware info from PF, negotiated mailbox version, queue arrays, stats, link info, mailbox pointer, hardware ops, IRQ vectors, and timeout work. Hardware state includes VF queue registers, MSI-X vectors, mailbox registers, descriptor DMA memory, and PF-maintained VF configuration reached via mailbox.

## Dependencies And Integration Points
The file depends on Linux PCI/netdev/AER/DMA/NAPI/MSI-X APIs, `octep_vf_config.h`, `octep_vf_main.h`, chip-specific VF files, VF Tx/Rx helpers, VF mailbox helpers, and VF ethtool ops. It requires a compatible PF and firmware mailbox protocol for MAC, firmware info, link, stats, MTU, and offload configuration.

## Risks And Edge Cases
- The VF requests only queue MSI-X vectors; mailbox notifications are multiplexed into queue 0 by chip-specific handlers.
- Probe depends on a live PF mailbox. PF absence or protocol mismatch prevents netdev registration.
- The Tx DMA error cleanup path uses SGL length indexes that should be checked against mapping layout.
- `octep_vf_open()` cleanup after `netif_set_real_num_*` failure disables/deletes NAPI even if NAPI was not yet added in that path.
- Feature changes must be accepted by PF; local netdev features are updated only after mailbox success.
- Etthool/stats rely on PF bulk reads and can report stale state if mailbox calls fail.

## Test Signals
Test module load/unload, VF probe with compatible and incompatible PF versions, open/stop/reopen, Tx/Rx traffic, queue-full and timeout recovery, mailbox-backed MAC/MTU/offload changes, link up/down notifications, MSI-X interrupt affinity, DMA debug, PF removal or VF hot-unplug, and netdev registration failure unwinding.
