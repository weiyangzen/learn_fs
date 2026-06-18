# Research: subset-b-004609

Grouped source research for subset B work item `subset-b-004609`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_fp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_fp.c

## Purpose
This file implements the qede fast path: Tx descriptor construction and completion, Rx buffer provisioning and CQE processing, NAPI polling, MSI-X fastpath interrupt entry, XDP transmit/redirect support, checksum/GRO metadata, tunnel offload filtering, and PTP timestamp handoff from packets to `qede_ptp`.

## Important APIs, Types, and Functions
The central queue types are `struct qede_fastpath`, `struct qede_rx_queue`, `struct qede_tx_queue`, `struct sw_rx_data`, `struct qede_agg_info`, qede software Tx rings, and qed chain objects used for FW descriptor rings.

Public driver entry points include `qede_alloc_rx_buffer()`, `qede_free_tx_pkt()`, `qede_txq_has_work()`, `qede_has_rx_work()`, `qede_recycle_rx_bd_ring()`, `qede_update_rx_prod()`, `qede_poll()`, `qede_msix_fp_int()`, `qede_start_xmit()`, `qede_select_queue()`, `qede_features_check()`, and `qede_xdp_transmit()`.

Important internal helpers include `qede_xmit_type()`, `qede_update_tx_producer()`, `qede_tx_int()`, `qede_xdp_tx_int()`, `qede_rx_process_cqe()`, `qede_rx_xdp()`, `qede_rx_build_skb()`, `qede_rx_build_jumbo()`, the TPA/GRO helpers `qede_tpa_start()`, `qede_tpa_cont()`, `qede_tpa_end()`, and checksum classifiers `qede_check_csum()`, `qede_check_tunn_csum()`, and `qede_check_notunn_csum()`.

## Control Flow
Transmit starts in `qede_start_xmit()`. The code chooses an offload type from skb checksum/GSO/encapsulation state, optionally linearizes skb fragments, produces FW Tx BDs, maps linear and fragmented skb data for DMA, fills VLAN, L4 checksum, tunnel, IPv6 extension, and LSO fields, stores the skb in the software ring, advances `sw_tx_prod`, and rings the doorbell through `qede_update_tx_producer()`. Tx completion is driven by NAPI through `qede_tx_int()`, which compares FW status-block consumer indices against qed chain indices, calls `qede_free_tx_pkt()` to unmap and free skb data, updates netdev byte/packet completion accounting, and wakes stopped queues when descriptor space returns.

Receive setup allocates order-0 pages in `qede_alloc_rx_buffer()`, maps full pages for DMA, and places page segments into Rx BDs. NAPI calls `qede_rx_int()`, which processes completion CQEs until budget or hardware consumer exhaustion. Regular CQEs can run XDP first. `XDP_PASS` continues into skb construction; `XDP_TX` and `XDP_REDIRECT` allocate replacement buffers before consuming the current BD; drop/abort paths recycle BDs. Non-XDP packets build skb data from page segments, handle jumbo packets spanning multiple BDs, set protocol/hash/checksum/Rx queue metadata, record PTP Rx timestamps when CQE flags indicate a timestamped timesync packet, and pass packets through GRO.

TPA/GRO CQEs are handled as a small state machine. TPA start builds the initial skb and records aggregation state, continuation appends page frags, and end verifies lengths and BD counts, finalizes protocol/checksum/GSO metadata, and submits the aggregated skb. `qede_poll()` also handles XDP Tx completions, flushes redirects, completes NAPI when no more status-block work exists, acknowledges interrupts, and flushes pending XDP Tx doorbells.

## State and Persistence Behavior
The file maintains volatile queue state: software producer/consumer indices, filled Rx buffer counts, page offsets within reused Rx pages, DMA mappings, skb pointers, XDP frame/page ownership, TPA aggregation state, per-queue statistics, and hardware doorbell producer values. It persists nothing beyond in-memory driver state and netdev statistics. DMA mappings and page references are lifetime-sensitive and move between device ownership, driver rings, XDP, and the networking stack.

## Dependencies and Integration Points
It depends on qed chain/status-block and doorbell APIs, `struct eth_*_bd`/CQE formats from the qed firmware interface, Linux netdev/NAPI/skbuff/GRO APIs, DMA mapping APIs, XDP/BPF helpers, tunnel and checksum helpers, VLAN helpers, and `qede_ptp_record_rx_ts()`/`qede_ptp_tx_ts()` from the PTP layer. `qede_main.c` allocates and starts the queues consumed here and wires `qede_start_xmit`, `qede_poll`, IRQ handlers, and XDP hooks into netdev operations.

## Risks
The highest risks are descriptor/accounting mismatches and DMA lifetime errors. Tx failure cleanup must return qed chain producers to the pre-packet position and unmap exactly the segments that were mapped. Rx page reuse depends on correct `page_offset`, refcount, and DMA unmap behavior, especially with XDP because pages are mapped bidirectionally. Memory barriers around status-block reads and doorbell writes are essential to avoid missed completions or firmware reading stale descriptors. TPA error paths can leak or double-use pages if aggregation state and `tpa_start_fail` handling drift. Hardware checksum classification must not mark bad packets as `CHECKSUM_UNNECESSARY`, especially for tunneled traffic. Only one PTP Tx timestamp can be outstanding, so timestamp requests may be skipped under load.

## Test Signals
Useful signals include sustained TCP/UDP transmit and receive, high-fragment skb transmit, TSO/TSO6, VLAN insertion/receive, VXLAN/Geneve/GRE offloads, IPIP offload suppression, jumbo receive, GRO/TPA aggregation, XDP pass/drop/tx/redirect, queue stop/wake stress, Tx timeout diagnostics, and PTP hardware timestamping. Kernel debug signals include DMA API debugging, page refcount debugging, NAPI budget behavior under netpoll budget zero, no stuck netdev queues, stable `rx_alloc_errors` under memory pressure, and no missed interrupts after status-block acknowledgement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_fp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_main.c

## Purpose
This file is the qede PCI/netdev lifecycle and slowpath coordinator. It binds supported QLogic/Marvell FastLinQ PCI IDs, obtains the lower-layer `qed` Ethernet operations, creates and registers the netdev, configures features and queues, opens/closes vports, manages NAPI and interrupts, handles SR-IOV, TC offload, stats, RDMA and PTP integration, link updates, Tx timeout logging, AER, and firmware/hardware recovery.

## Important APIs, Types, and Functions
Important top-level objects are the `qede_pci_driver`, `qede_ll_ops` callback table, `qede_netdev_ops` variants for PF/VF/XDP, `qede_netdev_notifier`, and state in `struct qede_dev`: `cdev`, `ops`, `ndev`, fastpath arrays, queue counts, `sp_flags`, `err_flags`, `state`, stats, devlink, RDMA and PTP pointers.

Key lifecycle functions are `qede_init()`, `qede_cleanup()`, `qede_probe()`, `__qede_probe()`, `qede_remove()`, `__qede_remove()`, `qede_shutdown()`, `qede_open()`, `qede_close()`, `qede_load()`, `qede_unload()`, and `qede_reload()`. Queue/resource helpers include `qede_set_num_queues()`, `qede_alloc_fp_array()`, `qede_init_fp()`, `qede_alloc_mem_load()`, `qede_start_queues()`, `qede_stop_queues()`, `qede_setup_irqs()`, and `qede_sync_free_irqs()`. Slowpath and error functions include `qede_sp_task()`, `qede_link_update()`, `qede_schedule_recovery_handler()`, `qede_recovery_handler()`, `qede_schedule_hw_err_handler()`, and `qede_io_error_detected()`.

## Control Flow
Module init initializes forced speed maps, gets `qed` Ethernet ops, registers the netdev notifier, and registers the PCI driver. Probe calls the lower-layer `qed` probe and slowpath start, reads device info, allocates or reconnects a netdev, configures netdev features and operations, registers devlink and netdev in normal probe mode, adds RDMA support, enables PTP for PFs, registers callbacks with `qed`, and starts periodic stats work when configured.

Opening a netdev powers the device to D0 and calls `qede_load()`. Load chooses queue counts and interrupt resources, allocates fastpath structures, initializes Rx/Tx/XDP queue metadata, allocates status blocks and rings, sets real netdev queue counts, registers NAPI, requests MSI-X or configures SIMD handlers, starts the vport, starts Rx/Tx/XDP queues, activates the vport with RSS/Tx switching settings, configures TC layout and VLAN filters, requests link up, marks the device open, and applies coalescing. Close calls `qede_unload()`, which stops OS Tx, drops carrier, tears down link and queues, stops fastpath, releases ARFS filters and interrupts, removes NAPI, frees queue memory, clears PTP skip counters, and updates driver state.

Deferred work in `qede_sp_task()` serializes recovery, Rx mode changes, ARFS configuration, hardware error reporting, and AER recovery. The recovery path marks `QEDE_STATE_RECOVERY`, calls lower-layer recovery prolog, unloads if the interface was open, removes and reprobes the lower-layer device in recovery mode, reloads queues if needed, and restores the previous state or detaches the netdev on failure.

## State and Persistence Behavior
The file owns long-lived in-memory driver state for the netdev lifetime: device identity, feature flags, queue topology, interrupt metadata, fastpath structures, stats snapshots, requested queue counts, coalescing preferences, VLAN list, RDMA registration state, PTP state, and devlink handle. Runtime state transitions are guarded by `qede_lock` and RTNL-aware wrappers. No durable storage is written; user-visible settings survive reload/recovery only when held in `qede_dev` fields, such as coalescing entries and requested queue counts.

## Dependencies and Integration Points
It depends heavily on `linux/qed/qed_if.h` and `struct qed_eth_ops` for PCI probe/remove, slowpath, vport, queue, interrupt, devlink, doorbell recovery, statistics, link, and firmware error APIs. It integrates with netdev operations from this file and other qede modules: fastpath (`qede_fp.c`), filters/Rx mode/VLAN/ARFS/TC helpers, ethtool, XDP, DCB, RDMA (`qede_rdma.c`), PTP (`qede_ptp.c`), SR-IOV `iov` operations, devlink fatal error reporting, PCI AER, and netdevice notifiers for name/MAC changes.

## Risks
The load/unload and recovery paths are ordering-sensitive. NAPI, IRQs, queue stop, fastpath stop, memory free, and lower-layer callbacks must be sequenced so no completion path touches freed rings. Recovery mode intentionally skips some normal removal steps, so stale `cdev`, devlink, RDMA, and stats state must be carefully reattached. `qede_sp_task()` uses different locking rules for recovery versus other flags; deadlocks are possible around RTNL, SR-IOV disable, and internal locks. Queue count/resource calculations must match allocated netdev queues and MSI-X vectors. Tx timeout handling reports diagnostics and schedules hardware error work only for PFs, so VF behavior depends on PF recovery. PTP is disabled after RDMA removal and before lower-layer remove; work cancellation must prevent timestamp work from using a stopped device.

## Test Signals
Build coverage should include PF, VF, SR-IOV, XDP-capable VF, DCB, ARFS, TC flower, and devlink configurations. Runtime signals include successful probe/remove loops, open/close/reload stress, queue count changes, link up/down callbacks, SR-IOV VF configuration, mqprio/flower offload operations, XDP attach/detach and traffic, PTP enable/disable, RDMA driver registration, PCI AER simulation, firmware recovery, Tx timeout handling, and no use-after-free under concurrent netdev notifier, close, and recovery events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ptp.c

## Purpose
This file implements qede hardware timestamping and PHC support. It wraps the lower-layer `qed_eth_ptp_ops` in Linux PTP clock, hwtstamp ioctl, cyclecounter/timecounter, Tx timestamp work, and Rx timestamp attachment APIs used by the fastpath.

## Important APIs, Types, and Functions
The private `struct qede_ptp` stores `qed_eth_ptp_ops`, `ptp_clock_info`, `cyclecounter`, `timecounter`, registered `ptp_clock`, Tx timestamp work, one pending Tx skb, timestamp filter settings, and a spinlock protecting PTP hardware operations and timecounter state.

PHC callbacks are `qede_ptp_adjfine()`, `qede_ptp_adjtime()`, `qede_ptp_gettime()`, `qede_ptp_settime()`, and `qede_ptp_ancillary_feature_enable()`. Netdev timestamp APIs are `qede_hwtstamp_set()`, `qede_hwtstamp_get()`, and `qede_ptp_get_ts_info()`. Lifecycle/data-path APIs are `qede_ptp_enable()`, `qede_ptp_disable()`, `qede_ptp_tx_ts()`, and `qede_ptp_rx_ts()`.

## Control Flow
PTP enable allocates `struct qede_ptp`, binds it to `edev`, validates `edev->ops->ptp`, enables PTP in hardware, initializes Tx timestamp work, initializes a 64-bit cyclecounter/timecounter seeded with real time, configures any prior filters, fills `ptp_clock_info`, and registers the PHC. PTP disable unregisters the clock, cancels Tx timestamp work, frees any held Tx skb, clears the in-progress bit, disables hardware PTP, frees state, and clears `edev->ptp`.

`qede_hwtstamp_set()` requires the netdev to be running, rejects unsupported Tx modes, records requested Tx/Rx filters, calls `qede_ptp_cfg_filters()`, and returns the normalized Rx filter to the caller. Filter configuration maps Linux `HWTSTAMP_FILTER_*` values to qed firmware filter enums, normalizes narrow sync/delay filters to event filters, updates `QEDE_FLAGS_TX_TIMESTAMPING_EN`, and serializes the hardware call with the PTP spinlock.

Tx timestamping is single-outstanding. `qede_ptp_tx_ts()` is called from `qede_start_xmit()` for `SKBTX_HW_TSTAMP` skbs, sets `SKBTX_IN_PROGRESS`, takes an skb reference, records `jiffies`, and schedules work. `qede_ptp_task()` polls `read_tx_ts()` until a timestamp is available or a two-second timeout expires, then converts cycles through the timecounter, reports the timestamp with `skb_tstamp_tx()`, frees the held skb, and clears the in-progress bit. Rx timestamping is called from Rx CQE processing when the hardware records a timestamp for a timesync packet; it reads hardware Rx cycles, converts to ns, and writes `skb_hwtstamps(skb)->hwtstamp`.

## State and Persistence Behavior
PTP state is in-memory and bound to the PF netdev lifetime. Timestamp configuration (`tx_type`, `rx_filter`, `hw_ts_ioctl_called`) persists across filter reconfiguration while `edev->ptp` exists, but not across full driver removal. `timecounter` state persists across PHC reads and software time adjustments; frequency adjustment is delegated to hardware through `adjfreq`. `edev->ptp_skip_txts` records skipped or timed-out Tx timestamp requests and is reported through qede statistics.

## Dependencies and Integration Points
The file depends on Linux PHC/PTP, `net_tstamp`, `timecounter`, skb timestamp APIs, qede device locking, and `qed_eth_ptp_ops` methods: `enable`, `disable`, `read_cc`, `adjfreq`, `cfg_filters`, `read_tx_ts`, and `read_rx_ts`. It integrates with `qede_main.c` for PF-only enable/disable and netdev hwtstamp operations, and with `qede_fp.c` for Tx and Rx timestamp data-path calls.

## Risks
The PTP spinlock serializes hardware PTP operations and timecounter access, so long-running lower-layer operations under the spinlock would affect softirq latency. Tx timestamp work reschedules immediately while waiting for hardware, which can churn workqueue CPU until timeout. Only one Tx timestamp can be in progress, so concurrent requests are skipped. `qede_ptp_adjfine()` refuses to operate unless the interface is open, but other PHC operations mostly manipulate software timecounter state independent of netdev state. Filter normalization must remain aligned with firmware capabilities or users may see broader timestamping than requested. Disable ordering must cancel work after Tx queues are drained to avoid new scheduling while freeing `ptp`.

## Test Signals
Test with `ethtool -T`, `SIOCSHWTSTAMP`/netlink hwtstamp set/get, PHC reads and adjustments, `phc2sys`/`ptp4l`, Tx timestamp bursts, Rx PTP event traffic for v1/v2 L2 and UDP filters, interface close while timestamps are pending, driver remove/reprobe, and firmware paths where Tx timestamp read times out. Check `ptp_skip_txts`, no lingering `QEDE_FLAGS_PTP_TX_IN_PRORGESS`, valid PHC index, and no use-after-free after PTP disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ptp.h

## Purpose
This header exposes qede PTP and hardware timestamping entry points to the rest of the qede driver and provides the inline Rx CQE timestamp gate used by the fastpath.

## Important APIs, Types, and Functions
The header includes Linux PTP, net timestamp, and timecounter interfaces plus `qede.h`. It declares `qede_ptp_rx_ts()`, `qede_ptp_tx_ts()`, `qede_hwtstamp_get()`, `qede_hwtstamp_set()`, `qede_ptp_disable()`, `qede_ptp_enable()`, and `qede_ptp_get_ts_info()`.

The inline `qede_ptp_record_rx_ts()` checks the Rx CQE parsing flags. If `TIMESTAMPRECORDED` is set and `TIMESYNCPKT` is also set, it calls `qede_ptp_rx_ts(edev, skb)`. If hardware recorded a timestamp for a non-PTP packet, it emits an informational diagnostic instead of attaching a timestamp.

## Control Flow
Receive processing in `qede_fp.c` calls `qede_ptp_record_rx_ts()` after skb protocol/hash/checksum metadata is prepared and before passing the skb to the stack. The inline function makes the fastpath cheap when no timestamp bit is present and delegates all timestamp conversion and skb hwtstamp mutation to `qede_ptp.c`.

## State and Persistence Behavior
The header owns no storage. Its inline helper reads CQE flags and may cause `qede_ptp_rx_ts()` to mutate skb timestamp metadata. PTP lifecycle and filter state live in the `struct qede_ptp` implementation hidden in `qede_ptp.c`.

## Dependencies and Integration Points
It depends on firmware CQE bit definitions such as `PARSING_AND_ERR_FLAGS_TIMESTAMPRECORDED_SHIFT` and `PARSING_AND_ERR_FLAGS_TIMESYNCPKT_SHIFT`, qede logging macros, and skb/netdev types from `qede.h`. It integrates fastpath Rx processing with the PTP implementation without exposing the private `struct qede_ptp` layout.

## Risks
The inline assumes CQE parsing flags are valid for the regular fast-path CQE form passed by the caller. A mismatch in firmware flag definitions would either miss timestamps or call into PTP for non-timesync traffic. Logging for unexpected non-PTP timestamps happens in the Rx path, so repeated firmware anomalies could add log noise under traffic.

## Test Signals
Compile coverage should verify all qede objects that include the header see the needed PTP and CQE types. Runtime signals are Rx PTP packets acquiring hardware timestamps, ordinary packets not being timestamped, and the informational path triggering only when hardware sets timestamp-recorded without the timesync packet bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_rdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_rdma.c

## Purpose
This file implements the glue between the Ethernet qede driver and the separate qedr RDMA driver. It tracks RDMA-capable qede devices, lets the qedr module register/unregister callbacks, creates a per-device workqueue for asynchronous RDMA notifications, and forwards qede netdev lifecycle events such as up/down/close/MAC change/MTU change to qedr.

## Important APIs, Types, and Functions
Global state is `qedr_drv`, `qedr_dev_list`, and `qedr_dev_list_lock`. Per-device state is under `edev->rdma_info`, including list entry, `qedr_dev`, workqueue, event list, kref, completion, and `exp_recovery`.

Driver-facing exported APIs are `qede_rdma_register_driver()` and `qede_rdma_unregister_driver()`. qede lifecycle APIs are `qede_rdma_supported()`, `qede_rdma_dev_add()`, `qede_rdma_dev_remove()`, `qede_rdma_dev_event_open()`, `qede_rdma_dev_event_close()`, `qede_rdma_event_changeaddr()`, and `qede_rdma_event_change_mtu()`. Internal helpers dispatch add/remove/open/close/shutdown/change notifications and manage queued `struct qede_rdma_event_work` nodes.

## Control Flow
When qede probes a supported device, `qede_rdma_dev_add()` creates a single-thread RDMA workqueue, initializes event tracking, adds the device to the global list, and calls the currently registered qedr driver's `add()` callback if present. During normal removal, qede destroys the event workqueue, removes the qedr device unless recovery already did so, clears `qedr_dev`, and deletes the list entry. Recovery removal avoids full workqueue teardown and marks `exp_recovery` to suppress later event enqueueing.

When qedr registers, it becomes the singleton `qedr_drv`, and every qede device already on the list is added to qedr; devices whose netdev is running and operational also receive `QEDE_UP`. When qedr unregisters, each attached non-recovery device is removed and the singleton pointer is cleared.

Asynchronous events are added with `qede_rdma_add_event()`. It rejects recovery and missing-device cases, takes a kref unless destruction has begun, reuses an idle event node or allocates one with `GFP_ATOMIC`, initializes work, queues it to the per-device workqueue, and drops the kref. The work handler maps event enums to the appropriate qedr `notify()` calls.

## State and Persistence Behavior
State is in-memory only. The global driver pointer and device list persist while modules are loaded. Per-device work nodes remain on `rdma_event_list` and are reused when not pending. `kref` and `event_comp` coordinate workqueue destruction with concurrent event creation. `exp_recovery` records that expected recovery is in progress and suppresses events or duplicate qedr removal.

## Dependencies and Integration Points
It depends on `linux/qed/qede_rdma.h` for `struct qedr_driver` and event enums, qede device state, netdev operational state, workqueues, lists, mutexes, krefs, and completions. It is called from qede probe/remove, link open/close updates, netdev MAC change notifier, and MTU change paths. It exports registration symbols for the qedr module.

## Risks
The main risks are concurrency and lifetime errors between qede removal, queued RDMA events, and qedr unregister. Event nodes are reused based on `work_pending()`, so correctness relies on the single-thread workqueue and cleanup flushing before freeing nodes. Recovery mode intentionally skips some normal teardown; wrong `exp_recovery` transitions could either leak qedr devices or notify a partially removed qedr instance. Global list operations are protected by one mutex, but event enqueue uses per-device fields outside that mutex and depends on kref destruction coordination.

## Test Signals
Test RDMA-capable and non-RDMA hardware paths, qede probe before and after qedr module load, qedr unload while qede devices exist, interface up/down/link changes, MAC and MTU changes, normal remove, and firmware recovery. Useful signals include correct qedr add/remove/notify counts, no events after workqueue destruction, no list corruption, no use-after-free during concurrent unregister and netdev close, and no RDMA actions for unsupported devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qla3xxx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qla3xxx.c

## Purpose
This file is the complete legacy QLogic ISP3XXX Ethernet PCI driver. It handles PCI probe/remove, netdev and ethtool operations, EEPROM/NVRAM reading, PHY/PETBI initialization and link state management, DMA queue allocation, Tx/Rx datapath processing, NAPI and interrupt handling, MSI option handling, timers, reset work, and adapter up/down transitions for QLA3022/QLA3032 devices.

## Important APIs, Types, and Functions
Important driver state is `struct ql3_adapter` from `qla3xxx.h`, including MMIO registers, locks, flags, NVRAM data, PHY identity, request/response queues, large/small Rx buffer queues, Tx control blocks, NAPI, workqueue, and timer state. Module parameters are `debug` and `msi`. Device binding is through `ql3xxx_pci_tbl`, `ql3xxx_driver`, `ql3xxx_probe()`, and `ql3xxx_remove()`.

Important hardware helpers include semaphore/register accessors `ql_sem_spinlock()`, `ql_sem_lock()`, `ql_set_register_page()`, `ql_read_*()`, and `ql_write_*()`. EEPROM and PHY helpers include `ql_get_nvram_params()`, `eeprom_readword()`, MII read/write helpers, `PHY_Setup()`, PETBI and PHY negotiation functions, and `ql_link_state_machine_work()`. Data path functions include `ql3xxx_send()`, `ql_send_map()`, `ql_process_mac_tx_intr()`, `ql_process_mac_rx_intr()`, `ql_process_macip_rx_intr()`, `ql_tx_rx_clean()`, `ql_poll()`, and `ql3xxx_isr()`. Resource/lifecycle functions include `ql_alloc_mem_resources()`, `ql_free_mem_resources()`, `ql_adapter_initialize()`, `ql_adapter_reset()`, `ql_adapter_up()`, `ql_adapter_down()`, `ql_cycle_adapter()`, `ql3xxx_open()`, `ql3xxx_close()`, and reset/timeout work handlers.

## Control Flow
Probe enables PCI, requests regions, sets 64-bit DMA, allocates a netdev, maps BAR registers, initializes locks and NAPI, reads and validates NVRAM checksum, chooses MAC/PHY information, sets MTU and MAC from NVRAM, configures netdev features for QL3032 checksum/SG support, registers the netdev, creates a single-thread workqueue, initializes reset/timeout/link delayed work and the adapter timer, and prints device information.

Opening the device calls `ql_adapter_up()`: memory resources are allocated, MSI may be enabled, IRQ is requested, the driver hardware semaphore is acquired, `ql_adapter_initialize()` programs queues, shadow producer/consumer addresses, buffer queues, frame size, NVRAM-driven local RAM parameters, PHY/MAC settings, and function enable bits, then NAPI and interrupts are enabled and the link timer starts. Closing calls `ql_adapter_down()`: queue and carrier are stopped, interrupts and IRQ/MSI are disabled, timer and NAPI are stopped, optional chip reset is attempted under hardware lock, and all DMA resources are freed.

Transmit uses `ql3xxx_send()`. It reserves a Tx control block, calculates segment count, fills an outbound MAC IOCB, optionally enables QL3032 checksum offload, maps skb linear data and fragments through `ql_send_map()` into IOCB/OAL address lists, advances the request producer, writes the producer register, and decrements the atomic Tx credit count. Tx completions in `ql_process_mac_tx_intr()` unmap DMA segments, update stats, free the skb, and return a Tx credit.

Receive completions are pulled from the response queue in NAPI. `ql_tx_rx_clean()` decodes response opcodes, handles Tx completions, MAC Rx, and IP Rx. Rx handlers consume small/large buffer indices, unmap the selected skb buffer, adjust or copy headers for QL3022 two-buffer completions, apply QL3032 checksum status, set protocol, submit through `napi_gro_receive()`, update stats, and release buffer controls back to free lists. `ql_poll()` updates small/large buffer queue producer registers and the response consumer register before re-enabling interrupts.

The ISR handles fatal error/reset indications by stopping queue/carrier, disabling interrupts, setting reset flags, and queueing reset work; normal completion interrupts disable interrupts and schedule NAPI. The adapter timer queues link-state work, which polls hardware link state, drives PHY/PETBI autonegotiation, configures MAC speed/duplex/pause when link comes up, and restarts itself.

## State and Persistence Behavior
The driver keeps all operational state in `struct ql3_adapter`: hardware page selection, flags (`QL_ADAPTER_UP`, reset bits, MSI, link master/optical), NVRAM image, queue indices, DMA addresses, skb ownership, Tx credits, link state, and work/timer objects. Persistent device configuration is read from EEPROM/NVRAM but not written by this file. DMA-coherent queues, shadow registers, small buffers, large skb buffers, and Tx OAL lists are allocated on open and freed on close or remove.

## Dependencies and Integration Points
It depends on PCI, DMA mapping, MMIO, netdev, NAPI, ethtool, skbuff, timer/workqueue, spinlock, and mii/link constants. It integrates with hardware-specific register and descriptor definitions in `qla3xxx.h`, Linux ethtool link settings, netdev start/stop/xmit/timeout operations, and optional MSI. The qla3xxx device is standalone and does not use the qede/qed split architecture.

## Risks
The driver has many ordering-sensitive hardware interactions: semaphore acquisition, register page selection, firmware reset bits, queue producer/consumer writes, and MII scan enable/disable must remain serialized under the expected locks. Tx/Rx DMA cleanup is complex, especially QL3032 outbound address list continuation entries and QL3022 two-buffer Rx headers. Reset work frees outstanding skb mappings while the device is being cycled; races with close/remove or IRQ/NAPI would be severe. The cleanup path in `ql_send_map()` contains a suspicious final `dma_unmap_single()` argument using a mapped address where a length is expected, making DMA API debug especially important around map-failure injection. Remove cancels delayed work without `cancel_delayed_work_sync()` and destroys the workqueue, so pending timer/link work ordering deserves scrutiny. NVRAM checksum, PHY identification, and supported MTU assumptions can prevent device bring-up or misconfigure link.

## Test Signals
Test probe/remove, open/close loops, MSI and shared-IRQ modes, normal and jumbo MTUs, QL3022 and QL3032 hardware, checksum offload, scatter/gather Tx with many fragments, NAPI budget limits, link up/down/autonegotiation for copper and optical, EEPROM checksum failure handling, Tx timeout recovery, fatal error/reset interrupts, concurrent close during reset work, and DMA mapping failure injection. Useful kernel signals include DMA API debug, lockdep around hardware locks and workqueue paths, no leaked skbs or coherent DMA allocations after close, accurate ethtool link settings, and stable netdev stats under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qla3xxx.c -->
