# subset-b-005949 Research

Grouped research for the ceph-client networking socket, TCP, switchdev, stream parser, and traffic-control action headers. Each section is source-path titled and delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sock.h -->
# sources/distributed-fs/ceph-client/include/net/sock.h

Purpose: Defines the Linux networking core socket representation and the socket-layer protocol interface used by INET, TCP, UDP, raw, SMC, UNIX-like integrations, BPF hooks, timestamping, memory accounting, wait queues, and skb ownership.

Important APIs/types/functions: `socket_lock_t` combines a softirq spinlock with user-context ownership and lockdep state. `struct sock_common` is the shared prefix for full sockets, request sockets, and timewait sockets, carrying addresses, ports, lookup nodes, net namespace, flags, state, and refcount. `struct sock` adds queues, timers, callbacks, memory counters, pacing, cgroup/memcg data, BPF storage, timestamp flags, and `sk_reuseport_cb`. `struct proto` is the transport vtable for connect, accept, sendmsg, recvmsg, backlog receive, hash/unhash, memory pressure, slab layout, and diagnostics. Inline helpers cover list membership, refcounting, `sk_add_backlog()`, wait loops, socket flags, memory charge/reclaim, lock/unlock fast paths, destination cache management, skb owner assignment, timestamp/control-message emission, queue mapping, and socket capability checks.

Control flow: Protocol code allocates or clones sockets through `sk_alloc()`/`sk_clone()`, binds them to a `proto`, hashes them into per-protocol lookup tables, queues receive skbs through backlog or receive queues, and releases refs through `sock_put()`/destruct callbacks. Receive paths use `sk_backlog_rcv()` with indirect-call optimization for TCP, then callbacks such as `sk_data_ready()` wake waiters. Send paths test `sk_stream_is_writeable()`, charge memory with `sk_wmem_schedule()`/`sk_mem_charge()`, and use skb destructors such as `sock_wfree()` or `sock_rfree()` to unwind accounting. Blocking socket operations use `sk_wait_event()` to release the socket lock while sleeping and detect disconnect races with `sk_disconnects`.

State and persistence behavior: State is entirely in-memory kernel state. Persistent invariants include `sk_refcnt`, hash/list membership, `sk_state`, queue lengths, `sk_forward_alloc`, timestamp counters, drop counters, and callback pointers. RCU protects wait queues, filters, dst cache, reuseport state, BPF storage, and some protocol-specific data. `dontcopy` markers prevent unsafe fields from being copied during socket clone. Locking is split between `sk_lock.slock`, socket lock ownership, callback rwlock, peer lock, timer synchronization, RCU, atomics, and READ_ONCE/WRITE_ONCE pairs.

Dependencies/integration points: Includes skb, dst, checksum, netdevice, l3mdev, memcg, cgroup, security, timestamping, and socket UAPI headers. `struct proto` connects the socket layer to TCP and other transports; `struct socket_alloc` connects VFS inodes to sockets; BPF, RPS, busy poll, zerocopy, timestamping, and cgroup hooks use fields from `struct sock`.

Risks: The header is layout-sensitive and concurrency-sensitive. Incorrect refcount/list ordering can free live sockets. Memory accounting mistakes can bypass protocol or cgroup pressure. Missing RCU or socket-lock protection around pointers such as `sk_user_data`, `sk_filter`, `sk_dst_cache`, or action callbacks can create use-after-free bugs. Timestamp and skb control buffer overlays require strict size and offset discipline.

Test signals: Build coverage across IPv4, IPv6, BPF, memcg, busy-poll, timestamping, and RCU-free configurations; socket lifecycle tests for bind/listen/accept/connect/close; skb receive/send accounting tests; lockdep/KCSAN/KASAN runs; timestamp and error-queue tests; packetdrill or selftests that exercise backlog, wait, reuseport, and memory-pressure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sock_reuseport.h -->
# sources/distributed-fs/ceph-client/include/net/sock_reuseport.h

Purpose: Declares the SO_REUSEPORT group container and helpers that let multiple sockets share a bind bucket while selecting a concrete socket by hash, BPF program, CPU, or migration policy.

Important APIs/types/functions: `struct sock_reuseport` stores RCU lifetime, socket array capacity/counts, closed-socket count, incoming CPU, SYN queue overflow timestamp, stable group id, bind-in-any and has-connections flags, optional BPF selector program, and flexible `socks[]`. The public API includes `reuseport_alloc()`, `reuseport_add_sock()`, `reuseport_detach_sock()`, `reuseport_stop_listen_sock()`, `reuseport_select_sock()`, `reuseport_migrate_sock()`, BPF attach/detach helpers, `reuseport_has_conns()`, `reuseport_has_conns_set()`, and `reuseport_update_incoming_cpu()`.

Control flow: A listener or bound socket enters a reuseport group at allocation/add time. Incoming packet lookup calls `reuseport_select_sock()` with the hash and skb context; an attached BPF program may override selection. Closed listening sockets can be stopped or migrated through `reuseport_stop_listen_sock()` and `reuseport_migrate_sock()`. `reuseport_has_conns()` performs an RCU read-side lookup of `sk->sk_reuseport_cb`.

State and persistence behavior: State is per-group kernel memory referenced from `struct sock::sk_reuseport_cb` and protected by RCU plus the global `reuseport_lock` for mutations. The group id survives socket-array growth. `synq_overflow_ts` is shared by TCP syncookie logic for listeners in the same group.

Dependencies/integration points: Depends on `sock.h`, `skbuff.h`, filter/BPF infrastructure, and spinlocks. TCP uses the overflow timestamp, packet lookup uses it from UDP/TCP hash paths, and BPF reuseport arrays depend on the socket group.

Risks: Array resize, detach, and selection must preserve RCU safety. Incorrect closed-socket accounting can select dead listeners or block migration. BPF selector return validation is security-sensitive.

Test signals: SO_REUSEPORT selftests with TCP and UDP, BPF selector tests, listener close/migration tests, SYN flood syncookie behavior across a reuseport group, KCSAN/RCU stall checks during concurrent add/detach/select.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sock_reuseport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/stp.h -->
# sources/distributed-fs/ceph-client/include/net/stp.h

Purpose: Provides the small kernel registration contract for Spanning Tree Protocol handlers keyed by Ethernet group address.

Important APIs/types/functions: `struct stp_proto` carries a `group_address`, receive callback `rcv(const struct stp_proto *, struct sk_buff *, struct net_device *)`, and opaque `data`. `stp_proto_register()` and `stp_proto_unregister()` install or remove protocol handlers.

Control flow: A bridge or STP implementation registers a protocol descriptor. The Ethernet receive path can match destination group address and invoke the `rcv` callback with the skb and ingress device. Unregistration removes the callback association.

State and persistence behavior: The header declares no storage; registered protocols live in networking core state. The `data` pointer is caller-owned and must outlive registration.

Dependencies/integration points: Depends on Ethernet address definitions and skb/net_device types. Integrates with bridge/STP receive handling and any module implementing STP-like link-local protocols.

Risks: Callback lifetime and module unload ordering are the main risks. Bad group address registration can steal or drop bridge control traffic.

Test signals: Module register/unregister tests, STP BPDU receive tests on bridge ports, unload with active traffic, and duplicate address registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/stp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/strparser.h -->
# sources/distributed-fs/ceph-client/include/net/strparser.h

Purpose: Defines the stream parser framework used by TCP upper layers such as TLS and BPF stream parsers to split a byte stream into message skbs.

Important APIs/types/functions: `struct strp_stats` and `struct strp_aggr_stats` track message, byte, memory, header, size, timeout, abort, and interrupt counters. `struct strp_callbacks` supplies parser operations: `parse_msg`, `rcv_msg`, `read_sock`, `read_sock_done`, `abort_parser`, and optional lock/unlock callbacks. `struct strp_msg` and `_strp_msg` overlay skb control buffer state with full length, offset, and accumulated length. `struct sk_skb_cb` reserves skb `cb[]` space for private parser state, TLS control, and BPF temporary register. `struct strparser` stores the attached sock, paused/stopped/aborted flags, current skb chain, needed bytes, work items, stats, and callbacks.

Control flow: `strp_init()` attaches the parser to a socket. Data-ready paths call `strp_data_ready()` or `strp_check_rcv()`, which schedule parser work and use the callback `read_sock` to pull bytes. `parse_msg` determines message length; when enough bytes are accumulated, `rcv_msg` receives the completed skb. `strp_pause()` and `strp_unpause()` throttle delivery. `strp_stop()` and `strp_done()` shut down work and timers.

State and persistence behavior: Parser state is in memory and tied to a lower socket. `paused`, `stopped`, `aborted`, and interrupt flags gate processing. Delayed work implements message timeout behavior, and statistics can be saved or aggregated when a parser is detached.

Dependencies/integration points: Depends on `skbuff.h` and `sock.h`, and is used by TCP BPF stream parser paths declared from `tcp.h` plus TLS receive processing.

Risks: skb control-buffer overlays must fit with other users. Parser callbacks are called with the attached socket lock held, so lock inversion is possible. Incorrect `full_len` or `need_bytes` handling can split messages incorrectly, leak skbs, or overrun maximum message size.

Test signals: TLS and BPF stream parser selftests, partial-header/body delivery, pause/unpause, timeout/abort paths, memory allocation failure, oversized-message rejection, and skb `cb[]` size build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/strparser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/switchdev.h -->
# sources/distributed-fs/ceph-client/include/net/switchdev.h

Purpose: Defines the switchdev API that lets bridge, VXLAN, MRP, VLAN, MDB, and FDB control-plane events be offloaded to switch ASIC drivers through notifier and object/attribute contracts.

Important APIs/types/functions: Attribute ids cover port STP/MST state, bridge flags, mrouter, ageing time, VLAN filtering/protocol, multicast disable, MRP role, and VLAN MSTI. Object ids cover port VLAN, port/host MDB, MRP ring/in roles, tests, and states. `struct switchdev_attr`, `struct switchdev_obj`, and specialized object structs carry offload requests. Notifier types cover FDB add/delete/offload/flush, port object add/delete, port attr set, VXLAN FDB events, and bridge-port offload replay. APIs include `switchdev_bridge_port_offload()`, `switchdev_bridge_port_unoffload()`, `switchdev_bridge_port_replay()`, `switchdev_deferred_process()`, port attr/object add/del, notifier registration/calls, and handler helpers for FDB/object/attr dispatch.

Control flow: Bridge or VXLAN code constructs a switchdev attr/object/notifier info and calls blocking or atomic notifiers. Drivers register notifier blocks, use handler helpers to filter supported devices and foreign devices, and perform offload callbacks. Deferred mode lets operations escape atomic context. With `CONFIG_NET_SWITCHDEV` disabled, inline stubs return `-EOPNOTSUPP`, `NOTIFY_DONE`, or no-op success as appropriate.

State and persistence behavior: This header defines event payloads rather than persistent global state. Persistent offload state is held by bridge core and drivers. `complete` callbacks and `complete_priv` let asynchronous/deferred operations report completion.

Dependencies/integration points: Depends on netdevice, notifier, list, and FIB headers. Integrates bridge VLAN/MDB/FDB code, VXLAN FDB, MRP, DSA, ASIC drivers, and netlink extack reporting.

Risks: Offload and software bridge state must remain synchronized. Deferred operations can race with device unregister or bridge teardown. Foreign-device filtering mistakes can program the wrong ASIC. Stub behavior under disabled config must be acceptable to callers.

Test signals: Bridge switchdev selftests, FDB/VLAN/MDB replay after port offload, deferred operation tests, extack checks, device unregister while offloaded, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/switchdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_bpf.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_bpf.h

Purpose: Declares the traffic-control BPF action private state.

Important APIs/types/functions: `struct tcf_bpf` embeds `struct tc_action`, an RCU-protected `struct bpf_prog *filter`, either a BPF fd or classic BPF instruction count, raw `sock_filter` operations, and an optional BPF action name. `to_bpf()` casts a generic `tc_action`.

Control flow: TC action creation loads or references a BPF program and stores it in `filter`; packet action execution dereferences the program and runs it to decide the TC action result. Replacement is RCU-based.

State and persistence behavior: Action state is per TC action instance. The BPF program pointer is RCU-protected; classic BPF ops and name are owned by action lifetime.

Dependencies/integration points: Depends on Linux filter/BPF infrastructure and `net/act_api.h`. Integrated with `tc_wrapper.h` as `tcf_bpf_act`.

Risks: Program lifetime, RCU dereference, verifier assumptions, and fd/program replacement are safety-critical.

Test signals: TC BPF selftests for direct-action and legacy modes, action replace/delete under traffic, verifier rejection, and RCU/KASAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_connmark.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_connmark.h

Purpose: Defines TC connmark action state for copying conntrack marks into skb marks or otherwise applying connmark behavior.

Important APIs/types/functions: `struct tcf_connmark_parms` stores the net namespace, conntrack zone, action result, and RCU head. `struct tcf_connmark_info` embeds `tc_action` and RCU pointer to params. `to_connmark()` casts the action.

Control flow: TC action setup allocates params and installs them through RCU. Packet execution reads params, looks up conntrack state in the configured zone, and applies the configured action.

State and persistence behavior: Per-action params are immutable between replacements and freed after RCU grace period. Namespace and zone select conntrack lookup context.

Dependencies/integration points: Depends on `act_api.h` and conntrack runtime implementation. Called from `tc_wrapper.h` as `tcf_connmark_act` when built in.

Risks: Net namespace lifetime and RCU replacement must be correct. Missing conntrack state should not corrupt skb marks.

Test signals: TC connmark tests with multiple zones/namespaces, action replacement while traffic runs, no-conntrack fallback, and module unload checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_connmark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_csum.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_csum.h

Purpose: Defines TC checksum-update action state and a safe accessor for offload/driver code.

Important APIs/types/functions: `struct tcf_csum_params` stores `update_flags`, generic TC action, and RCU head. `struct tcf_csum` embeds `tc_action` and RCU params pointer. `tcf_csum_update_flags()` reads the configured checksum update flags under RCU.

Control flow: Classifier action execution reads `update_flags` and fixes selected L3/L4 checksums after packet edits. The accessor supports code that needs to inspect the action without duplicating RCU details.

State and persistence behavior: Params are per-action, RCU-replaced, and otherwise immutable for readers.

Dependencies/integration points: Depends on `linux/tc_act/tc_csum.h` UAPI flags and `act_api.h`; integrated with `tcf_csum_act`.

Risks: Incorrect flags can leave stale checksums after NAT/pedit/skbmod. Readers must not dereference params outside an RCU-safe region.

Test signals: Packet tests for IPv4, TCP, UDP, ICMP checksum repair after edits, action replace/delete races, and hardware offload flag export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_csum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ct.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_ct.h

Purpose: Defines TC conntrack action state, optional NAT/label/flowtable configuration, and helpers for hardware/offload code to inspect conntrack action parameters.

Important APIs/types/functions: With conntrack enabled, `struct tcf_ct_params` stores helper, template conntrack, zone, action, mark/mask, label arrays/masks, NAT range, IPv4 range flag, label ownership, ct action, RCU head, TC flow table, and netfilter flowtable pointer. `struct tcf_ct` embeds `tc_action` and RCU params. Accessors return zone, ct action, flowtable, and helper with lockdep-protected dereference. `tcf_ct_flow_table_restore_skb()` restores skb conntrack state from a flowtable cookie when `CONFIG_NET_ACT_CT` is enabled.

Control flow: TC ct action setup creates params from netlink, packet execution commits, clears, NATs, or looks up conntrack state, and flowtable paths can restore skb nfct from a cookie before continuing.

State and persistence behavior: Per-action params are RCU-replaced. Netfilter conntrack objects are refcounted externally. Flowtable restore increments the conntrack ref before attaching it to the skb.

Dependencies/integration points: Depends on `act_api.h`, TC ct UAPI, netfilter conntrack, NAT, labels, and flowtable when enabled. Integrated with `tcf_ct_act`.

Risks: Refcounting nf_conn from cookies is critical. Label array sizing must match `NF_CT_LABELS_MAX_SIZE`. Disabled-config stubs return neutral values, so callers must tolerate no conntrack support.

Test signals: TC ct selftests for commit/zone/NAT/mark/label/helper, flowtable offload restore, disabled-config builds, action replacement under load, and conntrack ref leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ctinfo.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_ctinfo.h

Purpose: Defines TC ctinfo action state for copying conntrack metadata such as DSCP and connmark into packets or skb marks.

Important APIs/types/functions: `struct tcf_ctinfo_params` stores net namespace, action, DSCP mask/state mask, cpmark mask, zone, mode, and DSCP mask shift. `struct tcf_ctinfo` embeds `tc_action`, RCU params, and atomic stats for DSCP set/errors and cpmark set. Mode bits are `CTINFO_MODE_DSCP` and `CTINFO_MODE_CPMARK`.

Control flow: Packet action reads params, finds conntrack state in the selected zone, and applies DSCP or mark updates depending on mode bits while updating stats.

State and persistence behavior: Params are RCU-replaced; counters persist for the action instance until deletion.

Dependencies/integration points: Depends on `act_api.h` and conntrack action implementation. Exposed to TC netlink stats and `tc_wrapper.h`.

Risks: Mask/shift mistakes can overwrite unrelated DSCP or mark bits. Atomic stats must correspond to actual packet outcomes.

Test signals: DSCP and cpmark transfer tests, invalid mask validation, zone isolation, stats checks, and replace/delete concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ctinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_defact.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_defact.h

Purpose: Defines the generic/default TC action container used by simple actions carrying opaque action data.

Important APIs/types/functions: `struct tcf_defact` embeds `tc_action`, stores data length in `tcfd_datalen`, and stores opaque data in `tcfd_defdata`. `to_defact()` casts the generic action.

Control flow: Setup allocates opaque data from netlink configuration, action execution interprets it in the implementation, and deletion frees it with the action.

State and persistence behavior: State is per-action heap data, not RCU-param based in this header.

Dependencies/integration points: Depends on `act_api.h`; used by simple/default action implementations.

Risks: Opaque data length and ownership validation are central; mismatched length can cause parser overread or leak.

Test signals: Netlink create/replace/delete with varying data sizes, invalid length rejection, and action dump symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_defact.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_gact.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_gact.h

Purpose: Defines the generic TC action state and inline predicates used by classifiers and offload code to identify common action results.

Important APIs/types/functions: `struct tcf_gact` embeds `tc_action` and, with `CONFIG_GACT_PROB`, probabilistic action fields and packet counter. `__is_tcf_gact_act()` checks action identity and result, including extended actions. Helpers identify OK, SHOT, TRAP, GOTO_CHAIN, CONTINUE, RECLASSIFY, and PIPE; `tcf_gact_goto_chain_index()` extracts the chain index.

Control flow: Packet execution returns the configured action, optionally probabilistically. Offload and classifier code use helpers to reason about terminal or chaining behavior without open-coding TC action constants.

State and persistence behavior: State is per action; probabilistic mode keeps an atomic packet counter. Helpers are gated by `CONFIG_NET_CLS_ACT` and otherwise return false.

Dependencies/integration points: Depends on `act_api.h` and TC gact UAPI. Integrated with classifier chains and `tc_wrapper.h`.

Risks: Extended action comparisons must preserve chain-index bits. Disabled config can silently make helper predicates false.

Test signals: gact OK/drop/trap/reclassify/pipe/goto tests, probabilistic mode distribution, chain-index extraction, and offload translation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_gact.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_gate.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_gate.h

Purpose: Defines the TC gate action state for time-aware packet gating schedules.

Important APIs/types/functions: `struct action_gate_entry` is a compact exported schedule entry. `struct tcfg_gate_entry` is the internal list node with index, gate state, interval, IPV, and max octets. `struct tcf_gate_params` stores priority, base time, cycle time, extension, flags, clock id, entry count, entry list, and RCU head. `struct tcf_gate` embeds `tc_action` and runtime state: current gate status, close time, octet counters, next entry, hrtimer, and timekeeping offset. Accessors read locked params for priority, base/cycle times, entry count, and `tcf_gate_get_list()` copies the schedule list to an allocated array.

Control flow: Configuration installs a schedule list. Runtime hrtimer advances entries, opens/closes the gate, tracks max octets, and action execution allows or blocks packets according to current gate status.

State and persistence behavior: Schedule params are RCU-replaced but accessed here through the action lock. Runtime gate status, timers, current octets, and next entry mutate continuously while traffic and timer callbacks run.

Dependencies/integration points: Depends on `act_api.h`, TC gate UAPI, hrtimers, and timekeeping. Integrated with time-sensitive networking qdisc/action flows.

Risks: Entry count/list mismatch causes `tcf_gate_get_list()` to fail. Timer, lock, and RCU interactions are subtle. Allocating the exported list with GFP_ATOMIC can fail under pressure.

Test signals: Schedule validation, base-time/cycle-time timer behavior, max-octet enforcement, list dump correctness, action replace/delete while timer active, and clock-id coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_gate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ife.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_ife.h

Purpose: Defines TC IFE action state and metadata operation registration for Inter-FE encapsulation metadata.

Important APIs/types/functions: `struct tcf_ife_params` stores destination/source MAC, ethertype, flags, metadata list, and RCU head. `struct tcf_ife_info` embeds `tc_action` and RCU params. `struct tcf_meta_info` binds a metadata operation to a value and id. `struct tcf_meta_ops` defines check, encode, decode, get, alloc, release, and validate callbacks plus module ownership. Helpers allocate, check, encode, validate, and release u16/u32 metadata; `register_ife_op()` and `unregister_ife_op()` manage metadata plugins.

Control flow: IFE action setup builds a metadata list and Ethernet encapsulation parameters. Packet execution encodes or decodes metadata through registered `tcf_meta_ops`. Metadata modules register their ids and callbacks before use.

State and persistence behavior: Action params are RCU-replaced; metadata op registry is global module state; metadata values live in per-action lists.

Dependencies/integration points: Depends on `act_api.h`, Ethernet helpers, RTNL, and module aliases `ife-meta-*`. Integrated with `tcf_ife_act`.

Risks: Metadata module lifetime and list ownership must be correct. Encode/decode length validation is security-sensitive.

Test signals: IFE encode/decode round trips for u16/u32 metadata, module register/unregister, malformed metadata length rejection, action replacement, and MAC/ethertype dump tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ife.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_mirred.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_mirred.h

Purpose: Defines TC mirror/redirect action state for sending packets to another net device or block.

Important APIs/types/functions: `struct tcf_mirred` embeds `tc_action`, stores mirror/redirect direction/action, block id, MAC header transmit mode, RCU net_device pointer, netdevice tracker, and list node. Helpers identify egress redirect, egress mirror, ingress redirect, ingress mirror, and return the target device with RTNL dereference.

Control flow: Action execution clones or redirects packets to the configured target device/block based on `tcfm_eaction`. Offload/classifier code uses helpers to classify direction and mode.

State and persistence behavior: Target device pointer is RCU-protected and tracked with `netdevice_tracker`; action is linked into a mirred list for lifecycle management.

Dependencies/integration points: Depends on TC mirred UAPI, act API, net_device, RTNL, and `tc_wrapper.h`.

Risks: Device unregister races, redirect loops, and incorrect ingress/egress classification can misroute packets or leak device references.

Test signals: Mirror and redirect tests for ingress/egress, target device removal, block redirect, action dump, and loop prevention checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_mirred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_mpls.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_mpls.h

Purpose: Defines TC MPLS action parameters and RCU accessors for push/pop/modify MPLS operations.

Important APIs/types/functions: `struct tcf_mpls_params` stores MPLS action, label, generic TC action, traffic class, TTL, BOS, protocol, and RCU head. Sentinel constants mark unset TC, BOS, and label. `struct tcf_mpls` embeds `tc_action` and RCU params. Accessors return action, protocol, label, TC, BOS, and TTL under RCU.

Control flow: Packet execution reads params and edits MPLS headers according to configured action. Offload code can query exact params through accessors.

State and persistence behavior: Per-action params are immutable for RCU readers and replaced as a whole.

Dependencies/integration points: Depends on MPLS TC UAPI and `act_api.h`. Integrated with `tcf_mpls_act` and hardware offload translation.

Risks: Wrong sentinel handling can push invalid labels or unset fields. RCU readers must not retain param pointers after unlock.

Test signals: MPLS push/pop/modify tests, unset-field validation, offload dump, action replacement under traffic, and protocol endian checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_mpls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_nat.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_nat.h

Purpose: Defines TC NAT action state for simple IPv4 address translation.

Important APIs/types/functions: `struct tcf_nat_parms` stores action, old address, new address, mask, flags, and RCU head. `struct tcf_nat` embeds `tc_action` and RCU params. `to_tcf_nat()` casts the action.

Control flow: Configuration installs address/mask/flag params. Packet execution matches and rewrites IPv4 addresses and fixes dependent checksums, returning the configured TC action.

State and persistence behavior: Params are per-action and RCU-replaced.

Dependencies/integration points: Depends on `linux/types.h`, `act_api.h`, and packet checksum helpers in implementation; integrated with `tcf_nat_act`.

Risks: Endian and mask handling errors can rewrite wrong addresses. NAT edits must be paired with checksum updates.

Test signals: Source and destination NAT packet tests, partial mask cases, checksum validation, replace/delete under traffic, and invalid address netlink validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_nat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_pedit.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_pedit.h

Purpose: Defines TC packet edit action state and accessors for key-based header modifications.

Important APIs/types/functions: `struct tcf_pedit_key_ex` stores extended header type and command. `struct tcf_pedit_parms` stores key array, optional extended key array, action, max offset hint, key count, flags, and RCU head. `struct tcf_pedit` embeds `tc_action` and RCU params. Helpers identify pedit actions and read key count, header type, command, mask, value, and offset under RCU.

Control flow: Netlink setup builds key arrays. Packet execution iterates keys, computes offsets, applies masks/values, and returns configured action. Offload code uses accessors to translate edits.

State and persistence behavior: Params are per-action and RCU-replaced. Key arrays must remain valid until RCU free.

Dependencies/integration points: Depends on TC pedit UAPI, `act_api.h`, and packet header parsing code.

Risks: Index bounds are caller responsibility for accessors. Offset calculation and mask/value endian handling can corrupt headers. Missing extended keys default to network header type and max command sentinel.

Test signals: Pedit tests for IPv4, IPv6, TCP/UDP fields, extended command modes, malformed key counts, offload translation, and concurrent replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_pedit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_police.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_police.h

Purpose: Defines TC policing action parameters, token-bucket runtime state, legacy compatibility format, and locked accessors for rates and bursts.

Important APIs/types/functions: `struct tcf_police_params` stores action, result, EWMA rate, MTU, byte and packet bursts, MTU peak tokens, rate/peak/pps configs and presence flags, plus RCU head. `struct tcf_police` embeds `tc_action`, RCU params, cacheline-aligned lock, token counters, packet tokens, and last time. `tc_police_compat` mirrors old policer UAPI. Accessors return byte rate, byte burst, packet rate, packet burst, MTU, peak byte rate, EWMA rate, and rate overhead while the action lock is held.

Control flow: Runtime refills tokens from elapsed time, compares packet size/count against configured byte/packet/peak buckets, updates token state under `tcfp_lock`, and returns conform or exceed action.

State and persistence behavior: Config params are RCU-replaced and read under action lock in accessors. Mutable token state persists per action and changes for every packet.

Dependencies/integration points: Depends on `act_api.h`, psched rate configs, TC netlink dump, and `tcf_police_act`.

Risks: Burst conversion uses nanosecond arithmetic and can overflow if not bounded by setup validation. Locking must protect token state. Byte and packet modes must not be confused.

Test signals: Rate/peak/pps policing tests, token refill over time, burst conversion checks, legacy dump compatibility, replacement while traffic runs, and lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_police.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_sample.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_sample.h

Purpose: Defines TC sample action state for probabilistic packet sampling to psample groups.

Important APIs/types/functions: `struct tcf_sample` embeds `tc_action`, sample rate, truncate flag, truncate size, RCU psample group pointer, group number, and list node. Accessors return rate, truncate flag, and truncate size.

Control flow: Packet action samples approximately one out of `rate` packets, optionally truncates copied packet data, and sends samples to the configured psample group while returning the configured TC action.

State and persistence behavior: Per-action state persists until deletion; psample group pointer is RCU-protected; list node supports group/action lifecycle.

Dependencies/integration points: Depends on `act_api.h`, TC sample UAPI, and `net/psample.h`; integrated with `tcf_sample_act`.

Risks: Truncation size must not exceed packet bounds. Group lifetime and RCU access must be correct. Sampling rate zero or invalid values must be rejected at setup.

Test signals: Sampling distribution tests, truncate-size validation, psample group deletion under traffic, action dump, and disabled psample behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_sample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbedit.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbedit.h

Purpose: Defines TC skbedit action state and helpers for editing skb metadata such as mark, priority, packet type, queue mapping, and DS field inheritance.

Important APIs/types/functions: `struct tcf_skbedit_params` stores action, flags, priority, mark/mask, queue mapping, mapping modulo, packet type, and RCU head. `struct tcf_skbedit` embeds `tc_action` and RCU params. Helpers test exact configured flags and read mark, ptype, priority, queue mapping; ingress helper distinguishes RX and TX queue mapping based on `tcfa_flags`.

Control flow: Action execution reads params and updates skb metadata fields. Offload/classifier code uses helpers to detect which metadata edit is represented.

State and persistence behavior: Params are per-action and RCU-replaced. Helpers take short RCU read sections for param fields.

Dependencies/integration points: Depends on `act_api.h` and skbedit UAPI. Queue mapping integrates with device TX/RX queue selection.

Risks: `is_tcf_skbedit_with_flag()` checks equality, not bit inclusion, so combined flags need careful handling. Ingress/egress queue mapping depends on `tcfa_flags`.

Test signals: Mark/mask, priority, ptype, TX/RX queue mapping, inherit DS field tests, combined flag behavior, and action replacement under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbedit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbmod.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbmod.h

Purpose: Defines TC skbmod action state for modifying Ethernet header fields.

Important APIs/types/functions: `struct tcf_skbmod_params` stores RCU head, 64-bit operation flags, action, destination MAC, ethertype, and source MAC. `struct tcf_skbmod` embeds `tc_action` and RCU params. `to_skbmod()` casts the action.

Control flow: Setup stores requested Ethernet modifications. Packet execution reads params, updates source/destination MAC and/or ethertype, and returns configured TC action.

State and persistence behavior: Params are per-action and RCU-replaced as a unit.

Dependencies/integration points: Depends on `act_api.h`, skbmod UAPI, and Ethernet header helpers; integrated with `tcf_skbmod_act`.

Risks: Flags must match initialized fields. Header edits require sufficient headroom/linear data and must not be applied to non-Ethernet packets.

Test signals: Source/destination MAC and ethertype modification tests, invalid packet type handling, action dump, hardware offload translation, and replacement while traffic runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbmod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_tunnel_key.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_tunnel_key.h

Purpose: Defines TC tunnel_key action state and helpers for setting, releasing, and copying tunnel metadata.

Important APIs/types/functions: `struct tcf_tunnel_key_params` stores RCU head, tunnel-key action, generic TC action, and `metadata_dst *` encapsulation metadata. `struct tcf_tunnel_key` embeds `tc_action` and RCU params. Helpers identify set/release actions under action lock, return `ip_tunnel_info`, and duplicate tunnel info including options with `kmemdup()`.

Control flow: Packet execution sets skb tunnel metadata from `tcft_enc_metadata` or releases existing tunnel metadata. Offload code can inspect and copy tunnel info for hardware programming.

State and persistence behavior: Params are per-action and RCU-replaced. Metadata dst lifetime is owned by params; copied tunnel info is caller-owned.

Dependencies/integration points: Depends on `act_api.h`, tunnel_key UAPI, and `dst_metadata.h`; used by VXLAN/Geneve/IP tunnel offload paths.

Risks: `tcf_tunnel_info()` assumes metadata is present for set actions. Copy size includes variable options and must match allocation. Lockdep-protected dereference requires action lock.

Test signals: Set/release tests for VXLAN/Geneve options, metadata copy/free checks, null metadata rejection, offload translation, and replace/delete races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_tunnel_key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_vlan.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_vlan.h

Purpose: Defines TC VLAN action state and RCU accessors for VLAN push, pop, modify, and Ethernet push parameters.

Important APIs/types/functions: `struct tcf_vlan_params` stores generic action, VLAN action, push destination/source MACs, push VID, protocol, priority, priority-present flag, and RCU head. `struct tcf_vlan` embeds `tc_action` and RCU params. Accessors return VLAN action, push VID/protocol/priority, and copy push Ethernet addresses under RCU.

Control flow: Packet action reads params and manipulates VLAN tags or pushed Ethernet metadata. Offload code uses accessors to translate VLAN edits into hardware rules.

State and persistence behavior: Params are per-action and RCU-replaced. Accessors do not retain pointers after RCU unlock.

Dependencies/integration points: Depends on `act_api.h` and VLAN TC UAPI; integrated with `tcf_vlan_act`.

Risks: VLAN protocol endian handling, priority-present semantics, and MAC copy ordering must match action configuration. Missing linear header data can break packet edits.

Test signals: VLAN push/pop/modify tests for 802.1Q and 802.1ad, priority-present cases, push Ethernet address copying, hardware offload translation, and action replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_vlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_wrapper.h -->
# sources/distributed-fs/ceph-client/include/net/tc_wrapper.h

Purpose: Provides retpoline-aware wrappers around TC action and classifier indirect calls, replacing common built-in indirect calls with direct calls when safe and falling back to function pointers otherwise.

Important APIs/types/functions: Under `CONFIG_MITIGATION_RETPOLINE`, static keys `tc_skip_wrapper_act` and `tc_skip_wrapper_cls` control whether wrappers are skipped. `TC_INDIRECT_ACTION_DECLARE()` and `TC_INDIRECT_FILTER_DECLARE()` declare indirect-callable action/classifier functions. `tc_act()` checks built-in action function pointers for gact, mirred, pedit, skbedit, skbmod, police, BPF, connmark, csum, ct, ctinfo, gate, MPLS, NAT, tunnel_key, VLAN, IFE, simple, and sample. `tc_classify()` similarly checks BPF, u32, flower, fw, matchall, basic, cgroup, flow, and route4 classifiers. `tc_wrapper_init()` enables skip static keys on x86 without retpoline when more than one built-in target exists. Without retpoline mitigation, wrappers are simple direct pointer calls.

Control flow: Packet classification and action execution call `tc_classify()`/`tc_act()` instead of raw function pointers. The wrapper fast-path compares the operation pointer against built-in functions and calls the direct symbol; if no match or skipping is enabled, it uses the original function pointer.

State and persistence behavior: Only static key state persists globally. No per-action state is stored here.

Dependencies/integration points: Depends on `pkt_cls.h`, CPU feature checks, static keys, and indirect call wrapper support. Integrates all built-in TC classifier/action implementations.

Risks: The wrapper must preserve exact call semantics and config guards. Missing a built-in target only loses optimization, but wrong function comparison or signature mismatch is fatal. Static key enable policy must match CPU retpoline needs.

Test signals: Build matrix for retpoline/non-retpoline and modular/built-in TC actions, packet classifier/action selftests, objdump or ftrace checks for direct-call paths, and runtime tests with static keys toggled by CPU feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp.h -->
# sources/distributed-fs/ceph-client/include/net/tcp.h

Purpose: Central TCP internal header defining constants, option layout, exported TCP functions, per-skb control block, congestion-control API, timers, syncookie helpers, authentication integration, fast open, queues, BPF/ULP hooks, and many inline algorithms shared by TCP implementation files.

Important APIs/types/functions: Defines TCP timing/retry/window/MSS constants, option numbers/lengths, ECN/AccECN flags, TFO flags, RACK flags, and SNMP stat macros. Exports main TCP entry points such as `tcp_v4_rcv()`, send/recv, connect/close, option parsing, syncookie helpers, output/retransmit functions, RTO/window/MSS helpers, congestion-control registration, MD5/AO lookup hooks, Fast Open context, ULP registration, BPF sock_ops calls, and init/offload functions. Key types include `tcp_splice_state`, `tcp_skb_cb`, `ack_sample`, `rate_sample`, `tcp_congestion_ops`, `tcp_md5sig_key/info`, `tcp_sigpool`, `tcp_fastopen_request/context`, `tcp_ulp_ops`, `tcp_request_sock_ops`, `tcp_sock_af_ops`, `tcp_key`, and `tcp_plb_state`.

Control flow: TCP receive starts from `tcp_v4_rcv()`/IPv6 equivalent, parses options, handles listen/request/timewait states, validates syncookies or authentication, then feeds established sockets through `tcp_rcv_state_process()` or `tcp_rcv_established()`. Send paths queue skbs with `tcp_skb_entail()`, push frames, segment/retransmit through output helpers, maintain write and retransmit queues, and use timers for retransmit, delayed ACK, zero-window probes, pacing, and compressed ACKs. ACK processing feeds congestion-control callbacks with `rate_sample`, updates SACK/loss counters, cwnd, pacing, and recovery state. Optional paths include Fast Open, MPTCP collapse checks, BPF sock_ops, stream parser/BPF redirects, TCP-AO/MD5 authentication, SMC static key checks, and ULP callbacks.

State and persistence behavior: TCP state lives in `struct tcp_sock`, `inet_connection_sock`, request/timewait sockets, skb `TCP_SKB_CB`, global/per-net sysctls, per-cpu orphan counters, static keys, congestion-control lists, Fast Open keys, and per-socket auth/ULP data. Inline helpers enforce sequence-number wrap semantics, cwnd/rto/window calculations, queue membership in rb/list queues, timestamp clocks, SNE/auth key selection, and memory-pressure behavior. State is volatile kernel memory; some metrics are cached per destination by implementation code.

Dependencies/integration points: Depends on socket core, inet connection/timewait/request/hash tables, checksum/IP/ECN/dst/xfrm/MPTCP/TCP-AO/SNMP/BPF/memcg/siphash headers. It is included by most TCP implementation files and exposes hooks to procfs, GRO/GSO, syncookies, congestion-control modules, BPF, TLS/ULP, Fast Open, MD5, AO, and netfilter/drop reason reporting.

Risks: This header is highly concurrency and layout sensitive. skb control block size must fit `sk_buff::cb`. Sequence wrap helpers must be used consistently. Timer calculations mix jiffies, usec, nsec, and TCP timestamp units. Auth key lookup and static keys must not dereference missing AO/MD5 state. Congestion-control callbacks must preserve cwnd invariants, and queue/rbtree helpers must keep retransmit and write queues synchronized.

Test signals: TCP selftests and packetdrill for handshake, syncookies, retransmit, SACK/RACK, ECN/AccECN, keepalive, zero-window probes, TFO, MD5/AO, BPF sock_ops, ULP/TLS, GRO/GSO, IPv4/IPv6, proc iteration, memory pressure, and KASAN/KCSAN/lockdep runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp_ao.h -->
# sources/distributed-fs/ceph-client/include/net/tcp_ao.h

Purpose: Defines TCP Authentication Option internal state, key layout, counters, option parsing hooks, hash/key derivation APIs, and no-op stubs for builds without TCP-AO.

Important APIs/types/functions: `union tcp_ao_addr` stores IPv4 or IPv6 address. `struct tcp_ao_hdr` maps TCP option fields and `tcp_ao_hdr_maclen()` derives MAC length. `struct tcp_ao_counters` tracks good/bad packets, key misses, required-AO drops, and dropped ICMPs. `struct tcp_ao_key` stores hlist node, address/prefix/family/l3index, raw master key, sigpool id, digest and MAC sizes, send/receive ids, RCU head, per-key counters, and two traffic keys. `struct tcp_ao_info` stores key list, cached current/rnext keys, counters, required/ICMP policy, initial sequence numbers, send/receive SNE, and refcount. IPv4/IPv6 context structs define pseudoheader key inputs. APIs cover transmit hashing, inbound hash validation, key lookup, established-key caching, key copy to child sockets, traffic-key calculation, SNE computation, reset preparation, socket option parsing/get/repair, timewait transfer, connect/established transitions, syncookie integration, and common parsing of AO/MD5 options.

Control flow: Userspace installs master keys through TCP-AO sockopts. During connect/listen/accept, AO initializes traffic keys from addresses, ports, and ISNs. Transmit paths choose current key, compute SNE, hash TCP header/payload, and write AO MAC. Receive paths parse auth options, lookup matching key by l3index/address/family/sndid/rcvid, compute expected hash, update counters, and drop or accept. Timewait and reset paths carry enough AO state to authenticate late packets or resets.

State and persistence behavior: AO state is per socket and RCU-managed. `current_key` and `rnext_key` are cached only for established states and require READ_ONCE/WRITE_ONCE if accessed without socket lock. SNE tracks upper sequence number extension to prevent replay across 32-bit sequence wrap. Static keys `tcp_ao_needed` and `tcp_md5_needed` gate overhead when unused.

Dependencies/integration points: Integrated from `tcp.h`, TCP option parser, MD5 compatibility paths, TCP syncookies, request/timewait sockets, IPv4/IPv6 pseudoheader hashing, sigpool crypto helpers, and sockopt get/set/repair paths.

Risks: Key lifetime, RCU, and refcounting are security-critical. Incorrect SNE basis can accept replayed segments or reject valid wraparound traffic. AO and MD5 option coexistence parsing must be unambiguous. Stubs must return `-ENOPROTOOPT` or neutral values consistently when AO is disabled.

Test signals: TCP-AO selftests for IPv4/IPv6, key rotation, current/rnext behavior, listener-to-child copy, timewait, reset, syncookie, ICMP ignore policy, SNE wraparound, repair sockopts, AO-required drops, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp_ao.h -->
