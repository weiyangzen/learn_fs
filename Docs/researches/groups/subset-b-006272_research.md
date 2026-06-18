# subset-b-006272 scheduler qdisc research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_htb.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_htb.c

Purpose: implements the classful Hierarchical Token Bucket qdisc, including software shaping, direct unshaped traffic, per-class filters, optional rate estimators, watchdog-driven wakeups, and hardware offload through `TC_SETUP_QDISC_HTB`. It schedules a tree of `htb_class` nodes where leaves own child qdiscs and inner nodes provide borrowing hierarchy.

Important APIs, types, and functions: `struct htb_sched` stores the class hash, root filter block, direct queue, watchdog/work item, per-level event queues, active row masks, and optional offload direct qdiscs. `struct htb_class` stores rate/ceil configs, token buckets, parent/children links, per-class filter block, leaf qdisc or inner feed trees, statistics, and rbtree nodes. Qdisc entry points are `htb_enqueue`, `htb_dequeue`, `htb_init`, `htb_attach`, `htb_reset`, `htb_destroy`, and `htb_dump`; class operations include `htb_change_class`, `htb_delete`, `htb_graft`, `htb_tcf_block`, `htb_bind_filter`, and stats/dump helpers.

Control flow: enqueue first calls `htb_classify`, which honors direct `skb->priority`, root filters, inner-class filters, and default class fallback. Packets classified as `HTB_DIRECT` enter `direct_queue`; leaf packets enqueue into `cl->leaf.q` and activate that leaf. Dequeue drains the direct queue first, then updates `q->now`, processes expired class-mode events from `wait_pq`, scans active rows by level and priority, resolves a leaf through feed trees with `htb_lookup_leaf`, dequeues from the child qdisc, advances DRR deficits, deactivates empty leaves, and charges the leaf plus ancestors through `htb_charge_class`. If no packet can be sent, the watchdog is scheduled at the nearest event time or a work item reschedules the root.

State and persistence behavior: state is entirely in-kernel and runtime-only. Token and ceil buckets are kept as nanosecond credit in `tokens`, `ctokens`, `t_c`, `buffer`, and `cbuffer`; `cmode` transitions among `HTB_CAN_SEND`, `HTB_MAY_BORROW`, and `HTB_CANT_SEND`. Rbtree membership (`row`, `feed`, `wait_pq`) persists only while a class is active or waiting. `htb_reset` cancels the watchdog, clears activity trees, resets direct packets and leaf queues, and returns classes to sendable mode. No file-backed persistence exists; user configuration is reconstructed through netlink dumps.

Dependencies and integration points: depends on qdisc core class hash, `pkt_cls` filter blocks, `psched_ratecfg`, `qdisc_watchdog`, `net_rate_estimator`, rbtree helpers, and netlink HTB attributes. Hardware offload integrates with `ndo_setup_tc(TC_SETUP_QDISC_HTB)` for create, destroy, node modify, leaf allocation, queue query, and leaf deletion. In offload mode, leaves are associated with hardware TX queues and child qdiscs are grafted to netdev queues instead of only the root software qdisc.

Risks: correctness depends on rbtree membership invariants and `RB_CLEAR_NODE` discipline; stale feed pointers are mitigated by `last_ptr_id` recovery. Class mutation is complex around parent leaf-to-inner and inner-to-leaf transitions, especially with offload rollback and queue movement. Token calculations clamp to `mbuffer`, and wrong rate/cell inputs could create shaping surprises. Direct queue overflow drops packets outside class stats. Hysteresis trades accuracy for fewer mode transitions. Offload stats use bias aggregation and can diverge if driver callbacks or queue migration fail.

Test signals: exercise class add/change/delete, deep tree rejection, default/direct classification, filters targeting inner classes, borrowing versus lending counters, watchdog wakeup after token exhaustion, qlen notifications after child drops, graft replacement, reset behavior, and netlink dump round trips. Offload tests should cover create failure rollback, leaf-to-inner transitions, last-child deletion, queue query bounds, stats aggregation, and device up/down graft paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_htb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_ingress.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_ingress.c

Purpose: implements the `ingress` and `clsact` pseudo-qdiscs used to attach classifier/action chains to device ingress and egress paths without normal enqueue/dequeue behavior. They are control-plane objects that bind `tcf_block`s into TCX mini qdisc entries.

Important APIs, types, and functions: `struct ingress_sched_data` owns one `tcf_block`, `tcf_block_ext_info`, and `mini_Qdisc_pair`; `struct clsact_sched_data` owns separate ingress and egress versions. `ingress_init` and `clsact_init` validate parent handles, create/fetch TCX entries with `tcx_entry_fetch_or_create`, initialize `mini_qdisc_pair`, and acquire blocks with `tcf_block_get_ext`. Destroy paths release blocks, decrement miniq references, remove inactive TCX entries, and decrement ingress/egress queue counters. Class ops expose `find`, `bind_tcf`, `tcf_block`, and block index setters/getters.

Control flow: creating an ingress qdisc only works under `TC_H_INGRESS`; clsact only works under `TC_H_CLSACT`. On init, the code increments the global ingress/egress queue accounting, installs a mini qdisc pair connected to the device TCX ingress or egress entry, configures binder type and `chain_head_change`, obtains the filter block, then binds the block into the miniq pair. Chain head changes call `mini_qdisc_pair_swap`, allowing packet path readers to see updated classifier heads. No packet enqueue/dequeue occurs in this file.

State and persistence behavior: runtime state is the filter block pointer, TCX entry reference, block index, and mini qdisc pair. Block indexes are set through qdisc ops and returned to userspace for shared block reporting. Destroy is responsible for releasing TCX entries only when no other TCX users remain. There is no persistent storage; netlink dump returns an empty options nest.

Dependencies and integration points: integrates with `net/tcx.h`, `pkt_cls`, `tcf_block_get_ext`, mini qdisc pairs, global ingress/egress queue counters, and module registration for `ingress` and `clsact`. Binder types distinguish `FLOW_BLOCK_BINDER_TYPE_CLSACT_INGRESS` and `FLOW_BLOCK_BINDER_TYPE_CLSACT_EGRESS`.

Risks: init error paths after TCX reference increments can leak references if future changes add failures without unwind. Parent handle validation is essential because these qdiscs are not normal root children. Destroy assumes RTNL-style protection and uses `rtnl_dereference` for TCX entries. clsact has two independent blocks, so partial init failure handling is a sensitive area.

Test signals: verify invalid parent rejection, creation/destruction of ingress and clsact, shared block indexes, filter attach/detach propagation through `chain_head_change`, TCX entry cleanup when no programs/mini qdiscs remain, and module registration rollback if clsact registration fails after ingress registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_ingress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_mq.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_mq.c

Purpose: implements the root `mq` classful multiqueue scheduler. It is a structural qdisc that exposes one class per TX queue and attaches one child qdisc to each device queue, while aggregating stats at the root.

Important APIs, types, and functions: the file uses `struct mq_sched` from scheduler internals. `mq_init_common`, `mq_destroy_common`, `mq_attach`, `mq_dump_common`, `mq_select_queue`, `mq_leaf`, `mq_find`, `mq_dump_class`, `mq_dump_class_stats`, and `mq_walk` are exported in the `NET_SCHED_INTERNAL` namespace and reused by related schedulers. `mq_offload`, `mq_offload_stats`, `mq_graft`, and `mq_dump` implement mq-specific offload and class operations. `mq_qdisc_ops` registers id `mq`.

Control flow: init requires `TC_H_ROOT` and a multiqueue device, preallocates an array sized by `dev->num_tx_queues`, and creates default child qdiscs with minor handles `1..num_tx_queues`. Attach grafts those children onto the corresponding netdev queues, hashes real TX queues, then frees the temporary array. Graft deactivates the device if needed, replaces a queue's sleeping qdisc, marks the new qdisc as one-TX-queue/no-parent, reactivates the device, and notifies hardware offload.

State and persistence behavior: before attach, child qdisc references live in `priv->qdiscs`; after attach the array is freed and the durable runtime state is in `netdev_queue->qdisc_sleeping`. Root qstats are reconstructed on dump by locking each child and summing per-CPU/basic/queue stats. Configuration is device-derived; there is no persistent storage or tunable netlink payload.

Dependencies and integration points: depends on multiqueue netdev APIs, `dev_graft_qdisc`, default qdisc selection, qdisc hash management, `qdisc_offload_dump_helper`, and `ndo_setup_tc(TC_SETUP_QDISC_MQ)`. It is also a library provider for shared mq root behavior.

Risks: init can return after partial child allocation and relies on destroy cleanup for allocated qdiscs. `mq_queue_get` must reject out-of-range class IDs or graft/leaf paths would dereference invalid queues. Stats aggregation must handle both lockless and locked child qdisc accounting. Offload support must tolerate `-EOPNOTSUPP`.

Test signals: create on non-root or single-queue devices should fail; multiqueue create should expose one class per TX queue. Test graft while device is up, stats aggregation across child qdiscs, class walking skip/stop behavior, offload create/destroy/graft/stats callbacks, and real TX queue count changes through `mq_change_real_num_tx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_mq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_mqprio.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_mqprio.c

Purpose: implements the root `mqprio` qdisc, mapping socket priorities to traffic classes and traffic classes to hardware TX queue ranges. It can configure software queue mapping or delegate ownership to hardware through `TC_SETUP_QDISC_MQPRIO`.

Important APIs, types, and functions: `struct mqprio_sched` stores child qdisc pointers, mode, shaper, hardware offload state, netlink flags, min/max rates, and frame preemption (`fp`) settings. Key routines are `mqprio_parse_opt`, `mqprio_parse_nlattr`, `mqprio_parse_tc_entries`, `mqprio_enable_offload`, `mqprio_disable_offload`, `mqprio_init`, `mqprio_attach`, `mqprio_graft`, `mqprio_dump`, `mqprio_dump_class_stats`, and `mqprio_walk`.

Control flow: init validates root placement, multiqueue support, classid capacity, option length, queue mapping via `mqprio_validate_qopt`, and offload capabilities. Extended netlink attributes are allowed only in hardware mode. Child qdiscs are precreated for every TX queue. If `qopt->hw` is set, the qdisc builds an offload request with optional mode/shaper/rate/preemption fields and calls `ndo_setup_tc`; otherwise it programs `netdev_set_num_tc` and each `netdev_set_tc_queue`. Priority-to-TC mappings are always applied to the netdev.

State and persistence behavior: child qdiscs move from the preattach array to netdev queues at attach. The netdev stores TC queue mappings and priority maps; `mqprio_qopt_reconstruct` reconstructs dumps from device state. Private state preserves offload mode, flags, rate arrays, and frame preemption values for dump/offload teardown. Destroy either disables hardware offload or clears `num_tc`.

Dependencies and integration points: uses the shared mqprio library, ethtool MAC merge/preemption support (`ethtool_dev_mm_supported`), netdev TC mapping APIs, child qdisc grafting, and `ndo_setup_tc(TC_SETUP_QDISC_MQPRIO)`. It shares `mq_change_real_num_tx` with mq-style roots.

Risks: extended attrs are tightly coupled to `qopt->hw`; accepting them in software mode would create state userspace cannot enforce. Hardware drivers may override or validate queue counts differently, so offload capability queries matter. Frame preemption must reject unsupported devices. Stats for virtual traffic classes unlock and relock around child qdisc locks, which is sensitive to locking order. Class IDs have two regions: per-queue classes and virtual traffic-class classes.

Test signals: validate queue count overlaps/ranges, hardware and software modes, DCB versus channel mode/shaper combinations, min/max rate dumping, frame preemption with and without MAC merge support, class walking order, virtual TC stats aggregation, child grafting while up, and destroy behavior for offload and non-offload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_mqprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_mqprio_lib.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_mqprio_lib.c

Purpose: provides shared mqprio helpers used by `mqprio` and related qdiscs such as taprio. The helpers validate traffic-class queue mappings, reconstruct a `tc_mqprio_qopt` from netdev state, and convert per-TC frame-preemption settings into an offload bitmask.

Important APIs, types, and functions: `mqprio_validate_qopt` is exported and validates `num_tc`, priority-to-TC map bounds, and optionally queue counts. `mqprio_validate_queue_counts` checks nonzero queue counts, range within `real_num_tx_queues`, and overlap unless explicitly allowed. `mqprio_qopt_reconstruct` fills `num_tc`, priority map, counts, and offsets from `struct net_device`. `mqprio_fp_to_offload` builds `preemptible_tcs` from `TC_FP_PREEMPTIBLE` entries.

Control flow: validation first rejects `num_tc > TC_MAX_QUEUE`, then verifies every `prio_tc_map` entry is less than `num_tc`. If requested, each TC queue interval `[offset, offset + count)` is checked for nonzero size, device bounds, and pairwise overlap. Reconstruction reads device TC state linearly. Frame-preemption conversion scans all queue slots and sets one bit per preemptible TC.

State and persistence behavior: this file owns no long-lived state. It reads caller-provided qopts and netdev fields, writes caller-provided output structs, and reports validation failures through extack messages.

Dependencies and integration points: depends on netdevice TC fields, netlink extack formatting, `TC_QOPT_MAX_QUEUE`, `TC_BITMASK`, and `TC_FP_*` constants. Exports symbols with GPL visibility for other scheduler modules.

Risks: callers choose whether queue counts are validated and whether overlap is allowed, so misuse can accept configurations a device cannot execute. Reconstruction trusts netdev state to be coherent. Error messages include queue count/offset data and should remain aligned with iproute2 expectations.

Test signals: unit-style tests should cover invalid `num_tc`, priority map entries outside range, zero queue counts, queue ranges exceeding `real_num_tx_queues`, overlapping intervals with overlap allowed and disallowed, reconstruction from programmed netdev TC state, and preemptible bitmask generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_mqprio_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_mqprio_lib.h -->
# sources/distributed-fs/ceph-client/net/sched/sch_mqprio_lib.h

Purpose: declares the shared mqprio helper API for validation, qopt reconstruction, and frame-preemption offload conversion.

Important APIs, types, and functions: forward-declares `struct net_device`, `struct netlink_ext_ack`, and `struct tc_mqprio_qopt`; includes `<linux/types.h>` for `u32`; and declares `mqprio_validate_qopt`, `mqprio_qopt_reconstruct`, and `mqprio_fp_to_offload`. The `mqprio_fp_to_offload` prototype references `struct tc_mqprio_qopt_offload` through scheduler headers included by users.

Control flow: no executable control flow exists in the header. It provides compile-time linkage between qdisc implementations and `sch_mqprio_lib.c`.

State and persistence behavior: no state is owned here. The header constrains callers to pass explicit input/output structures.

Dependencies and integration points: the include guard `__SCH_MQPRIO_LIB_H` prevents duplicate declarations. Consumers must include the appropriate packet scheduler definitions for mqprio constants and offload struct layout. The file is intentionally local to `net/sched`, not a broad userspace ABI header.

Risks: signature drift between this header and implementation would break mqprio/taprio builds. Because one prototype uses `TC_QOPT_MAX_QUEUE` and `struct tc_mqprio_qopt_offload`, include ordering matters for consumers.

Test signals: build coverage is the main signal: compile all mqprio-lib consumers, verify no missing declarations or incompatible prototypes, and ensure symbol exports in the C file match the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_mqprio_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_multiq.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_multiq.c

Purpose: implements the legacy `multiq` qdisc, a classful scheduler that maps packets to child bands based on `skb_get_queue_mapping()` and services bands round-robin while avoiding stopped hardware TX queues.

Important APIs, types, and functions: `struct multiq_sched_data` stores active band count, max bands, current round-robin band, root filter block/list, and an array of child qdiscs. Main functions are `multiq_classify`, `multiq_enqueue`, `multiq_dequeue`, `multiq_peek`, `multiq_tune`, `multiq_init`, `multiq_graft`, class dump/stat helpers, and `multiq_tcf_block`.

Control flow: enqueue runs root filters for actions only, then chooses the band from `skb_get_queue_mapping`; out-of-range mappings fall back to band 0. The selected child receives the skb, and root qlen increments only on success. Dequeue cycles from the last served band, skips stopped TX queues using `netif_xmit_stopped`, and dequeues the first available child packet. Tune sets `bands` to `real_num_tx_queues`, purges and removes children above the new band count, and creates default pfifo children for active bands that are still noop.

State and persistence behavior: runtime state consists of the child qdisc array and `curband`. `max_bands` follows `num_tx_queues`; `bands` follows `real_num_tx_queues`. Reset clears children and resets `curband`. No persistent storage exists; netlink dump emits bands and max bands.

Dependencies and integration points: depends on multiqueue netdev state, packet classifier blocks, child qdisc replacement, qdisc hash registration, and pfifo defaults. Unlike root `mq`, this qdisc is a normal enqueue/dequeue scheduler with one device queue as its parent qdisc queue.

Risks: tune allocation uses `q->max_bands - qopt->bands`, so assumptions about `real_num_tx_queues <= num_tx_queues` are important. Class/graft operations assume valid class indices returned by `multiq_find`. Filters do not choose a class; they only permit action handling before queue mapping. Stopped-queue skipping prevents head-of-line blocking but may starve a stopped band until hardware wakes.

Test signals: create on non-multiqueue devices should fail; changing real queue count should add/remove children; enqueue should honor queue mappings and fallback; dequeue should skip stopped queues and rotate fairly; grafting should replace one band; filter actions should drop/stolen packets correctly; dumps should report band counts and child handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_multiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_netem.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_netem.c

Purpose: implements the `netem` network emulator qdisc, adding configurable delay, jitter, loss models, ECN marking, duplication, reordering, corruption, rate serialization, and slot-based delivery windows. It can also act classfully by grafting a child qdisc behind the time FIFO.

Important APIs, types, and functions: `struct netem_sched_data` holds time-ordered queues (`t_root`, `t_head`, `t_tail`), optional child qdisc, watchdog, impairment parameters, correlated random states, PRNG seed/state, distribution tables, loss-model state, and slot state. Key functions are `netem_enqueue`, `netem_dequeue`, `tfifo_enqueue`, `netem_peek`, `netem_change`, `get_loss_clg`, `tabledist`, `packet_time_ns`, `netem_segment`, `get_slot_next`, dump/graft/class helpers, and `check_netem_in_tree`.

Control flow: enqueue decides duplication count, loss or ECN marking, optional orphaning, cloning, corruption, GSO segmentation when corrupting large packets, limit enforcement, and duplicate reinsertion through the root qdisc. It computes `time_to_send` from latency/jitter distribution plus rate serialization against the latest queued send time, or inserts selected reordering packets at the immediate head. Time-scheduled packets go into a fast linear tail queue when timestamps are monotonic, otherwise into an rbtree. Dequeue first drains immediate head packets, then checks the earliest time FIFO item and slot constraints, schedules the watchdog if not yet deliverable, and optionally moves matured packets into the child qdisc before final dequeue.

State and persistence behavior: runtime state includes queue contents, per-skb `time_to_send`, PRNG seed/state, correlation memory, Markov loss state, distribution tables allocated with `kvmalloc`, and slot byte/packet budgets. `netem_change` swaps new distribution tables under the tree lock and frees old tables afterward. Reset clears all internal queues, child queue, and watchdog. Dumps expose current parameters and PRNG seed but queued packet timing is not persistent.

Dependencies and integration points: uses qdisc watchdog, rbtree skb helpers, `prandom` state, random bytes, GSO segmentation, ECN helpers, reciprocal division for cell serialization, rtnetlink free helpers, netlink policies, and qdisc class ops for one optional child. `check_netem_in_tree` prevents unsafe combinations of duplicating netems in a qdisc tree.

Risks: impairment interactions are subtle: duplicate reinsertion must avoid recursively duplicating duplicates, corruption must handle checksum and GSO segmentation, and parent backlog corrections after segmentation must match the number and size of accepted segments. Time FIFO uses skb fields (`next`, `prev`, rbnode/tstamp storage) and must restore `skb->dev` before delivery. Negative time inputs are rejected for new 64-bit attrs, but legacy tick values are still converted. Slot scheduling can delay packets beyond their own timestamps.

Test signals: cover deterministic PRNG seed dumps, delay/jitter distribution behavior, rate serialization, slot packet/byte limits, random/4-state/Gilbert-Elliot loss, ECN marking versus drop, duplicate tree rejection, corruption of normal and GSO skbs, queue limit drops, child qdisc grafting, watchdog scheduling, reset cleanup, and netlink dump/change round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_netem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_pie.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_pie.c

Purpose: implements the PIE active queue management qdisc, controlling queue delay by periodically adjusting a probabilistic early drop/mark value and optionally estimating dequeue rate.

Important APIs, types, and functions: `struct pie_sched_data` contains `pie_vars`, `pie_params`, `pie_stats`, an adaptation timer, and a backpointer to the qdisc. Exported algorithm helpers include `pie_drop_early`, `pie_process_dequeue`, and `pie_calculate_probability`. Qdisc operations are `pie_qdisc_enqueue`, `pie_qdisc_dequeue`, `pie_change`, `pie_init`, `pie_reset`, `pie_destroy`, `pie_dump`, and `pie_dump_stats`.

Control flow: enqueue first enforces `sch->limit`, then calls `pie_drop_early` using backlog and packet size. If the random decision does not drop, the skb is tail-enqueued and enqueue time is recorded when dequeue-rate estimation is disabled. If PIE would drop and ECN is enabled with probability at or below 10%, ECN-capable packets are marked and enqueued instead. Dequeue pops the head packet and calls `pie_process_dequeue`, which updates queue delay from skb timestamps or from measured drain rate and reduces burst allowance. The timer periodically calls `pie_calculate_probability` under the root qdisc lock and reschedules itself by `tupdate`.

State and persistence behavior: all state is runtime: parameters, delay variables, drop probability, accumulated probability, drain-rate samples, burst allowance, and stats counters. `pie_change` updates parameters under the tree lock and drops excess packets if the limit shrinks. `pie_reset` clears the queue and reinitializes variables; destroy stops the timer. Dumps convert psched time back to microseconds and expose stats through xstats.

Dependencies and integration points: depends on `<net/pie.h>` for common PIE math/state, qdisc queue helpers, ECN marking, timers, psched time conversion, random bytes, and netlink attributes. Exported helpers can be reused by other PIE-derived qdiscs.

Risks: timer and enqueue/dequeue paths share variables, so READ/WRITE_ONCE and locking choices matter. Probability arithmetic uses fixed-point-style scaling and must avoid overflow/underflow. Bytemode scales probability by packet size only up to MTU. Limit reduction drops queued packets synchronously. Misconfigured `tupdate`, target, or alpha/beta values can create unstable delay behavior.

Test signals: validate default init, parameter changes and dumps, limit shrink backlog reduction, ECN marking threshold, bytemode behavior for small/large packets, dequeue-rate estimator on/off paths, timer probability adjustment, burst allowance decay, reset variable reinitialization, and xstats values for drops/marks/delay/probability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_pie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_plug.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_plug.c

Purpose: implements the `plug` qdisc, which buffers packets until explicit netlink control commands release one epoch or release indefinitely. It is designed for output buffering/commit workflows such as checkpoint-based fault tolerance.

Important APIs, types, and functions: `struct plug_sched_data` stores `unplug_indefinite`, `throttled`, byte `limit`, packet counts for current and last epochs, and packets currently allowed for release. Qdisc operations are `plug_enqueue`, `plug_dequeue`, `plug_init`, and `plug_change`; reset uses `qdisc_reset_queue`.

Control flow: enqueue enforces a byte backlog limit and, while not indefinitely unplugged, increments `pkts_current_epoch` before tail enqueue. Dequeue returns `NULL` when throttled; otherwise it drains all packets in indefinite mode or decrements `pkts_to_release` for finite release mode. When the release count reaches zero, the qdisc throttles itself until another release command. `plug_change` handles `TCQ_PLUG_BUFFER`, `TCQ_PLUG_RELEASE_ONE`, `TCQ_PLUG_RELEASE_INDEFINITE`, and `TCQ_PLUG_LIMIT`.

State and persistence behavior: epoch packet counters are volatile qdisc state. `TCQ_PLUG_BUFFER` rolls current epoch count into last epoch and starts a new one; `TCQ_PLUG_RELEASE_ONE` adds last epoch packets to the releasable count; `TCQ_PLUG_RELEASE_INDEFINITE` clears epoch counters and makes the qdisc pass-through until the next buffer command. No persistent storage exists.

Dependencies and integration points: uses basic qdisc tail/head queues, netlink `tc_plug_qopt`, `netif_schedule_queue` to restart transmission after release, device MTU/tx_queue_len for default limit, and module registration as `plug`.

Risks: release accounting is packet-count based, so drops or queue purges between buffer and release can alter what is actually available. Limit changes do not proactively trim backlog. The qdisc intentionally returns `NULL` while throttled, so watchdogs or callers must rely on release commands to reschedule. Counter overflow is possible in theory for long-running unbounded epochs.

Test signals: initialize with default and explicit limits; verify initial throttling; buffer/release-one sequencing across multiple epochs; indefinite release pass-through and re-plug behavior; limit drops; queue scheduling after release commands; reset behavior; invalid action and short netlink option rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_plug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_prio.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_prio.c

Purpose: implements the classful `prio` qdisc, a strict-priority band scheduler with configurable priority-to-band mapping, optional root filters, child qdiscs per band, and hardware offload support.

Important APIs, types, and functions: `struct prio_sched_data` stores band count, root filter block/list, `prio2band` map, and up to `TCQ_PRIO_BANDS` child qdiscs. Core functions are `prio_classify`, `prio_enqueue`, `prio_dequeue`, `prio_peek`, `prio_tune`, `prio_graft`, `prio_offload`, `prio_dump`, class stat/dump helpers, and `prio_tcf_block`.

Control flow: classification first honors class IDs encoded in `skb->priority` for this qdisc, otherwise runs root filters and handles actions. Without a valid filter result, it maps `skb->priority & TC_PRIO_MAX` through `prio2band`; invalid class IDs fall back to priority 0 mapping. Enqueue sends to the selected child and updates root backlog/qlen on success. Dequeue and peek scan bands from lowest index to highest, giving strict priority to lower-numbered bands. Tune validates band count and priomap, preallocates any new child qdiscs before locking, applies offload, commits the new map, purges removed bands, and releases old children.

State and persistence behavior: runtime state is the priomap and child qdisc pointers. Removed bands are purged before being put. Reset clears child qdiscs but keeps mapping. Dump emits `tc_prio_qopt` and optionally refreshes offload stats. There is no persistent storage.

Dependencies and integration points: integrates with classifier blocks, child qdisc grafting/hash, pfifo defaults, `qdisc_offload_dump_helper`, `qdisc_offload_graft_helper`, and `ndo_setup_tc(TC_SETUP_QDISC_PRIO)`. Qevents are not used; filters can still steal/drop/trap packets through TC actions.

Risks: strict priority can starve lower bands by design. Offload errors from `prio_offload` are ignored during tune, so software state may exist without hardware acceleration. The child array is fixed size and depends on validation before access. Backlog accounting must remain aligned between root and child.

Test signals: validate missing/invalid options, band count bounds, priomap entries, filter action handling, priority fallback paths, strict dequeue ordering, child graft defaults, removed-band purging, dump/offload stats, hardware graft notification, and destroy offload teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_prio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_qfq.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_qfq.c

Purpose: implements Quick Fair Queueing Plus, a classful fair-queueing qdisc that groups classes into aggregates by weight and maximum packet size, schedules aggregates using virtual start/finish times, and uses DRR among classes within each aggregate.

Important APIs, types, and functions: `struct qfq_sched` stores root filter block, class hash, virtual times `V/oldV`, in-service aggregate, total weight, group bitmaps, group array, and nonfull aggregate list. `struct qfq_class` owns stats, child qdisc, aggregate pointer, DRR deficit, and active-list node. `struct qfq_aggregate` owns timestamps, group pointer, class weight/lmax, inverse weight, budget, active classes, and nonfull linkage. Key functions include `qfq_change_class`, `qfq_enqueue`, `qfq_dequeue`, `qfq_activate_agg`, `qfq_schedule_agg`, `qfq_choose_next_agg`, `qfq_deactivate_agg`, `qfq_slot_insert`, `qfq_update_eligible`, and class ops.

Control flow: class creation validates weight/lmax, creates a child pfifo, finds or creates a matching aggregate, inserts the class, and grows the class hash. Enqueue classifies via direct classid or root filters, grows the aggregate lmax if the packet is larger, enqueues into the child, updates class/root stats, activates the class in its aggregate if idle, and schedules the aggregate if it became newly backlogged. Dequeue serves `in_serv_agg`; if the aggregate has no active class or insufficient budget, it charges actual service, requeues active aggregates with updated timestamps, chooses the next eligible aggregate, then dequeues one packet via DRR and advances virtual time by `len * iwsum`.

State and persistence behavior: state is runtime-only: virtual timestamps, per-aggregate slots, group bitmaps for eligible/ineligible and blocked/unblocked states, active class lists, budgets, deficits, and child queues. Reset deactivates classes and resets children but keeps configured classes. Destroy removes classes from aggregates, kills estimators, releases child qdiscs and the filter block.

Dependencies and integration points: uses qdisc class hash, classifier blocks, child qdisc grafting, rate estimators, bit operations, hlist/list helpers, fixed-point arithmetic constants, netlink `TCA_QFQ_WEIGHT` and `TCA_QFQ_LMAX`, and qdisc stats. It has no hardware offload path.

Risks: algorithm correctness depends on timestamp wraparound comparisons, group bitmap state transitions, and slot rotation/removal invariants. Dynamic lmax/weight changes can move classes between aggregates while preserving fairness only approximately; slot index capping handles some out-of-order effects. `wsum` must never exceed `QFQ_MAX_WSUM` and `iwsum` depends on nonzero weight sum. Child qdisc non-work-conserving behavior is warned but can reduce service.

Test signals: create/change/delete classes with weight/lmax bounds, total-weight overflow rejection, classifier and direct classid selection, enqueue lmax growth for large/GSO packets, DRR class rotation within an aggregate, aggregate budget exhaustion/requeue, group eligibility transitions, qlen notify deactivation, reset/destruction cleanup, and dump stats for class weight/lmax.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_qfq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_red.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_red.c

Purpose: implements Random Early Detection as a classful wrapper around one child qdisc, with optional ECN marking, harddrop/nodrop flags, adaptive RED timer, qevents for mark/early-drop, and hardware offload support.

Important APIs, types, and functions: `struct red_sched_data` stores limit, flags/userbits, adaptive timer, child qdisc, RED parameters/variables/stats, and qevents. Main routines are `red_enqueue`, `red_dequeue`, `__red_change`, `red_change`, `red_init`, `red_destroy`, `red_offload`, `red_adaptative_timer`, dump/stat helpers, and class graft/leaf/find operations.

Control flow: enqueue updates average queue length with `red_calc_qavg`, ends idle periods, asks `red_action` whether to pass, probabilistically mark/drop, or hard mark/drop. ECN-capable packets may be marked and sent through the mark qevent; non-ECT packets may still be queued in nodrop mode. Congestion drops can run the early-drop qevent before final drop. Accepted packets enqueue into the child and update root backlog/qlen; child drops increment `pdrop`. Dequeue pulls from the child, updates root stats, and starts an idle period when empty.

State and persistence behavior: RED state includes EWMA variables, idle tracking, stats counters, qevents, child qdisc, and optional adaptive timer. `__red_change` can create a new bfifo child, swap it under the tree lock, reset RED parameters/variables, and start/stop the adaptive timer. Destroy deletes qevents, timer, offload state, and child qdisc. Dumps reconstruct RED options and flags, not packet queue contents.

Dependencies and integration points: uses `<net/red.h>` algorithms, ECN helpers, qevent APIs, child qdisc grafting, netlink bitfield policy, qdisc offload helpers, and `ndo_setup_tc(TC_SETUP_QDISC_RED)`.

Risks: flag compatibility is split between historic `tc_red_qopt.flags` bits and new bitfield attributes; validation must keep combinations legal. Adaptive timer runs under root lock and must be canceled on destroy/change. Qevent handlers can consume the skb. Offload stats require driver support and the qdisc sets `TCQ_F_OFFLOADED` elsewhere based on core behavior. Child replacement purges old queues.

Test signals: validate required parms/stab, flag combinations including ECN/harddrop/nodrop, probabilistic and forced mark/drop counters, qevent mark/drop handling, adaptive timer operation, idle period behavior, child graft and dump class, offload replace/destroy/graft/stats, and netlink dump round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_red.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_sfb.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_sfb.c

Purpose: implements Stochastic Fair Blue as a classful wrapper around one child qdisc. It hashes flows into multiple virtual queue buckets, adjusts marking probabilities per bucket, identifies likely nonresponsive flows, and optionally ECN marks or drops before child enqueue.

Important APIs, types, and functions: `struct sfb_sched_data` stores child qdisc, classifier block/list, timing and queue parameters, token-bucket penalty state, active hash slot, double-buffering flag, two `sfb_bins` arrays, and stats. `struct sfb_bucket` stores virtual qlen and marking probability; `struct sfb_skb_cb` stores up to two hash values per skb. Key functions are `sfb_enqueue`, `sfb_dequeue`, `increment_qlen`, `decrement_qlen`, `sfb_swap_slot`, `sfb_rate_limit`, `sfb_classify`, `sfb_change`, `sfb_reset`, and dump/stat/class helpers.

Control flow: enqueue enforces hard qlen limit, advances hash perturbation on `rehash_interval`, enables double buffering during warmup, obtains a flow hash from an external classifier classid or skb hash, updates bucket probabilities based on virtual qlen, and records the minimum qlen/probability across levels. Flows with min qlen above `max` are bucket-dropped; flows with saturated probability are considered inelastic and subject to penalty token limiting. Otherwise a random draw below `p_min` causes ECN mark or early drop. Accepted packets enqueue to the child; only successful child enqueue increments virtual bucket qlens. Dequeue pulls from the child and decrements qlens recorded in the skb control block.

State and persistence behavior: all state is runtime: bucket qlens/probabilities, perturbation keys, double-buffering slot, rehash/token timestamps, penalty tokens, child queue, and counters. `sfb_change` replaces the child qdisc with a pfifo, resets all bins and perturbations, and installs new parameters. `sfb_reset` clears buckets and reinitializes slot 0. No persistent storage exists.

Dependencies and integration points: uses siphash perturbations, skb flow hashes, optional TC classifiers, ECN helpers, child qdisc grafting, qdisc class ops, and netlink `tc_sfb_qopt`. External classifiers can provide classid salt; otherwise skb hash drives bucket selection.

Risks: qlen accounting depends on saving hash values before child enqueue and decrementing the same hashes on dequeue. Double buffering temporarily accounts a packet in two hash tables. Probability is Q0.16 saturated arithmetic; parameter extremes can overdrop or undermark. `sfb_dump_class`, class change, and delete return `-ENOSYS`, so it is only minimally classful around one child. Hard queue limit uses root `sch->q.qlen`, not child-specific byte backlog.

Test signals: default parameter init, custom change/dump, classifier-provided salt versus skb hash, rehash and warmup double buffering, virtual qlen increment/decrement, ECN mark versus drop, inelastic penalty token behavior, child drop accounting, hard queue limit, grafting child qdisc, reset bucket clearing, and xstats maxqlen/maxprob/avgprob.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_sfb.c -->
