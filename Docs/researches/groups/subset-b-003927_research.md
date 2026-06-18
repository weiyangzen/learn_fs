# subset-b-003927 research

Grouped research for HFI1 IPoIB, netdev RX, MSI-X, MMU notifier, OPFN, and MAD management files under `sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_main.c

## Purpose
`ipoib_main.c` wires HFI1 accelerated IP-over-InfiniBand support into the RDMA netdev allocation path. It wraps the generic IPoIB netdev operations with HFI1-specific transmit, receive, multicast, queue, and QP bookkeeping so an `RDMA_NETDEV_IPOIB` device can use HFI1 SDMA and receive contexts.

## Important APIs, types, and functions
- `qpn_from_mac()` derives the local QPN from the IPoIB MAC address bytes 1..3.
- `hfi1_ipoib_dev_init()` and `hfi1_ipoib_dev_uninit()` delegate to the original netdev ops and register or remove the netdev in `dd->netdev_rx->dev_tbl` by QPN.
- `hfi1_ipoib_dev_open()` opens the underlying IPoIB device, looks up the matching rdmavt QP under RCU, pins it in `priv->qp`, then enables HFI1 RX queues and TX NAPI.
- `hfi1_ipoib_dev_stop()` disables TX NAPI and RX queues, drops the QP reference, and calls the original `ndo_stop`.
- `hfi1_ipoib_mcast_attach()` and `hfi1_ipoib_mcast_detach()` locate the QP and call `ib_attach_mcast()` or `ib_detach_mcast()`.
- `hfi1_ipoib_setup_rn()` fills `struct rdma_netdev` callbacks, initializes `struct hfi1_ipoib_dev_priv`, allocates TX and RX resources, and replaces `netdev->netdev_ops`.
- `hfi1_ipoib_rn_get_params()` is the exported capability hook used by the RDMA core to request HFI1 accelerated IPoIB parameters.

## Control flow
The RDMA core calls `hfi1_ipoib_rn_get_params()` for `RDMA_NETDEV_IPOIB`. The function rejects unsupported netdev types, disabled AIP capability, devices without netdev receive contexts, and invalid ports. It then reports private-data size, TX queue count from `dd->num_sdma`, RX queue count from `dd->num_netdev_contexts`, and `hfi1_ipoib_setup_rn()` as the initializer.

During netdev setup, the file preserves the original IPoIB `netdev_ops` in `priv->netdev_ops`, installs HFI1 send, multicast, timeout, and P_Key callbacks in `struct rdma_netdev`, initializes TX request rings first, initializes the accelerated RX path second, and finally substitutes a small HFI1 `net_device_ops` wrapper. Open and stop are symmetric around the QP reference and queue enable state: the original IPoIB open must succeed before HFI1 looks up the QP, and a failed QP lookup unwinds by stopping the original netdev.

## State and persistence
The main persistent in-memory state is `struct hfi1_ipoib_dev_priv`: original netdev ops, device/port pointers, P_Key state, Q_Key, QP reference, and TX/RX resources. The QPN-to-netdev xarray entry in `netdev_rx` is created at `ndo_init` and erased at `ndo_uninit`, so receive demultiplexing depends on the MAC-derived QPN remaining stable. No state is persisted across driver unload or reboot.

## Dependencies and integration points
This file integrates with RDMA netdev allocation, generic IPoIB netdev callbacks, rdmavt QP lookup/reference APIs, HFI1 netdev RX helpers, HFI1 IPoIB TX/RX helpers, multicast verbs, and P_Key queries. It assumes HFI1 AIP capability and receive contexts were configured by broader device initialization.

## Risks
- MAC-derived QPN mapping is central to RX demultiplexing; MAC address changes after registration would need careful synchronization with `dev_tbl`.
- `hfi1_ipoib_dev_stop()` returns early when `priv->qp` is NULL, so callers rely on the failed-open path having already stopped the original netdev.
- Multicast attach/detach and open independently look up the QP; races with QP teardown depend on correct RCU and rdmavt reference behavior.
- Setup changes `netdev->netdev_ops` only after TX/RX initialization; future initialization changes must preserve this unwind ordering.

## Test signals
- Build with HFI1 AIP/IPoIB enabled and verify `hfi1_ipoib_rn_get_params()` rejects non-IPoIB types, disabled AIP, zero netdev contexts, and invalid ports.
- Exercise interface open/close, including failed QP lookup, and confirm RX queues, TX NAPI, and QP references are balanced.
- Validate VLAN or child IPoIB devices that depend on QPN registration in `hfi1_netdev_add_data()`.
- Test multicast join/leave paths with valid and missing QPs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_rx.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_rx.c

## Purpose
`ipoib_rx.c` converts HFI1 accelerated IPoIB receive buffers into Linux `sk_buff`s and connects IPoIB RX initialization to the shared HFI1 netdev receive-context layer. It is intentionally small: packet demultiplexing and receive-context polling live elsewhere, while this file handles SKB preparation and IPoIB-specific RSM setup.

## Important APIs, types, and functions
- `copy_ipoib_buf()` copies the received IPoIB buffer into an SKB, sets checksum state, initializes protocol from the packet data, sets `mac_header`, and pulls the IPoIB encapsulation header.
- `prepare_frag_skb()` allocates large packets from NAPI fragment cache with `napi_alloc_frag()` and wraps them with `build_skb()`, falling back to `napi_alloc_skb()` only when fragment allocation fails.
- `hfi1_ipoib_prepare_skb()` chooses small SKB allocation versus fragment-backed allocation, then calls `copy_ipoib_buf()`.
- `hfi1_ipoib_rxq_init()` increments or creates HFI1 netdev RX queues through `hfi1_netdev_rx_init()` and programs AIP receive-side mapping through `hfi1_init_aip_rsm()`.
- `hfi1_ipoib_rxq_deinit()` reverses that order with `hfi1_deinit_aip_rsm()` and `hfi1_netdev_rx_destroy()`.

## Control flow
Receive polling code calls `hfi1_ipoib_prepare_skb()` with a receive queue, payload size, and source data pointer. The function accounts for `HFI1_IPOIB_ENCAP_LEN`, uses normal NAPI SKB allocation for packets that fit in a page-sized SKB, and uses a fragment-backed SKB for larger packets. After allocation, it copies data, marks the checksum as none, sets the packet protocol from the leading bytes, and strips the encapsulation header before handing the SKB to the network stack.

Initialization is tied to netdev creation in `ipoib_main.c`: RX queues are initialized before the HFI1 netdev ops are exposed, and deinitialized by the netdev destructor. Shared receive queues are reference-counted by `netdev_rx.c`; this file adds the IPoIB-specific RSM programming around that shared lifetime.

## State and persistence
This file does not own long-lived state beyond the NAPI allocation behavior. It relies on `struct hfi1_netdev_rxq` for the NAPI instance and on `struct hfi1_ipoib_dev_priv` for the device pointer. AIP RSM hardware state is programmed on init and cleared on deinit; there is no persistence outside device runtime.

## Dependencies and integration points
The code uses Linux SKB/NAPI allocation APIs, HFI1 IPoIB constants from `ipoib.h`, shared HFI1 netdev RX setup from `netdev.h`, and hardware RSM helpers `hfi1_init_aip_rsm()` and `hfi1_deinit_aip_rsm()`.

## Risks
- `copy_ipoib_buf()` reads the protocol from the beginning of `data`; callers must guarantee at least the encapsulation header is present and aligned enough for the cast.
- Large receive allocation uses fragment cache sizing that includes SKB shared info; off-by-one sizing would corrupt SKB metadata.
- RX init programs AIP RSM after netdev RX allocation. If RSM setup can fail in future, the function would need an unwind path because it currently returns the RX init status only.

## Test signals
- Exercise small and large IPoIB receives through NAPI and verify protocol, header offsets, packet length, and checksum state.
- Inject allocation failures for `napi_alloc_frag()`, `build_skb()`, and `napi_alloc_skb()` to confirm null handling.
- Open and destroy multiple IPoIB netdevs to verify shared RX queue reference counting and AIP RSM init/deinit balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_tx.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_tx.c

## Purpose
`ipoib_tx.c` implements HFI1 accelerated IPoIB transmit over SDMA. It owns per-netdev TX queues, circular request rings, SDMA descriptor construction, IB 9B UD header construction, xmit-more batching, NAPI completion cleanup, SDMA descriptor starvation sleep/wakeup handling, queue stop/wake thresholds, and timeout diagnostics.

## Important APIs, types, and functions
- `struct ipoib_txparms` collects per-packet transmit context: HFI device, AH attributes, port, TX queue, flow tuple, destination QPN, header size, and entropy.
- Circular ring helpers `hfi1_txreq_from_idx()`, `hfi1_ipoib_used()`, `hfi1_ipoib_ring_hwat()`, and `hfi1_ipoib_ring_lwat()` manage `struct hfi1_ipoib_circ_buf`.
- Queue control helpers `hfi1_ipoib_stop_txq()`, `hfi1_ipoib_wake_txq()`, `hfi1_ipoib_check_queue_depth()`, and `hfi1_ipoib_check_queue_stopped()` coordinate netdev subqueue state with ring fullness and descriptor starvation counters.
- `hfi1_ipoib_build_ib_tx_headers()` creates LRH/GRH/BTH/DETH headers and PBC for UD SEND_ONLY packets, including P_Key, Q_Key, PSN, SL-to-SC mapping, VL mapping, entropy, and source QPN.
- `hfi1_ipoib_build_tx_desc()` and `hfi1_ipoib_build_ulp_payload()` initialize SDMA descriptors for PBC/header plus SKB linear and paged payload.
- `hfi1_ipoib_send_dma_single()` and `hfi1_ipoib_send_dma_list()` submit one TX request or batch a list for `netdev_xmit_more()`.
- `hfi1_ipoib_sdma_sleep()`, `hfi1_ipoib_sdma_wakeup()`, and `hfi1_ipoib_flush_txq()` integrate the TX queue with SDMA iowait.
- `hfi1_ipoib_txreq_init()`, `hfi1_ipoib_txreq_deinit()`, `hfi1_ipoib_napi_tx_enable()`, and `hfi1_ipoib_napi_tx_disable()` own lifetime.

## Control flow
The netdev send path enters `hfi1_ipoib_send()`, rejects packets larger than the RDMA netdev MTU plus IPoIB encapsulation, builds `ipoib_txparms` from the address handle and SKB queue mapping, derives the service channel from `ibp->sl_to_sc`, and chooses list or single submission based on `netdev_xmit_more()` and whether a batch is already pending.

Both submit paths call `hfi1_ipoib_send_dma_common()`. That routine reserves a ring slot, initializes an `ipoib_txreq`, builds headers, builds SDMA descriptors, and switches SDMA engine when the flow changes. The single path advances the ring tail and calls `sdma_send_txreq()`. The list path flushes any pending list before a flow change, appends the descriptor to `tx_list`, advances the ring, and flushes only when the networking stack stops batching.

SDMA completion calls `hfi1_ipoib_sdma_complete()`, stores status, marks the TX request complete with release semantics, and schedules TX NAPI. `hfi1_ipoib_poll_tx_ring()` consumes completed entries in order, frees SKBs, cleans SDMA descriptors, advances the ring head with release semantics, updates completion counters, and wakes stopped queues when below the low-water mark.

## State and persistence
Each `struct hfi1_ipoib_txq` stores a ring, pending SDMA list, iowait object, current flow, selected SDMA engine, NAPI object, queue index, and counters. Request lifetime is ring-based: SKBs and descriptors are attached at tail reservation, completed by SDMA callback, then freed by NAPI from head order. Atomic fields `stops`, `ring_full`, and `no_desc` allow independent stop reasons. There is no persistent state beyond runtime memory and hardware descriptor submission.

## Dependencies and integration points
The file depends on Linux netdev multiqueue/NAPI APIs, SKB fragment APIs, HFI1 SDMA APIs, rdmavt AH/QP structures, HFI1 header/PBC helpers, tracepoints, SL-to-SC and SC-to-VL mappings, and iowait scheduling. It is invoked through `struct rdma_netdev.send` installed by `ipoib_main.c`.

## Risks
- Ring correctness depends on paired release/acquire operations between SDMA completion, TX NAPI, and tail/head updates.
- Queue stop/wake uses multiple atomic stop reasons; missed balancing can leave a subqueue permanently stopped or prematurely woken.
- Flow changes force list flushes. Errors during flush drop the current SKB and may leave queued descriptors for later cleanup.
- SDMA `-EBUSY` and `-ECOMM` are treated as accepted/queued conditions; other errors mark the request complete and rely on NAPI cleanup.
- The local source contains duplicated declarations in `hfi1_ipoib_send_dma_common()` and `hfi1_ipoib_sdma_sleep()` (`u32 head;` and duplicate `container_of` assignment). If this exact tree is compiled, those are build-breaking C errors and should be caught by the build.

## Test signals
- Compile HFI1 IPoIB TX to catch API drift and the duplicated declarations noted above.
- Stress multiqueue transmit with varying `tx_queue_len`, `netdev_xmit_more()` batching, flow changes, and SDMA engine selection.
- Force SDMA descriptor starvation to validate `hfi1_ipoib_sdma_sleep()`, iowait queueing, flush work, and queue wakeup.
- Inject SDMA completion errors and verify SKB freeing, netdev stats, NAPI completion, and timeout diagnostics.
- Exercise GRH and non-GRH address handles, P_Key/Q_Key changes, SL-to-SC changes, and MTU oversize drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mad.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mad.c

## Purpose
`mad.c` is the HFI1 management datagram implementation. It handles OPA and legacy IB Subnet Management Agent and Performance Management Agent requests, reports and mutates port state, validates management keys and P_Keys, manages traps, exposes counters and error info, programs fabric-management tables, and applies congestion-control state.

## Important APIs, types, and functions
- Trap support centers on `struct trap_node`, `send_trap()`, `check_and_add_trap()`, `hfi1_handle_trap_timer()`, `subn_handle_opa_trap_repress()`, and event helpers such as `hfi1_bad_pkey()`, `hfi1_cap_mask_chg()`, `hfi1_sys_guid_chg()`, and `hfi1_node_desc_chg()`.
- SMA validation and dispatch use `check_mkey()`, `process_subn_opa()`, `process_subn()`, `subn_get_opa_sma()`, `subn_set_opa_sma()`, aggregate handlers, and length/status helpers.
- Port state and configuration are served by `__subn_get_opa_portinfo()`, `__subn_set_opa_portinfo()`, `__subn_get_opa_psi()`, `__subn_set_opa_psi()`, transition tables, and `set_port_states()`.
- Fabric tables include P_Key table handlers, SL-to-SC, SC-to-SL, SC-to-VL transmit/non-transmit mappings, buffer control, VL arbitration, cable info, LED info, and link-width/speed setters.
- PMA support includes OPA port status, data counters, error counters, error info, clear operations, and legacy IB `PortCounters` and `PortCountersExt` compatibility.
- Congestion control uses `struct cc_state`, `apply_cc_state()`, congestion setting/table get/set handlers, and HFI congestion log extraction.
- `hfi1_process_mad()` is the exported entry point called by the MAD core and dispatches by base version to OPA or IB processing.

## Control flow
Incoming MADs enter `hfi1_process_mad()`. OPA packets go through `hfi1_process_opa_mad()`, which selects the limited management P_Key for replies, identifies local SMPs, applies local SMP P_Key checks, and dispatches subnet or performance classes. IB-format packets go through the smaller `hfi1_process_ib_mad()` path, which supports legacy node info and performance counters.

OPA subnet processing copies the request to the response buffer, validates class version and M_Key, sets the response length to the OPA SMP header, and dispatches GET, SET, TRAP_REPRESS, or pass-through response methods. GET usually clears the SMP data area before filling the requested attribute. SET mutates driver or hardware state, then often calls the corresponding GET handler to return current state. Aggregate GET/SET iterates nested attributes inside one SMP and flags segment-level errors.

PMA processing validates class version and attribute modifiers, checks selected port and VL masks, computes response sizes with flexible-array helpers, reads HFI1 device and port counters, converts transmit-wait counters from TXE cycles to flit times, and clears selected counters on SET clear requests. Trap flow creates notice payloads, queues by priority, rate-limits list length, sends through QP0 via the MAD send agent, and honors trap repress messages.

## State and persistence
The file mutates substantial runtime and hardware state: port LID/LMC, SM LID/SL/AH, M_Key and lease timers, subnet timeout, link width/speed enable masks, link state, partition enforcement and P_Key tables, MTUs per VL, operational VLs, SC/VL/SL tables, buffer-control and VL-arbitration tables, congestion-control shadows, LED override state, counters, and cached LCB read values. Trap state is held in `ibp->rvp.trap_lists`, trap timer, TIDs, and send-agent AH. Congestion-control active state is RCU-protected and replaced atomically after updates.

Most state is not persistent across reset, but many writes program hardware CSRs or fabric-manager tables and therefore affect live link behavior immediately. Several counters are cumulative until explicitly cleared or link-up reset paths run.

## Dependencies and integration points
`mad.c` integrates with the RDMA MAD core, rdmavt port/QP/AH state, HFI1 port and device counter APIs, HFI1 link-state control, P_Key helpers, fabric-manager table helpers, cable EEPROM access, LED override, event dispatch, tracepoints, RCU, timers, spinlocks, and hardware CSR access. It consumes OPA definitions from RDMA headers and local compatibility/header files.

## Risks
- This is a high-blast-radius management path: invalid SET handling can bounce links, change partitioning, alter VL mappings, or clear counters.
- M_Key and P_Key validation are security-sensitive, especially the difference between local SMPs, limited management P_Key, and full management P_Key.
- Flexible response sizes for OPA PMA and aggregate attributes must stay within MAD data buffers.
- Trap lifetime crosses timers, send buffers, repress messages, and port-down cleanup; list and `in_use` state must remain consistent.
- Counter conversion keeps previous samples in `ppd`; link-width changes, counter wraps, and clear operations must keep derived flit counters coherent.
- Congestion-control state uses RCU replacement and spinlock-protected staging; readers and writers must preserve the lock/RCU contract.

## Test signals
- Compile with RDMA MAD, OPA, HFI1, and rdmavt enabled, plus sparse/smatch for endian, bounds, and flexible-array checks.
- Unit or hardware tests should cover M_Key failures, lease timeout, bad P_Key traps, trap repress, port-down trap cleanup, and local versus remote SMP P_Key rules.
- Fabric-manager tests should exercise PortInfo/PSI state transitions, LID/SM changes, MTU/VL changes, P_Key updates with and without limited management P_Key, and SC/VL table restrictions while Armed or Active.
- PMA tests should verify response sizing, selected port/VL masks, counter saturation, clear masks, link-width conversion, A0/BX differences, and legacy IB counter compatibility.
- Congestion tests should validate setting congestion settings and CCT blocks, reading logs, RCU state replacement, and log reset-on-read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mad.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mad.h

## Purpose
`mad.h` defines HFI1's local OPA MAD data structures, attribute IDs, trap payloads, congestion-control layouts, buffer-control layouts, counter conversion helpers, and function prototypes used by `mad.c` and other HFI1 code. It bridges OPA management definitions not fully represented by generic RDMA headers.

## Important APIs, types, and functions
- OPA trap constants identify GID, multicast, port-state, link-integrity, capability, system GUID, M_Key, P_Key, Q_Key, switch bad P_Key, and link-width downgrade notices.
- `struct opa_mad_notice_attr` models the notice payload union for multiple trap types.
- `struct ib_pma_portcounters_cong` provides an IB PMA congestion counter layout.
- Congestion data types include HFI congestion log events, congestion setting attributes and shadows, CCT table attributes and shadows, `struct cc_table_shadow`, and RCU-protected `struct cc_state`.
- Buffer and table types include `struct vl_limit`, `struct buffer_control`, and `struct sc2vlnt`.
- Attribute-modifier macros decode OPA nport, block count, start block, async update, SM config start, cable-info address, and cable-info length fields.
- Inline helpers `get_link_speed()` and `convert_xmit_counter()` support PMA transmit-wait conversion.
- Prototypes export P_Key change, trap timer, link-width conversion, and transmit-wait counter sampling.

## Control flow
The header has no standalone control flow. Its macros are used by `mad.c` dispatchers to validate and decode `attr_mod`, choose response sizes, convert counter units, and build or parse OPA management payloads. The inline conversion helpers are called by PMA counter reporting paths.

## State and persistence
Most types in this header describe wire-visible management payloads or runtime shadows. `struct cc_state` is explicitly designed as an active, RCU-protected per-port congestion state snapshot, while shadow structures let the driver keep host-endian copies of wire-endian management data. No state is allocated by this header itself.

## Dependencies and integration points
The header includes RDMA PMA, OPA SMI, OPA PortInfo, and local `opa_compat.h`. Its definitions must remain ABI-compatible with OPA management packet layouts because `mad.c` casts MAD payload bytes directly to these packed structures.

## Risks
- Packed structure layout and endian annotations are protocol-critical; field reordering or padding changes would break MAD interoperability.
- Attribute-modifier masks must match OPA bit assignments. Mistakes can make handlers accept invalid requests or reject valid fabric-manager traffic.
- `OPA_AM_CI_ADDR_SMASK` and `OPA_AM_CI_LEN_SMASK` are intended to describe cable-info fields; mask macro correctness should be checked carefully against the OPA definitions because downstream bounds checks rely on decoded address/length.
- Counter conversion uses integer scaling and assumes valid nonzero link width values passed by callers.

## Test signals
- Compile with `BUILD_BUG_ON()` or static assertions around packed structure sizes if adding fields.
- Exercise MAD get/set handlers that use every attribute-modifier macro.
- Validate transmit-wait conversion for 25G and 12.5G speeds, default and downgraded link widths, and zero or unsupported link-width masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mmu_rb.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mmu_rb.c

## Purpose
`mmu_rb.c` implements an interval-tree cache of user memory ranges tied to Linux MMU notifier invalidations. HFI1 users can register nodes representing pinned or cached memory, search and evict them, and receive asynchronous remove callbacks when the process address space invalidates a range.

## Important APIs, types, and functions
- `hfi1_mmu_rb_register()` allocates a cacheline-aligned `struct mmu_rb_handler`, initializes an interval tree, LRU list, delete list, work item, and MMU notifier, then registers against `current->mm`.
- `hfi1_mmu_rb_unregister()` unregisters the notifier, flushes delete work, removes all nodes, invokes remove callbacks, drops the mm reference, and frees the aligned allocation.
- `hfi1_mmu_rb_insert()` inserts a non-overlapping `struct mmu_rb_node` for the registered `mm`, optionally using `ops->filter` for overlap semantics.
- `hfi1_mmu_rb_get_first()` searches for the first overlapping node and refreshes its LRU position.
- `hfi1_mmu_rb_release()` and internal release callbacks move nodes to deferred removal and queue work.
- `hfi1_mmu_rb_evict()` walks LRU nodes with only the handler reference and lets `ops->evict()` select victims.
- `mmu_notifier_range_start()` removes overlapping nodes during invalidation and defers sleeping remove callbacks to `handle_remove()`.

## Control flow
Users register a handler with callbacks and a workqueue. Insert validates that the current process matches the registered `mm`, checks for an existing matching interval, inserts into the cached interval tree, and appends to LRU. Searches require the caller to hold the handler spinlock and return an overlapping node.

On MMU invalidation, the notifier holds the handler lock, iterates all interval-tree nodes overlapping the invalidated range, removes each from the tree and LRU list, and drops its kref with `release_nolock()`. That callback queues the node on `del_list` and schedules `handle_remove()` so `ops->remove()` can sleep outside the notifier and spinlock context.

Unregister prevents future notifications first, flushes delete work, drains the tree under lock into a local list, and calls `ops->remove()` through `release_immediate()` for each remaining node.

## State and persistence
`struct mmu_rb_handler` owns an MMU notifier, spinlock, cached interval tree, LRU list, deferred delete list, workqueue pointer, callback table, callback argument, and original allocation pointer. `struct mmu_rb_node` stores address, length, cached last address, tree node, list node, handler pointer, and kref. State is per-process-mm runtime state and has no persistence beyond handler lifetime.

## Dependencies and integration points
The file depends on Linux `mmu_notifier`, interval tree macros, rb trees, krefs, workqueues, process `mm` lifetime management, spinlocks, and HFI1 tracepoints. Callers provide HFI1-specific memory-cache callbacks through `struct mmu_rb_ops`.

## Risks
- `ops->filter()` and `ops->evict()` must not sleep because they are called under the handler spinlock.
- `ops->remove()` may sleep, so all paths must avoid invoking it under the spinlock or MMU notifier critical section; the deferred delete path enforces this.
- Current-mm checks mean insert/evict from the wrong process silently fail or return `-EPERM`.
- Address arithmetic uses `addr + len - 1` and page alignment; zero lengths or overflowed ranges would be dangerous if callers pass invalid nodes.
- Kref ownership must be consistent between tree references, external users, eviction, invalidation, and unregister.

## Test signals
- Test overlapping insert rejection with and without a filter callback.
- Trigger `munmap()`, process exit, and invalidation while nodes are referenced, confirming deferred remove callbacks run after references drop.
- Exercise unregister with live nodes, queued delete work, and empty trees.
- Stress LRU eviction under concurrent searches and invalidations with lockdep enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mmu_rb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mmu_rb.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mmu_rb.h

## Purpose
`mmu_rb.h` declares the HFI1 MMU notifier interval-tree abstraction. It defines the node, callback contract, handler state, and public functions used by HFI1 memory-registration code to track process virtual address ranges.

## Important APIs, types, and functions
- `struct mmu_rb_node` contains the virtual address range, interval-tree node, owning handler, LRU/delete list linkage, and kref.
- `struct mmu_rb_ops` supplies optional `filter()`, mandatory-style `remove()`, and optional eviction policy callback. The comment states `filter` and `evict` must not sleep; only `remove` may sleep.
- `struct mmu_rb_handler` stores the MMU notifier, spinlock-protected cached rb root, callback context, LRU and delete lists, work item, workqueue, and aligned allocation pointer.
- Public APIs are `hfi1_mmu_rb_register()`, `hfi1_mmu_rb_unregister()`, `hfi1_mmu_rb_insert()`, `hfi1_mmu_rb_release()`, `hfi1_mmu_rb_evict()`, and `hfi1_mmu_rb_get_first()`.

## Control flow
The header establishes the lifecycle: register a handler for the current `mm`, insert initialized nodes, search or evict them under the handler rules, release krefs through `hfi1_mmu_rb_release()`, and unregister to remove all remaining ranges and the notifier.

## State and persistence
All declared state is runtime-only and scoped to one `mmu_rb_handler`. Nodes are caller-allocated objects whose final cleanup is delegated to `ops->remove()`.

## Dependencies and integration points
The header includes `hfi.h`, which provides kernel and HFI1 context. The implementation integrates with Linux MMU notifiers, rb trees, lists, krefs, and HFI1 memory-cache users.

## Risks
- Callers must obey locking comments: `hfi1_mmu_rb_get_first()` requires the handler lock, while `hfi1_mmu_rb_release()` must not be called while already holding it.
- Callback sleepability requirements are part of the ABI and are easy to violate when adding new memory-cache users.
- Node address/length fields must be initialized before insertion and remain stable while in the tree.

## Test signals
- Compile all users after callback signature changes.
- Lockdep tests around search, release, notifier invalidation, and unregister.
- Fault-injection tests for registration allocation failure and MMU notifier registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mmu_rb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/msix.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/msix.c

## Purpose
`msix.c` allocates, requests, maps, frees, and synchronizes HFI1 MSI-X interrupt vectors. It covers general device interrupts, SDMA engines, kernel receive contexts, and accelerated netdev receive contexts.

## Important APIs, types, and functions
- `msix_initialize()` computes the required vector count, allocates PCI MSI-X vectors, allocates `dd->msix_info.msix_entries`, initializes the vector bitmap, and records capacity.
- `msix_request_irq()` is the central allocator: it reserves a free vector bit, calls `pci_request_irq()`, records IRQ metadata, and requests affinity.
- `msix_request_general_irq()`, `msix_request_sdma_irq()`, `msix_request_rcd_irq()`, and `msix_netdev_request_rcd_irq()` build names, choose handlers, and remap hardware interrupt sources to vectors.
- `msix_request_irqs()` requests the general vector, all SDMA vectors, and all kernel receive context vectors, enabling SDMA interrupt sources as it goes.
- `msix_free_irq()` releases affinity and PCI IRQ state for one vector and clears the in-use bit.
- `msix_clean_up_interrupts()` frees all requested IRQs, metadata, and PCI vectors.
- `msix_netdev_synchronize_irq()` waits for all netdev receive-context IRQ handlers to finish before queue disable.

## Control flow
Device setup calls `msix_initialize()` before individual IRQ requests. The total vector count is `1 + num_sdma + n_krcv_queues + num_netdev_contexts`, and must be below the hardware vector limit. Later request helpers reserve vectors from the bitmap and remap HFI1 interrupt source indexes to the allocated MSI-X number.

The general IRQ is required to be vector zero; if allocation returns any other vector, it is freed and setup fails. SDMA requests enable SDMA, progress, idle, and error interrupt sources. Kernel receive contexts are requested during `msix_request_irqs()`, while netdev receive contexts use the exported netdev-specific request helper from `netdev_rx.c`.

Cleanup iterates all possible requested vectors, frees those with non-null `arg`, clears metadata, frees the entry array, resets max count, and calls `pci_free_irq_vectors()`.

## State and persistence
MSI-X runtime state lives in `dd->msix_info`: allocated entry array, in-use bitmap, spinlock, and max requested count. Individual receive contexts and SDMA engines store their assigned `msix_intr`; receive contexts also store interrupt register/mask fields. State is runtime-only and tied to PCI device lifetime.

## Dependencies and integration points
This file depends on Linux PCI MSI-X APIs, HFI1 affinity helpers, interrupt handlers from receive and SDMA code, HFI1 hardware remap functions, and netdev receive queue lifecycle. It is a prerequisite for receive and SDMA interrupt-driven operation.

## Risks
- `msix_request_irq()` sets a bitmap bit before validating `type`; an invalid type returns `-EINVAL` without clearing the bit. Current callers pass constants, but future callers should preserve that invariant or fix the ordering.
- Partial failures in `msix_request_irqs()` return immediately; higher-level probe code must call cleanup to release already requested vectors.
- General IRQ must be vector zero, so changes to allocation order can break initialization.
- Netdev IRQ synchronization assumes netdev contexts have valid `msix_intr` entries.

## Test signals
- Probe tests with different SDMA, kernel receive, and netdev context counts, including vector-limit failure.
- Fault-injection for PCI vector allocation, metadata allocation, individual `pci_request_irq()`, and affinity failures.
- Verify interrupt remapping for general, SDMA, kernel receive, and netdev receive contexts.
- Exercise cleanup after partial request failure and after netdev contexts are allocated/freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/msix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/msix.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/msix.h

## Purpose
`msix.h` declares the HFI1 MSI-X interrupt-management API used by device setup, receive contexts, SDMA engines, and netdev receive contexts.

## Important APIs, types, and functions
- Core lifecycle: `msix_initialize()`, `msix_request_irqs()`, and `msix_clean_up_interrupts()`.
- Per-source request/free helpers: `msix_request_general_irq()`, `msix_request_rcd_irq()`, `msix_request_sdma_irq()`, and `msix_free_irq()`.
- Netdev-specific helpers: `msix_netdev_request_rcd_irq()` and `msix_netdev_synchronize_irq()`.

## Control flow
The expected order is initialize PCI MSI-X capacity, request general/SDMA/kernel receive interrupts, request netdev receive interrupts as netdev contexts are allocated, synchronize netdev IRQs before disabling their queues, and clean up all interrupts during device teardown or probe failure.

## State and persistence
The header declares functions that mutate `struct hfi1_devdata`, `struct hfi1_ctxtdata`, and `struct sdma_engine` interrupt fields. It declares no state of its own.

## Dependencies and integration points
It includes `hfi.h` for core HFI1 types and is included by receive, SDMA, and device initialization code. It abstracts Linux PCI IRQ details away from those users.

## Risks
- Callers must pair successful request helpers with `msix_free_irq()` or full cleanup.
- Netdev callers must synchronize IRQs before freeing or disabling NAPI contexts.
- Any signature change affects several HFI1 subsystems.

## Test signals
- Compile users across HFI1 device, SDMA, receive, and netdev paths.
- Probe and teardown tests should check that each requested interrupt is freed exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/msix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/netdev.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/netdev.h

## Purpose
`netdev.h` defines the shared HFI1 receive-context abstraction used by accelerated netdev/IPoIB support. It provides the receive queue structure, top-level RX manager structure, constants, inline accessors, and public lifecycle/table APIs.

## Important APIs, types, and functions
- `struct hfi1_netdev_rxq` binds one NAPI object to one HFI1 receive context and its parent `hfi1_netdev_rx`.
- `struct hfi1_netdev_rx` owns the dummy NAPI netdevice, HFI1 device pointer, RX queue array, receive queue count, first free RMT index, QPN/device xarray, and atomic reference counters for enabled queues and active netdevs.
- `HFI1_MAX_NETDEV_CTXTS` limits accelerated netdev contexts to eight.
- Inline helpers return context count, receive context pointer, and free RMT index.
- Public APIs allocate/free the RX manager, initialize/destroy shared RX queues, enable/disable queues, compute context count, and manage xarray data by ID.
- `hfi1_netdev_rx_napi()` is declared as the chip-level NAPI poll function.

## Control flow
Higher-level device setup calls `hfi1_alloc_rx()` to allocate the manager. IPoIB netdev setup calls `hfi1_netdev_rx_init()` to allocate contexts on first user and `hfi1_netdev_rx_destroy()` on final user. Open/stop call `hfi1_netdev_enable_queues()` and `hfi1_netdev_disable_queues()` to toggle NAPI and hardware receive context state. Receive demultiplexing uses the xarray APIs to map QPN-like IDs to netdev private data.

## State and persistence
State is runtime-only. Atomic `netdevs` reference-counts users of the shared queue allocation; atomic `enabled` reference-counts netdevs that have enabled receive processing. `dev_tbl` stores dynamic ID-to-data mappings for IPoIB devices and VLAN-like children.

## Dependencies and integration points
The header depends on Linux netdevice, NAPI, and xarray APIs plus HFI1 core context types. It integrates IPoIB setup, netdev RX implementation, MSI-X request paths, and chip-level receive polling.

## Risks
- Inline accessors assume `dd->netdev_rx` and the indexed `rxq` exist; callers must honor lifecycle ordering.
- Atomic counters drive allocation and enable/disable transitions; imbalance can leak receive contexts or disable queues while users remain.
- Xarray operations use caller-provided integer IDs; ID collisions return errors during add and must be handled by netdev setup.

## Test signals
- Multi-netdev open/close tests should verify `netdevs` and `enabled` transitions.
- Receive demultiplexing tests should add, find, iterate, and remove xarray entries, including collision handling.
- Context-count tests should cover AIP disabled, no available contexts, CPU mask limits, and the eight-context cap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/netdev_rx.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/netdev_rx.c

## Purpose
`netdev_rx.c` manages HFI1 receive contexts dedicated to accelerated netdev traffic. It allocates hardware receive contexts, attaches NAPI instances and MSI-X interrupts, enables/disables queues under shared reference counts, and stores QPN-to-netdev mappings for IPoIB receive demultiplexing.

## Important APIs, types, and functions
- `hfi1_netdev_allocate_ctxt()` creates a kernel receive context with netdev-specific flags, fast/slow handlers, and sequence count setup.
- `hfi1_netdev_setup_ctxt()` allocates receive header queues, eager buffers, configures receive-control bits, and installs netdev receive function maps.
- `hfi1_netdev_deallocate_ctxt()` disables receive control, frees MSI-X IRQs, clears TIDs/P_Keys, decrements stats, and frees the context.
- `hfi1_num_netdev_contexts()` chooses how many contexts to reserve based on AIP capability, available contexts, NUMA-local CPUs, and `HFI1_MAX_NETDEV_CTXTS`.
- `hfi1_netdev_rxq_init()` allocates `rxq` entries, allots contexts, adds NAPI to a dummy netdev, and requests netdev receive IRQs.
- `hfi1_netdev_rx_init()`/`destroy()` reference-count shared RX queue allocation.
- `hfi1_netdev_enable_queues()`/`disable_queues()` reference-count active NAPI/hardware queue enable state.
- `hfi1_alloc_rx()`/`hfi1_free_rx()` own the top-level `dd->netdev_rx` manager.
- Xarray helpers add, remove, load, and iterate data by integer ID.

## Control flow
At device initialization, `hfi1_alloc_rx()` creates the manager and a dummy netdev used only for NAPI registration. When the first IPoIB netdev initializes, `hfi1_netdev_rx_init()` increments `netdevs` from zero and calls `hfi1_netdev_rxq_init()` under `hfi1_mutex`. That function allocates one queue per configured netdev context, creates and configures each HFI1 context, pins it with `hfi1_rcd_get()`, attaches NAPI, and requests an MSI-X vector using the netdev NAPI interrupt handler.

On netdev open, `hfi1_netdev_enable_queues()` increments `enabled`; only the first opener enables all NAPI objects and hardware receive contexts. On stop, `hfi1_netdev_disable_queues()` decrements the counter; the final disable synchronizes all netdev IRQs, disables receive contexts/interrupts, synchronizes NAPI, and disables NAPI. Final netdev destruction deinitializes NAPI, contexts, IRQs, and queue memory.

## State and persistence
Runtime state includes the RX manager, dummy netdev, queue array, hardware receive contexts, MSI-X assignments, NAPI state, xarray device table, and atomic user counters. Hardware receive context state and interrupts are enabled only while at least one netdev is open. Nothing persists across device teardown.

## Dependencies and integration points
This file integrates HFI1 context allocation, receive header/eager buffer setup, receive-control programming, NAPI, MSI-X netdev IRQ requests, HFI1 global mutex, xarray demultiplexing, IPoIB RSM setup from `ipoib_rx.c`, and chip-level receive handlers.

## Risks
- Error unwinding in `hfi1_netdev_rxq_init()` iterates down from the failing index and must handle partially initialized entries correctly.
- `hfi1_netdev_disable_queues()` depends on `atomic_dec_if_positive()` semantics; counter imbalance can skip the actual disable path or over-disable.
- Receive context allocation is blocked when `HFI1_FROZEN` is set; callers need to surface `-EIO`.
- Xarray add uses `GFP_NOWAIT`, so allocation failure can make IPoIB netdev init fail under memory pressure.
- MSI-X and NAPI lifetimes are tightly coupled; IRQs must be synchronized before disabling/freeing NAPI contexts.

## Test signals
- Probe with AIP enabled/disabled, no available contexts, different NUMA CPU masks, and frozen device state.
- Fault-inject context creation, receive header queue setup, eager buffer setup, NAPI/IRQ request failures, and verify unwind.
- Open/stop multiple IPoIB netdevs concurrently and confirm hardware queues enable once and disable once.
- Validate xarray ID collision, lookup, removal, and iteration during receive demux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/netdev_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opa_compat.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opa_compat.h

## Purpose
`opa_compat.h` provides local OPA definitions and helpers that HFI1 needs before or beyond generic Linux RDMA core coverage. In this subset it mainly supplies OPA management attribute IDs, PMA status codes, port-state helpers, and OPA physical port-state enumeration.

## Important APIs, types, and functions
- OPA SMA attribute IDs define congestion info, HFI congestion log, HFI congestion setting, and congestion control table.
- OPA PMA attribute IDs define port status, clear port status, data counters, error counters, and error info.
- `OPA_PM_STATUS_REQUEST_TOO_LARGE` is a PMA response status used when computed replies exceed MAD payload size.
- `port_states_to_logical_state()` and `port_states_to_phys_state()` decode fields from `struct opa_port_states`.
- `enum opa_port_phys_state` extends familiar IB physical states with OPA offline and test states and documents valid read/write ranges.

## Control flow
There is no standalone control flow. `mad.c` includes this header through `mad.h` and uses its constants and inline decoders during SMA/PMA dispatch and PortInfo/PortStateInfo handling.

## State and persistence
The header defines constants and inline helpers only. It owns no state.

## Dependencies and integration points
The helpers assume RDMA OPA structures such as `struct opa_port_states` are available from included RDMA headers. The definitions are part of HFI1's management protocol compatibility surface.

## Risks
- Values must match OPA management specifications and any upstream RDMA core definitions. Divergence would break fabric-manager interoperability.
- The physical state enum documents that only values 0..3 are valid on writes while more values are returned on reads; SET handlers must preserve that distinction.
- The include guard name `_LINUX_H` is broad and could conflict with other headers if included in unusual orders.

## Test signals
- Compile all HFI1 MAD users after RDMA core OPA header updates.
- Exercise PortStateInfo and PortInfo GET/SET paths that use logical and physical state decoders.
- Check for macro value duplication if generic RDMA headers gain equivalent definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opa_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opfn.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opfn.c

## Purpose
`opfn.c` implements Omni-Path Feature Negotiation for HFI1 RC QPs. OPFN uses a reserved BTH extended bit plus an atomic compare-swap-shaped work request to exchange feature parameters between peers, currently for TID RDMA.

## Important APIs, types, and functions
- `struct hfi1_opfn_type` maps a feature code to request, response, reply, and error callbacks.
- `hfi1_opfn_handlers[]` currently registers TID RDMA callbacks: `tid_rdma_conn_req`, `tid_rdma_conn_resp`, `tid_rdma_conn_reply`, and `tid_rdma_conn_error`.
- `opfn_conn_request()` chooses the next requested-but-not-completed feature, asks its handler for local data, posts an `IB_WR_OPFN` atomic work request to `HFI1_VERBS_E_ATOMIC_VADDR`, and marks the feature in progress.
- `opfn_conn_response()` handles an incoming OPFN request and builds atomic response data.
- `opfn_conn_reply()` processes the response to a locally posted OPFN request.
- `opfn_conn_error()` clears negotiated state and calls feature error hooks when the QP enters error.
- `opfn_qp_init()` initializes or requests negotiation on RC QP attribute changes, especially RTS transitions with supported MTU.
- `opfn_trigger_conn_request()` sees the BTH extended bit on incoming traffic and starts negotiation if enabled.
- `opfn_init()` and `opfn_exit()` manage the high-priority OPFN workqueue.

## Control flow
QP modification calls `opfn_qp_init()`. For RC QPs with TID RDMA capability and 4K or 8K path MTU, it initializes local TID RDMA OPFN data and sets the requested bit when the QP transitions to RTS. Negotiation starts only after the peer advertises the OPFN extended bit in BTH1; `opfn_trigger_conn_request()` records that support and either calls `opfn_conn_request()` directly or queued work schedules it.

`opfn_conn_request()` runs under the per-QP OPFN spinlock until it needs to call `ib_post_send()`, then drops the lock to avoid QP lock recursion. Responses and replies validate the feature code in the low nibble, call the feature-specific handler, update `completed`, clear `curr`, and report errors to feature handlers when renegotiation or QP error invalidates previous state.

## State and persistence
Per-QP state lives in `struct hfi1_opfn_data`: peer extended-bit support, requested feature bitmask, completed feature bitmask, current in-progress feature, lock, and work item. TID RDMA parameter state lives in QP private data owned by the TID RDMA code. OPFN state is runtime-only and reset on QP error or unsupported MTU transitions.

## Dependencies and integration points
The file integrates with rdmavt QPs and ACK entries, HFI1 QP private data, RDMA work requests, TID RDMA negotiation callbacks, HFI1 capability bits, tracepoints, and a dedicated workqueue used to avoid posting sends while holding QP locks.

## Risks
- OPFN uses a reserved/extended protocol encoding; both peers and the RC path must agree on BTH bit and atomic-address semantics.
- Posting sends while managing QP locks is subtle; queued work avoids a known double-lock path, but direct calls still need caller context awareness.
- Feature bitmask math assumes feature codes start at one and fit in 16-bit masks.
- If `ib_post_send()` fails, the code clears `curr` and reschedules; repeated failure can spin work unless the underlying condition changes.
- Renegotiation clears completed state and invokes feature error callbacks; TID RDMA users must tolerate that transition.

## Test signals
- RC QP tests should cover RTS transition, unsupported MTU clearing, peer extended-bit detection, and successful TID RDMA negotiation.
- Inject invalid feature codes, missing handlers, handler refusal, and `ib_post_send()` failure.
- Force QP error during in-progress and completed negotiation and verify TID RDMA error callbacks and bitmasks reset.
- Concurrency tests should exercise simultaneous incoming OPFN trigger and local QP attribute changes under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opfn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opfn.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opfn.h

## Purpose
`opfn.h` documents and declares HFI1 Omni-Path Feature Negotiation. It defines the protocol constants, feature codes, per-QP OPFN state, reserved work-request opcode mapping, and public hooks used by QP and receive paths.

## Important APIs, types, and functions
- Documentation block describes OPFN architecture: peer discovery through BTH bit 24, compare-swap opcode and `U64_MAX` address, and ULP-transparent negotiation.
- `IB_BTHE_E_SHIFT` defines the extended-bit position in BTH1.
- `HFI1_VERBS_E_ATOMIC_VADDR` defines the special atomic virtual address for OPFN packets.
- `enum hfi1_opfn_codes` currently includes `STL_VERBS_EXTD_TID_RDMA`.
- `struct hfi1_opfn_data` stores peer support, requested/completed masks, current feature, spinlock, and work item.
- `IB_WR_OPFN` maps OPFN sends to `IB_WR_RESERVED3`.
- Function prototypes expose send, response, reply, error, QP init, trigger, module init, and module exit hooks.

## Control flow
The header defines the public lifecycle: initialize OPFN workqueue at driver/module setup, initialize per-QP OPFN state during QP changes, trigger requests when incoming packets advertise the extended bit, process request/response/reply packets from the RC path, handle QP errors, and destroy the workqueue at exit.

## State and persistence
`struct hfi1_opfn_data` is per-QP runtime state. It is guarded by its spinlock and has no persistence beyond QP lifetime.

## Dependencies and integration points
The header includes Linux workqueues, RDMA verbs, and rdmavt QP definitions. It is consumed by HFI1 QP/RC/TID RDMA code that needs to negotiate feature support without exposing the protocol to upper-layer protocols.

## Risks
- The `IB_WR_OPFN` alias uses a reserved work-request opcode; changes in RDMA core reserved opcode use could conflict.
- The protocol encodes feature code in low data bits and masks in 16-bit fields, so adding features requires careful bounds checks.
- The spelling in the documentation says "Feature Negotion"; harmless for code, but searchability/documentation polish may suffer.

## Test signals
- Compile all QP, RC, and TID RDMA users after changing constants or structure fields.
- Protocol tests should confirm bit 24 detection, special atomic address matching, and feature-code extraction.
- Add-feature tests should validate mask capacity, handler table bounds, and backward compatibility with peers that do not set the extended bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opfn.h -->
