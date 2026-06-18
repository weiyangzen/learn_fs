# subset-b-006182 grouped research

This grouped report covers Linux networking core files from `sources/distributed-fs/ceph-client/net/core`. Each file section is bounded by reconciliation markers so it can be split into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/flow_dissector.c -->
# sources/distributed-fs/ceph-client/net/core/flow_dissector.c

Purpose: Implements the generic skb flow dissector used by packet classifiers, hashing, receive-side steering, BPF helpers, tunnel handling, and offload rule matching. It extracts protocol-independent keys from an skb or raw packet buffer, including basic protocol fields, L2/L3/L4 addresses, ports, VLANs, MPLS labels, tunnel metadata, conntrack state, ICMP, TCP flags, GRE key IDs, PPPoE, L2TPv3, ARP, CFM, TIPC, and hash material.

Important APIs, types, and functions: `skb_flow_dissector_init()` builds a `struct flow_dissector` from key descriptors and enforces mandatory control/basic keys. `__skb_flow_dissect()` is the central parser. Helper APIs include `skb_flow_get_ports()`, `skb_flow_get_icmp_tci()`, `skb_flow_dissect_meta()`, `skb_flow_dissect_ct()`, `skb_flow_dissect_tunnel_info()`, `skb_flow_dissect_hash()`, `flow_get_u32_src()`, `flow_get_u32_dst()`, `flow_hash_from_keys()`, `flow_hash_from_keys_seed()`, `make_flow_keys_digest()`, `__skb_get_hash_net()`, `__skb_get_hash_symmetric_net()`, `skb_get_hash_perturb()`, `skb_get_poff()`, and `__get_hash_from_flowi6()`. Static dissector instances `flow_keys_dissector`, `flow_keys_basic_dissector`, and symmetric dissector keys are initialized at `core_initcall`.

Control flow: `__skb_flow_dissect()` derives packet data, protocol, network offset, and header length from the skb when raw data is not supplied, with special DSA tag adjustment. It optionally delegates to an attached BPF flow dissector in the root namespace or current netns; non-`CONTINUE` BPF results are translated into target keys and terminate parsing. Native parsing then loops across L2/L3 protocols with bounded recursion (`MAX_FLOW_DISSECT_HDRS`). It handles VLAN stacking, PPPoE, MPLS stacks, FCoE, ARP/RARP, BATMAN, PTP, HSR/PRP, CFM, IPv4, and IPv6. A second loop processes IP protocols and extension headers, including GRE, IPv6 option headers, fragments, IP-in-IP, IPv6-in-IP, MPLS, TCP, ICMP, L2TP, ESP, AH, and port extraction. Success records transport offset and basic protocol fields; malformed or unsupported required headers return false but still set final control/basic fields consistently.

State and persistence: Runtime state is in exported dissector definitions, BPF program arrays attached to namespaces, the per-boot siphash secret `hashrnd`, skb control fields, metadata dst/tunnel info, and conntrack labels/mark/zone when enabled. No disk persistence exists. Hashing mutates a local `flow_keys` copy for symmetric ordering before siphashing and guarantees nonzero hashes.

Dependencies and integration points: This file sits at the center of `net/flow_dissector.h`, skb accessors, BPF netns attach infrastructure, DSA, tunnel metadata, conntrack, MPLS, PPP, GRE/PPTP, TIPC, VLAN, IPv6 extension parsing, and traffic control flower/offload matching. It supplies the key format consumed by `flow_offload.c`, cls_flower, RFS/RPS hashing, BPF packet helpers, and skb hash APIs.

Risks: Parser offset mistakes can create out-of-bounds header access, wrong flow hashing, classifier bypass, or tunnel offload mismatches. The BPF root-vs-netns exclusivity check is security-sensitive. Fragment handling must avoid reading L4 headers for non-first fragments unless explicitly allowed. Header-loop bounding prevents protocol recursion abuse. Conntrack and tunnel key extraction must preserve optional compile-time behavior. Hash changes can affect flow distribution and user-observable steering.

Test signals: Exercise IPv4/IPv6 TCP/UDP/SCTP/DCCP, ICMP id-bearing and non-id types, first and later fragments, VLAN/CVLAN, MPLS entropy labels, GRE/PPTP/TEB, PPPoE, L2TPv3, ESP/AH, ARP, CFM, HSR/PRP, DSA-tagged frames, tunnel metadata, and packets with BPF flow dissectors attached in init and non-init netns. Validate skb hash nonzero behavior, symmetric hash direction stability, `skb_get_poff()`, cls_flower key extraction, and malformed-short-header rejection under KASAN/KMSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/flow_dissector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/flow_offload.c -->
# sources/distributed-fs/ceph-client/net/core/flow_offload.c

Purpose: Provides generic flow rule, action, and flow block helper infrastructure used by traffic control and drivers to translate classifier rules into hardware or indirect offload callbacks. It is a glue layer between flow dissector match keys and driver setup blocks.

Important APIs, types, and functions: `flow_rule_alloc()` and `offload_action_alloc()` allocate flexible action containers and default every action `hw_stats` field to `FLOW_ACTION_HW_STATS_DONT_CARE`. The many `flow_rule_match_*()` accessors map typed flow matches to key/mask pointers using `skb_flow_dissector_target()`. Cookie helpers allocate/free `struct flow_action_cookie`. Flow block APIs include `flow_block_cb_alloc()`, `flow_block_cb_free()`, `flow_block_cb_lookup()`, `flow_block_cb_priv()`, `flow_block_cb_incref()`, `flow_block_cb_decref()`, `flow_block_cb_is_busy()`, and `flow_block_cb_setup_simple()`. Indirect offload APIs include `flow_indr_dev_register()`, `flow_indr_dev_unregister()`, `flow_indr_block_cb_alloc()`, `flow_indr_dev_setup_offload()`, and `flow_indr_dev_exists()`.

Control flow: Direct flow block setup handles bind/unbind commands, rejects unsupported binder types when ingress-only, avoids duplicate callbacks with `flow_block_cb_is_busy()`, allocates callback nodes, and attaches/removes them from both tc flow block and driver-owned lists. Indirect offload registration is guarded by `flow_indr_block_lock`; registering an already registered `(cb, cb_priv)` increments a refcount, while first registration adds the provider and immediately registers existing qdisc offload entries. Unregistration decrements, removes the provider on final reference, collects indirect block callbacks needing cleanup, releases the mutex, reoffloads actions off, invokes cleanup callbacks, and frees provider state. Setup for an indirect device records qdisc/device/data metadata on bind, removes it on unbind, and calls every registered indirect callback.

State and persistence: State is in process memory only: global lists for indirect block callbacks, indirect providers, and indirect device/qdisc records, plus callback refcounts and driver block lists. No persistent storage exists. Lifetime is controlled by mutex protection, list membership, callback cleanup hooks, and optional release functions.

Dependencies and integration points: Depends on flow dissector key layouts, `net/flow_offload.h`, rtnetlink/tc setup types, qdisc state, action reoffload callbacks, and driver-maintained flow block lists. Drivers use these helpers to participate in clsact/qdisc offload without duplicating block callback bookkeeping.

Risks: Refcount/list bugs can leak driver callbacks, leave stale indirect devices, or double-clean flow blocks. `flow_rule_match_*()` assumes the rule dissector actually contains the requested key; callers must check rule masks/used keys at higher layers. Indirect registration replays existing qdiscs while holding the mutex, so callback behavior must not create lock inversions. Returning count vs `-EOPNOTSUPP` in `flow_indr_dev_setup_offload()` is subtle and affects caller fallback.

Test signals: Bind/unbind flow blocks for ingress-only and unsupported binder types; duplicate bind should return `-EBUSY`, missing unbind `-ENOENT`. Register/unregister indirect providers with multiple refs and verify cleanup callback ordering. Exercise qdisc creation before and after provider registration. Validate all typed `flow_rule_match_*()` accessors against flower rules with key/mask pairs, including tunnel, ct, PPPoE, L2TP, and MPLS matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/flow_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gen_estimator.c -->
# sources/distributed-fs/ceph-client/net/core/gen_estimator.c

Purpose: Implements the generic rate estimator used by networking subsystems to derive smoothed packet-per-second and byte-per-second rates from basic counters. It is designed for controlled load service style estimation, not as a primary statistics collection mechanism.

Important APIs, types, and functions: `struct net_rate_estimator` stores source counter pointers, optional stats lock, per-cpu counter pointer, EWMA parameters, seqcount-protected samples, last byte/packet totals, timer state, and RCU head. Public APIs are `gen_new_estimator()`, `gen_kill_estimator()`, `gen_replace_estimator()`, `gen_estimator_active()`, and `gen_estimator_read()`. `est_fetch_counters()` snapshots `gnet_stats_basic_sync`; `est_timer()` updates EWMA values and reschedules itself.

Control flow: `gen_new_estimator()` validates netlink `gnet_estimator` options, allowing interval values from -2 through 3 and `ewma_log` from 1 through 30. It allocates state, initializes seqcount and source pointers, snapshots current counters, replaces any existing estimator under the optional lock, preserves old average rates, schedules the first timer tick, RCU-publishes the new pointer, and RCU-frees the old estimator after deleting its timer. Timer callbacks fetch counters, compute deltas scaled by interval, apply EWMA decay, publish `avbps` and `avpps` under seqcount with preemption disabled, advance `next_jiffies`, compensate delayed timers, and re-arm. `gen_kill_estimator()` atomically clears the RCU pointer, synchronously shuts down the timer, and frees by RCU. Reads use RCU plus seqcount retry.

State and persistence: Estimator state is dynamically allocated and referenced through an RCU pointer owned by the caller. It persists only while the owning qdisc/class/object keeps the pointer. Samples are in fixed-point form internally and right-shifted by 8 when exported.

Dependencies and integration points: Relies on `gen_stats.c` basic counter helpers, u64 stats synchronization, timers, jiffies, RCU, netlink estimator attributes, and optional caller spinlocks. `gnet_stats_copy_rate_est()` consumes `gen_estimator_read()` output.

Risks: Incorrect locking around caller counters can produce inconsistent rates. Timer replacement must avoid use-after-free and preserve existing estimates. Invalid EWMA/interval options must be rejected to avoid shifts outside supported range. Delayed timers can cause bursts or stale rates; the code clamps next scheduling when behind.

Test signals: Create, replace, read, and kill estimators for global and per-cpu counters. Validate option rejection for short attributes, interval out of range, and bad `ewma_log`. Use rapidly changing counters and delayed timer conditions to confirm monotonic timer rescheduling, seqcount-consistent reads, and no timer firing after `gen_kill_estimator()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gen_estimator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gen_stats.c -->
# sources/distributed-fs/ceph-client/net/core/gen_stats.c

Purpose: Implements generic netlink statistics dumping helpers for traffic control and networking objects. It serializes basic counters, hardware counters, rate estimates, queue stats, and application-specific xstats into TLV attributes, while optionally filling legacy `tc_stats` compatibility structures.

Important APIs, types, and functions: `gnet_stats_start_copy_compat()` and `gnet_stats_start_copy()` initialize a `struct gnet_dump`, optionally create a top-level nested stats attribute, and optionally acquire a stats spinlock. `gnet_stats_basic_sync_init()`, `gnet_stats_add_basic()`, and internal read helpers aggregate synchronized 64-bit counters from global or per-cpu sources. Copy APIs are `gnet_stats_copy_basic()`, `gnet_stats_copy_basic_hw()`, `gnet_stats_copy_rate_est()`, `gnet_stats_copy_queue()`, `gnet_stats_copy_app()`, and `gnet_stats_finish_copy()`.

Control flow: Start-copy zeroes the dump handle, records compatibility attribute types, stores the skb and padding type, and takes the caller lock with bottom halves disabled. The copy helpers aggregate source stats, update compatibility fields when requested, and append netlink attributes when a top-level destination exists. Basic and rate copies emit 64-bit extension attributes only when legacy-width values would truncate. Application stats are duplicated into `d->xstats` for later compatibility output. Finish-copy patches the top-level attribute length, emits compatibility stats/xstats, releases the lock, and frees duplicated xstats. On any netlink append failure, `gnet_stats_copy()` releases the lock, frees xstats, resets the dump handle fields, and returns `-1`.

State and persistence: State is per dump operation in `struct gnet_dump`; copied xstats may be temporarily allocated with `GFP_ATOMIC`. There is no persistent storage. Counter aggregation reads are lockless for per-cpu `u64_stats` with retry loops, or optionally protected by caller locks for running qdisc counters.

Dependencies and integration points: Depends on rtnetlink/netlink attribute APIs, `linux/gen_stats.h`, qdisc generic stats structures, `gen_estimator.c` for rate samples, per-cpu stats, and tc legacy ABI attribute IDs. It is used by qdisc/class/action dump paths that need consistent stats under optional locks.

Risks: Failure paths intentionally unlock the stats lock; callers must not unlock again after `-1`. Incorrect top-level tail adjustment around padding would corrupt nested attribute lengths. Running counter reads must not occur from hard IRQ when per-cpu/running paths are used. Truncation behavior must preserve legacy compatibility while exposing 64-bit counters.

Test signals: Dump stats with and without a top-level container, with compatibility attributes enabled and disabled, with per-cpu and single-counter sources, and with forced small skb tailroom to exercise failure unlock/free behavior. Validate 64-bit packet/rate extension emission only when needed, xstats duplication and cleanup, and lockdep behavior for `gnet_stats_basic_sync_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gen_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gro.c -->
# sources/distributed-fs/ceph-client/net/core/gro.c

Purpose: Implements core Generic Receive Offload registration, packet coalescing, flushing, NAPI receive handling, and fragment-based GRO helpers. It lets protocol offload modules merge compatible incoming packets into larger skbs before passing them up the stack.

Important APIs, types, and functions: `dev_add_offload()` and `dev_remove_offload()` manage RCU-protected `packet_offload` registrations on `net_hotdata.offload_base`. Merge helpers include `skb_gro_receive()` and `skb_gro_receive_list()`. Flush and completion APIs include `__gro_flush()`, `gro_receive_skb()`, `napi_get_frags()`, `napi_gro_frags()`, `__skb_gro_checksum_complete()`, `gro_init()`, and `gro_cleanup()`. Lookup helpers `gro_find_receive_by_type()` and `gro_find_complete_by_type()` expose registered offload callbacks by ethertype.

Control flow: New offload handlers are inserted by priority under `offload_lock` and removed with RCU synchronization. `gro_receive_skb()` marks NAPI ownership, initializes GRO offsets, calls `dev_gro_receive()`, and then finishes according to result. `dev_gro_receive()` hashes the skb to a GRO bucket, compares existing held skbs for same-flow eligibility, finds a protocol `gro_receive` callback, initializes `napi_gro_cb`, validates checksum state, invokes the protocol callback, completes any returned previous skb, and either holds, merges, consumes, or emits the skb normally. Bucket counts and a bitmask track pending flows. Flush walks pending buckets and completes skbs in age order. Fragment mode builds an skb from driver-provided frags, copies/pulls Ethernet headers into a common layout, and then feeds the same receive path.

State and persistence: Runtime state lives in `struct gro_node`: per-bucket skb lists/counts, bitmask, rx_list, rx_count, and cached NAPI id. Each skb uses `struct napi_gro_cb` in `skb->cb` for offsets, checksum state, count, age, flush/free flags, and same-flow state. Registered offloads live in the global hotdata list. No durable persistence exists.

Dependencies and integration points: Depends on skb memory/frags/truesize accounting, NAPI, protocol GRO callbacks for IPv4/IPv6 and others, `net_hotdata` tunables, checksum APIs, metadata dst, nfct, tc skb extensions, PSP coalesce comparison, busy-poll/NAPI ids, and tracepoints. It is a receive-path performance-critical component used by drivers and tunnel stacks.

Risks: Incorrect frag stealing or truesize updates can corrupt memory accounting, page-pool recycling, or skb lifetime. Same-flow comparisons must include metadata, VLANs, devices, slow GRO state, and security-sensitive extensions to avoid merging unrelated packets. GRO bucket limits and flush ordering affect latency. Checksum state transitions must not mark bad hardware checksums valid. Offload removal must wait for RCU readers before freeing handlers.

Test signals: Exercise TCP/IPv4 and TCP/IPv6 GRO, UDP tunnel GRO, GSO input to GRO, page-pool vs non-page-pool merge rejection, head_frag and frag_list merge paths, max GRO size, legacy max size, MAX_SKB_FRAGS fallback, bucket overflow flushing, `netif_elide_gro()`, fragment-based driver receive, checksum complete/unnecessary paths, and offload add/remove races under RCU/lockdep/KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gro_cells.c -->
# sources/distributed-fs/ceph-client/net/core/gro_cells.c

Purpose: Provides per-cpu GRO cells for virtual or tunnel devices that want to enqueue received skbs into a per-cpu NAPI context before running GRO and normal receive processing.

Important APIs, types, and functions: `struct gro_cell` contains a per-cpu skb queue, NAPI instance, and local BH lock. Public functions are `gro_cells_receive()`, `gro_cells_init()`, and `gro_cells_destroy()`. `gro_cell_poll()` is the NAPI poll method. `percpu_free_defer_callback()` frees per-cpu storage after an RCU grace period.

Control flow: `gro_cells_receive()` takes RCU, drops packets if the device is down, falls back to `netif_rx()` when cells are unavailable, the skb is cloned, or GRO is elided, otherwise locks the current CPU cell, checks queue length against `net_hotdata.max_backlog`, enqueues the skb, schedules NAPI for the first queued skb, and returns receive status. Polling dequeues up to budget under the local lock and passes each skb to `napi_gro_receive()`, completing NAPI when under budget. Init allocates per-cpu cells, initializes queues/locks, marks NAPI as no busy poll, adds NAPI to the device, and enables it for every possible CPU. Destroy disables/deletes NAPI, purges queued skbs, and frees per-cpu memory by `call_rcu()` or expedited synchronize fallback.

State and persistence: Per-cpu queues and NAPI state persist for the lifetime of the owning `gro_cells`. `gcells->cells` is nulled after destroy. Device references are implicit through NAPI registration; no disk persistence exists.

Dependencies and integration points: Depends on skb queues, per-cpu allocation, local locks, NAPI, `net_hotdata.max_backlog`, device up flags, RCU, and virtual/tunnel device receive paths.

Risks: Destroy must not free per-cpu cells while netpoll or RCU readers can still traverse device NAPI lists. Queue overflow must drop and account correctly. Cloned skbs bypass cells to avoid unsafe GRO mutation. Local lock use must match BH context assumptions and PREEMPT_RT behavior.

Test signals: Initialize/destroy cells on virtual devices, receive while device is up/down, queue overflow at `max_backlog`, cloned skb fallback, `netif_elide_gro()` fallback, NAPI budget-limited polling, and destroy during namespace cleanup with RCU callback allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gro_cells.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gso.c -->
# sources/distributed-fs/ceph-client/net/core/gso.c

Purpose: Implements Generic Segmentation Offload dispatch and validation helpers. It routes GSO skbs to registered protocol segmentation callbacks and computes whether segmented packets would fit network or MAC length constraints.

Important APIs, types, and functions: `skb_eth_gso_segment()` dispatches by explicit ethertype; `skb_mac_gso_segment()` derives network protocol through possible VLAN headers and dispatches after temporarily pulling MAC/VLAN headers. `__skb_gso_segment()` is the main segmentation entry and handles checksum/head preparation and GSO partial feature filtering. `skb_gso_validate_network_len()` and `skb_gso_validate_mac_len()` validate post-segmentation sizes. Internal helpers compute transport, network, and MAC segment lengths and handle `GSO_BY_FRAGS`.

Control flow: Segmentation lookup scans `net_hotdata.offload_base` under RCU for a `gso_segment` callback matching the protocol. `__skb_gso_segment()` first ensures the skb is writable when checksum fields need to be initialized, trims `NETIF_F_GSO_PARTIAL` unless the device's partial features can actually support the skb, initializes `SKB_GSO_CB`, resets MAC metadata, and calls MAC-level segmentation. After callback return, it warns for bad offload if checksum verification was required but no error was returned. Validation computes expected per-segment lengths from header offsets, encapsulation state, TCP/SCTP/UDP_L4 type, and gso_size; `GSO_BY_FRAGS` walks frag_list children instead of using a constant payload size.

State and persistence: No independent persistent state. It reads skb shared info, device feature bits, GSO control block space, protocol offload registrations, and skb header pointers.

Dependencies and integration points: Shares `net_hotdata.offload_base` with GRO, depends on packet offload callbacks registered by protocol stacks, skb GSO metadata, checksum conventions, netdev feature flags, VLAN/network protocol helpers, and driver transmit feature negotiation.

Risks: Header pull/push imbalance can corrupt skb layout. Incorrect partial-GSO feature filtering may send unsupported packets to drivers. Length validation must handle encapsulation and `GSO_BY_FRAGS` accurately to avoid oversized segments. Checksum preparation differs between TX and RX/OVS paths.

Test signals: Segment TCPv4/v6, SCTP, UDP_L4, VLAN-tagged, encapsulated, and unsupported protocol skbs. Validate GSO partial acceptance/rejection against device features, checksum-needed paths, `GSO_BY_FRAGS` frag list sizes, network MTU checks, and MAC length checks. Confirm callback absence returns `-EPROTONOSUPPORT` and malformed protocol detection returns `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/gso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/hotdata.c -->
# sources/distributed-fs/ceph-client/net/core/hotdata.c

Purpose: Defines cacheline-aligned global networking hot data defaults and the aligned data object used by other net/core paths.

Important APIs, types, and functions: Exports `struct net_hotdata net_hotdata`, initialized with the global offload list head and defaults for GRO normal batching, netdev budget, budget usecs, timestamp prequeue, backlog limit, qdisc burst, TX/RX weights, max skb frags, deferred skb free cap, and per-cpu memory reserve. Also defines `struct net_aligned_data net_aligned_data`.

Control flow: There is no executable control flow beyond static initialization and export. Other networking paths mutate or read fields directly or via sysctl-facing code.

State and persistence: This is runtime global kernel state. Defaults persist for the boot lifetime and may be adjusted by sysctl or subsystem initialization depending on field. No disk persistence is implemented here.

Dependencies and integration points: `gro.c` and `gso.c` use `offload_base`; `gro_cells.c` uses `max_backlog`; netdev budget and weights feed core receive/transmit scheduling; memory reserve and skb frag defaults integrate with socket memory and skb allocation policy.

Risks: Because fields are hot and global, layout/cacheline changes can affect performance. Unsafe updates to list or tunables without expected synchronization can race readers. Changing defaults alters system-wide networking behavior.

Test signals: Boot-time sanity should confirm offload list initialization before protocol registration, sysctl reads/writes for tunables, receive backlog behavior at default `max_backlog`, and performance regressions around hot cacheline fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/hotdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/hwbm.c -->
# sources/distributed-fs/ceph-client/net/core/hwbm.c

Purpose: Provides helper functions for hardware buffer manager pools, letting drivers allocate, construct, count, and free buffers sized either as page fragments or kmalloc objects.

Important APIs, types, and functions: `hwbm_buf_free()` frees buffers according to `bm_pool->frag_size`. `hwbm_pool_refill()` allocates one buffer with `netdev_alloc_frag()` for page-sized fragments or `kmalloc()` for larger buffers, then invokes an optional pool `construct` callback. `hwbm_pool_add()` fills a pool with a requested number of buffers under `buf_lock`.

Control flow: Pool add locks `buf_lock`, rejects already-full pools, rejects additions beyond configured size, checks unsigned overflow, then calls refill in a loop until either the requested count is reached or allocation/construct fails. It increments `buf_num` by the number actually added and returns that count. Refill frees the buffer and returns `-ENOMEM` if construction fails.

State and persistence: State is in the caller-owned `struct hwbm_pool`: configured size, current `buf_num`, `frag_size`, mutex, and optional construct callback. This file does not maintain global state or persistence.

Dependencies and integration points: Used by network drivers with hardware buffer managers, depends on skb fragment allocation, kmalloc, mutexes, and driver-specific construct callbacks that typically hand buffers to hardware rings.

Risks: The construct callback owns device-specific side effects; returning failure after partially handing a buffer to hardware would leak or corrupt ownership. `buf_num` is updated only after the loop, so callbacks must not depend on it during refill. Allocation context is `GFP_KERNEL` in pool add. Large `frag_size` changes allocation/free mode and must remain consistent.

Test signals: Add buffers to empty, partially full, and full pools; request too many buffers; simulate allocation and construct failures; verify free path for <= PAGE_SIZE and > PAGE_SIZE buffers; run with lockdep around concurrent add attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/hwbm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/ieee8021q_helpers.c -->
# sources/distributed-fs/ceph-client/net/core/ieee8021q_helpers.c

Purpose: Implements helper mappings between IEEE 802.1Q traffic types, NIC traffic classes, and IETF DSCP values. It codifies table-based queue mappings and DSCP-to-traffic-type policy used by networking components that configure priority handling.

Important APIs, types, and functions: `ieee8021q_tt_to_tc()` maps `enum ieee8021q_traffic_type` to a traffic class for one through eight queues using static tables based on IEEE 802.1Q-2022 Annex I examples. `ietf_dscp_to_ieee8021q_tt()` maps DSCP values to IEEE traffic types, with explicit handling for CS/AF/EF/VOICE_ADMIT values and fallback to `SIMPLE_IETF_DSCP_TO_IEEE8021Q_TT()`. Compile-time `TT_MAP_SIZE_OK()` assertions ensure each table covers all traffic types.

Control flow: Traffic-type-to-class validates the traffic type range, switches on `num_queues`, asserts the selected table size, and returns a mapped class or `-EINVAL` for unsupported queue counts. DSCP mapping switches over known DSCP values, grouping service classes into background, best effort, excellent effort, critical applications, video, voice, internetwork control, and network control, then falls back for values without explicit policy.

State and persistence: All mappings are static read-only arrays. No mutable state or persistence exists.

Dependencies and integration points: Depends on `net/dscp.h` and `net/ieee8021q.h`. It is likely consumed by drivers or qdisc/priority configuration paths that translate packet QoS markings into hardware queue or traffic class choices.

Risks: Policy choices affect QoS behavior and interoperability. Invalid queue counts return errors; callers must handle them rather than silently using class 0. DSCP fallback behavior must remain consistent with macro semantics. Table changes can reorder traffic priority for existing deployments.

Test signals: Unit-test all traffic types across 1-8 queues, invalid traffic type values, invalid queue counts, every explicitly mapped DSCP, and fallback DSCP values. Compile-time assertions should fail if `IEEE8021Q_TT_MAX` grows without table updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/ieee8021q_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/link_watch.c -->
# sources/distributed-fs/ceph-client/net/core/link_watch.c

Purpose: Implements deferred network device link state notification and RFC2863 operational state policy. It batches carrier/dormant/testing changes, rate-limits non-urgent notifications, and activates/deactivates qdiscs when device link state changes.

Important APIs, types, and functions: Public entry points are `linkwatch_init_dev()`, `__linkwatch_sync_dev()`, `linkwatch_sync_dev()`, `linkwatch_run_queue()`, and `linkwatch_fire_event()`. Internal pieces include `default_operstate()`, `rfc2863_policy()`, `linkwatch_urgent_event()`, `linkwatch_add_event()`, `linkwatch_schedule_work()`, `linkwatch_do_dev()`, `__linkwatch_run_queue()`, and delayed work `linkwatch_work`.

Control flow: `linkwatch_fire_event()` determines urgency, sets the device pending bit, queues the device with a held ref if not already pending, and schedules delayed work. Urgent events can force immediate work and set `LW_URGENT`; non-urgent work respects `linkwatch_nextevent` rate limiting. The work handler takes RTNL and runs the queue, optionally urgent-only. Queue processing splices the global list to a local list, skips absent devices or non-urgent devices during urgent-only runs, clears pending state with memory ordering, updates RFC2863 operstate, activates/deactivates qdisc state based on carrier, emits `netif_state_change()`, releases device refs, and requeues leftover work.

State and persistence: Global state includes `linkwatch_flags`, `linkwatch_nextevent`, delayed work, event list, and spinlock. Each device uses `link_watch_list`, a pending bit, and a tracker-held reference while queued. State is boot/runtime only.

Dependencies and integration points: Integrates with netdevice carrier/dormant/testing flags, DSA/lower-layer iflink logic, LAG devices, qdisc activation/deactivation, RTNL locking, workqueues, jiffies, and netdev reference tracking.

Risks: Reference release must occur under the documented lock/tracker ordering or devices can be freed while processed. Rate limiting must not delay urgent up/qdisc-changing events too long. `default_operstate()` has special behavior when devices are unregistering and RTNL may not be held. Pending-bit memory ordering protects against lost events. Lock ordering across event list spinlock, RTNL, and per-device ops locks is critical.

Test signals: Simulate carrier up/down, dormant/testing, lower-layer down through iflink, LAG port/master events, qdisc changing on up events, repeated flapping to test rate limit, urgent-only processing, sync during unregister, and concurrent fire/sync under lockdep and reftracker diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/link_watch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/lock_debug.c -->
# sources/distributed-fs/ceph-client/net/core/lock_debug.c

Purpose: Registers debug netdevice notifiers that assert expected RTNL, per-net RTNL, and device ops locking for netdevice events. It is a runtime diagnostic guard for networking lock discipline.

Important APIs, types, and functions: `netdev_debug_event()` is the notifier callback and is exported in the `NETDEV_INTERNAL` namespace. Initialization uses pernet operations `rtnl_net_debug_net_ops`, a global notifier block `rtnl_net_debug_block`, and `rtnl_net_debug_init()` at `subsys_initcall`.

Control flow: On each notifier event, `netdev_debug_event()` converts notifier info to `net_device`, switches over the event enum, and asserts the required lock context. `NETDEV_XDP_FEAT_CHANGE` requires `netdev_assert_locked()` then falls through to events requiring `netdev_ops_assert_locked()`, which then fall through to many events requiring `ASSERT_RTNL()`. `NETDEV_CHANGENAME` asserts per-net RTNL with `ASSERT_RTNL_NET(net)`. Per-net init allocates/registers a notifier per namespace; global init registers pernet ops and then the global notifier, unwinding on failure.

State and persistence: State is notifier registration state plus one per-net notifier block stored in generic net namespace storage. No durable persistence exists.

Dependencies and integration points: Depends on netdevice notifier chains, RTNL/per-net RTNL locking APIs, net namespace generic storage, and netdev ops locks. It observes broad netdevice lifecycle and configuration events.

Risks: Missing switch cases intentionally trigger compiler warnings because there is no default. Incorrect assertions can generate false positives or hide real lock violations. Registration failure handling must avoid dangling pernet subsystems.

Test signals: Build with warning-as-error after adding new netdev events to ensure switch coverage. Trigger representative notifier events under correct and incorrect locks in debug kernels, including XDP feature change, register/up/down/change, changename with per-net RTNL, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/lock_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/lwt_bpf.c -->
# sources/distributed-fs/ceph-client/net/core/lwt_bpf.c

Purpose: Implements BPF lightweight tunnel encapsulation operations, allowing routes to attach BPF programs for input, output, and xmit processing. It also supports BPF-triggered reroute, redirect on xmit, and IP encapsulation header push helper behavior.

Important APIs, types, and functions: `struct bpf_lwt_prog` stores a BPF program and display name; `struct bpf_lwt` stores input/output/xmit programs and address family. Core execution is `run_lwt_bpf()`. Datapath callbacks are `bpf_input()`, `bpf_output()`, and `bpf_xmit()`. State lifecycle is handled by `bpf_build_state()` and `bpf_destroy_state()`. Netlink helpers include `bpf_parse_prog()`, fill/size/cmp functions, and `bpf_encap_ops`. `bpf_lwt_push_ip_encap()` is the exported helper for pushing IPv4/IPv6 encapsulation headers.

Control flow: `run_lwt_bpf()` disables BH, sets BPF net context, refreshes skb data pointers, runs the program, and interprets return codes: `BPF_OK` and `BPF_LWT_REROUTE` continue, `BPF_REDIRECT` is allowed only where requested and performs `skb_do_redirect()`, `BPF_DROP` frees the skb and returns `-EPERM`, and invalid returns free the skb with `-EINVAL`. Input programs may reroute via `ip_route_input_noref()` or `ip6_route_input()` and then call `dst_input()`. Output programs run before the original dst output callback. Xmit programs can continue, redirect, or reroute through new IPv4/IPv6 output route lookup, then `dst_output()`. Build-state parses nested netlink attributes for IN/OUT/XMIT programs and optional headroom, obtains BPF programs by type, sets lwt redirect flags, and returns a `LWTUNNEL_ENCAP_BPF` state. Init registers BPF encap ops with lwtunnel.

State and persistence: BPF route state is embedded in `lwtunnel_state->data`; program references are held with `bpf_prog_get_type()` and released by `bpf_prog_put()`. Program names are duplicated from netlink and used for comparison/fill output. No disk persistence exists beyond route configuration managed elsewhere.

Dependencies and integration points: Integrates with `lwtunnel.c`, BPF program types `LWT_IN`, `LWT_OUT`, `LWT_XMIT`, skb redirect infrastructure, IPv4/IPv6 route lookup, dst input/output callbacks, GRE/UDP/IPIP GSO metadata, skb headroom expansion, and netlink route attributes.

Risks: Return-code handling owns skb lifetime; invalid or disallowed redirect paths must not leak or double-free. Reroute must reset dst and reserve headroom for the new device. `bpf_parse_prog()` currently leaks `prog->name` if `bpf_prog_get_type()` fails after name allocation unless caller destruction covers the partially initialized state. Comparison by name rather than program identity is documented as a FIXME and can affect delete matching. GSO encapsulation support only permits TCP GSO and must reject unsupported tunnel protocols safely.

Test signals: Attach LWT BPF IN/OUT/XMIT programs for IPv4 and IPv6 routes; exercise OK, DROP, REDIRECT, REROUTE, and invalid return values. Verify xmit redirect and reroute, original input/output fallback, missing orig callbacks, netlink build errors, headroom limit rejection, fill/cmp behavior, program reference release, and `bpf_lwt_push_ip_encap()` with IPv4, IPv6, GRE, UDP tunnel, IPIP, GSO and non-GSO skbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/lwt_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/lwtunnel.c -->
# sources/distributed-fs/ceph-client/net/core/lwtunnel.c

Purpose: Provides generic lightweight tunnel infrastructure for route encapsulation types such as MPLS, ILA, SEG6, BPF, RPL, IOAM6, and XFRM. It manages encap ops registration, state construction/destruction, netlink serialization, comparison, and datapath dispatch.

Important APIs, types, and functions: Exports static key `nf_hooks_lwtunnel_enabled`. State and registration APIs include `lwtunnel_state_alloc()`, `lwtunnel_encap_add_ops()`, `lwtunnel_encap_del_ops()`, `lwtunnel_build_state()`, `lwtunnel_valid_encap_type()`, `lwtunnel_valid_encap_type_attr()`, and `lwtstate_free()`. Netlink/route helpers are `lwtunnel_fill_encap()`, `lwtunnel_get_encap_size()`, and `lwtunnel_cmp_encap()`. Datapath callbacks are `lwtunnel_output()`, `lwtunnel_xmit()`, and `lwtunnel_input()`.

Control flow: Encapsulation ops are stored in an RCU pointer array indexed by encap type and installed/removed with `cmpxchg`; removal synchronizes the network stack. State build validates type, looks up ops under RCU, grabs the module owner, calls the type-specific `build_state()`, and drops the module ref on failure. Validation can autoload modules named `rtnl-lwt-<TYPE>` for supported types. Attribute validation walks nexthops and validates any `RTA_ENCAP_TYPE`. Free calls type-specific destroy if present and drops the module owner. Fill/size/compare dispatch to registered ops if available. Datapath output/xmit/input verify dst/lwtstate, enforce device transmit recursion limits, dispatch through type-specific callbacks under RCU, and free the skb on unsupported or invalid paths.

State and persistence: Global state is the RCU `lwtun_encaps[]` ops table and the netfilter static key. Per-route runtime state is `struct lwtunnel_state`, allocated with optional private data and module reference ownership. Persistence of route configuration is outside this file.

Dependencies and integration points: Integrates with rtnetlink route attributes, nexthop parsing, module autoload, dst entries, route output/input paths, per-encap modules such as BPF (`lwt_bpf.c`), MPLS/SEG6/etc., RCU, module refcounts, and dev transmit recursion accounting.

Risks: Module refcounting must match successful state builds and frees. Missing ops or unsupported callbacks free skbs in datapath, which is correct but easy to mis-handle in callers. Input expects softirq context. `lwtstate_free()` indexes `lwtun_encaps[lws->type]` without revalidating type, relying on valid constructed state. Recursion guard protects against route loops and must remain in every datapath.

Test signals: Register/unregister encap ops, validate module autoload, build/fill/size/cmp/free states for each encap type, parse multipath nexthop attrs, exercise output/xmit/input success and unsupported callbacks, route loop recursion limit, invalid dst/lwtstate, and concurrent ops removal under RCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/lwtunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/mp_dmabuf_devmem.h -->
# sources/distributed-fs/ceph-client/net/core/mp_dmabuf_devmem.h

Purpose: Declares the page-pool dmabuf device-memory provider interface used when `CONFIG_NET_DEVMEM` is enabled, and provides no-op/error inline stubs when it is disabled.

Important APIs, types, and functions: Enabled builds declare `mp_dmabuf_devmem_init()`, `mp_dmabuf_devmem_alloc_netmems()`, `mp_dmabuf_devmem_destroy()`, and `mp_dmabuf_devmem_release_page()`. Disabled builds inline `init` as `-EOPNOTSUPP`, allocation as `0`, destroy as no-op, and release as `false`.

Control flow: There is no runtime control flow in the header beyond compile-time selection. Callers can use the API unconditionally and rely on stubs to report unsupported device memory.

State and persistence: State is held by the page pool and implementation compiled elsewhere when enabled. This header stores no state and has no persistence.

Dependencies and integration points: Includes `net/netmem.h` and operates on `struct page_pool` and `netmem_ref`. It integrates with page-pool receive memory, dmabuf-backed device memory, and network drivers capable of using devmem-backed buffers.

Risks: Callers must treat `0` allocation and `-EOPNOTSUPP` init as unsupported, not as transient allocation success. Enabled/disabled behavior must remain ABI-compatible for code built across config combinations. Release returning false in stubs means normal page-pool release paths must handle non-devmem netmem.

Test signals: Build with `CONFIG_NET_DEVMEM=y` and disabled. For disabled builds, verify callers handle `-EOPNOTSUPP`, null netmem allocation, no-op destroy, and false release. For enabled builds, test page-pool init/destroy and devmem netmem allocation/release through the real implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/mp_dmabuf_devmem.h -->
