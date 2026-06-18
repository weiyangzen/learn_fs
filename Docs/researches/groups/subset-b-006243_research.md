# Research: subset-b-006243

Grouped research for the requested netfilter/IPVS source files. Each section title preserves the source path and is wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_xmit.c -->
## sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_xmit.c

### Purpose
`ip_vs_xmit.c` implements the packet transmit side of IPVS forwarding. It turns an `ip_vs_conn` decision into a concrete packet action for null, bypass, NAT/masquerade, direct-routing, IP tunnel, and ICMP forwarding modes for IPv4 and, when enabled, IPv6. It is called after IPVS has matched a service/connection and is responsible for route lookup, destination-route caching, TTL/hop-limit handling, MTU/PMTU checks, header rewriting, encapsulation, conntrack handoff, and final submission to the netfilter output path or local stack.

### Important APIs, Types, And Functions
Key local state is `struct ip_vs_dest_dst`, cached behind `ip_vs_dest->dest_dst` with RCU and protected updates under `dest->dst_lock`. `__ip_vs_dst_set()` installs or clears cached dst entries, while `__ip_vs_dst_check()` validates cached route obsolescence. Route modes are represented by local `IP_VS_RT_MODE_*` flags, including local/non-local permission, redirect allowance, source-binding, known next-hop, and tunnel mode.

The central route helpers are `__ip_vs_get_out_rt()` for IPv4 and `__ip_vs_get_out_rt_v6()` for IPv6. They resolve or reuse routes, enforce local/non-local boundary rules through `crosses_local_route_boundary()`, decrement TTL via `decrement_ttl()`, compute tunnel-adjusted MTU, call `ensure_mtu_is_adequate()`, and replace the skb dst. Transmit entry points include `ip_vs_nat_xmit()`, `ip_vs_tunnel_xmit()`, `ip_vs_dr_xmit()`, `ip_vs_bypass_xmit()`, `ip_vs_null_xmit()`, `ip_vs_icmp_xmit()`, plus IPv6 variants. Tunnel helpers include `ip_vs_prepare_tunneled_skb()`, `ipvs_gue_encap()`, `ipvs_gre_encap()`, and `ip_vs_tunnel_xmit_prepare()`.

### Control Flow
Most transmitters first obtain an output route for `cp->daddr` or the original packet destination. NAT paths allow both local and non-local destinations and optionally redirect remote traffic to local addresses; direct-routing and bypass paths use a known or packet destination route; tunnel paths reserve outer-header headroom and encapsulate. Once routing succeeds, NAT transmitters ensure writable headers, run the protocol `dnat_handler`, rewrite destination addresses, set `ignore_df`, and call `ip_vs_nat_send_or_cont()`. Direct and bypass paths mostly preserve packet headers after TTL/MTU validation and call `ip_vs_send_or_cont()`. Tunnel paths build an outer IPv4 or IPv6 header, optionally insert GUE or GRE, configure GSO/offload metadata, and call `ip_local_out()` or `ip6_local_out()` after conntrack confirmation/reset.

### State And Persistence
Persistent runtime state is mostly kernel in-memory route cache state on `ip_vs_dest`, with RCU-delayed freeing, and per-connection flags in `struct ip_vs_conn`. SKB state is heavily mutated: `skb->ipvs_property`, dst, checksum state, timestamp, `ignore_df`, network/transport headers, and optional conntrack references are changed. There is no durable storage.

### Dependencies And Integration Points
The file integrates with the routing stack (`ip_route_output_key`, `ip6_route_output`, XFRM), netfilter hooks (`NF_HOOK`, `NF_INET_LOCAL_OUT`), IPVS protocol handlers (`dnat_handler`, ICMP NAT helpers), conntrack/IPVS glue (`ip_vs_confirm_conntrack`, `ip_vs_update_conntrack`, `ip_vs_notrack`, `nf_reset_ct`), tunnel/offload helpers (`iptunnel_handle_offloads`, UDP/GUE/GRE helpers), and ICMP/ICMPv6 error reporting.

### Risks
The highest-risk areas are route cache lifetime and invalidation, local/non-local boundary checks that prevent loopback or local-address abuse, MTU accounting for nested GUE/GRE/remcsum headers, checksum/offload metadata correctness, and NAT-to-local duplicate conntrack protection for synced connections. Any change to skb ownership, early-demux socket orphaning, or `skb_dst_set_noref()` usage can create leaks, use-after-free, or incorrect local delivery. Fragmented IPv6 and ICMP error paths need careful testing because they selectively avoid sending errors for non-first fragments or nested ICMP.

### Test Signals
Useful signals include IPVS NAT, DR, tunnel, bypass, and local-node traffic over IPv4 and IPv6; GUE and GRE tunnel modes with and without checksum/remcsum and GSO; PMTU/DF too-big behavior; TTL/hop-limit expiry; NAT to loopback rejection; synced-connection DNAT-to-local protection; ICMP and ICMPv6 forwarding for MASQ and non-MASQ connections; destination removal/device-down route cache invalidation; and conntrack-enabled versus notrack flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_xmit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_bpf_link.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_bpf_link.c

### Purpose
`nf_bpf_link.c` implements BPF link attachment for netfilter hooks. It lets users create `BPF_LINK_TYPE_NETFILTER` links that register a BPF program as a netfilter hook for IPv4 or IPv6, optionally enabling IP defragmentation before the BPF program runs.

### Important APIs, Types, And Functions
`struct bpf_nf_link` embeds `struct bpf_link`, owns an `nf_hook_ops`, tracks the target net namespace, and stores an optional defrag hook module reference. `bpf_nf_link_attach()` validates `union bpf_attr`, allocates/primes the BPF link, optionally calls `bpf_nf_enable_defrag()`, registers `nf_register_net_hook()`, and settles the link. `nf_hook_run_bpf()` builds `struct bpf_nf_ctx` and executes the program with `bpf_prog_run_pin_on_cpu()`.

Verifier integration is provided through `netfilter_verifier_ops`: `nf_is_valid_access()` exposes read-only `skb` and `state` fields as trusted BTF pointers, and `bpf_nf_func_proto()` returns base helper prototypes. Link lifecycle is handled by `bpf_nf_link_release()`, `bpf_nf_link_detach()`, `bpf_nf_link_dealloc()`, `bpf_nf_link_show_info()`, and `bpf_nf_link_fill_link_info()`.

### Control Flow
Attach validates protocol family, hook number, flags, and priority. Defrag requests require priority after conntrack defrag and dynamically request `nf_defrag_ipv4` or `nf_defrag_ipv6` if the hook is not registered. Link release is idempotent through `cmpxchg(&dead, 0, 1)`, unregisters the net hook, disables defrag, and drops the netns tracker.

### State And Persistence
State is in-memory per link: hook ops, net namespace reference, defrag module reference, and a `dead` flag. The link FD owns lifetime; no durable state exists.

### Dependencies And Integration Points
This code integrates BPF link core, BPF verifier/BTF, netfilter hook registration, net namespace lifetime tracking, and optional netfilter defrag modules. `BPF_F_NETFILTER_IP_DEFRAG` is reported in link info when defrag is active.

### Risks
Priority validation is security-sensitive because defrag and conntrack confirm ordering must remain intact. Module reference handling around global RCU defrag hooks must avoid unload races. Link release must be idempotent across FD close and explicit detach. Context verifier rules must remain strict: writes are rejected and only trusted `sk_buff` and `nf_hook_state` pointers are exposed.

### Test Signals
Test attach/detach for IPv4 and IPv6 hook points, invalid family/hook/priority/flags, defrag auto-module loading and cleanup, link info/fdinfo reporting, namespace teardown with live links, verifier rejection of invalid context access, and packet verdict behavior for BPF-returned netfilter verdicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_bpf_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conncount.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conncount.c

### Purpose
`nf_conncount.c` maintains per-key counts of active conntrack entries, backing connlimit-style rules and nftables expressions that need to count connections matching an arbitrary key such as source address or subnet.

### Important APIs, Types, And Functions
`struct nf_conncount_tuple` stores a tracked tuple, zone, insertion CPU, and jiffies stamp. `struct nf_conncount_rb` stores one counted key, an `nf_conncount_list`, and an RCU rb node. `struct nf_conncount_data` owns 256 rb-tree buckets, a GC work item, pending tree bitmap, net pointer, and key length.

Exported APIs are `nf_conncount_init()`, `nf_conncount_destroy()`, `nf_conncount_count_skb()`, `nf_conncount_add_skb()`, `nf_conncount_gc_list()`, `nf_conncount_list_init()`, and `nf_conncount_cache_free()`. Internal flow is split between tuple extraction (`get_ct_or_tuple_from_skb()`), list add/GC (`__nf_conncount_add()`, `find_or_evict()`), tree insertion/counting (`insert_tree()`, `count_tree()`), and background cleanup (`tree_gc_worker()`).

### Control Flow
For an skb-backed count, the code extracts an existing conntrack or derives a tuple from the packet, then hashes the key into one of 256 rb trees. Existing keys update their list under `list_lock`; missing keys allocate an rb node plus first tuple and insert under the bucket lock. Lists are periodically scanned to remove tuples whose conntrack can no longer be found or whose TCP state is TIME_WAIT/CLOSE. Empty rb nodes are removed with RCU freeing. Calls without an skb count an existing key after a GC pass.

### State And Persistence
State is in-memory per `nf_conncount_data` instance. It persists for the lifetime of the rule/expression using it. Two slab caches store rb nodes and tuple nodes. Stale entries are tolerated briefly to avoid racing unconfirmed conntracks that are about to be inserted.

### Dependencies And Integration Points
The module depends on conntrack tuple parsing/lookup, zones, TCP state names, rbtree and list APIs, RCU, spinlocks, workqueues, jhash, and per-net namespace conntrack state. It is exported to netfilter rule modules rather than registering packet hooks itself.

### Risks
Concurrency risk is high: lookups are RCU-visible while bucket/list mutation uses spinlocks. Stale tuple eviction intentionally waits for two jiffies or same-CPU provenance to avoid dropping entries before conntrack confirmation. Allocation failures return zero counts for hotdrop-like behavior in some paths, so callers must treat zero carefully. Tree GC counting currently uses a collection counter rather than storing collected nodes in the first scan; changes should preserve the two-phase remove-under-lock model.

### Test Signals
Exercise duplicate SYN trains, local loopback confirmed-before-rule cases, TCP close/TIME_WAIT cleanup, UDP/non-TCP retention, zone-aware counting, concurrent inserts for the same key, rb-node removal under RCU, allocation failure behavior, destroy while GC work is pending, and key length validation including non-u32-multiple and over-limit keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conncount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_acct.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_acct.c

### Purpose
`nf_conntrack_acct.c` provides the global default for conntrack flow accounting. It initializes each net namespace's `net->ct.sysctl_acct` setting from the module parameter.

### Important APIs, Types, And Functions
The key state is static `nf_ct_acct`, exposed as module parameter `acct`. The single function `nf_conntrack_acct_pernet_init(struct net *net)` copies that default into `net->ct.sysctl_acct`.

### Control Flow
During per-net conntrack initialization, conntrack core calls `nf_conntrack_acct_pernet_init()`. Later allocation paths consult `net->ct.sysctl_acct` through accounting extension helpers, not in this file.

### State And Persistence
The module parameter is global kernel state. Each net namespace receives its own sysctl copy, so subsequent per-net changes are independent of the boot/module default.

### Dependencies And Integration Points
This file integrates with conntrack extension allocation through `nf_conntrack_acct.h` and with per-net initialization in `nf_conntrack_core.c`.

### Risks
Risk is low. The main compatibility concern is preserving module parameter naming/permissions because user space may depend on `acct`.

### Test Signals
Check module parameter default propagation into new net namespaces, sysctl accounting enable/disable behavior, and that accounting counters appear only when the per-net setting or templates request the extension.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_amanda.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_amanda.c

### Purpose
`nf_conntrack_amanda.c` is the Amanda backup protocol conntrack helper. It parses Amanda UDP control replies from the server, extracts advertised TCP ports for DATA, MESG, INDEX, and STATE connections, and creates expectations so related TCP data connections can be tracked and NATed.

### Important APIs, Types, And Functions
The helper registers two `struct nf_conntrack_helper` entries for IPv4 and IPv6 UDP port 10080. `amanda_help()` is the packet parser. It uses textsearch configs prepared from `ts_algo` for `CONNECT`, newline, and command tokens. `nf_nat_amanda_hook` is an RCU-exported NAT integration hook. `amanda_exp_policy` allows up to four expected connections with a 180 second expectation timeout.

### Control Flow
Only reply-direction packets are parsed. The helper refreshes the master UDP timeout to `master_timeout`, locates a `CONNECT` line, then scans that line for advertised service tokens. For each valid port string it allocates an expectation, initializes it from the original tuple endpoints and TCP destination port, and either delegates to NAT if the connection is NATed or calls `nf_ct_expect_related()`. Expectation allocation/add failures cause helper logging and packet drop because allowing the control packet through would advertise an untracked data connection.

### State And Persistence
Runtime state consists of module parameters, compiled textsearch objects, helper registration, the RCU NAT hook pointer, and transient expectations attached to master conntracks. No durable state exists.

### Dependencies And Integration Points
The file depends on textsearch, conntrack helpers, conntrack expectations, ecache helper logging, UDP/TCP headers, and optional NAT helper registration via `nf_nat_amanda_hook`.

### Risks
Payload parsing must remain bounded by skb length and line end offsets. Port parsing uses `simple_strtoul`; invalid, zero, or overly long ports stop that token. Textsearch preparation failure must unwind all previously prepared configs. NAT hooks run under RCU and can alter packet payload, so offsets relative to UDP payload must remain correct.

### Test Signals
Test IPv4/IPv6 Amanda control replies, delayed replies refreshing UDP timeout, multiple DATA/MESG/INDEX/STATE ports, malformed or partial lines, textsearch algorithm failure, expectation table full, NATed and non-NATed flows, and module unload destroying textsearch configs after helper unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_amanda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_bpf.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_bpf.c

### Purpose
`nf_conntrack_bpf.c` exposes unstable conntrack kfuncs to XDP and TC-BPF programs. BPF programs can allocate, look up, insert, release, and modify conntrack entries using typed BTF references and verifier-enforced lifetime rules.

### Important APIs, Types, And Functions
`struct bpf_ct_opts` carries namespace selection, error output, L4 protocol, direction, zone id/direction, and reserved bytes. Tuple conversion is handled by `bpf_nf_ct_tuple_parse()`. `__bpf_nf_ct_lookup()` and `__bpf_nf_ct_alloc_entry()` implement common lookup/allocation for XDP and skb contexts. Public kfuncs include `bpf_xdp_ct_alloc()`, `bpf_xdp_ct_lookup()`, `bpf_skb_ct_alloc()`, `bpf_skb_ct_lookup()`, `bpf_ct_insert_entry()`, `bpf_ct_release()`, `bpf_ct_set_timeout()`, `bpf_ct_change_timeout()`, `bpf_ct_set_status()`, and `bpf_ct_change_status()`.

Verifier integration uses BTF IDs for `struct nf_conn` and `struct nf_conn___init`, `KF_ACQUIRE`/`KF_RELEASE` flags in `nf_ct_kfunc_set`, and `_nf_conntrack_btf_struct_access()` to limit writes to supported fields such as `mark` when configured. `register_nf_conntrack_bpf()` registers the set for XDP and SCHED_CLS and installs the BTF access callback.

### Control Flow
Lookup validates options and tuple length, resolves an optional target net namespace by nsid, initializes a conntrack zone, calls `nf_conntrack_find_get()`, stores lookup direction in `opts->dir`, and returns a referenced `nf_conn`. Allocation builds original and reply tuples, resolves namespace/zone, calls `nf_conntrack_alloc()`, clears protocol-private data, and sets an initial timeout. Insert marks the entry confirmed, calls `nf_conntrack_hash_check_insert()`, frees on failure, and returns a normal `nf_conn` reference. Release drops the reference with `nf_ct_put()`.

### State And Persistence
State changes are real conntrack table changes: allocated entries consume per-net conntrack count, inserted entries enter the global hash table, timeout/status mutations affect normal GC and protocol behavior. BPF references are verifier-managed and must be released or transferred.

### Dependencies And Integration Points
This file integrates BPF verifier/kfunc/BTF infrastructure with conntrack core allocation, hash insertion, timeout/status mutation, zones, net namespace nsid lookup, XDP receive-device netns, and TC skb device/socket netns.

### Risks
The interface is explicitly unstable but still security-sensitive. Option-size compatibility must remain strict because older callers use 12-byte options without zone fields. Namespace references must always be put. Insert failure must free the unconfirmed entry exactly once. Verifier write permissions must not accidentally expose mutable conntrack internals beyond supported fields. Status changes are constrained by `nf_ct_change_status_common()` but BPF can still influence packet state substantially.

### Test Signals
Run BPF selftests for XDP and TC lookup/allocation/insert/release, invalid option sizes, reserved bytes, unsupported protocols, IPv4/IPv6 tuple sizes, netns id lookup failure, zone id/direction behavior, timeout and status mutation, verifier leak detection for unreleased refs, write access rejection, and insert clash or table-full paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_broadcast.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_broadcast.c

### Purpose
`nf_conntrack_broadcast.c` is a helper utility for broadcast UDP-like protocols. It creates a permanent expectation for replies from hosts in the local broadcast subnet back to the originating local socket.

### Important APIs, Types, And Functions
The exported function is `nf_conntrack_broadcast_help()`. It inspects the skb route, input/output netns, IPv4 broadcast address, primary interface address mask, master helper, and master conntrack helper extension. It allocates and installs an `nf_conntrack_expect` with `NF_CT_EXPECT_PERMANENT`.

### Control Flow
The helper only acts on locally generated original-direction packets whose route is marked `RTCF_BROADCAST` and whose socket net namespace matches the conntrack net. It finds the primary interface address whose broadcast address equals the packet destination, uses that mask for expected source addresses, copies the reply tuple from the master conntrack, narrows source UDP port to the helper's port when available, installs a permanent expectation, and refreshes the master timeout.

### State And Persistence
State is a permanent expectation linked to the master conntrack and global expectation table until removed with the master/helper lifecycle. No module-private persistent structures exist.

### Dependencies And Integration Points
The function depends on IPv4 routing, inet device address lists under RCU, conntrack helpers, expectations, zones, and net namespace helpers.

### Risks
The helper is IPv4-specific and assumes RCU-safe address iteration. Permanent expectations can be broad if masks are wrong; primary address selection and broadcast matching are therefore important. It deliberately ignores non-local sockets, non-broadcast routes, and reply-direction packets.

### Test Signals
Test local broadcast traffic on primary and secondary addresses, namespace mismatch, non-broadcast route, reply-direction packet, missing helper pointer, expectation allocation failure, zone propagation, timeout refresh, and permanent expectation removal when the master connection is destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_broadcast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_core.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_core.c

### Purpose
`nf_conntrack_core.c` is the central implementation of netfilter connection tracking. It parses packet tuples, allocates and confirms conntrack objects, maintains the global hash table, performs lockless RCU lookups, handles expectations, dispatches protocol trackers, manages accounting/events/extensions, resolves insertion clashes, runs garbage collection and early drop, exposes netlink tuple helpers, and owns global/per-net initialization and cleanup.

### Important APIs, Types, And Functions
Global state includes `nf_conntrack_hash`, `nf_conntrack_htable_size`, `nf_conntrack_max`, `nf_conntrack_locks[]`, `nf_conntrack_expect_lock`, `nf_conntrack_generation`, and `conntrack_gc_work`. Hashing uses siphash over tuple, zone id, and netns mix. Tuple helpers include `nf_ct_get_tuplepr()`, `nf_ct_get_tuple()`, `nf_ct_get_tuple_ports()`, `get_l4proto()`, `nf_ct_invert_tuple()`, and `nf_ct_get_id()`.

Core lifecycle functions are `nf_conntrack_alloc()`, `nf_conntrack_free()`, `init_conntrack()`, `resolve_normal_ct()`, `nf_conntrack_in()`, `__nf_conntrack_confirm()`, `nf_conntrack_hash_check_insert()`, `nf_ct_delete()`, and `nf_ct_destroy()`. Lookup and collision handling use `____nf_conntrack_find()`, `__nf_conntrack_find_get()`, `nf_conntrack_find_get()`, `nf_conntrack_tuple_taken()`, `nf_ct_resolve_clash()`, and `nf_ct_resolve_clash_harder()`. Cleanup/resize/init flows are `nf_ct_iterate_cleanup_net()`, `nf_ct_iterate_destroy()`, `nf_conntrack_hash_resize()`, `nf_conntrack_init_start()`, `nf_conntrack_init_end()`, `nf_conntrack_init_net()`, `nf_conntrack_cleanup_start()`, `nf_conntrack_cleanup_end()`, and `nf_conntrack_cleanup_net_list()`.

### Control Flow
`nf_conntrack_in()` is the packet entry point. It ignores already tracked or untracked packets, derives L4 protocol and offset, handles ICMP error packets specially, then calls `resolve_normal_ct()`. Resolution parses a tuple, looks for it under the template-derived zone, and allocates a new conntrack if no match exists. New allocation builds the reply tuple, applies template timeout/account/timestamp/label/event extensions, checks expectations, attaches master/helper state for expected flows, and associates the unconfirmed object with the skb.

Protocol-specific packet handlers update state and timeout. Confirmation later inserts original and reply tuplehashes into the global table under ordered bucket locks after duplicate and chain-length checks. If insertion races, clash resolution may reattach the skb to the winner or insert a reply-only fixed-timeout NAT clash entry. Destruction marks entries dying, reports destroy events, unlinks from hash lists, handles missed-event retry via ecache if needed, removes expectations/helpers/NAT bysource state, and frees after references drain.

### State And Persistence
Conntrack state is in-memory per net namespace and globally hashed. Each `nf_conn` stores original/reply tuples, status bits, timeout, optional extensions, master relationship, protocol-private state, zone, and netns pointer. The hash table is RCU-visible and uses `SLAB_TYPESAFE_BY_RCU`, so refcount-after-lookup revalidation and confirmed-bit ordering are central invariants. Per-net counters enforce `nf_conntrack_max`; GC and early-drop pressure are runtime-only.

### Dependencies And Integration Points
This file integrates nearly every conntrack subsystem: protocol trackers, helpers, expectations, extension allocation, accounting, timestamps, labels, synproxy, NAT hooks, BPF kfunc registration, netlink tuple encoding, nf_queue cleanup, net namespace lifecycle, RCU, workqueues, seqcount-protected hash resize, and exported `nf_ct_hook` operations used by other netfilter code.

### Risks
This is high-risk concurrency code. Correctness depends on lock ordering for dual buckets, `nf_conntrack_locks_all` during resize, generation seqcount retry, RCU nulls-list restart checks, confirmed-bit publication after hash insertion, extension generation validation before and after insertion, and refcount-zero semantics for `SLAB_TYPESAFE_BY_RCU`. Behavioral risks include tuple parsing with fragments/extensions, expectation races, NAT clash handling, table-full early drop, destroy event retry ownership, per-net cleanup loops that can block on references, and BPF registration cleanup order.

### Test Signals
Required signals include IPv4/IPv6 TCP/UDP/ICMP/SCTP/GRE tracking, fragmented packets and IPv6 extension headers, expected related connections, helper assignment, accounting/timestamp/event extensions, confirmation races with cloned broadcast skbs, NAT tuple clashes, table-full early drop, GC expiry, hash resize while traffic flows, net namespace teardown, nf_queue reinjection during module cleanup, BPF kfunc registration/use, netlink tuple filters, and destroy-event listener congestion causing ecache retry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ecache.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ecache.c

### Purpose
`nf_conntrack_ecache.c` implements conntrack event caching and delivery. It stores per-connection event masks, reports conntrack and expectation events to registered notifiers, tracks missed events, and retries destroy events that could not be delivered immediately.

### Important APIs, Types, And Functions
`nf_conn_pernet_ecache()` returns per-net event state. Reporting flows through `nf_conntrack_eventmask_report()`, `__nf_conntrack_eventmask_report()`, `nf_ct_deliver_cached_events()`, and `nf_ct_expect_event_report()`. Notifier registration uses `nf_conntrack_register_notifier()` and `nf_conntrack_unregister_notifier()` under `nf_ct_ecache_mutex`. Destroy retry uses `ecache_work_evict_list()`, `ecache_work()`, and `nf_conntrack_ecache_work()`. Extension allocation uses `nf_ct_ecache_ext_add()`.

### Control Flow
Event reporting first ignores unconfirmed conntracks or missing ecache extensions. It builds an event item, merges requested events with missed bits, calls the RCU notifier, and updates the `missed` bitmask if the notifier reports congestion. Destroy event failure moves conntracks to a per-net dying list; delayed work retries event delivery, unlinks successfully delivered entries, and finally drops conntrack references. Per-net initialization sets the default sysctl event mode, delayed work, dying list, and spinlock.

### State And Persistence
State is per connection (`struct nf_conntrack_ecache`: masks, cached events, missed bits, portid, optional timestamp) and per net namespace (dying list, lock, delayed work, event callback pointer). No durable storage exists. Sysctl default comes from module-level `nf_ct_events`.

### Dependencies And Integration Points
The file integrates with conntrack extensions, ctnetlink event listeners, expectation reporting, per-net conntrack state, delayed workqueues, RCU notifier pointers, and timestamp extension support.

### Risks
Destroy-event retry changes ownership: if delivery fails, `nf_ct_put()` is deferred to the ecache worker. Missed events may be sent more than once, which is intentional but must remain harmless. Event mask width is guarded by `BUILD_BUG_ON(__IPCT_MAX >= 16)`. Registration assumes a single notifier per netns and relies on netns pre-exit RCU synchronization.

### Test Signals
Test listener absent/present/autodetect modes, cached event delivery, missed-event retry, destroy event congestion and later success, expectation new/destroy notification, notifier register/unregister, timestamp refresh, per-net cleanup canceling delayed work, and ctnetlink listener toggling with `sysctl_events=2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ecache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_expect.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_expect.c

### Purpose
`nf_conntrack_expect.c` manages conntrack expectations: temporary or permanent rules created by helpers to classify future related connections, such as FTP data channels or Amanda streams.

### Important APIs, Types, And Functions
Global state includes `nf_ct_expect_hash`, `nf_ct_expect_hsize`, `nf_ct_expect_max`, expectation slab cache, and siphash seed. Exported APIs include `nf_ct_expect_alloc()`, `nf_ct_expect_init()`, `nf_ct_expect_related_report()`, `nf_ct_expect_find_get()`, `nf_ct_find_expectation()`, `nf_ct_remove_expect()`, `nf_ct_remove_expectations()`, `nf_ct_unexpect_related()`, `nf_ct_unlink_expect_report()`, `nf_ct_expect_iterate_destroy()`, and `nf_ct_expect_iterate_net()`.

### Control Flow
Helpers allocate an expectation, initialize tuple/mask/net/zone/helper metadata, and submit it through `nf_ct_expect_related_report()`. Under `nf_conntrack_expect_lock`, the code checks for identical expectations, mask clashes, per-helper class limits, and global table limit. Successful insertion adds a timer reference, links into the master's expectation list and global hash, increments counts, and emits an event. Packet lookup calls `nf_ct_find_expectation()`, which verifies the expectation is active, the master is confirmed and alive, gets a master reference, and either returns a permanent expectation or unlinks a one-shot expectation.

### State And Persistence
Expectations are in-memory, refcounted, RCU-freed objects. They are stored both in the global expectation hash and the master conntrack helper list. Timers expire non-permanent expectations. Per-net `expect_count` tracks global pressure.

### Dependencies And Integration Points
This file is used by conntrack helpers, conntrack core allocation for related flows, event cache reporting, procfs display, zones, net namespace proc setup, and the shared `nf_conntrack_expect_lock`.

### Risks
Expectation masks can be broad, so clash detection is critical. Master lifetime is subtle because unfulfilled expectations do not hold a master reference until matched. Timer deletion controls whether an expectation can be unlinked safely. Permanent expectations are not one-shot and must be used carefully. Procfs iteration is RCU-based and only displays matching net namespace entries.

### Test Signals
Test helper max_expected eviction, global expectation table full, identical expectation replacement, mask clash rejection, timeout expiry, permanent expectations, userspace/inactive flags in proc output, net namespace filtering, expected connection creation inheriting mark/secmark/master/helper, and cleanup of all expectations when a master conntrack dies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_expect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_extend.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_extend.c

### Purpose
`nf_conntrack_extend.c` implements dynamic extension storage for `struct nf_conn`. It lets optional subsystems attach helper, NAT, sequence adjustment, accounting, event cache, timestamp, timeout, labels, synproxy, and act_ct data to conntrack objects before confirmation.

### Important APIs, Types, And Functions
`nf_ct_ext_type_len[]` maps extension IDs to structure sizes based on config. `total_extension_size()` validates the u8 offset/length design. `nf_ct_ext_add()` appends a zeroed extension to `ct->ext`, reallocating with a preallocation floor. `__nf_ct_ext_find()` validates an extension ID and generation before returning a pointer. `nf_ct_ext_bump_genid()` invalidates old extension pointers during teardown/reconfiguration and waits one second.

### Control Flow
Extension add is only safe for unconfirmed conntracks. It computes aligned offset from current length, grows storage, initializes offsets and generation for a new extension block, records offset/length, zeroes the added region, and returns the new extension pointer. Lookup rejects missing or generation-stale extensions unless the gen id has been zeroed after confirmation by core insertion.

### State And Persistence
State is per-conntrack heap allocation plus the global atomic extension generation. Extension storage lives until the conntrack is freed.

### Dependencies And Integration Points
Every optional conntrack subsystem that stores per-flow data depends on this allocator. Conntrack core validates extension generation around insertion and bumps genid during module cleanup to prevent stale helper pointers from being found.

### Risks
The u8 offset/length layout imposes a hard 255-byte total extension limit, guarded by build-time checks. Adding extension types requires updating both `nf_ct_ext_type_len[]` and `total_extension_size()`. Reallocating confirmed conntracks would race readers and is warned against. Generation invalidation must stay paired with core insertion and destroy iteration rules.

### Test Signals
Test combinations of enabled config extensions, repeated add of same ID returning NULL, allocation failure, unconfirmed-only warnings, extension lookup before and after genid bump, insertion after stale genid returning `-EAGAIN`, and build-time failure when extension count/size exceeds limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_extend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ftp.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ftp.c

### Purpose
`nf_conntrack_ftp.c` is the FTP conntrack helper. It parses FTP control-channel commands and replies, tracks command line boundaries across TCP packets, extracts active/passive data-channel addresses and ports, and creates expectations for related TCP data connections with optional NAT payload mangling.

### Important APIs, Types, And Functions
The helper registers IPv4 and IPv6 `struct nf_conntrack_helper` entries for configured ports, defaulting to FTP port 21. Parser functions include `try_rfc959()` for PORT/PASV numeric tuples, `try_rfc1123()` for flexible PASV replies, `try_eprt()`, `try_epsv_response()`, `get_port()`, `try_number()`, and `find_pattern()`. Line state is stored in `struct nf_ct_ftp_master` helper data using `find_nl_seq()` and `update_nl_seq()`. `nf_nat_ftp_hook` is the RCU NAT hook.

### Control Flow
The helper only parses established traffic. It linearizes the skb, computes TCP payload boundaries, takes `nf_ftp_lock`, verifies the packet begins at a remembered post-newline sequence, and scans for direction-specific commands: PORT/EPRT from client, 227/229 replies from server. A full match allocates an expectation for the opposite direction, validates address policy using the `loose` parameter, and either delegates to NAT or calls `nf_ct_expect_related()`. Partial command matches are dropped to avoid losing parser synchronization. On newline-terminated payloads, it records the next sequence number.

### State And Persistence
Module state includes configured ports, `loose`, helper array, global spinlock, and NAT hook pointer. Per-flow state lives in helper extension data: recent sequence numbers after newlines and pickup flags for userspace-injected conntracks. Expectations are transient related-flow state.

### Dependencies And Integration Points
The helper integrates with TCP conntrack state, conntrack helper extension data, expectations, NAT helper payload rewriting, seqadj, ctnetlink restore via `nf_ct_ftp_from_nlattr()`, IPv4/IPv6 address parsing, and module aliasing for helper auto-load.

### Risks
FTP parsing is fragile because commands can span packets, payload can be NAT-mangled, and passive replies are not strictly formatted. Dropping partial matches is intentional but can affect unusual traffic. `nf_ftp_lock` avoids seqadj/NAT deadlock interactions with `ct->lock`; changes must preserve lock ordering. `loose=1` can open expectations to third-party addresses and should be tested as a policy-sensitive mode.

### Test Signals
Test active PORT, passive PASV, EPRT/EPSV over IPv4 and IPv6, commands split across TCP segments, multiple configured ports, NATed payload rewriting and sequence adjustment, ctnetlink-restored flows with pickup flags, strict versus loose address policy, malformed numeric fields, partial command drop, expectation table full, and helper unregister on module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ftp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_asn1.c -->
## sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_asn1.c

### Purpose
`nf_conntrack_h323_asn1.c` is a compact BER/PER decoding library used by the H.323 conntrack/NAT helper. It decodes selected H.323, RAS, H.245 multimedia control, and Q.931 user-user information structures into C structs defined by generated field tables.

### Important APIs, Types, And Functions
The local `field_t` descriptor describes ASN.1 type, size/range constraints, attributes, output offset, and child fields. `struct bitstr` tracks input buffer, current byte, end, and bit offset. Primitive bit readers are `get_len()`, `get_bit()`, `get_bits()`, `get_bitmap()`, and `get_uint()`. Decoder functions are dispatched from `Decoders[]`: null, bool, oid, int, enum, bit string, numeric string, octet string, BMP string, sequence, sequence-of, and choice.

Exported decode entry points are `DecodeRasMessage()`, `DecodeMultimediaSystemControlMessage()`, and `DecodeQ931()`. `DecodeH323_UserInformation()` is the Q.931 nested UUIE decoder. The generated schema tables are included from `nf_conntrack_h323_types.c`.

### Control Flow
Each public decode function initializes a `bitstr` and invokes the appropriate top-level descriptor. Sequence decoding reads extension and optional-field bitmaps, decodes root fields, then decodes extension fields or skips unknown newer-version open fields. Choice decoding reads the selected alternative and decodes or skips based on extension/open-field metadata. Sequence-of decodes a count, writes a capped count to output when requested, and decodes only storable entries while still advancing over all input entries. Q.931 parsing manually checks the protocol discriminator, skips call reference and message type metadata, then searches information elements for UserUserIE and delegates to the H.323 user-information decoder.

### State And Persistence
The decoder is stateless across calls. It writes decoded fields into caller-provided output structs according to descriptor offsets and stores some octet-string values as offsets into the original input buffer. There is no allocation or durable state.

### Dependencies And Integration Points
It depends on generated H.323 descriptor tables and public H.323 structs/error codes from `nf_conntrack_h323_asn1.h`. Conntrack/NAT H.323 helpers use the decoded addresses, ports, and message variants to create expectations and NAT mappings.

### Risks
The main risk is parser safety. Every bit/byte advance must be preceded or followed by `nf_h323_error_boundary()` checks. Range checks reject oversized bitmaps and unknown non-extension choices, while extension fields may be skipped for forward compatibility. Offsets written into output structs are relative to `bs->buf`, so callers must keep the source buffer valid while interpreting them. Generated table changes can silently alter offsets and decode coverage.

### Test Signals
Test valid RAS, H.245, and Q.931 messages; truncated buffers at every primitive length boundary; extension fields and unknown newer-version alternatives; oversized bitmaps/counts; open-field length skipping; sequence-of counts larger than output capacity; Q.931 without UUIE; bad protocol discriminator; and H323_TRACE builds for readable decode traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_asn1.c -->
