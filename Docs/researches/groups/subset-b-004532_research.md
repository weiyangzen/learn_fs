# subset-b-004532 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/htb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/htb.c

Purpose: implements the mlx5e software HTB offload tree and maps Linux `tc_htb_qopt_offload` operations to mlx5 firmware QoS nodes plus per-leaf transmit queues.

Important APIs/functions: `mlx5e_htb_init`, `mlx5e_htb_cleanup`, `mlx5e_htb_enumerate_leaves`, `mlx5e_htb_get_txq_by_classid`, `mlx5e_htb_leaf_alloc_queue`, `mlx5e_htb_leaf_to_inner`, `mlx5e_htb_leaf_del`, `mlx5e_htb_leaf_del_last`, and `mlx5e_htb_node_modify`. Internal state is `struct mlx5e_htb` and `struct mlx5e_qos_node`, using a classid hash table plus a leaf-qid bitmap.

Control flow: HTB creation prepares the select-queue state, allocates QoS SQ storage when the netdev is open, creates a root software node, creates the firmware root, and applies the select-queue change. Leaf creation allocates a compact qid, creates a software leaf, converts byte rates to firmware bandwidth share/max-average-bw, creates a firmware leaf, and opens/activates a QoS SQ if channels are up. Leaf-to-inner and leaf-delete-last are two-step firmware topology transitions that reuse qids while stopping queues and resetting qdiscs to prevent traffic leakage between classes. Deletion compacts qids by moving the highest active QoS SQ into the removed qid slot.

State and persistence: state is in memory only. Node lookup is RCU-visible to the TX datapath, and qid changes use `WRITE_ONCE`, `synchronize_net`, and qdisc resets. Firmware object ids are kept in nodes and destroyed best-effort on teardown or topology mutation.

Dependencies and integration: depends on `en/htb.h`, `en.h`, mlx5 core QoS firmware helpers, `qos.c` SQ lifecycle helpers, and `selq` queue selection. It is driven by `mlx5e_htb_setup_tc` in `qos.c`.

Risks: firmware failures during topology conversion can leave partial hardware state that is handled with rollback or force-mode cleanup. Queue compaction is subtle because qid exposure, netdev queue counts, qdisc state, and SQ lifecycle must remain synchronized. Rate conversion treats firmware `0` bandwidth share as unlimited, so low/invalid rates rely on upstream validation.

Test signals: exercise HTB create/destroy, leaf add/delete/modify, leaf-to-inner promotion, last-child collapse, open vs closed netdev paths, firmware error injection, qid compaction, and concurrent TX queue selection during class deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/htb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/htb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/htb.h

Purpose: declares the mlx5e HTB offload interface shared between TC setup code, queue lifecycle code, and the TX queue selector.

Important APIs/types: exposes opaque `struct mlx5e_htb`, `MLX5E_QOS_MAX_LEAF_NODES`, `mlx5e_fp_htb_enumerate`, leaf enumeration/query helpers, leaf topology mutation helpers, node modification, allocation/free, init, and cleanup.

Control flow: callers allocate an HTB object, initialize it from a `tc_htb_qopt_offload`, use command-specific helpers as TC changes arrive, enumerate leaves to open/activate QoS SQs, and clean it up on qdisc destroy.

State and persistence: the header hides all tree internals. Persistence is only the lifetime of the allocated HTB instance; callers must serialize mutations through the driver state lock as expected by the implementation.

Dependencies and integration: includes `en.h`, forward-declares `mlx5e_selq`, and uses `netlink_ext_ack` for user-visible TC errors. `qos.h` calls these APIs to implement `mlx5e_htb_setup_tc`.

Risks: the ABI is intentionally low-level; callers must pass class ids/qids from the TC command consistently and must not enumerate leaves after cleanup.

Test signals: compile coverage with `CONFIG_NET_SCHED`, HTB offload command coverage, and queue-open enumeration under channel reopen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/htb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/hv_vhca_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/hv_vhca_stats.c

Purpose: exports per-channel mlx5e RX/TX packet and byte counters to a Hyper-V vHCA statistics agent.

Important APIs/functions: `mlx5e_hv_vhca_stats_create` allocates the backing buffer and registers an `MLX5_HV_VHCA_AGENT_STATS` agent; `mlx5e_hv_vhca_stats_destroy` unregisters it. Internal helpers size the buffer, fill `struct mlx5e_hv_vhca_per_ring_stats`, process control-block commands, and run the delayed stats work.

Control flow: Hyper-V calls the control callback with an update command. A zero command cancels work; `MLX5_HV_VHCA_STATS_UPDATE_ONCE` queues a single immediate write; other commands are interpreted as 100 ms units and requeue periodic work. The work clears the buffer, snapshots `priv->channel_stats`, writes to the vHCA agent, and requeues if a period remains.

State and persistence: stores `stats_agent.buf`, `stats_agent.agent`, `stats_agent.work`, and `stats_agent.delay` in `mlx5e_priv`. The buffer layout is fixed version 1 and sized from `priv->stats_nch`; no persistent storage exists outside the Hyper-V shared agent.

Dependencies and integration: uses `lib/hv_vhca.h`, `lib/hv.h`, `priv->wq`, and channel stats. The header compiles this away unless `CONFIG_PCI_HYPERV_INTERFACE` is enabled.

Risks: stats are sampled without explicit per-counter synchronization and can be transient. Buffer sizing depends on `stats_nch` staying compatible with the registered agent. Failed writes stop the current periodic chain by returning before requeue.

Test signals: Hyper-V-enabled builds, agent create/destroy failures, update-once and periodic control commands, channel-count changes across open/close, and vHCA write error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/hv_vhca_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/hv_vhca_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/hv_vhca_stats.h

Purpose: provides the conditional public entry points for mlx5e Hyper-V vHCA stats export.

Important APIs/functions: declares `mlx5e_hv_vhca_stats_create` and `mlx5e_hv_vhca_stats_destroy` when `CONFIG_PCI_HYPERV_INTERFACE` is enabled; otherwise supplies no-op inline stubs.

Control flow: main driver code can call create/destroy unconditionally, with the compile-time option deciding whether a real vHCA stats agent is installed.

State and persistence: no state in the header; the implementation stores its agent state in `mlx5e_priv`.

Dependencies and integration: includes `en.h` for `struct mlx5e_priv`; bridges mlx5e channel stats with the Hyper-V PCI interface.

Risks: no-op stubs mean tests on non-Hyper-V builds do not exercise agent lifecycle or delayed-work cancellation.

Test signals: build both enabled and disabled configurations, and verify callers do not need additional ifdefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/hv_vhca_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mapping.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mapping.c

Purpose: implements a generic data-to-id mapping service used by mlx5e offload paths that need compact hardware tags and reverse lookup on packet completion/receive.

Important APIs/functions: `mapping_create`, `mapping_create_for_id`, `mapping_destroy`, `mapping_add`, `mapping_remove`, and `mapping_find`. Internal state combines an xarray from id to item, a jhash hashtable from data to item, optional delayed-removal work, and a shared-context list keyed by image GUID/type.

Control flow: `mapping_add` hashes the caller data and either bumps an existing item count or allocates a new item and xarray id in `[1, max_id]`. `mapping_remove` decrements the count, removes the item from the data hash when the count reaches zero, and either frees the xarray id immediately or puts it on a delayed pending list. Delayed work frees expired items and reschedules for the nearest remaining timeout. `mapping_find` performs an RCU-protected xarray lookup and copies the stored data to the caller.

State and persistence: all state is in kernel memory. Delayed removal keeps old ids visible for `MAPPING_GRACE_PERIOD` to avoid hardware races where packets carry an id after software has reused it. Shared contexts are refcounted globally under `shared_ctx_lock`.

Dependencies and integration: uses xarray allocation, jhash, RCU freeing, delayed work, and mlx5 software image GUID constants. TC receive code uses mapping contexts to decode register metadata.

Risks: `mapping_destroy` assumes no live users remain; it flushes delayed work and destroys the xarray but does not walk active non-delayed mappings itself. Delayed removal must preserve old data long enough for hardware completion paths but not leak ids indefinitely.

Test signals: duplicate add/remove reference counts, max-id exhaustion, delayed id reuse race tests, shared-context refcounting, and RCU lookup during concurrent remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mapping.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mapping.h

Purpose: declares the mlx5e generic mapping context API for allocating stable ids for arbitrary fixed-size data blobs.

Important APIs/functions: opaque `struct mapping_ctx`; `mapping_add`, `mapping_remove`, `mapping_find`, `mapping_create`, `mapping_destroy`, and `mapping_create_for_id`.

Control flow: users create a context for a fixed data size and maximum id, add data to receive an id, later find data by id, and remove ids when offloaded state is no longer needed. `mapping_create_for_id` reuses a shared context for a hardware/software identity tuple.

State and persistence: describes xarray-backed id lookup, data hashing, RCU reads, and optional delayed removal to avoid hardware id reuse races.

Dependencies and integration: no heavy includes; consumers include it from TC/offload paths that store ids in firmware metadata registers.

Risks: callers must provide buffers of exactly the configured data size and balance add/remove calls.

Test signals: API users should test id allocation boundaries, duplicate data coalescing, and delayed-removal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mod_hdr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mod_hdr.c

Purpose: caches and manages mlx5 modify-header objects for TC offload actions, avoiding duplicate firmware objects for identical action sequences.

Important APIs/functions: `mlx5e_mod_hdr_tbl_init`, `mlx5e_mod_hdr_tbl_destroy`, `mlx5e_mod_hdr_attach`, `mlx5e_mod_hdr_detach`, `mlx5e_mod_hdr_get`, `mlx5e_mod_hdr_alloc`, `mlx5e_mod_hdr_dealloc`, and `mlx5e_mod_hdr_get_item`.

Control flow: attach builds a key from action bytes, looks in the table under a mutex, and either refcounts an existing handle or inserts a new handle before allocating the firmware modify-header object. A completion lets concurrent attachers wait for the first allocation result. Detach decrements the refcount and, for the final user, removes the hash entry, deallocates the firmware object if allocation succeeded, and frees the handle. The action-buffer allocator grows static or dynamic action arrays up to firmware namespace limits.

State and persistence: the table is in memory, keyed by copied action bytes and action count. Handles maintain refcount, firmware pointer, completion, and allocation result. No persistent state exists outside firmware objects.

Dependencies and integration: uses Linux hashtables/refcounts/completions and `mlx5_modify_header_alloc/dealloc`; namespace-specific limits come from FDB or NIC RX capabilities.

Risks: attach intentionally publishes an in-progress handle, so all error paths must complete and detach correctly. Static action arrays become dynamic after growth and must be deallocated only when `is_static` is false.

Test signals: identical concurrent attaches, firmware allocation failure, detach after failed attach, action-array growth from static and dynamic buffers, and max-action exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mod_hdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mod_hdr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mod_hdr.h

Purpose: defines the public modify-header action buffer and cached handle API used by mlx5e TC offloads.

Important APIs/types: `struct mlx5e_tc_mod_hdr_acts`, opaque `struct mlx5e_mod_hdr_handle`, `DECLARE_MOD_HDR_ACTS_ACTIONS`, `DECLARE_MOD_HDR_ACTS`, allocation/deallocation helpers, attach/detach/get helpers, table init/destroy, and `mlx5e_mod_hdr_max_actions`.

Control flow: callers build action arrays, append entries with `mlx5e_mod_hdr_alloc`, attach the completed action list to get a cached firmware handle, use `mlx5e_mod_hdr_get` in flow rule construction, then detach and deallocate actions.

State and persistence: tracks whether an actions array is static or heap-backed. Cached firmware object state lives in the implementation.

Dependencies and integration: includes mlx5 flow namespace definitions and uses FDB vs kernel namespace capability fields to determine maximum actions.

Risks: callers must increment `num_actions` consistently after writing allocated action slots and must not free static action storage through normal `kfree`.

Test signals: compile-time static action declarations, namespace capability variation, and TC pedit/action offload flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mod_hdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/monitor_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/monitor_stats.c

Purpose: configures mlx5 firmware monitor counters and handles monitor-counter EQ events by refreshing driver stats and rearming the counters.

Important APIs/functions: `mlx5e_monitor_counter_supported`, `mlx5e_monitor_counter_init`, and `mlx5e_monitor_counter_cleanup`. Internal helpers check capabilities, program PPCNT/Q-counter watch lists, arm counters, and process events through a work item.

Control flow: support detection checks every device in the scalable-device set for enough monitor counter capacity. Init installs a monitor-counter notifier per device, programs required PPCNT and rx-out-of-buffer q-counter monitors, arms each device, and queues stats update work. When an event arrives, a work item takes `state_lock`, updates NDO stats, releases the lock, and rearms all devices. Cleanup clears the monitor list in firmware, unregisters notifiers, and cancels work.

State and persistence: notifier and work structures live in `mlx5e_priv`; firmware monitor counter configuration persists until cleanup or device reset.

Dependencies and integration: uses mlx5 EQ notifiers, command opcodes `SET_MONITOR_COUNTER` and `ARM_MONITOR_COUNTER`, scalable-device iteration, q-counter ids, and mlx5e stats update.

Risks: command execution errors are ignored in setup/arm paths, so lack of monitor functionality may be silent after support checks. Event storms depend on workqueue serialization and rearm behavior.

Test signals: devices with and without PPCNT/Q-counter capacities, SD multi-device setups, EQ event handling, cleanup ordering, and stats refresh after rx-out-of-buffer events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/monitor_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/monitor_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/monitor_stats.h

Purpose: declares the mlx5e monitor-counter lifecycle and capability API.

Important APIs/functions: `mlx5e_monitor_counter_supported`, `mlx5e_monitor_counter_init`, and `mlx5e_monitor_counter_cleanup`.

Control flow: callers check support before initializing monitor counters, then clean them up during device teardown.

State and persistence: no header-owned state; implementation stores notifier/work state in `mlx5e_priv` and firmware monitor configuration in the device.

Dependencies and integration: relies on `struct mlx5e_priv` from surrounding mlx5e headers.

Risks: the header documents no locking contract, so callers must follow the implementation expectation that init/cleanup are part of driver lifecycle.

Test signals: build coverage and feature-gated init/cleanup sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/monitor_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/params.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/params.c

Purpose: computes and builds mlx5e queue, CQ, RQ, SQ, XDP, XSK, SHAMPO, and ICOSQ parameters from device capabilities and netdev runtime settings.

Important APIs/functions: striding-RQ helpers such as `mlx5e_mpwrq_page_shift`, `mlx5e_mpwrq_umr_mode`, `mlx5e_mpwrq_log_wqe_sz`, `mlx5e_mpwqe_get_log_rq_size`, linear/nonlinear RX decisions, validation helpers, `mlx5e_build_rq_params`, `mlx5e_build_rq_param`, `mlx5e_build_sq_param`, `mlx5e_build_channel_param`, and `mlx5e_build_xsk_channel_param`.

Control flow: RX setup first chooses cyclic vs linked-list striding RQ based on feature flags, CQE compression capabilities, and whether striding RQ can produce acceptable skb layout. MPWRQ calculations derive page shift, UMR mapping mode, WQE size, stride size/count, RQ size, and UMR workqueue capacity. Legacy cyclic RQ builds fragment arrays and refill bulk parameters from MTU, headroom, XDP, and page size. Queue builders fill firmware contexts with CQ size, compression layout, WQ type/stride, PD, VLAN/FCS settings, stop room, NUMA placement, and ICOSQ sizing.

State and persistence: functions are mostly pure calculations into caller-provided parameter structs. They read capabilities and netdev params but persist no global state. The generated contexts become hardware queue creation inputs.

Dependencies and integration: depends on mlx5 capability macros, page pool/XDP socket constraints, DIM moderation, accel features such as kTLS/IPsec/PSP, and port link speed for slow PCI heuristics.

Risks: many calculations are capability-dependent and unsigned; warnings guard underflow and invalid stride combinations. XSK unaligned/oversized frame modes are especially sensitive because UMR entry size changes queue capacity. Incorrect stop-room or ICOSQ sizing can deadlock queue recovery or UMR posting.

Test signals: MTU extremes, XDP attach/detach, XSK aligned/unaligned/chunk-size variations, CQE compression layouts, SHAMPO/LRO, kdump defaults, slow PCI detection, and firmware capability matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/params.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/params.h

Purpose: defines mlx5e queue parameter data structures and declares the parameter calculation/building API.

Important APIs/types: `struct mlx5e_xsk_param`, `mlx5e_rq_opt_param`, `mlx5e_cq_param`, `mlx5e_rq_param`, `mlx5e_sq_param`, `mlx5e_channel_param`, `mlx5e_create_sq_param`, MPWRQ dynamic helpers, RX layout helpers, CQ/SQ/RQ builders, validation helpers, and `mlx5e_params_print_info`.

Control flow: channel open code fills these parameter structs through build functions, then passes the embedded firmware contexts and workqueue parameters to queue creation functions. Optional `rq_opt` carries XSK or per-queue page-size settings.

State and persistence: structures are per-channel/per-queue configuration snapshots. Inline helpers only read or format fields; no global state is held.

Dependencies and integration: includes `en.h` and depends on mlx5 firmware context sizes, mlx5e params, netdev queue config, and XSK metadata.

Risks: callers must zero structs before use where required and must pass matching `params`/`rq_opt` to calculations and builders. `mlx5e_params_print_info` calls MPWRQ helpers even for cyclic RQ to print stride size, so capability assumptions still matter.

Test signals: compile coverage across feature flags, channel parameter construction, XSK channel construction, and validation failures for unsupported MPWRQ settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/pcie_cong_event.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/pcie_cong_event.c

Purpose: creates a firmware PCIe congestion event object, handles object-change events, and exposes high/low/stale transition counters through the mlx5e stats framework.

Important APIs/functions: `mlx5e_pcie_cong_event_init`, `mlx5e_pcie_cong_event_cleanup`, firmware command helpers for create/destroy/query, threshold config retrieval/validation, the EQ notifier, and stats group callbacks.

Control flow: init exits if unsupported, reads driverinit devlink threshold parameters, validates low < high for inbound/outbound directions, allocates state, creates a general object of type `PCIE_CONG_EVENT`, registers an OBJECT_CHANGE notifier, and stores it in `priv->cong_event`. Events queue work that queries the object, compares new inbound/outbound high-state bits with the last state, increments transition counters, and counts stale events when no bit changed. Cleanup unregisters the notifier, cancels work, destroys the object, and frees memory.

State and persistence: `struct mlx5e_pcie_cong_event` holds the firmware object id, last state, notifier/work, and ethtool stats. Firmware configuration persists while the object exists.

Dependencies and integration: uses devlink params from `devlink.h`, mlx5 general-object commands, EQ notifier infrastructure, and the mlx5e stats group macro system.

Risks: threshold parameters are driverinit values, so runtime changes may require reinit. Query initializes `new_cong_state` in the caller, and stale event counts can reveal duplicate notifications. Destroy errors are logged but cannot be repaired.

Test signals: unsupported devices, invalid threshold devlink values, create/register rollback, simulated object-change events, stale events, and cleanup with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/pcie_cong_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/pcie_cong_event.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/pcie_cong_event.h

Purpose: declares the PCIe congestion event lifecycle hooks for mlx5e.

Important APIs/functions: `mlx5e_pcie_cong_event_init` and `mlx5e_pcie_cong_event_cleanup`.

Control flow: the driver calls init during private feature setup and cleanup during teardown; unsupported hardware returns success without installing state.

State and persistence: no header state; implementation stores `priv->cong_event` and a firmware general object.

Dependencies and integration: assumes `struct mlx5e_priv` is available to callers through mlx5e core headers.

Risks: callers must pair cleanup with successful or partially successful init paths because init can allocate and then fail during notifier/object setup.

Test signals: build coverage, init/cleanup pairing, and stats group visibility when `priv->cong_event` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/pcie_cong_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port.c

Purpose: wraps mlx5 Ethernet port firmware registers for autoneg/link modes, port buffers, priority-to-buffer mapping, shared-buffer controls, and FEC configuration.

Important APIs/functions: `mlx5_port_query_eth_autoneg`, `mlx5_port_set_eth_ptys`, `mlx5e_port_linkspeed`, PBMC/SBPR/SBCM/PPTB query/set wrappers, `mlx5e_fec_in_caps`, `mlx5e_get_fec_mode`, and `mlx5e_set_fec_mode`.

Control flow: register wrappers allocate or stack-build input/output buffers, set `local_port`/selectors, and call `mlx5_core_access_reg`. Link speed queries extended PTYS first and falls back to legacy PTYS when needed. FEC logic queries PPLM, walks supported link-mode fields gated by PCAM feature bits, maps ethtool FEC policy to lane-speed-specific firmware policies, clears unsupported speeds to auto, and writes the updated PPLM.

State and persistence: no driver-local long-lived state. Successful register writes persist in firmware/admin port configuration.

Dependencies and integration: depends on mlx5 register layouts (`PTYS`, `PBMC`, `SBPR`, `SBCM`, `PPTB`, `PPLM`), port capability helpers, and ethtool-facing FEC constants from `port.h`.

Risks: FEC field coverage must track new link modes and capability bits. `mlx5_port_set_eth_ptys` denies autoneg disable when unsupported. Priority-to-buffer packing uses four bits per priority and depends on valid buffer indices from callers.

Test signals: extended vs legacy PTYS devices, missing PCAM/PPLM support, every FEC policy and lane-speed class, register access failures, and priority-buffer round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port.h

Purpose: declares Ethernet port register helper APIs and mlx5e FEC policy constants.

Important APIs/functions: autoneg query/set, link speed query, PBMC/SBPR/SBCM/PPTB buffer helpers, FEC capability/get/set helpers, and enum values for NOFEC, Firecode, RS variants, and LLRS.

Control flow: higher-level ethtool/DCB/port-buffer code calls these wrappers rather than building raw mlx5 register commands directly.

State and persistence: header has no state. Register writes performed by the implementation change firmware/admin state.

Dependencies and integration: includes mlx5 core driver types and `en.h`; used heavily by `port_buffer.c` and ethtool link settings paths.

Risks: enum values must stay aligned with firmware/ethtool translation code. Callers must pass adequately sized register buffers for query functions that accept `void *out`.

Test signals: compile coverage plus link mode, buffer, and FEC ethtool tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port_buffer.c

Purpose: implements DCB/PFC-aware manual port buffer configuration, including headroom sizes, xoff/xon thresholds, priority-to-buffer mapping, and shared-buffer pool allocation.

Important APIs/functions: `mlx5e_port_query_buffer` and `mlx5e_port_manual_buffer_config`. Internal helpers query shared-buffer pools, select SBCM pool parameters, update shared-buffer splits, set PBMC, calculate xoff, update lossless thresholds, and derive lossy/lossless buffer state from PFC.

Control flow: query reads PBMC, converts cell counts to bytes, and reports network, internal, spare, and headroom sizes. Manual config starts from current PBMC, computes xoff from link speed, cable length, and MTU, then applies requested change bits for cable length, PFC, prio-to-buffer, or explicit buffer sizes. Lossless buffers get xoff/xon thresholds and cannot be zero-sized; total requested headroom must fit current headroom plus spare. If needed, PBMC is written after shared-buffer pools and SBCM class settings are updated, then PPTB is written for prio mapping.

State and persistence: reads `priv->dcbx.port_buff_cell_sz`, `cable_len`, and `xoff`; updates `priv->dcbx.xoff` after successful/attempted recalculation. Firmware PBMC/SBPR/SBCM/PPTB writes persist port buffer configuration.

Dependencies and integration: uses `port.c` register wrappers, DCB PFC structures, pause/PFC queries, link speed, and mlx5 PCAM/SBCAM capabilities.

Risks: buffer-cell conversion truncates to firmware cell units. Shared-buffer pool update errors must happen before PBMC write to avoid inconsistent pool/buffer state. Threshold math requires enough size for xoff plus max MTU plus one cell.

Test signals: PFC on/off transitions, global pause handling, prio remapping, cable length changes, MTU extremes, insufficient buffer errors, and devices without SBCAM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port_buffer.h

Purpose: defines mlx5e port-buffer constants, support checks, change-bit flags, data structures, and public buffer configuration APIs.

Important APIs/types: `MLX5E_MAX_NETWORK_BUFFER`, `MLX5E_TOTAL_BUFFERS`, `MLX5E_DEFAULT_CABLE_LEN`, `MLX5_BUFFER_SUPPORTED`, change flags for cable/PFC/prio/size, `struct mlx5e_bufferx_reg`, `struct mlx5e_port_buffer`, `mlx5e_port_manual_buffer_config`, and `mlx5e_port_query_buffer`.

Control flow: callers query current port buffer state or request manual changes by passing a change bitmask plus optional PFC, buffer-size, and priority mapping data.

State and persistence: structures mirror firmware PBMC buffer entries in byte units. Implementation writes persistent port register state and updates DCB runtime fields.

Dependencies and integration: includes `en.h` and `port.h`; capability macro checks PBMC and PPTB PCAM support.

Risks: callers must provide arrays sized for eight priorities/buffers and valid change-specific pointers.

Test signals: DCB user configuration paths and capability-gated support reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/ptp.c

Purpose: implements the dedicated mlx5e PTP TX/RX channel, hardware timestamp reconciliation, PTP flow-steering rules, and PTP queue lifecycle.

Important APIs/functions: `mlx5e_ptp_open`, `mlx5e_ptp_close`, activate/deactivate, `mlx5e_ptp_get_rqn`, RX flow-steering allocation/free/manage, metadata tracking, and skb timestamp callback handling. Internal functions manage TX SQs, timestamp CQs, metadata freelists/maps, NAPI polling, unhealthy recovery, and PTP RX rules.

Control flow: open sets TX/RX state from params, adds NAPI, builds PTP-specific SQ/RQ params, opens TX CQs and timestamp CQs per TC, opens PTP SQs with `ts_cqe_to_dest_cqn`, and optionally opens a cyclic PTP RQ. TX packets needing PTP use metadata ids; normal TX CQ supplies a CQE timestamp while the timestamp CQ supplies a port timestamp. Once both are present, the code checks their delta and reports the port timestamp, or marks the SQ unhealthy on large divergence. RX activation installs rules for UDP v4/v6 PTP event port and L2 `ETH_P_1588`.

State and persistence: `struct mlx5e_ptp` holds data path queues, NAPI, state bits, and channel metadata. Each `mlx5e_ptpsq` owns a metadata freelist, skb map, pending timestamp CQE list, CQ stats, and recovery work. Flow-steering state is stored in `struct mlx5e_ptp_fs`.

Dependencies and integration: depends on mlx5e TX/RX queue creation, CQ polling, health reporter, flow-steering redirect helpers, hwtstamp config, PTP classifier constants, and netdev queue/NAPI APIs.

Risks: timestamp delivery uses two asynchronous CQ streams; late or missing port CQEs can exhaust metadata and trigger recovery. The skb control block is reused and must be initialized before timestamp tracking. Flow-steering set/unset protects against invalid add/remove while channels are open.

Test signals: PTP TX over L2 and UDP v4/v6, timestamp delta aborts, late/lost CQEs, metadata exhaustion recovery, RX rule activation/deactivation, open rollback at each queue stage, and multi-TC PTP TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/ptp.h

Purpose: declares PTP channel data structures, metadata helpers, packet classification helper, and lifecycle APIs.

Important APIs/types: `struct mlx5e_ptp_metadata_fifo`, `mlx5e_ptp_metadata_map`, `mlx5e_ptpsq`, `mlx5e_ptp`, PTP state bits, `mlx5e_use_ptpsq`, FIFO/map inline helpers, open/close/activate/deactivate, RX FS helpers, `mlx5e_ptpsq_track_metadata`, and skb hwtstamp helpers.

Control flow: TX code uses `mlx5e_use_ptpsq` to route timestamped PTP skbs to PTP SQs, obtains metadata from the freelist, stores skbs in the metadata map, and later lets CQ handlers complete timestamps.

State and persistence: all structures are runtime channel state. Metadata FIFO counters are byte-sized with a mask sized to firmware metadata capacity.

Dependencies and integration: includes mlx5e core, stats, TX/RX, PTP classify/time headers, and workqueue support.

Risks: metadata FIFO/map helpers are intentionally small and assume caller-side capacity checks and synchronization. `mlx5e_use_ptpsq` relies on skb flow dissection and only selects ETH_P_1588 or UDP PTP event traffic.

Test signals: classifier coverage for L2/PTP UDP packets, metadata freelist empty checks, and compile coverage with PTP RX profile features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/qos.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/qos.c

Purpose: connects mlx5 firmware QoS nodes to mlx5e transmit queues for HTB offload and mqprio rate limiting.

Important APIs/functions: `mlx5e_qos_bytes_rate_check`, `mlx5e_qos_max_leaf_nodes`, `mlx5e_qid_from_qos`, QoS SQ open/activate/deactivate/close helpers, all-queue lifecycle helpers, `mlx5e_reset_qdisc`, `mlx5e_htb_setup_tc`, and mqprio rate-limit allocation/init/cleanup/get-node helpers.

Control flow: HTB setup validates unsupported prio/quantum fields, creates/destroys the HTB object, dispatches TC HTB commands to `htb.c`, and returns qids for leaf queue allocation/query. QoS SQ opening allocates per-channel RCU arrays, creates stats storage, opens CQ/SQ with the firmware node id, and publishes the SQ pointer. Activation disables the netdev queue, updates `txq2sq` mappings with a write barrier, and starts the SQ. Deactivation removes mappings before queues are restarted. MQPRIO creates a firmware root and one capped-bandwidth leaf per TC.

State and persistence: stores QoS SQ arrays per channel, stats arrays in `priv`, HTB state in `priv->htb`, and mqprio firmware node ids in `struct mlx5e_mqprio_rl`. Firmware QoS nodes persist until cleanup.

Dependencies and integration: depends on `en/htb.h`, queue builders in `params.c`, mlx5 core QoS commands, TC setup callbacks, RCU state access, and netdev qdisc APIs.

Risks: queue index math changes when PTP SQs or DCB TCs are enabled. `txq2sq` updates rely on barriers and queue stopping. Partial SQ open failures are tolerated but require null checks throughout lifecycle paths.

Test signals: HTB command matrix, channel reopen with existing leaves, PTP enabled qid mapping, RCU/NAPI close synchronization, mqprio max-rate nodes, and SQ open failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/qos.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/qos.h

Purpose: declares mlx5e QoS, HTB offload, QoS SQ lifecycle, and mqprio rate-limit APIs.

Important APIs/types: `BYTES_IN_MBIT`, QoS rate/capability helpers, `mlx5e_qid_from_qos`, QoS SQ open/activate/deactivate/close/reactivate/reset functions, all-queue lifecycle functions, `mlx5e_htb_setup_tc`, and opaque `struct mlx5e_mqprio_rl` lifecycle/accessors.

Control flow: HTB and channel code use this header to allocate/open/activate QoS queues when HTB is active and to dispatch TC qdisc commands.

State and persistence: no header-owned state; implementation stores queue arrays, stats, HTB object, and firmware QoS ids.

Dependencies and integration: includes mlx5 core device type; forward-declares mlx5e structures and TC HTB offload type.

Risks: callers must hold the appropriate driver state lock for lifecycle operations and must map qids through `mlx5e_qid_from_qos` before touching netdev queues.

Test signals: compile coverage in TC/HTB enabled builds and mqprio rate-limit flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bond.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bond.c

Purpose: handles bonding of mlx5 eswitch representors by assigning shared metadata and programming ingress/egress ACL behavior for active-slave failover.

Important APIs/functions: `mlx5e_rep_bond_init`, `mlx5e_rep_bond_cleanup`, `mlx5e_rep_bond_enslave`, and `mlx5e_rep_bond_unslave`. Internal notifier handlers process `NETDEV_CHANGEUPPER` and `NETDEV_CHANGELOWERSTATE`.

Control flow: init registers a per-netdev notifier when egress forward-to-vport ACLs are supported. Enslave creates or reuses metadata for the LAG master, allocates a slave entry, and programs ingress vport metadata. Unslave clears ingress metadata, removes egress bond ACLs, updates representor bond RX rules, and frees metadata when the last slave leaves. On lower-state changes, the active TX-enabled slave becomes the forwarding vport for passive representors; the active representor gets the unique metadata RX rule.

State and persistence: `struct mlx5e_rep_bond` owns a notifier and metadata list. Each LAG metadata object tracks eswitch, LAG netdev, metadata register value, slave list, and count. Hardware ACL programming persists until updated or unslaved.

Dependencies and integration: uses netdevice LAG events, representor private data, eswitch ACL helpers, match metadata allocation, and `mlx5e_rep_bond_update`.

Risks: all enslave/unslave paths require RTNL. Cleanup unregisters the notifier but does not explicitly walk metadata, relying on netdev unlink events. Incorrect active-slave handling can misdirect representor traffic.

Test signals: representor bond create/delete, active slave failover, metadata allocation exhaustion, mixed non-representor lower devices, and notifier unregister during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bond.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bridge.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bridge.c

Purpose: bridges Linux switchdev bridge events to mlx5 eswitch bridge offload operations for representor ports, peer eswitches, LAGs, VLANs, MDBs, FDBs, and bridge attributes.

Important APIs/functions: `mlx5e_rep_bridge_init` and `mlx5e_rep_bridge_cleanup`. Internal notifier callbacks handle netdev upper changes, switchdev blocking object/attribute changes, async FDB events, and periodic FDB aging/update work.

Control flow: init creates eswitch bridge offload state under RTNL, allocates an ordered workqueue, registers switchdev, blocking switchdev, and netdevice notifiers, then starts periodic update work. Netdev upper changes link/unlink local or peer vports to bridge masters after validating LAG shared-FDB constraints. Blocking switchdev callbacks add/delete VLANs and MDBs and set bridge attrs such as ageing time, VLAN filtering/protocol, multicast, and supported flags. Nonblocking FDB events are copied to heap work items, processed under RTNL, and then cleaned up.

State and persistence: state lives in `struct mlx5_esw_bridge_offloads`, including workqueue, notifiers, delayed update work, and eswitch bridge tables. Individual FDB work owns a dev reference and copied MAC address.

Dependencies and integration: uses Linux bridge/switchdev/netdevice notifiers, mlx5 eswitch bridge helpers, LAG shared-FDB checks, and representor vport/vhca-id discovery.

Risks: notifier contexts require careful allocation flags and async work. LAG and peer-eswitch paths depend on identifying the correct representor and hardware owner. Cleanup ordering must cancel delayed work and unregister all notifiers before destroying bridge state.

Test signals: bridge enslave/unenslave, VLAN/MDB add/delete, FDB add/delete to bridge/device, LAG master validation, peer representor offload, and teardown with queued FDB work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bridge.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bridge.h

Purpose: declares representor bridge-offload lifecycle hooks with compile-time stubs.

Important APIs/functions: `mlx5e_rep_bridge_init` and `mlx5e_rep_bridge_cleanup`, real when `CONFIG_MLX5_BRIDGE` is enabled and no-op otherwise.

Control flow: representor setup can call init/cleanup unconditionally; configuration controls whether switchdev bridge offload support is installed.

State and persistence: no header state. Implementation state is eswitch bridge offload context and notifiers.

Dependencies and integration: includes `en.h`; integrates representor initialization with optional eswitch bridge support.

Risks: non-bridge builds skip all bridge offload logic, so tests must cover both stub and enabled paths.

Test signals: build configurations with and without `CONFIG_MLX5_BRIDGE` and representor bridge lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/neigh.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/neigh.c

Purpose: tracks neighbour entries used by representor TC tunnel encapsulations and updates offloaded flows when ARP/ND state or MAC addresses change.

Important APIs/functions: `mlx5e_rep_neigh_init`, `mlx5e_rep_neigh_cleanup`, `mlx5e_rep_neigh_entry_lookup`, `mlx5e_rep_neigh_entry_create`, `mlx5e_rep_neigh_entry_release`, and `mlx5e_rep_queue_neigh_stats_work`.

Control flow: init creates an rhashtable, RCU list, encap mutex, delayed stats work, computes the minimum neighbour probe interval, and registers a netevent notifier. Neighbour update events allocate work in atomic context, hold the neighbour and hash entry, then under RTNL snapshot neighbour MAC/state and update each attached encap flow through `mlx5e_rep_update_flows`. Periodic stats work walks the RCU list with refcounted entries and updates neighbour-used values. Delay-probe updates adjust flow-counter sampling when relevant devices change.

State and persistence: `neigh_update` holds the hashtable, list, lock, notifier, and delayed work. Each `mlx5e_neigh_hash_entry` stores key, device, encap list, refcount, and RCU node. State is runtime only and tied to representor lifetime.

Dependencies and integration: uses ARP/ND neighbour tables, netevent notifier, flow counters, TC encap update hooks, RTNL, rhashtable, RCU, and tracepoints.

Risks: refcount/RCU/list interactions are delicate because neighbour events can race with encap detach and cleanup. Cleanup flushes the workqueue before destroying the table, so any new notifier event after unregister must be impossible.

Test signals: IPv4 and IPv6 neighbour updates, neighbour device changes, encap attach/detach races, delay-probe interval changes, cleanup with queued work, and flow reoffload after MAC change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/neigh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/neigh.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/neigh.h

Purpose: declares representor neighbour tracking APIs with stubs when TC action offload support is disabled.

Important APIs/functions: neighbour init/cleanup, lookup/create/release of `mlx5e_neigh_hash_entry`, and queueing neighbour stats work.

Control flow: TC tunnel encap code attaches flows to neighbour entries, netevent code updates them, and cleanup removes notifier/table state. Disabled builds return success or no-op for lifecycle functions.

State and persistence: no header-owned state; implementation stores hash/list/refcount state under `mlx5e_rep_priv`.

Dependencies and integration: includes `en.h` and `en_rep.h`; guarded by `CONFIG_MLX5_CLS_ACT`.

Risks: callers in enabled builds must release looked-up/created entries and hold required locks described in the implementation.

Test signals: build with and without `CONFIG_MLX5_CLS_ACT`, encap-neighbour reference balancing, and stats work scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/neigh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/tc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/tc.c

Purpose: implements TC offload plumbing for mlx5 representors, including direct and indirect block callbacks, tunnel neighbour encap attachment, flow reoffload, action offload, and representor RX metadata handling.

Important APIs/functions: `mlx5e_rep_tc_init/cleanup/enable/disable`, `mlx5e_rep_setup_tc`, `mlx5e_rep_tc_netdevice_event_register/unregister`, `mlx5e_rep_encap_entry_attach/detach`, `mlx5e_rep_update_flows`, `mlx5e_rep_tc_event_port_affinity`, and `mlx5e_rep_tc_receive`.

Control flow: direct TC setup registers ingress eswitch flower/matchall callbacks and normalizes FT offload rules into the reserved chain. TC init creates shared eswitch TC tables and unready-flow state. Indirect block registration supports tunnel devices, VLANs on the representor, macvlan passthru, bond-backed macvlan, and OVS internal-port egress when supported. Indirect flow callbacks route flower replace/destroy/stats to the uplink representor context. Action callbacks dispatch to mlx5e TC action implementations. RX handling decodes reg_c0/reg_c1 metadata, restores CT/tunnel/IPsec context, updates skb state, and forwards through `dev_queue_xmit` or GRO.

State and persistence: uplink representor state owns TC tables, unready flow list, indirect block list, tunnel entropy refs, neighbour encap links, and reoffload work. Flow hardware state persists in eswitch tables until removed.

Dependencies and integration: uses mlx5e TC core, neighbour tracking, mapping contexts, tunnel helpers, flow block APIs, fs chains, CT, sample, int-port, IPsec RX, and representor private data.

Risks: indirect block binding must reject unsupported devices and avoid duplicate binds. Encap updates require RTNL plus eswitch encap table lock. RX metadata parsing must keep bit masks aligned with firmware register layout; wrong decoding can mis-forward or drop packets.

Test signals: flower replace/delete/stats, matchall stats, FT offload chain/prio validation, indirect tunnel/VLAN/macvlan/OVS offloads, neighbour MAC changes, port-affinity reoffload, and representor RX with CT/tunnel/IPsec metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/tc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/tc.h

Purpose: declares representor TC offload lifecycle, flow update, encap-neighbour, setup, and receive APIs with disabled-build fallbacks.

Important APIs/functions: TC init/cleanup, netdevice event register/unregister, enable/disable, port-affinity event, `mlx5e_rep_update_flows`, encap attach/detach, `mlx5e_rep_setup_tc`, and `mlx5e_rep_tc_receive`.

Control flow: representor lifecycle calls init/register/enable and their cleanup pairs; netdev TC setup calls `mlx5e_rep_setup_tc`; RX code calls `mlx5e_rep_tc_receive` to decode offload metadata before delivering skbs.

State and persistence: no header state. Enabled implementation stores TC offload state under representor/uplink private data; disabled fallback receives packets through GRO without TC metadata processing.

Dependencies and integration: includes skb, `en_tc.h`, and `en_rep.h`; guarded by `CONFIG_MLX5_CLS_ACT`.

Risks: disabled fallback changes behavior significantly by bypassing metadata restoration, so feature-gated tests must cover both modes.

Test signals: compile both configurations, representor setup callbacks, encap API call balance, and RX fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/tc.h -->
