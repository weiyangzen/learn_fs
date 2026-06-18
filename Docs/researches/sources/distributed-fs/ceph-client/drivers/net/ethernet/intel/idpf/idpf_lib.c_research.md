# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lib.c

## Purpose
`idpf_lib.c` is the central IDPF driver lifecycle and netdevice implementation file. It manages MSI-X vectors, mailbox interrupts, vport allocation and release, netdev creation, MAC filters, open/stop paths, queue resource reset, hard reset recovery, SR-IOV configuration, periodic service/statistics work, feature changes, MTU and MAC changes, DMA memory helpers, hardware timestamp NDOs, and the `net_device_ops` table.

## Important APIs, types, and functions
- Interrupt/vector management: `idpf_intr_req()`, `idpf_intr_rel()`, `idpf_req_rel_vector_indexes()`, vector LIFO helpers, and mailbox IRQ helpers.
- Vport/netdev lifecycle: `idpf_init_task()`, `idpf_vport_alloc()`, `idpf_cfg_netdev()`, `idpf_vport_open()`, `idpf_vport_stop()`, `idpf_vport_dealloc()`, `idpf_vport_rel()`, `idpf_deinit_task()`.
- Reset flows: `idpf_service_task()`, `idpf_vc_event_task()`, `idpf_init_hard_reset()`, `idpf_check_reset_complete()`, and `idpf_initiate_soft_reset()`.
- Netdev ops: `idpf_open()`, `idpf_stop()`, `idpf_set_rx_mode()`, `idpf_set_features()`, `idpf_change_mtu()`, `idpf_set_mac()`, `idpf_get_stats64()`, hwtstamp get/set, XDP hooks, and `idpf_netdev_ops`.
- Feature/filter state: MAC filter add/delete/restore/remove helpers, flow steering cleanup, `idpf_vport_get_hsplit()`, `idpf_vport_set_hsplit()`, and promiscuous mode handling.
- Datapath validation: `idpf_chk_tso_segment()` and `idpf_features_check()` enforce hardware offload limits before TX.
- DMA helpers: `idpf_alloc_dma_mem()` and `idpf_free_dma_mem()`.
- SR-IOV/IDC/PTP hooks: `idpf_sriov_configure()`, IDC init/deinit/event calls, and PTP hwtstamp integration.

## Control flow
Initial device bring-up is asynchronous. Probe schedules `vc_event_task` with `IDPF_HR_DRV_LOAD`; the event task sets `IDPF_HR_RESET_IN_PROG` and calls `idpf_init_hard_reset()`. Hard reset initializes the default mailbox, starts mailbox processing, runs virtchnl core init, and waits until `idpf_init_task()` creates all default vports. `idpf_init_task()` allocates max queues through virtchnl, creates a vport, initializes per-vport config lists and RSS data, configures a netdev, repeats until all default vports exist, registers netdevs, clears reset/load flags, and starts periodic stats collection.

Interface open locks vport control, sets real queue counts, allocates vport interrupt resources, queue resources, queue IDs, interrupt registers, queue MMIO registers, RX buffers, XDP RXQ info, enables interrupts, configures queues through virtchnl, maps queue vectors, enables queues and vport, restores MAC filters, configures RSS, and finally marks the vport up. Stop performs the reverse: carrier off, TX disable, disable vport/queues, unmap vectors, optionally delete queues after queue-count changes, remove feature filters, deinit interrupts and XDP RXQ info, release queues/vectors, and clear `IDPF_VPORT_UP`.

Soft reset is a preallocation-based queue resource replacement flow. It clones the current vport up to the `link_up` field, adjusts the clone for queue count, descriptor count, MTU, or RSC changes, stops the live vport or deletes queues if down, requests new queues from the control plane, copies the clone back into the real vport, reallocates vector indexes if needed, updates netdev queue counts, refills default RSS LUT if queue count changed and userspace did not customize RSS, and reopens the vport if it was up. On failure it tries to add back the old queues and reopen the old vport.

Hard reset detaches netdevs, closes running interfaces while remembering `IDPF_VPORT_UP_REQUESTED`, issues IDC reset events, tears down virtchnl core and mailbox, triggers or observes firmware reset, waits for reset completion, rebuilds mailbox and virtchnl core, waits for vport init completion, reattaches/reopens previously running netdevs, and initializes IDC.

Netdev feature changes are serialized by vport control. RXHASH toggles update RSS when the interface is up. GRO_HW changes trigger an RSC soft reset. LOOPBACK sends an enable/disable virtchnl command. RX mode synchronizes unicast/multicast MAC filter lists asynchronously when called under addr-list spinlock and updates promiscuous/all-multicast flags through control-plane messages.

## State and persistence behavior
Adapter state includes workqueues, flags, mutexes, MSI-X arrays, vector LIFO, vport arrays, netdev arrays, control-plane connection manager, mailbox state, and capability-derived device ops. Vport state includes queue/vector resources, default MAC, vport ID/index, link state, timestamp config, and `dflt_qv_rsrc`. Per-vport persistent user settings are kept in `idpf_vport_config->user_config`: MAC filters, flow steering filters, RSS data, requested queue/descriptor counts, header split flag, promiscuous flags, and coalescing settings. These survive vport queue resource resets and are restored during open/reset.

Concurrency relies on `adapter->vport_ctrl_lock` for vport/netdev lifetime and configuration, `vector_lock` for MSI-X stack allocation, `queue_lock`/virtchnl synchronization elsewhere, spinlocks for MAC and flow steering lists, RTNL around netdev close/open where needed, delayed work cancellation during deinit/remove, and bit flags for remove/reset/vport-up state. DMA control queue memory is allocated with contiguous DMA attributes and page-aligned size.

## Dependencies and integration points
The file integrates with Linux PCI, netdevice, workqueue, MSI-X, NAPI, DMA, XDP/XSK, SR-IOV, PTP hwtstamp, and libeth TX validation APIs. It delegates hardware/control-plane operations to IDPF modules: virtchnl message helpers, queue allocation/configuration, interrupt register setup, RSS, TX/RX datapaths, XDP, IDC, PTP, and device-specific register ops. `idpf_main.c` owns probe/remove around these library routines.

## Risks and edge cases
- Reset ordering is high risk: workqueue cancellation, mailbox teardown, vport deallocation, IDC events, and netdev unregister must not race with callbacks.
- Soft reset copies only part of `struct idpf_vport`; adding fields before `link_up` may unintentionally become cloned state, while fields after it are intentionally preserved.
- Queue-change rollback after failed add/open is best effort; failures can leave the interface down or partially restored.
- MAC filter operations can be asynchronous from `.set_rx_mode`; firmware failures may be observed later and cached state can temporarily diverge.
- Vector LIFO accounting must remain exact across default vport reserved vectors, RDMA-reserved vectors, vport releases, and queue count changes.
- `idpf_features_check()` and TSO fragment walking encode hardware descriptor limits; off-by-one errors can surface as TX hangs or corrupted offloads.
- Remove paths free stale registered netdevs even if reset recovery failed earlier; double free/unregister ordering needs continued lockdep/KASAN coverage.

## Test signals
Signals include probe/remove/load-failure cleanup, interface open/close cycles, queue count and descriptor-count ethtool resets, MTU changes with RDMA IDC events, RXHASH/GRO_HW/LOOPBACK feature toggles, MAC address and multicast/promiscuous changes, SR-IOV enable/disable including assigned VF rejection, hard reset injection and recovery with netdev reopen, XDP/XSK attach and traffic, TX offload boundary tests, DMA allocation failure injection, MSI-X vector exhaustion/RDMA reservation cases, and concurrent ethtool/netdev/remove/reset stress.
