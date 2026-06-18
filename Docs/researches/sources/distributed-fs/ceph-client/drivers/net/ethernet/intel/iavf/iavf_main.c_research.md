# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_main.c

## Purpose
`iavf_main.c` is the core PCI/netdev driver for Intel Adaptive Virtual Functions. It owns module registration, PCI probe/remove, adapter allocation, netdev operations, queue and interrupt setup, RSS initialization, VLAN/MAC/filter bookkeeping, admin queue scheduling, reset recovery, TC offloads, feature negotiation, suspend/resume, and integration with PTP and virtchnl support.

## Important APIs, Types, And Functions
The module exposes `iavf_init_module`/`iavf_exit_module` around a static `pci_driver`, and the netdev behavior is defined by `iavf_netdev_ops`. Public helpers used by other iavf files include `iavf_status_to_errno`, `virtchnl_status_to_errno`, `iavf_allocate_dma_mem_d`, `iavf_free_dma_mem`, `iavf_allocate_virt_mem`, `iavf_free_virt_mem`, `iavf_schedule_reset`, `iavf_schedule_aq_request`, `iavf_irq_enable`, `iavf_get_num_vlans_added`, `iavf_add_filter`, `iavf_promiscuous_mode_changed`, `iavf_down`, `iavf_set_queue_vlan_tag_loc`, `iavf_config_rss`, `iavf_schedule_finish_config`, `iavf_parse_vf_resource_msg`, `iavf_reset_step`, `iavf_free_all_tx_resources`, `iavf_free_all_rx_resources`, and `iavf_process_config`.

Key internal functions cover interrupt mapping/request/free, Tx/Rx ring allocation/configuration, VLAN and MAC filter list state, RSS key/LUT programming, q-vector/NAPI setup, staged initialization, watchdog processing, admin queue draining, reset replay, TC mqprio/flower/u32 offload, feature fix/set, queue shaper netlink ops, PCI lifecycle, and PM.

## Control Flow
Probe enables the PCI device, configures DMA, maps BAR0, allocates the netdev and adapter, initializes locks/lists/work items/wait queues/PTP state, then schedules the watchdog. Initialization proceeds asynchronously through `iavf_watchdog_step`: `__IAVF_STARTUP` initializes AdminQ and sends API version; `__IAVF_INIT_VERSION_CHECK` validates PF API and requests VF resources; `__IAVF_INIT_GET_RESOURCES` parses VF resource data; `__IAVF_INIT_EXTENDED_CAPS` exchanges VLAN V2/RXDID/PTP capabilities; `__IAVF_INIT_CONFIG_ADAPTER` configures netdev features, interrupts, queues, RSS, VLAN offload, QoS/PTP, and reaches `__IAVF_DOWN`.

Open allocates Tx/Rx descriptors, requests traffic IRQs, installs the primary MAC filter, restores inactive/disabled FDIR filters, configures rings and queues, enables NAPI, schedules queue enable, and unmasks interrupts. Close marks VSI down, preserves only safe AQ work, calls `iavf_down`, waits briefly for PF confirmation that resources are released, and restores deferred AQ bits. Reset disables interrupts, optionally requests PF reset, waits for reset detection and completion, rebuilds AdminQ/RSS/interrupts as needed, replays MAC/cloud/filter state, restores rings and queues if previously running, and either returns to running or down.

The watchdog and adminq tasks form the async control loop. `iavf_schedule_aq_request` ORs bits into `adapter->aq_required` and wakes the watchdog. `iavf_process_aq_command` sends one pending virtchnl or firmware command per pass in a fixed priority order. `iavf_adminq_task` drains ARQ events and calls `iavf_virtchnl_completion`, then logs and clears AQ error bits.

## State And Persistence Behavior
Adapter state is held in `adapter->state`, `last_state`, `flags`, `aq_required`, `current_op`, lists, queues, rings, RSS buffers, VLAN caps, QoS caps, PTP state, wait queues, and workqueue items. State is in-memory and rebuilt after PCI probe. Across netdev down/up and VF reset, the driver attempts to preserve user-visible configuration: MAC/VLAN filters, FDIR filters, cloud filters, advanced RSS, queue counts, RSS key/LUT, VLAN offload toggles, shaper values, and PTP configuration where supported.

List-backed state is protected by spinlocks: MAC/VLAN, cloud filters, FDIR filters, advanced RSS, and promiscuous flags. Netdev operations that mutate core state assert or take the netdev lock; some paths also use RTNL when changing registered queue counts. Wait queues synchronize `ndo_stop` and MAC-address changes with virtchnl completions.

## Dependencies And Integration Points
This file depends on PCI, netdevice, NAPI, MSI-X, DMA, ethtool, TC, flow dissector, net shaper, PTP, libie/libeth, virtchnl, and iavf shared AdminQ code. It integrates with `iavf_txrx.c` for transmit/receive rings, `iavf_virtchnl.c` for PF messages and completions, `iavf_ethtool.c` for ethtool ops installation, `iavf_fdir.c`/`.h` for FDIR state, `iavf_adv_rss.c` for advanced RSS, `iavf_ptp.c` for timestamping, and shared headers for hardware registers and status codes.

## Risks
The major risks are ordering and concurrency around async PF communication. AQ bit priority can starve lower-priority work if a command remains pending. Close/reset/remove paths must avoid freeing DMA resources before PF confirms queues are disabled. Reset can run while netdev operations are in flight, so lock ordering between RTNL, netdev lock, workqueue cancellation, and spinlocks is critical. Feature negotiation must tolerate PFs that omit optional capabilities or return invalid MTU/RXDID/VLAN data. TC and FDIR offloads accept only strict masks and limited actions, so user-visible errors must remain accurate. Several paths replay cached state after reset; leaks or stale flags can duplicate filters or leave PF state inconsistent.

## Test Signals
High-value tests include PCI probe/remove error unwinds, staged init retries and PF communication failure recovery, open/close with PF response delay, VF reset while running and while down, ring/channel/MTU changes that force reset, RSS AQ/register/PF modes, VLAN V1/V2 filtering and strip/insert toggles, MAC replacement wait outcomes, ntuple enable/disable and FDIR cleanup, TC mqprio ADQ add/delete, TC flower/u32 offloads, queue shaper set/delete and reset replay, suspend/resume, PTP capability negotiation, and AQ overflow/error register handling.
