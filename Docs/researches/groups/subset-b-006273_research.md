# subset-b-006273 research

Grouped research for the requested source files under `sources/distributed-fs/ceph-client/net/sched` and `sources/distributed-fs/ceph-client/net/sctp`. Each section preserves the source path and is bounded for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_sfq.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_sfq.c

## Purpose
`sch_sfq.c` implements the Linux traffic-control `sfq` qdisc, a stochastic fairness queueing scheduler. It hashes packets into per-flow slots, schedules active slots using a deficit round-robin style quantum, and optionally applies RED/ECN behavior per hashed flow. The implementation is optimized for low memory by storing slot/link references as `u16` indexes rather than pointers.

## Important APIs, types, and functions
- `struct sfq_sched_data` is the qdisc private state: packet/flow limits, hash divisor, perturbation key, classifier block, hash table, slot array, RED parameters/stats, depth lists, active round-robin tail, quantum, and perturbation timer.
- `struct sfq_slot` stores one hashed flow queue, including skb intrusive queue anchors, queue length, round-robin link, depth-list link, hash index, deficit allotment, backlog, and `red_vars`.
- `sfq_classify()` maps an skb to a 1-based class/hash bucket using either explicit `skb->priority`, configured tc filters via `tcf_classify()`, or `skb_get_hash_perturb()`.
- `sfq_enqueue()` is the core enqueue path: classify, allocate a free slot for a new hash, apply RED/ECN decisions, enforce per-flow depth and global qdisc limit, update backlog/depth/round-robin state, and drop from the longest flow when over global limit.
- `sfq_dequeue()` walks the active ring, refills slot allotment by `quantum`, dequeues from the head of an eligible slot, removes empty flows from the hash table, and updates qdisc stats.
- `sfq_rehash()` drains all queued skbs and rebuilds the hash/slot layout when the perturbation key changes, avoiding out-of-order behavior from simply changing hashes in place.
- `sfq_change()` parses legacy and v1 `tc_sfq_qopt` options, validates quantum/divisor/perturb/RED settings, swaps RED state, trims over-limit backlog, and arms/cancels the perturbation timer.
- `sfq_init()`, `sfq_destroy()`, `sfq_dump()`, and class ops expose the qdisc to `tc`, filters, per-bucket stats, and module registration via `register_qdisc()`.

## Control flow
Initialization creates empty depth lists, default limit/depth/divisor/flows/quantum, random perturbation, classifier block, and deferred timer, then allocates `ht[]` and `slots[]` after optional option parsing. Enqueue classifies packets to buckets; a missing bucket consumes an unused slot from `dep[0]`, initializes RED state, and adds the slot to the active ring. Existing slots may RED-mark/drop before queueing. Dequeue always serves `q->tail->next`, rotating slots whose `allot` is exhausted and deducting packet length from allotment for non-empty slots. Timer-driven perturbation changes the hash key under the root qdisc lock and rehashes only when no filters are configured.

## State and persistence behavior
All runtime state is in qdisc memory: hash table, slot queues, RED averages, perturbation timer, and qdisc/class stats. No disk persistence exists. Slot membership is tracked simultaneously in depth lists (`dep[]`) and the active ring, so length changes must always go through `sfq_inc()`/`sfq_dec()`. The perturbation key persists only for the lifetime of the qdisc instance and is periodically regenerated when configured. Destruction tears down the classifier block, timer, slot/hash allocations, and RED parameters.

## Dependencies and integration points
The file integrates with the traffic-control qdisc API (`struct Qdisc_ops`, `Qdisc_class_ops`), tc filters (`tcf_block`, `tcf_classify()`), qdisc stats/backlog helpers, RED helpers from `<net/red.h>`, skb hashing with SipHash perturbation, and netlink option/dump ABI types from packet scheduler headers. Module alias `NET_SCH("sfq")` enables autoload from `tc qdisc add ... sfq`.

## Risks and edge cases
Hash collisions merge flows by design, weakening fairness. `sfq_init()` applies `sfq_change()` before allocating arrays, so option changes must avoid touching `ht[]`/`slots[]` before allocation; current `sfq_change()` may trim queues but `sch->q.qlen` is still empty during init. RED and headdrop paths adjust backlog by deltas, making accounting regressions likely if packet length or qdisc helper semantics change. Perturbation rehash can drop packets if the new hash layout exceeds maxflows/depth. `q->change` is `NULL` in `sfq_qdisc_ops` despite the presence of `sfq_change()`, so runtime changes may be unavailable in this snapshot unless wired elsewhere.

## Test signals
Useful tests include `tc qdisc add` with default and v1 RED parameters, classifier-directed class ids, perturbation with queued packets, global limit pressure, per-flow `depth` pressure, headdrop vs taildrop behavior, ECN marking counters, per-class stats dumps, and module autoload/unload. Packet accounting should verify `sch->q.qlen`, backlog, drops, overlimits, and tree reductions after RED drops, over-limit longest-flow drops, and rehash drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_sfq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_skbprio.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_skbprio.c

## Purpose
`sch_skbprio.c` implements the `skbprio` qdisc, a bounded priority queue keyed directly by `skb->priority`. It is intended for congestion scenarios where higher-priority packets should displace already queued lower-priority packets rather than merely waiting behind them.

## Important APIs, types, and functions
- `struct skbprio_sched_data` owns one `sk_buff_head` and one `gnet_stats_queue` for each priority, plus cached `highest_prio` and `lowest_prio` indexes.
- `calc_new_high_prio()` and `calc_new_low_prio()` rescan non-empty priority queues when the cached extrema become empty.
- `skbprio_enqueue()` clamps packet priority to `SKBPRIO_MAX_PRIORITY - 1`, enqueues while below `sch->limit`, drops the incoming packet if it is not above the current lowest priority, or admits it and tail-drops from the lowest-priority queue.
- `skbprio_dequeue()` removes from the current highest-priority queue, updates qdisc/class stats, and resets extrema when the qdisc becomes empty.
- `skbprio_change()`, `skbprio_init()`, `skbprio_dump()`, `skbprio_reset()`, and `skbprio_destroy()` manage the `limit`, queue initialization, netlink dump, and purge behavior.
- Class ops expose a class per priority value for stats and walking; the qdisc registers with id `skbprio`.

## Control flow
Init creates all priority queues, zeros per-priority stats, sets `highest_prio=0`, `lowest_prio=SKBPRIO_MAX_PRIORITY-1`, and defaults the global limit to 64 packets. Enqueue is O(1) in the common case: accept below limit, otherwise compare against the lowest non-empty priority. If the incoming priority is higher, it is queued and one packet from the tail of the lowest-priority queue is dropped. Dequeue always services the highest non-empty priority and recalculates extrema only when that priority queue drains.

## State and persistence behavior
All state is volatile qdisc memory. There is no timer, no classifier, and no child qdisc. The important persistent-in-memory invariant is that `highest_prio`/`lowest_prio` describe non-empty queue bounds or reset to their defaults when all queues are empty. `qstats[]` accumulates per-priority backlog, drops, and overlimits until reset/destroy.

## Dependencies and integration points
The file depends on the generic qdisc API, skb queue helpers, `gnet_stats`, and `tc_skbprio_qopt` netlink ABI. Module alias `NET_SCH("skbprio")` supports tc autoload. It does not use tc filter blocks; priority assignment is expected from socket/classification code before enqueue.

## Risks and edge cases
`qstats[prio].qlen` is passed to `gnet_stats_copy_queue()` but this file updates backlog/drops/overlimits, not the per-priority `qlen` field, so class queue-length stats may under-report. Enqueue uses `BUG_ON(!to_drop)` for an invariant violation in the full-queue replacement path; a stale `lowest_prio` would become fatal. The algorithm strongly favors high numeric `skb->priority`; callers must share that convention. Limit changes are immediate and can make an existing queue over-limit without trimming until future enqueue/drop activity.

## Test signals
Exercise priorities below, equal to, and above the current lowest priority at full limit; verify high priority packets displace low priority tail packets. Validate dequeue ordering from highest to lowest priority, reset behavior, `tc -s class/qdisc` stats, and runtime limit changes through netlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_skbprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_taprio.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_taprio.c

## Purpose
`sch_taprio.c` implements the Time Aware Priority Scheduler qdisc for IEEE 802.1Qbv-style gate control lists. It maps traffic classes to TX queues, opens and closes gates by schedule, optionally assists `SO_TXTIME` by assigning packet transmit timestamps, and can fully offload the schedule to hardware through `ndo_setup_tc(TC_SETUP_QDISC_TAPRIO)`.

## Important APIs, types, and functions
- `struct taprio_sched` is the qdisc private state: child qdiscs per TX queue, flags, clock conversion state, offload state, RCU-protected operational/admin schedules, hrtimer, current schedule entry, per-TC TXQ cursors, queueMaxSDU/preemption configuration, and txtime delay.
- `struct sched_gate_list` represents a schedule: entries, base/cycle times, cycle extension, per-TC maximum open durations, max frame lengths, and RCU reclamation.
- `struct sched_entry` represents one GCL entry: gate mask, interval, command, calculated per-TC gate durations, budgets, gate close times, end time, and next txtime.
- `taprio_enqueue()`, `taprio_enqueue_one()`, and `taprio_enqueue_segmented()` enforce max SDU, validate socket-provided txtime intervals, assign txtime in assist mode, and enqueue to the child qdisc selected by skb queue mapping.
- `taprio_dequeue()` chooses packets according to current gate mask. It supports normal TC-priority round robin and a compatibility path for drivers with broken mqprio behavior.
- `advance_sched()` is the software hrtimer callback that advances current entries, handles cycle restarts/admin-to-oper transitions, refreshes budgets/gate close times, and schedules the qdisc.
- `parse_taprio_schedule()`, `parse_sched_list()`, `taprio_parse_mqprio_opt()`, `taprio_parse_tc_entries()`, and `taprio_parse_clockid()` implement netlink validation and schedule construction.
- `taprio_enable_offload()`, `taprio_disable_offload()`, `taprio_sched_to_offload()`, `taprio_offload_get()`, and `taprio_offload_free()` manage hardware offload commands and shared offload object lifetime.
- `taprio_init()`, `taprio_change()`, `taprio_attach()`, `taprio_graft()`, dump/stats/class ops, and notifier registration integrate with qdisc lifecycle and netdevice changes.

## Control flow
Init requires root attachment on a multiqueue device, allocates one default pfifo child qdisc per TX queue, initializes the hrtimer and schedule state, records mqprio capability quirks, and calls `taprio_change()`. Change parses flags first, rejects simultaneous txtime-assist and full-offload, freezes flags after first configuration, parses/validates mqprio and TC entries, builds a new admin schedule, optionally programs mqprio mappings, parses the GCL, resolves clock semantics, derives queueMaxSDU, then either programs hardware offload or software/txtime mode. In software mode, a high-resolution timer advances `current_entry`, while dequeue enforces gates, guard bands, and byte budgets. In txtime-assist mode, enqueue computes `skb->tstamp` from the schedule and child qdiscs are later driven by ETF or driver timing. In full-offload mode, children are attached directly to TX queues and hardware is expected to enforce the schedule.

## State and persistence behavior
Schedules are in-memory RCU objects. `oper_sched` is active, `admin_sched` is pending, and old schedules are freed by `call_rcu()`. The hrtimer and `current_entry` track software schedule progress; full offload promotes admin to oper immediately for visibility but relies on hardware time for actual activation. Per-entry budgets are atomics because dequeue consumes them while schedule state is read under RCU. `taprio_list` plus a netdevice notifier lets link-speed changes recompute `picos_per_byte` and queueMaxSDU. There is no disk persistence.

## Dependencies and integration points
This file depends on qdisc core, mqprio helper code (`sch_mqprio_lib.h`), netlink ABI attributes for TAPRIO, netdevice TX queue/class mapping APIs, ethtool link settings and timestamp info, ethtool MAC Merge/preemption support, `ndo_setup_tc` offload hooks, hrtimers, RCU, static keys for mqprio quirks, GSO segmentation, socket `SO_TXTIME`, and optional driver offload stats. Module alias `NET_SCH("taprio")` supports tc autoload.

## Risks and edge cases
Time arithmetic and schedule transitions are the highest-risk areas: base time in the past is advanced to the next cycle, cycle extension semantics are marked as FIXME, and full offload visibility is only approximated without driver state callbacks. QueueMaxSDU uses estimated frame duration from link speed and optional size tables; missing size tables can make frame length estimates inaccurate. Txtime-assist assumes PHC/system clock synchronization outside the kernel. Full offload forbids explicit clockid and requires a PTP clock. Changing flags, clockid, or mqprio mapping on a running schedule is rejected, so update workflows must recreate the qdisc for those changes. GSO segmentation still drops oversized segments rather than segmenting to exact gate-fit size.

## Test signals
Tests should cover software mode, txtime-assist, and full-offload-capable devices or mocked `ndo_setup_tc`. Validate netlink rejection for invalid flags, missing clockid, full-offload clockid, too-small intervals/cycle time, unsupported preemption, unsupported queueMaxSDU, and running mapping changes. Runtime tests should check gate enforcement, guard bands, budget exhaustion, TXQ round robin per TC, admin-to-oper schedule replacement, base-time-in-past behavior, link speed notifier recomputation, dump of oper/admin schedules, child qdisc grafting, and offload stats handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_taprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_tbf.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_tbf.c

## Purpose
`sch_tbf.c` implements the Token Bucket Filter qdisc. It rate-limits packets using a main token bucket and optional peak-rate bucket, stores packets in a child qdisc, and schedules wakeups through a qdisc watchdog when insufficient tokens are available.

## Important APIs, types, and functions
- `struct tbf_sched_data` stores configured byte limit, maximum packet size, main/peak bucket depths, rate configs, current token counters, timestamp checkpoint, child qdisc, and watchdog.
- `psched_ns_t2l()` converts nanoseconds to bytes for rate-table compatibility, including ATM link-layer adjustment and overhead subtraction.
- `tbf_enqueue()` drops or GSO-segments packets larger than `max_size`, then enqueues into the child qdisc and mirrors qdisc backlog/qlen.
- `tbf_dequeue()` peeks the child, replenishes tokens from elapsed time, checks main and peak token availability, dequeues only when both buckets can pay for the packet, otherwise schedules the watchdog for the required time.
- `tbf_change()` parses nested TBF attributes, computes rate/peak configs, validates peak > rate and nonzero burst, creates or updates the child bfifo, swaps qdisc state under tree lock, and triggers hardware offload replacement.
- `tbf_offload_change()`, `tbf_offload_destroy()`, `tbf_offload_dump()`, and `tbf_offload_graft()` integrate with `TC_SETUP_QDISC_TBF`.
- Class ops expose the single child qdisc for grafting, walking, dumping, and leaf lookup.

## Control flow
Init creates the watchdog, starts with `noop_qdisc`, requires options, records current time, and delegates configuration to `tbf_change()`. Enqueue validates packet size and possible GSO segmentation before storing packets in the child. Dequeue never reorders: if the head packet lacks tokens, the watchdog is scheduled and the qdisc reports overlimit rather than searching for a smaller later packet. Reset purges the child and restores full buckets. Destroy cancels watchdog, destroys offload state, and puts the child.

## State and persistence behavior
Token counters, rate settings, child qdisc, and watchdog are volatile qdisc instance state. `q->t_c` is the last token checkpoint in nanoseconds. Runtime reconfiguration resets tokens to full buffer/mtu and may replace the child qdisc. Offload state is pushed to the driver but not persisted by this file.

## Dependencies and integration points
The file uses packet scheduler rate helpers, netlink TBF ABI, GSO segmentation, fifo child qdisc helpers, qdisc watchdog, qdisc classful grafting, and `ndo_setup_tc` offload hooks. Module alias `NET_SCH("tbf")` enables tc autoload. The default child is `bfifo` when a positive limit is configured.

## Risks and edge cases
Rate/latency correctness depends on nanosecond conversion, overhead handling, and peak bucket math. Very small bursts relative to MTU are warned but still allowed unless computed `max_size` is zero. GSO segmentation can alter qlen/backlog accounting; all paths need tree reduction validation. Limit only applies to the default fifo child; after grafting another child qdisc, the legacy limit is not necessarily effective. Offload errors are not fatal on change if helper behavior ignores unsupported devices, so software/hardware state visibility should be inspected in driver tests.

## Test signals
Validate rate shaping with and without peak rate, watchdog wakeups, no-reordering under a blocked head packet, GSO segmentation success/failure, malformed netlink attributes, peak <= rate rejection, burst/limit changes, child grafting, dump round trips including 64-bit rates, and offload replace/destroy/graft/stats callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_tbf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_teql.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_teql.c

## Purpose
`sch_teql.c` implements the TEQL link equalizer. Loading the module creates one or more virtual `teqlN` master netdevices and matching qdisc types; attaching the qdisc as root on physical slave devices lets the master transmit by rotating among available slaves.

## Important APIs, types, and functions
- `struct teql_master` embeds a dynamically registered `Qdisc_ops`, the virtual master device, circular slave qdisc list, module list link, and master TX stats.
- `struct teql_sched_data` stores the next slave pointer, master pointer, and per-slave skb queue.
- `teql_enqueue()` queues packets up to the slave device `tx_queue_len`; `teql_dequeue()` feeds queued packets to the master and wakes the master when a slave becomes available.
- `teql_qdisc_init()` validates root-only use, prevents loops, checks header/flag/MTU compatibility, and inserts the qdisc into the master's circular slave list.
- `teql_master_xmit()` is the master device transmit path: it rotates through slave qdiscs, checks running/stopped state, resolves neighbor headers, tries the slave TX lock, calls `netdev_start_xmit()`, updates stats, and advances the slave pointer.
- `teql_resolve()` and `__teql_resolve()` handle neighbor-cache resolution for devices requiring L2 headers.
- `teql_master_open()`, `teql_master_close()`, `teql_master_mtu()`, and stats ops implement the master netdevice behavior.
- `teql_init()` allocates/registers `teql%d` devices and matching qdisc ops according to `max_equalizers`; `teql_exit()` unregisters them.

## Control flow
Module init allocates each master netdevice, then registers a qdisc whose id equals the device name. A slave joins by installing that qdisc as root; qdisc init links it into the master's circular slave list and adjusts master MTU/flags when appropriate. Packets transmitted on the master loop over slaves from `master->slaves`, skipping stopped or detached qdiscs, resolving headers, and attempting immediate slave transmit. If all candidates are busy, the master queue is stopped; if no usable resolution/device exists, the packet is dropped and error/drop counters increase.

## State and persistence behavior
State is module and netdevice memory only: master device list, circular slave lists, per-slave skb queues, and TX counters. The master device persists while the module is loaded. Destroying a slave qdisc unlinks it and resets the master queue when the last slave is removed.

## Dependencies and integration points
The file integrates deeply with netdevice registration, qdisc registration, neighbor cache, dst entries, L2 header generation, netdev TX queue locking/state, module parameters, and ARP/header flags. It is a root qdisc and virtual netdevice pair rather than a normal standalone qdisc.

## Risks and edge cases
TEQL can cause packet reordering, especially across links with different rates; the source comments warn that large speed differences make the equalized link unusable. Address resolution only works for protocols using neighbor cache. The circular slave list manipulation is delicate during qdisc destroy. Header length, MTU, and flag compatibility checks happen at attach/open time and can reject mixed devices. Master TX mutates `skb->dev` and pulls headers during retry paths, so error paths and retries are sensitive to skb layout assumptions.

## Test signals
Test module load with multiple `max_equalizers`, creation of `teqlN` devices/qdiscs, root-only attach rejection, loop prevention, MTU/header compatibility, attach/detach of first and last slave, master open without slaves, round-robin TX across active slaves, busy queue stopping/waking, neighbor resolution failure/retry behavior, MTU change validation, and stats increments for successful TX, errors, and drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_teql.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/Kconfig -->
# sources/distributed-fs/ceph-client/net/sctp/Kconfig

## Purpose
`net/sctp/Kconfig` defines kernel configuration switches for SCTP support, SCTP object-count debugging, default cookie authentication policy, and SOCK_DIAG support.

## Important APIs, types, and functions
- `menuconfig IP_SCTP` is a tristate enabling SCTP protocol support. It depends on `INET` and selects crypto/hash and tunnel dependencies: SHA1, SHA256, crypto utils, CRC32C, and UDP tunnel support.
- `config SCTP_DBG_OBJCNT` enables `/proc/net/sctp/sctp_dbg_objcnt` object counters when `PROC_FS` is available.
- The cookie-HMAC choice defaults to `SCTP_DEFAULT_COOKIE_HMAC_SHA256`, with an alternative `SCTP_DEFAULT_COOKIE_HMAC_NONE`.
- `config INET_SCTP_DIAG` depends on `INET_DIAG` and follows it as a tristate for netlink socket diagnostics.

## Control flow
Configuration starts with `IP_SCTP`; all nested options are visible only when SCTP is enabled. The default cookie HMAC choice influences compile-time defaults used by SCTP sysctl/protocol initialization. Diagnostic support is enabled automatically when inet diag is enabled in compatible tristate form.

## State and persistence behavior
Kconfig values become build-time configuration and persist in the kernel `.config`. Runtime state is not managed in this file, but selected options control compiled objects, default cookie authentication behavior, and availability of proc/diag interfaces.

## Dependencies and integration points
This file feeds Kbuild and C preprocessor conditionals used by the SCTP Makefile and implementation files. It links SCTP to IPv4/INET, crypto primitives, CRC32C checksum support, UDP tunnel encapsulation, procfs debugging, sysctl-selected cookie HMAC defaults, and inet diag.

## Risks and edge cases
Disabling `IP_SCTP` hides all nested SCTP features. Selecting cookie HMAC `None` weakens cookie authentication defaults unless administrators override sysctl policy. `INET_SCTP_DIAG` is tied to `INET_DIAG`; diagnostic tooling will be absent when inet diag is not built. Debug object counts add diagnostic visibility but may slightly affect allocation/free paths via counters.

## Test signals
Build matrix coverage should include `IP_SCTP=y/m/n`, `SCTP_DBG_OBJCNT=y/n` with procfs, both cookie-HMAC defaults, `INET_SCTP_DIAG=y/m/n`, and IPv6 on/off because the Makefile conditionally adds IPv6 support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/Makefile -->
# sources/distributed-fs/ceph-client/net/sctp/Makefile

## Purpose
`net/sctp/Makefile` defines how SCTP protocol support and SCTP diagnostics are built from their component objects.

## Important APIs, types, and functions
- `obj-$(CONFIG_IP_SCTP) += sctp.o` builds the main SCTP module/built-in object.
- `obj-$(CONFIG_INET_SCTP_DIAG) += sctp_diag.o` builds the inet diag support object.
- `sctp-y` lists core protocol objects: state machine, protocol, endpoint/association, transport, chunks, make-chunk logic, input/output queues, socket API, primitive handling, auth, offload, stream schedulers, and interleaving.
- `sctp_diag-y := diag.o` maps the diag aggregate to `diag.o`.
- Conditional additions include `objcnt.o`, `proc.o`, `sysctl.o`, and `ipv6.o`.

## Control flow
Kbuild aggregates the listed `sctp-y` objects into `sctp.o` when `CONFIG_IP_SCTP` is enabled. Optional object lists are appended based on configuration. If IPv6 is modular or built-in, `ipv6.o` is included in SCTP via `subst m,y`.

## State and persistence behavior
This file has no runtime state. Its build decisions persist in the compiled kernel/module layout.

## Dependencies and integration points
The Makefile is the bridge between Kconfig symbols and SCTP implementation files. It includes the files researched in this subset: `endpointola.o`, `associola.o`, `chunk.o`, `bind_addr.o`, `debug.o`, `auth.o`, and diagnostic `diag.o`.

## Risks and edge cases
Omitting an object from `sctp-y` can produce unresolved symbols or silently remove protocol behavior. The IPv6 conditional uses `subst m,y` so IPv6 object code is included whenever IPv6 is available as built-in or module, which must match the SCTP module's symbol expectations. Diagnostic support is a separate object and module dependency path.

## Test signals
Build SCTP as built-in and module, with IPv6 built-in/module/disabled, diag enabled/disabled, proc/sysctl toggled, and debug object counts enabled to verify object aggregation and symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/associola.c -->
# sources/distributed-fs/ceph-client/net/sctp/associola.c

## Purpose
`associola.c` implements the SCTP association abstraction: allocation, initialization, lifetime, peer transport management, delayed input processing, association migration/update, PMTU/fragmentation state, receive-window accounting, association IDs, and ASCONF queue cleanup.

## Important APIs, types, and functions
- `sctp_association_init()` fills a provided association from endpoint/socket defaults: timers, TSNs, rwnd, streams, queues, bind address, peer capabilities, AUTH parameters, and random/auth chunks.
- `sctp_association_new()`, `sctp_association_free()`, `sctp_association_hold()`, `sctp_association_put()`, and `sctp_association_destroy()` manage allocation, reference counts, endpoint/socket holds, timers, queues, transports, auth keys, bind addresses, IDR entries, and RCU freeing.
- `sctp_assoc_add_peer()`, `sctp_assoc_rm_peer()`, `sctp_assoc_lookup_paddr()`, `sctp_assoc_del_nonprimary_peers()`, and `sctp_assoc_control_transport()` manage peer transport lists, hash table entries, path state, PMTU, heartbeat/SACK options, notifications, and active/retransmission path selection.
- `sctp_assoc_bh_rcv()` drains the association inqueue, handles first AUTH-before-COOKIE-ECHO special handling, enforces AUTH-required chunk placement, updates last-data/transport timestamps and stats, and dispatches chunks to `sctp_do_sm()`.
- `sctp_assoc_migrate()` moves an association between sockets/endpoints, used by peeloff-style workflows.
- `sctp_assoc_update()` updates an existing association from a new temporary association during COOKIE-ECHO/restart handling, including peer parameters, transports, TSN map, stream reset, AUTH peer vectors, and active key recomputation.
- `sctp_assoc_update_retran_path()`, `sctp_select_active_and_retran_path()`, and `sctp_assoc_choose_alter_transport()` select active/retransmission paths by state, error count, and last-heard time.
- `sctp_assoc_update_frag_point()`, `sctp_assoc_set_pmtu()`, and `sctp_assoc_sync_pmtu()` derive data fragmentation thresholds from PMTU, stream header size, user limits, and transports.
- `sctp_assoc_rwnd_increase()` and `sctp_assoc_rwnd_decrease()` update advertised receive window and may enqueue window-update SACKs.
- `sctp_assoc_set_bind_addr_from_ep()`, `sctp_assoc_set_bind_addr_from_cookie()`, `sctp_assoc_lookup_laddr()`, `sctp_assoc_set_id()`, and ASCONF cleanup helpers manage local addresses and association identity.

## Control flow
New associations start from socket/endpoint policy, then build queues, streams, bind address state, initial TSNs/tags, timers, AUTH vectors, and random parameters. Peer transports are added as remote addresses become known; the first transport becomes primary/retransmission path, and later transport state changes recompute active/retrans paths. Incoming chunks are processed asynchronously from the inqueue through the SCTP state machine with AUTH gating. Freeing marks the association dead, removes it from endpoint/socket accounting, drains queues/timers/transports/auth/ASCONF state, then drops the final reference so destruction can remove the IDR entry and free by RCU.

## State and persistence behavior
Association state is rich in-memory protocol state: SCTP state, timers, TSNs, rwnd/rwnd pressure, peer transport list/hash membership, path choices, stream state, AUTH keys/vectors, ASCONF queues and ack cache, bind addresses, PMTU/frag point, and stats. It is not persisted across reboot. Reference counts on endpoint/socket/association/transport/chunks and RCU list deletion protect concurrent input, timers, and lookups.

## Dependencies and integration points
The file depends on the SCTP endpoint, socket, transport, inqueue/outqueue/ulpqueue, state machine, stream, tsnmap, auth, ASCONF, ulpevent notification, IDR association registry, timers, IPv6 support, and kernel socket memory accounting. It is one of the core objects in the SCTP module and is called by input, socket, and state-machine code.

## Risks and edge cases
Lifetime is complex: timers may hold association references, inqueue work holds references, transports are RCU-deleted and unhashed, and association destruction warns if not marked dead. Peer removal must migrate transmitted chunks and reset cached path pointers to avoid use-after-free. Restart/update logic must preserve or reset TSNs according to association state. Receive-window math tracks `rwnd`, `rwnd_over`, and `rwnd_press`; accounting mistakes can advertise incorrect windows. AUTH chunk placement is silently discarded when missing required AUTH, which is correct but can obscure debugging. `sctp_assoc_add_peer()` failure after route/hash setup must unwind correctly.

## Test signals
Exercise association create/free under timer activity, endpoint backlog accounting for TCP-style listeners, adding/removing primary and non-primary transports, transport UP/DOWN/PF notifications, retransmission path election across states/error counts, COOKIE-ECHO restart/update paths, peeloff migration, AUTH-required chunk discard, first AUTH+COOKIE-ECHO handling, PMTU changes, rwnd increase/decrease/window-update SACK emission, association ID allocation/removal, and ASCONF ack cache cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/associola.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/auth.c -->
# sources/distributed-fs/ceph-client/net/sctp/auth.c

## Purpose
`auth.c` implements SCTP-AUTH support: HMAC algorithm selection, endpoint and association shared-key management, derivation of association secrets from peer/local AUTH parameters, chunk authentication policy, HMAC calculation, and socket API helpers for adding/deleting/deactivating keys and HMAC lists.

## Important APIs, types, and functions
- `sctp_hmac_list` describes supported HMAC ids: SHA1 and SHA256 are usable; reserved ids have zero length.
- `sctp_auth_key_put()`, `sctp_auth_create_key()`, `sctp_auth_shkey_create()`, `sctp_auth_shkey_hold()`, `sctp_auth_shkey_release()`, and `sctp_auth_destroy_keys()` manage sensitive key bytes and shared-key containers with refcounts.
- `sctp_auth_make_key_vector()`, local/peer vector helpers, `sctp_auth_compare_vectors()`, `sctp_auth_asoc_set_secret()`, and `sctp_auth_asoc_create_secret()` implement RFC key-vector concatenation and association secret derivation.
- `sctp_auth_asoc_copy_shkeys()` copies endpoint shared keys into an association; `sctp_auth_asoc_init_active_key()` computes the active association key and marks queued chunks needing AUTH.
- `sctp_auth_get_shkey()`, `sctp_auth_get_hmac()`, `sctp_auth_asoc_get_hmac()`, `sctp_auth_asoc_verify_hmac_id()`, and `sctp_auth_asoc_set_default_hmac()` provide lookup and negotiation helpers.
- `sctp_auth_send_cid()` and `sctp_auth_recv_cid()` evaluate whether a chunk type should be authenticated, ignoring forbidden chunk ids in CHUNKS parameters.
- `sctp_auth_calculate_hmac()` computes SHA1 or SHA256 HMAC over the AUTH chunk and subsequent packet bytes.
- `sctp_auth_ep_add_chunkid()`, `sctp_auth_ep_set_hmacs()`, `sctp_auth_set_key()`, `sctp_auth_set_active_key()`, `sctp_auth_del_key_id()`, `sctp_auth_deact_key_id()`, `sctp_auth_init()`, and `sctp_auth_free()` implement endpoint/association configuration APIs.

## Control flow
Endpoint initialization allocates HMAC and CHUNKS parameter buffers and a null key. Association creation copies endpoint shared keys, records active key id, and stores local AUTH parameters. Once peer AUTH parameters are available, active key initialization builds local and peer vectors, orders them numerically, concatenates optional endpoint key plus vectors, installs the association secret, and updates queued chunks that now require AUTH. Send/receive paths query chunk id policy, and AUTH chunk generation calls `sctp_auth_calculate_hmac()` with the appropriate active or temporary key.

## State and persistence behavior
Endpoint and association key lists are in-memory linked lists of `sctp_shared_key`, each optionally pointing to sensitive `sctp_auth_bytes`. Key bytes are freed with `kfree_sensitive()`. Associations cache `asoc_shared_key`, `active_key_id`, selected `shkey`, default HMAC id, and peer AUTH parameters. Deactivated keys remain listed until safe to free and can generate ULP notifications. No key material is persisted by this code.

## Dependencies and integration points
The file uses kernel SHA1/SHA256 HMAC helpers, SCTP endpoint/association/chunk structures, AUTH parameter structures from SCTP headers, ulpevent notifications for key free events, outqueue chunk lists, and debug object counters. It is initialized from endpoint creation and used by chunk creation, input validation, and socket option handlers.

## Risks and edge cases
Key-vector length arithmetic checks only `sctp_auth_create_key()` overflow; parameter lengths must be validated before reaching these helpers. HMAC id lookup assumes callers pass a supported id to `sctp_auth_get_hmac()`; unsupported ids can index reserved entries. `sctp_auth_set_key()` contains duplicate `memcpy()` into the new key buffer, harmless but suspicious. Active-key replacement rolls back on association secret allocation failure, so tests need to cover rollback. AUTH chunk policy intentionally ignores INIT/INIT-ACK/SHUTDOWN-COMPLETE/AUTH in CHUNKS parameters. Deactivation semantics rely on refcount/list state to decide when userland can free a key.

## Test signals
Test endpoint auth initialization/free, HMAC list validation requiring SHA1, unsupported HMAC rejection, key add/replace/delete/active/deactivate for endpoint and association, active-key secret recomputation, rollback on allocation failure, peer/local vector ordering with leading zeros and unequal lengths, SHA1/SHA256 HMAC calculation, chunk id policy including ignored forbidden ids, queued chunk auth marking, and sensitive key refcount/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/bind_addr.c -->
# sources/distributed-fs/ceph-client/net/sctp/bind_addr.c

## Purpose
`bind_addr.c` manages SCTP bind address lists for endpoints and associations. It supports copying/scoping local addresses, adding/deleting entries, serializing/deserializing address parameters, matching/conflict checks, wildcard detection, and address scope evaluation.

## Important APIs, types, and functions
- `sctp_bind_addr_init()`, `sctp_bind_addr_free()`, and internal `sctp_bind_addr_clean()` initialize and destroy `struct sctp_bind_addr` lists.
- `sctp_bind_addr_copy()` and `sctp_bind_addr_dup()` copy source bind lists with scope/address-family/peer-support filtering.
- `sctp_add_bind_addr()` allocates a `sctp_sockaddr_entry`, fills port/state/valid flag, and RCU-adds it to the list.
- `sctp_del_bind_addr()` marks an exact address invalid, RCU-removes it, and frees after grace period.
- `sctp_bind_addrs_to_raw()` serializes multi-address bind lists into SCTP address parameters; `sctp_raw_to_bind_addrs()` parses raw parameters back into a bind list.
- `sctp_bind_addr_match()`, `sctp_bind_addrs_check()`, `sctp_bind_addr_conflict()`, and `sctp_bind_addr_state()` provide lookup and conflict semantics.
- `sctp_find_unmatch_addr()` finds a local address absent from a packed address array, used by ASCONF delete workflows.
- `sctp_copy_one_addr()`, `sctp_is_any()`, `sctp_in_scope()`, `sctp_is_ep_boundall()`, and `sctp_scope()` implement wildcard and scope policy logic.

## Control flow
Bind lists are initialized with a port and empty address list. Copy operations iterate source addresses, expand wildcard entries through `sctp_copy_local_addr_list()`, and include only addresses in the requested SCTP scope and supported by local/peer IPv4/IPv6 flags. Raw parsing walks SCTP parameters, converts each with address-family callbacks, deduplicates by bind-state lookup, and cleans the partially built list on parse/allocation error. Match/conflict routines traverse under RCU and use protocol-family comparison callbacks.

## State and persistence behavior
The state is an in-memory RCU list of `sctp_sockaddr_entry` with address, state, validity flag, and list/RCU hooks. Deletion marks entries invalid before `list_del_rcu()`, allowing readers to skip removed entries. Port is stored in `sctp_bind_addr` and copied into addresses with missing ports. No persistence exists outside endpoint/association lifetime.

## Dependencies and integration points
The file depends on SCTP address-family dispatch (`sctp_get_af_specific()`), protocol-family compare callbacks, global local address list copying, net namespace SCTP scope policy, RCU list traversal, debug object counters, and ASCONF/socket binding paths. It is used by endpoint matching, association local address setup, cookie address reconstruction, and bind conflict checks.

## Risks and edge cases
Scope filtering is policy-sensitive and can silently omit addresses. Raw parameter parsing must handle malformed lengths and unknown address families; cleanup on partial failure is essential. `sctp_bind_addrs_to_raw()` deliberately omits a raw list when only one address exists, which callers must interpret correctly. RCU readers must honor `valid` because deleted entries can remain until grace period. IPv4/IPv6 wildcard and v6-only behavior depend on caller-provided flags and socket family.

## Test signals
Test wildcard expansion, IPv4/IPv6 allowed and peer-supported flags, scope policies disabled/enabled/private/link, add/delete exact address, duplicate raw address parsing, malformed raw parameter cleanup, match/conflict with IPv4 and IPv6 sockets, bound-all detection, single-address raw omission, ASCONF unmatch lookup, and RCU-safe deletion behavior under concurrent readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/bind_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/chunk.c -->
# sources/distributed-fs/ceph-client/net/sctp/chunk.c

## Purpose
`chunk.c` implements the `sctp_datamsg` abstraction for outbound user messages split into DATA chunks. It handles fragmentation by association PMTU/auth overhead, chunk grouping/refcounts, partial reliability abandonment checks, and send-failure notification generation.

## Important APIs, types, and functions
- `sctp_datamsg_init()`, `sctp_datamsg_new()`, `sctp_datamsg_hold()`, `sctp_datamsg_put()`, `sctp_datamsg_destroy()`, and `sctp_datamsg_free()` manage datamsg lifetime and attached fragment chunks.
- `sctp_datamsg_assign()` links a chunk to its parent datamsg and holds the datamsg reference.
- `sctp_datamsg_from_user()` creates DATA fragments from an `iov_iter`, using stream-specific `make_datafrag()`, `sctp_user_addto_chunk()`, auth key selection, PR-SCTP TTL setup, SACK/Cookie-ECHO bundling headroom, and first/middle/last flags.
- `sctp_chunk_abandoned()` evaluates PR-SCTP TTL and retransmission policies, updates abandoned counters, and marks the message abandoned.
- `sctp_chunk_fail()` records send failure/error on the parent datamsg.

## Control flow
Sendmsg paths call `sctp_datamsg_from_user()` with association, send info, and user iterator. The function computes `max_data` from `asoc->frag_point`, falls back to a minimum if zero, subtracts AUTH/SACK/Cookie-ECHO overhead where relevant, then loops over the user message creating first/middle/last DATA chunks. Each chunk gets user data copied in, skb layout restored for send, optional auth key pointer assigned, and membership in the datamsg fragment list. On failure, all created chunks and the datamsg are released. Later, datamsg destruction releases chunks and, if marked failed, emits send-failed events according to subscriptions.

## State and persistence behavior
Datamsg state is in-memory: refcount, fragment list, failure flags/error, delay/abandonment flags, and expiration jiffies. Chunks hold datamsg refs; datamsg destruction iterates chunks and drops references. Partial reliability state is recorded in association and stream abandoned counters. No persistence exists.

## Dependencies and integration points
The file integrates with SCTP stream scheduling/interleaving via `asoc->stream.si`, chunk creation helpers, user-copy helpers, AUTH policy and key lookup, association PMTU/frag point, SACK timer/outqueue state, PR-SCTP flags, ULP event generation, and socket send subscriptions.

## Risks and edge cases
Fragment sizing is sensitive to auth overhead, pending SACK bundling, early Cookie-ECHO bundling, and zero/too-small `frag_point`. If overhead subtraction underflows or leaves too small a fragment, send paths can fail or overrun expected PMTU. Error cleanup must drop every created chunk exactly once. `sctp_chunk_abandoned()` only treats middle fragments after the first differently before TSN assignment; PR-SCTP policy handling must match stream counters. Auth key selection overloads `sinfo_tsn`/`sinfo_ssn` semantics and can reject unknown keys.

## Test signals
Test unfragmented and multi-fragment sends, first/last flags, SACK-immediate/EOF flags, pending SACK and pre-cookie bundling size adjustments, DATA AUTH overhead with active and explicit keys, zero frag-point fallback warning path, allocation/copy failures cleanup, TTL and retransmission abandonment counter updates, send-failed and send-failed-event notifications, and datamsg refcount release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/chunk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/debug.c -->
# sources/distributed-fs/ceph-client/net/sctp/debug.c

## Purpose
`debug.c` provides string lookup tables for SCTP debug output: chunk types, states, event types, state-machine dispositions, primitives, miscellaneous events, and timers.

## Important APIs, types, and functions
- `sctp_cname()` maps base and extension chunk ids to readable names.
- `sctp_state_tbl`, `sctp_evttype_tbl`, and `sctp_status_tbl` export arrays for state-machine debug text.
- `sctp_pname()` maps primitive event ids.
- `sctp_oname()` maps miscellaneous event ids.
- `sctp_tname()` maps timeout ids and uses `BUILD_BUG_ON()` to keep the timer table aligned with `SCTP_EVENT_TIMEOUT_MAX`.

## Control flow
Each lookup checks whether the numeric subtype fits a known range/table and returns a string literal; unknown values return stable fallback strings. Extension chunk ids are handled by explicit switch cases.

## State and persistence behavior
The file contains only static/const lookup tables and no mutable runtime state.

## Dependencies and integration points
It depends on SCTP constants and subtype unions from `<net/sctp/sctp.h>`. The state machine and debug logging use these helpers to render readable traces.

## Risks and edge cases
Tables must stay synchronized with enum values in SCTP headers. Some range checks use `<= SCTP_EVENT_*_MAX`; if enum values and array lengths diverge, out-of-bounds access is possible except for the timer table protected by `BUILD_BUG_ON()`. New chunk extensions require explicit naming to avoid generic "unknown" logs.

## Test signals
Build-time coverage should catch timer table drift. Runtime/unit-style checks should call lookups for base, extension, boundary, and unknown ids, and verify state/event/status table indexes used by state-machine logging remain aligned with enums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/diag.c -->
# sources/distributed-fs/ceph-client/net/sctp/diag.c

## Purpose
`diag.c` implements SCTP support for `NETLINK_SOCK_DIAG`/inet diag. It can dump listening endpoints, per-association socket records, local/peer address lists, memory information, SCTP info, timers, and basic congestion string data.

## Important APIs, types, and functions
- `inet_diag_msg_sctpasoc_fill()` fills `inet_diag_msg` identity/state/timer fields from an SCTP association and primary path.
- `inet_diag_msg_sctpladdrs_fill()` and `inet_diag_msg_sctpaddrs_fill()` add local and peer sockaddr arrays as netlink attributes.
- `inet_sctp_diag_fill()` builds one netlink record for either an endpoint socket or a specific association, including common inet attrs, skmem, `sctp_info`, local addresses, optional congestion name, and peer addresses.
- `sctp_sock_dump_one()` handles exact association lookup replies; `sctp_sock_dump()` handles multi-association dumps from the transport traversal.
- `sctp_sock_filter()` and `sctp_ep_dump()` filter endpoint/association dumps by family, ports, states, and namespace.
- `sctp_diag_dump_one()` maps requested src/dst addresses to `union sctp_addr` and calls transport lookup.
- `sctp_diag_dump()` coordinates endpoint and association table traversal using `netlink_callback` cursor args.
- `sctp_diag_handler` registers SCTP as `IPPROTO_SCTP` with inet diag.

## Control flow
Module init registers an inet diag handler. Dump requests first optionally traverse endpoints for listening sockets, then traverse the SCTP transport hash for associations unless only listening states were requested. Exact lookup builds local/peer address structures from the request and invokes `sctp_transport_lookup_process()`. Fill paths lock sockets where needed, allocate skb replies for exact lookup, check cookies, verify association still belongs to the endpoint, and serialize netlink attributes.

## State and persistence behavior
This file owns no SCTP protocol state. It reads endpoint/association/socket state under socket locks, RCU, and traversal callbacks, and stores only dump cursor positions in `cb->args[]` across netlink dump iterations. The module registration persists while `sctp_diag` is loaded.

## Dependencies and integration points
It integrates with inet diag core, sock diag cookies, netlink attributes, SCTP endpoint and transport traversal helpers, `sctp_get_sctp_info()`, socket memory accounting, namespaces, capabilities (`CAP_NET_ADMIN`), and module aliasing for netlink protocol autoload.

## Risks and edge cases
Dump cursor use is subtle: `cb->args[]` fields track endpoint/listener and transport positions, and mistakes can skip or duplicate records. Association membership is rechecked after locking because peeloff/migration can move associations. Address serialization counts under RCU, then reserves and copies; list changes between count and copy are bounded by decrement logic but still require care. `inet_diag_msg_sctpasoc_fill()` assumes a primary path and at least one local bind address. Large address lists can hit `-EMSGSIZE`.

## Test signals
Test `ss`/inet_diag dump for listening SCTP sockets, one-to-many sockets with multiple associations, exact association lookup, IPv4 and IPv6 records, local and peer address attributes, skmem and `INET_DIAG_INFO`, cookie mismatch, namespace filtering, state/port/family filters, multi-part dump continuation, association peeloff during dump, and module register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/endpointola.c -->
# sources/distributed-fs/ceph-client/net/sctp/endpointola.c

## Purpose
`endpointola.c` implements the SCTP endpoint abstraction associated with a socket. Endpoints own bind addresses, association lists, input queues, AUTH defaults, cookie keys, buffer policies, and lookup/matching logic for incoming chunks before an association is known.

## Important APIs, types, and functions
- `gen_cookie_auth_key()` creates a random HMAC-SHA256 cookie key and wipes raw key bytes.
- `sctp_endpoint_init()` initializes endpoint policy from net namespace SCTP settings, AUTH state, input queue, bind address, association list, socket callbacks, buffer policies, cookie key, null shared key, PR-SCTP/reconfig/ECN flags, and socket/net references.
- `sctp_endpoint_new()`, `sctp_endpoint_free()`, `sctp_endpoint_hold()`, `sctp_endpoint_put()`, `sctp_endpoint_destroy()`, and `sctp_endpoint_destroy_rcu()` manage endpoint lifetime, socket holds, unhashing, auth/bind/inqueue cleanup, port release, RCU final free, and object counters.
- `sctp_endpoint_add_asoc()` links a non-temporary association into the endpoint and updates accept backlog for TCP-style listeners.
- `sctp_endpoint_is_match()` matches endpoint by net namespace, bound device, local port, and bind address.
- `sctp_endpoint_lookup_assoc()` finds an association/transport for a peer address through endpoint address transport lookup.
- `sctp_endpoint_is_peeled_off()` checks whether a peer address is already represented by a peeled-off association.
- `sctp_endpoint_bh_rcv()` drains the endpoint inqueue, handles first AUTH+COOKIE-ECHO special processing, looks up associations created during processing, enforces AUTH-required chunks, updates stats/last-heard transport time, and dispatches to the SCTP state machine.

## Control flow
Endpoint creation allocates zeroed memory, initializes AUTH if enabled, creates a null key, configures socket callbacks and write queue behavior, generates cookie authentication material, and takes a socket reference. Incoming chunks that do not yet have an association are queued to the endpoint inqueue. The bottom-half worker pops chunks, optionally defers an AUTH chunk preceding COOKIE-ECHO for later authentication, looks up any now-existing association by source address, and dispatches each chunk to `sctp_do_sm()`. Freeing marks the endpoint dead, closes socket state, unhashes it, and drops the endpoint reference; final destruction occurs after references drain.

## State and persistence behavior
Endpoint state is volatile: refcount/dead flag, inqueue, bind address list, association list, socket/net references, cookie auth key, auth chunk/HMAC/key lists, buffer policies, and feature flags. The cookie key is wiped on destruction. Final memory free is RCU-delayed so lookups can finish safely.

## Dependencies and integration points
This file ties together SCTP socket callbacks, endpoint hash lookup, bind address management, AUTH initialization, inqueue work scheduling, state machine dispatch, association lookup, global association existence checks, port binding, net namespace SCTP defaults, and IPv6-bound-device matching.

## Risks and edge cases
Endpoint destruction must avoid freeing while inqueue or hash lookups still reference it; refcounts and RCU are critical. AUTH-before-COOKIE-ECHO handling clones skb state and skips processing until cookie processing, so clone failure or ordering bugs affect authenticated setup. `sctp_endpoint_lookup_assoc()` returns transport under RCU without taking a transport reference in this function; callers must fit the established lookup contract. Peeled-off association detection runs under socket lock and assumes stable bind address list. Socket callbacks are overwritten during init and must match SCTP socket semantics.

## Test signals
Test endpoint create/free with auth enabled/disabled, ADDIP auth chunk additions, cookie key zeroing by inspection/instrumentation, endpoint hash match by namespace/device/port/address, association add/backlog accounting, endpoint inqueue processing with COOKIE-ECHO creating an association, AUTH-required discard behavior, peeled-off detection, endpoint free while chunks are queued, and port release during final destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/endpointola.c -->
