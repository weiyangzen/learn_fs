<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock.c -->
# sources/distributed-fs/ceph-client/net/core/sock.c

## Purpose
This is the central generic socket core for the Ceph client kernel source snapshot. It supplies protocol-independent `struct sock` allocation, initialization, cloning, destruction, buffer accounting, socket option handling, default protocol operation stubs, default wakeup callbacks, protocol registration, `/proc/net/protocols` exposure, and several common ioctl and timestamp helpers. Protocols such as TCP, UDP, raw sockets, UNIX sockets, and BPF sockmap/reuseport integrations rely on this file for shared lifetime and memory rules.

## APIs, Types, and Functions
Important exported APIs include capability checks `sk_ns_capable()`, `sk_capable()`, `sk_net_capable()`, receive helpers `__sock_queue_rcv_skb()`, `sock_queue_rcv_skb_reason()`, `__sk_receive_skb()`, route cache helpers `__sk_dst_check()`, `sk_dst_check()`, bind and option setters such as `sock_bindtoindex()`, `sock_set_reuseaddr()`, `sock_set_reuseport()`, `sock_set_timestamping()`, `sock_set_keepalive()`, `sock_set_rcvbuf()`, and `sock_set_mark()`. Generic SOL_SOCKET handling is in `sk_setsockopt()`, `sock_setsockopt()`, and `sk_getsockopt()`.

Object lifetime is handled through `sk_alloc()`, `sk_clone()`, `sk_free()`, `sk_destruct()`, `sk_common_release()`, `sock_init_data_uid()`, and `sock_init_data()`. Memory and skb ownership APIs include `sock_wfree()`, `__sock_wfree()`, `skb_set_owner_w()`, `sock_rfree()`, `sock_efree()`, `sock_pfree()`, `sock_wmalloc()`, `sock_omalloc()`, `sock_kmalloc()`, `sock_kmemdup()`, `sock_kfree_s()`, `sock_kzfree_s()`, `sock_alloc_send_pskb()`, `__sk_mem_raise_allocated()`, `__sk_mem_schedule()`, `__sk_mem_reduce_allocated()`, and `__sk_mem_reclaim()`. Locking and wait APIs include `lock_sock_nested()`, `release_sock()`, `__lock_sock_fast()`, `__release_sock()`, `__sk_flush_backlog()`, and `sk_wait_data()`. Protocol registration and introspection use `proto_register()`, `proto_unregister()`, `sock_load_diag_module()`, `sock_prot_inuse_get()`, `sock_inuse_get()`, and proc seq operations.

## Control Flow, State, and Persistence
Receive flow first applies socket filters and buffer limits, then either delivers directly through `sk_backlog_rcv()` under the socket lock or queues to backlog if userspace owns the socket. Receive queue insertion charges memory with `sk_rmem_schedule()`, sets skb ownership, forces dst references, updates drop counters, and wakes `sk_data_ready()`.

SOL_SOCKET set/get flow validates user buffers, handles lockless options where safe, then locks with `sockopt_lock_sock()` for stateful mutations. Several setters reset dst cache or rehash protocol tables when changing marks, device binding, routing, or reuse state. Timestamp options coordinate socket flags with global network timestamp enable/disable counters, and TCP timestamping option IDs initialize from sequence state when first enabled.

Allocation flow uses protocol slabs when present, charges security/cgroup/memcg state, assigns net namespace references, initializes lock classes per address family, and sets the biased write-memory reference. Clone flow raw-copies safe `struct sock` regions, reinitializes queues and accounting, copies filters and BPF storage, clears per-instance route and error state, and publishes the refcount only after a write barrier. Free flow waits for `sk_wmem_alloc` to drop, optionally broadcasts SOCK_DIAG destroy events, detaches reuseport state, runs protocol destructors, frees filters, BPF storage, fragments, peer credentials, net namespace tracking, cgroups, security state, slab memory, and module references.

Persistent state includes global sysctls `sysctl_wmem_max`, `sysctl_rmem_max`, defaults, static keys for memalloc sockets and high-order page-frag allocation, the protocol list protected by `proto_list_mutex`, per-net protocol in-use counters, per-socket queues/accounting fields, and RCU-protected route/filter/reuseport pointers. The file registers pernet subsystems for socket in-use accounting and protocol proc output.

## Dependencies and Integration
This file integrates with core kernel networking, net namespaces, netdevices, routing dst entries, XFRM, cgroups, memcg socket accounting, BPF socket filters/storage, sock_diag, TCP/UDP helpers, busy polling, page fragments, timers, SCM credentials, pidfds, security hooks, procfs, lockdep, and tracepoints. Protocol implementations plug in through `struct proto`, `struct proto_ops`, protocol slab/request/timewait ops, callback hooks, and optional `release_cb`, `rehash`, `diag_destroy`, `keepalive`, and memory pressure callbacks.

## Risks and Test Signals
Risk is concentrated in lifetime ordering, RCU and refcount transitions, socket option compatibility, and memory accounting. Regressions can manifest as use-after-free in delayed skb destructors, leaked `sk_omem_alloc` or `sk_forward_alloc`, lost wakeups in write/read wait paths, stale route caches after option updates, missing module references for protocol slabs, incorrect capability checks when called from BPF contexts, or incompatible old/new timestamp ABI behavior. Useful test signals include LTP/socket option tests, BPF sockopt and filter tests, KASAN/KCSAN/lockdep under TCP/UDP traffic, memcg socket pressure tests, `/proc/net/protocols` registration/unregistration coverage, netns create/destroy loops, sock_diag destroy listener tests, and packetdrill-style TCP timestamp/zerocopy/error-queue cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock_destructor.h -->
# sources/distributed-fs/ceph-client/net/core/sock_destructor.h

## Purpose
This small internal header centralizes the predicate for recognizing skb destructors that account against socket write memory. It lets code distinguish skbs whose destructor releases `sk_wmem_alloc` from other skb owner/destructor styles.

## APIs, Types, and Functions
The only API is `is_skb_wmem(const struct sk_buff *skb)`. It returns true when `skb->destructor` is `sock_wfree`, `__sock_wfree`, or, with `CONFIG_INET`, `tcp_wfree`. The header includes `<net/tcp.h>` because `tcp_wfree` is part of the predicate when INET is enabled.

## Control Flow, State, and Persistence
There is no state. The inline function performs direct function-pointer comparisons and is compiled into callers.

## Dependencies and Integration
It depends on socket skb destructor functions from `sock.c` and TCP write destructor support. It is an integration point for cleanup/debug logic that needs to classify write-owned skbs without duplicating destructor knowledge.

## Risks and Test Signals
The main risk is drift: adding a new write-memory destructor without updating this predicate can make diagnostics or cleanup logic misclassify skbs. Build coverage across `CONFIG_INET=y/m/n`, TCP transmit tests, and leak/debug paths that consume `is_skb_wmem()` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock_destructor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock_diag.c -->
# sources/distributed-fs/ceph-client/net/core/sock_diag.c

## Purpose
This file implements the generic NETLINK_SOCK_DIAG dispatcher, socket diagnostic handler registry, diagnostic cookies, optional classic filter reporting, destroy-event multicast, and per-net diag netlink socket setup. It lets protocol-specific diag modules expose dump and destroy operations through a common netlink family.

## APIs, Types, and Functions
Cookie helpers are `__sock_gen_cookie()`, `sock_diag_check_cookie()`, and `sock_diag_save_cookie()`. Attribute helpers include `sock_diag_put_meminfo()` and `sock_diag_put_filterinfo()`. Handler registration uses `sock_diag_register()`, `sock_diag_unregister()`, `sock_diag_register_inet_compat()`, and `sock_diag_unregister_inet_compat()`. Message dispatch is implemented by `sock_diag_rcv_msg()`, `__sock_diag_cmd()`, and the compat `TCPDIAG_GETSOCK` path. Destroy support includes `sock_diag_destroy()`, `sock_diag_broadcast_destroy()`, and workqueue callback `sock_diag_broadcast_destroy_work()`.

## Control Flow, State, and Persistence
Incoming netlink messages are received by the per-net `diag_nlsk`, passed through `netlink_rcv_skb()`, decoded by type, and dispatched to a registered per-family handler under RCU plus module reference. Missing handlers trigger `sock_load_diag_module()`. Destroy requests require `CAP_NET_ADMIN` in the socket net namespace and a protocol `diag_destroy` callback.

Destroy event broadcasting is asynchronous because it can be initiated from interrupt context. `sock_diag_broadcast_destroy()` allocates a small work item, queues it on `broadcast_wq`, formats an inet diag message with optional protocol info, multicasts to the appropriate group, then resumes normal socket destruction. Cookie state is stored atomically in each socket and generated from a global `DEFINE_COOKIE(sock_cookie)` source.

## Dependencies and Integration
Depends on netlink, net namespaces, module reference management, inet diag UAPI structures, socket memory info from `sock.c`, BPF classic filter metadata, nospec array hardening, and protocol-specific sock_diag modules. The pernet operations create and release `net->diag_nlsk`, and the bind callback autoloads IPv4/IPv6 diag modules for destroy multicast groups.

## Risks and Test Signals
Risks include missing module references around handler calls, incorrect RCU registration/unregistration, destroy broadcasts racing socket free, insufficient netlink message sizing, leaking sockets when work allocation fails, and capability mistakes for cross-netns destroy. Test signals include `ss`/inet_diag dump coverage, SOCK_DESTROY permission tests, module autoload tests, destroy multicast listeners, filter-info reporting with and without privileges, and KASAN/RCU debug during handler unregister while diag traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock_map.c -->
# sources/distributed-fs/ceph-client/net/core/sock_map.c

## Purpose
This file implements BPF `BPF_MAP_TYPE_SOCKMAP` and `BPF_MAP_TYPE_SOCKHASH` maps, helper functions for updating and redirecting sockets, BPF iterator support, BPF link attachment for sockmap programs, and socket protocol hook teardown through psock. It is the bridge between sockets, sk_msg/sk_skb BPF programs, and map-driven redirection.

## APIs, Types, and Functions
Array sockmap state is `struct bpf_stab` with a `struct sock **sks`, map-level `sk_psock_progs`, and a spinlock. Hash sockmap state is `struct bpf_shtab` with bucket array, element count, key-sized `struct bpf_shtab_elem`, and program slots. Map ops are exported through `sock_map_ops` and `sock_hash_ops`.

Update and lookup paths include `sock_map_alloc()`, `sock_map_free()`, `sock_map_update_elem_sys()`, `sock_map_update_elem()`, `sock_map_update_common()`, `sock_map_delete_elem()`, `sock_map_lookup()`, `sock_map_lookup_sys()`, `sock_hash_alloc()`, `sock_hash_free()`, `sock_hash_update_common()`, `sock_hash_delete_elem()`, `sock_hash_lookup()`, and get-next-key functions. BPF helpers include `bpf_sock_map_update`, `bpf_sock_hash_update`, `bpf_sk_redirect_map`, `bpf_sk_redirect_hash`, `bpf_msg_redirect_map`, and `bpf_msg_redirect_hash`, with their `bpf_func_proto` descriptors.

Program and link management uses `sock_map_get_from_fd()`, `sock_map_prog_detach()`, `sock_map_prog_update()`, `sock_map_bpf_prog_query()`, `sock_map_link_create()`, and `sock_map_link_ops`. Socket teardown hooks exported to protocols are `sock_map_unhash()`, `sock_map_destroy()`, and `sock_map_close()`.

## Control Flow, State, and Persistence
Map updates first validate the socket and state, lock the socket, establish or reuse a `sk_psock`, take references to map-level programs, initialize protocol psock hooks, and install stream parser/verdict or skb verdict callbacks. A `sk_psock_link` is then stored on the psock so socket teardown can delete every map entry that references the socket. Array updates replace an indexed pointer under `stab->lock`; hash updates allocate a new RCU element, add it at the bucket head, and remove the old element if replacing.

Lookup and redirect helpers run under RCU. Redirect is refused for missing sockets, TCP listeners, vsock ingress in skb redirects, vsock msg redirects, and non-TCP egress msg redirects. Free paths synchronize with RCU, remove map entries, take socket references where needed, lock sockets outside atomic regions, unlink psock links, stop parser/verdict paths, drop program references, and then free map storage. BPF links are serialized by the global `sockmap_mutex`, which protects attach/detach/update races and map lifetime as seen by `struct bpf_link`.

Persistent state lives in map objects, psock program slots, per-socket psock link lists, saved protocol callbacks, BPF link objects, and RCU hash/list elements. Iterators maintain seq private state over either array indices or hash buckets and expose key and `struct sock *` to BPF iterator programs.

## Dependencies and Integration
Depends on the BPF map subsystem, BPF links, BTF IDs, BPF iterators, sk_msg/sk_psock infrastructure, protocol `psock_update_sk_prot` callbacks, TCP stream parser support, UDP/vsock/UNIX suitability checks, RCU, socket locking, workqueue cancellation, and sock_diag headers. Protocols integrate by allowing psock protocol replacement and by routing close/unhash/destroy through the exported sock_map wrappers.

## Risks and Test Signals
High-risk areas are psock lifetime, program reference transfers, map replacement races, socket close/unhash recursion, RCU bucket iteration, and attach-type conflict handling between stream and skb verdict programs. Bugs can cause leaked psocks, stale map entries after socket close, redirect to closed/listening sockets, deadlocks between socket locks and bucket locks, or BPF link update races. Test signals include BPF selftests for sockmap/sockhash, stream parser/verdict combinations, link attach/update/detach, map replacement under traffic, socket close/unhash teardown, iterator reads during updates, KASAN/KCSAN/lockdep, and TCP/UNIX/vsock suitability edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock_reuseport.c -->
# sources/distributed-fs/ceph-client/net/core/sock_reuseport.c

## Purpose
This file implements SO_REUSEPORT group storage, socket selection, optional BPF selection, listener shutdown migration support, and BPF program attach/detach for reuseport groups. It optimizes listener lookup by maintaining a compact RCU-visible socket array per group.

## APIs, Types, and Functions
The global state is `reuseport_lock` and `reuseport_ida`. Public APIs include `reuseport_alloc()`, `reuseport_add_sock()`, `reuseport_detach_sock()`, `reuseport_stop_listen_sock()`, `reuseport_select_sock()`, `reuseport_migrate_sock()`, `reuseport_attach_prog()`, `reuseport_detach_prog()`, `reuseport_has_conns_set()`, and `reuseport_update_incoming_cpu()`. Internal helpers manage active and closed sections of the flexible `struct sock_reuseport` socket array, including `__reuseport_add_sock()`, `__reuseport_detach_sock()`, `__reuseport_add_closed_sock()`, `__reuseport_detach_closed_sock()`, `reuseport_grow()`, `reuseport_resurrect()`, and `reuseport_select_sock_by_hash()`.

## Control Flow, State, and Persistence
Groups start with `INIT_SOCKS` slots, grow by doubling up to `U16_MAX`, and are published through each socket's `sk_reuseport_cb` RCU pointer. Active listeners are stored from the front of the array; closed listeners kept for TCP request migration are stored from the back. Shutdown-capable TCP listeners may move from active to closed instead of immediately detaching if `tcp_migrate_req` or a migrate-capable BPF program is active.

Selection takes an RCU snapshot of the group, optionally runs either a `BPF_PROG_TYPE_SK_REUSEPORT` program or classic reuseport filter, and falls back to reciprocal hash selection. Hash selection avoids established sockets and can prefer sockets with `sk_incoming_cpu` matching the current CPU. Migration selection chooses a new listener for established/SYN_RECV children, optionally using BPF with a synthetic skb, then takes a socket reference before returning.

Persistent state includes group IDs, `bind_inany`, `has_conns`, `incoming_cpu`, `synq_overflow_ts`, active/closed counts, and an RCU-protected BPF program pointer. Group storage is freed by `reuseport_free_rcu()` after detaching all sockets and dropping program references.

## Dependencies and Integration
Integrates with TCP listener state, inet bind-conflict logic, BPF reuseport programs, classic socket filters, IDA allocation, RCU, skb cloning/pull/push helpers, per-net TCP migration sysctl, and BPF sockarray detach notifications. `sock.c` calls reuseport detach during socket destruction and exposes `SO_INCOMING_CPU` and reuseport BPF options.

## Risks and Test Signals
Risks include group array races during grow/detach, incorrect active-versus-closed socket accounting, stale BPF program references, migration to an unsuitable listener, CPU-count imbalance for incoming CPU preference, and fallback behavior when BPF returns an invalid index. Test signals include SO_REUSEPORT bind/listen concurrency, BPF selection selftests, TCP request migration tests, shutdown/listen resurrect paths, KCSAN/RCU debug during grow and detach, and CPU-affinity selection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sock_reuseport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/stream.c -->
# sources/distributed-fs/ceph-client/net/core/stream.c

## Purpose
This file provides generic stream-socket wait, wakeup, error, and queue cleanup helpers shared by stream protocols. It factors behavior common to TCP-like sendmsg/recvmsg implementations.

## APIs, Types, and Functions
Exported functions are `sk_stream_write_space()`, `sk_stream_wait_connect()`, `sk_stream_wait_close()`, `sk_stream_wait_memory()`, `sk_stream_error()`, and `sk_stream_kill_queues()`. The internal helper `sk_stream_closing()` checks FIN/closing states.

## Control Flow, State, and Persistence
`sk_stream_write_space()` wakes poll and async waiters when send memory becomes writable and the socket is not shut down. `sk_stream_wait_connect()` loops while the socket is in SYN states, checking errors, timeout, and signals, and increments `sk_write_pending` while sleeping. `sk_stream_wait_memory()` waits for send memory with `SOCKWQ_ASYNC_NOSPACE` and `SOCK_NOSPACE` set so later ACK-driven space changes generate wakeups; it also uses a randomized VM wait interval when memory is technically free to moderate pressure. `sk_stream_wait_close()` waits for closing states to drain. `sk_stream_kill_queues()` purges receive and error queues, asserts write queue/backlog invariants, and performs final memory reclaim.

## Dependencies and Integration
Depends on socket wait queues, TCP state bits, signal handling, poll flags, random numbers, skb queue helpers, and memory reclaim helpers from `sock.c`. Protocols call these helpers while holding the socket lock where documented.

## Risks and Test Signals
Risks are lost wakeups, incorrect timeout accounting, wrong signal-to-errno conversion, sleeping after `SOCK_DEAD`, and queue cleanup while packets can still arrive. Test signals include nonblocking connect/write tests, signal interruption tests, poll/epoll wakeup behavior, TCP close linger/drain tests, and lockdep around wait paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sysctl_net_core.c -->
# sources/distributed-fs/ceph-client/net/core/sysctl_net_core.c

## Purpose
This file registers `/proc/sys/net/core` sysctls for global and per-network-namespace network core tuning. It exposes socket buffer limits, backlog and NAPI budgets, RPS/RFS controls, flow limiting, BPF JIT controls, busy polling, timestamp behavior, qdisc defaults, tunnel inheritance policy, and several static-key backed toggles.

## APIs, Types, and Functions
The main tables are `net_core_table[]` for global core sysctls and `netns_core_table[]` for per-netns sysctls. Custom handlers include `dump_cpumask()`, `rps_default_mask_sysctl()`, `rps_sock_flow_sysctl()`, `flow_limit_cpu_sysctl()`, `flow_limit_table_len_sysctl()`, `set_default_qdisc()`, `proc_do_dev_weight()`, `proc_do_rss_key()`, `proc_do_skb_defer_max()`, `proc_dointvec_minmax_bpf_enable()`, `proc_dointvec_minmax_bpf_restricted()`, and `proc_dolongvec_minmax_bpf_restricted()`. Netns registration is handled by `sysctl_core_net_init()`, `sysctl_core_net_exit()`, and `sysctl_core_init()`. Boot parameter parsing is in `fb_tunnels_only_for_init_net_sysctl_setup()`.

## Control Flow, State, and Persistence
At `fs_initcall`, the global table is registered for `init_net`, and a pernet subsystem registers per-net tables. Non-init netns receive a duplicated `netns_core_table`; early per-net entries are pointer-adjusted from `init_net` to the target `struct net`, while buffer limit/default entries are made read-only outside init net. RPS and flow-limit writes allocate or free CPU masks/tables under mutexes and publish via RCU or release stores. BPF JIT writes are capability-gated and enforce config-specific min/max behavior. Device weight writes recompute hotdata receive/transmit weights from base weight and biases.

Persistent state includes global exported `sysctl_fb_tunnels_only_for_init_net` and `sysctl_devconf_inherit_init_net`, `net_hotdata` tunables, per-net `net->core` sysctl fields, RPS masks/tables, flow-limit per-CPU objects, static keys for RPS/RFS and skb defer disabling, and sysctl header pointers stored in `net->core.sysctl_hdr`.

## Dependencies and Integration
Depends on proc sysctl infrastructure, net namespaces, RPS/RFS, flow limit, softnet data, BPF JIT globals, packet scheduler default qdisc helpers, netdevice RSS key, busy poll variables, socket buffer globals from `sock.c`, static key sysctl handling, and boot `__setup`. It directly influences send/receive buffer bounds, backlog processing, CPU steering, timestamp delivery, and BPF observability/security.

## Risks and Test Signals
Risks include unsafe pointer adjustment for netns table copies, missing cleanup of per-net masks, inconsistent static-key toggles after sysctl writes, insufficient capability checks for BPF JIT visibility, accepting invalid non-power-of-two flow tables, and race-prone replacement of RPS/flow-limit structures. Test signals include sysctl read/write tests under init and non-init netns, capability tests for BPF JIT knobs, RPS/RFS table resize under traffic, flow-limit CPU bitmap updates, qdisc default changes, netns create/destroy leak checks, and static-key state validation for `skb_defer_max` and high-order allocation toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/sysctl_net_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/timestamping.c -->
# sources/distributed-fs/ceph-client/net/core/timestamping.c

## Purpose
This file supports PHY-level PTP hardware timestamping for transmitted and received skbs. It identifies PTP packets and defers timestamp handling to a PHY/MII timestamper when the netdevice timestamp provider is PHYLIB-backed or the PHY uses default hardware timestamping.

## APIs, Types, and Functions
The internal `classify()` wrapper calls `ptp_classify_raw()` only when the skb has a device, PHY device, and MII timestamper. Exported APIs are `skb_clone_tx_timestamp()` for transmit timestamp cloning and `skb_defer_rx_timestamp()` for receive timestamp deferral.

## Control Flow, State, and Persistence
Transmit flow verifies the skb has both socket and device, resolves the timestamping PHY through `dev->hwprov` under RCU or legacy `dev->phydev`, classifies the packet, clones the skb with socket ownership, and calls `mii_ts->txtstamp()`. Receive flow resolves the PHY similarly, temporarily pushes the Ethernet header if enough headroom exists, classifies the raw packet, restores the skb data pointer, and calls `mii_ts->rxtstamp()` if available.

No persistent state is owned here; it consumes RCU-protected netdevice timestamp provider state and PHY timestamper callbacks.

## Dependencies and Integration
Depends on PHYLIB, PTP classifier logic, skb cloning and headroom manipulation, netdevice hardware timestamp providers, and MII timestamper callbacks. It integrates with driver TX/RX paths that call these helpers when PHY timestamping may own timestamp production.

## Risks and Test Signals
Risks include using a PHY pointer after provider changes, mishandling skb headroom/data pointer restoration, failing to clone TX skbs under pressure, classifying packets without an Ethernet header, and missing timestamp callbacks when providers are non-default. Test signals include PTP over PHY hardware tests, TX clone failure injection, RX headroom boundary tests, provider switch tests under RCU debug, and packet capture/error-queue validation for timestamp delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/timestamping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/tso.c -->
# sources/distributed-fs/ceph-client/net/core/tso.c

## Purpose
This file provides software helpers for TCP/UDP segmentation offload header construction, payload iteration, and DMA mapping of GSO payload regions. Drivers can use it to build per-segment headers and walk payload DMA chunks without duplicating skb fragment logic.

## APIs, Types, and Functions
TSO header/data APIs are `tso_start()`, `tso_build_hdr()`, and `tso_build_data()`, operating on `struct tso_t`. DMA APIs are `tso_dma_map_init()`, `tso_dma_map_cleanup()`, `tso_dma_map_count()`, and `tso_dma_map_next()`, operating on `struct tso_dma_map`. The internal `tso_dma_iova_try()` attempts contiguous DMA IOVA mapping before fallback per-region mapping.

## Control Flow, State, and Persistence
`tso_start()` initializes transport header length, IPv4 ID, TCP sequence, IPv6 flag, initial payload pointer, and first frag index. `tso_build_hdr()` copies the original headers, adjusts IPv4 total length/ID or IPv6 payload length, updates TCP sequence and clears PSH/FIN/RST for non-final TCP segments, or updates UDP length. `tso_build_data()` advances sequence, remaining size, data pointer, and transitions from linear data to fragments.

DMA initialization maps payload after `hdr_len`. It first attempts DMA IOVA allocation and links the linear payload and each skb frag into one contiguous mapping with one sync. If that fails, it resets map state and maps the linear region and each frag independently with `dma_map_phys()`. Cleanup destroys IOVA or unmaps each region. `tso_dma_map_count()` predicts descriptor count for the next payload range, and `tso_dma_map_next()` yields DMA address/chunk pairs while advancing iterator state.

Persistent state is confined to caller-owned `struct tso_t` and `struct tso_dma_map`; DMA mappings persist until explicit cleanup.

## Dependencies and Integration
Depends on skb GSO metadata, TCP/UDP/IP/IPv6 headers, VLAN protocol detection, skb fragment APIs, DMA mapping and DMA IOVA APIs, unaligned access helpers, and net driver conventions. Integration is primarily with NIC drivers that need software segmentation or descriptor preparation for GSO skbs.

## Risks and Test Signals
Risks include incorrect header length assumptions, IPv4 ID/sequence drift, mishandling UDP GSO versus TCP, off-by-one fragment iteration, DMA leak on partial map failure, incorrect descriptor counts at region boundaries, and using `virt_to_phys()` only for valid linear skb memory. Test signals include driver selftests with linear-only and fragmented GSO skbs, IPv4/IPv6 TCP and UDP GSO checksums/lengths, DMA API debug, IOVA fallback fault injection, KASAN on frag iteration, and packet captures comparing segmented output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/tso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/utils.c -->
# sources/distributed-fs/ceph-client/net/core/utils.c

## Purpose
This file provides generic networking utilities that are useful outside protocol-specific IPv4/IPv6 stacks: network printk rate limiting, IPv4/IPv6 literal parsing, address-with-scope parsing, wildcard address detection, and transport checksum update helpers.

## APIs, Types, and Functions
Exported APIs are `net_ratelimit()`, `in_aton()`, `in4_pton()`, `in6_pton()`, `inet_pton_with_scope()`, `inet_addr_is_any()`, `inet_proto_csum_replace4()`, `inet_proto_csum_replace16()`, and `inet_proto_csum_replace_by_diff()`. Internal helpers include `xdigit2bin()`, `inet4_pton()`, and `inet6_pton()`. The file defines global `net_ratelimit_state`.

## Control Flow, State, and Persistence
`net_ratelimit()` delegates to `__ratelimit()` with a 5-second, 10-message default. `in_aton()` performs a permissive dotted decimal parse into big-endian IPv4. `in4_pton()` strictly parses four decimal octets with delimiter handling and overflow rejection. `in6_pton()` implements a state machine for hex words, `::` compression, delimiters, and IPv4-embedded suffixes; when compression is used it backfills zero words into the destination. `inet_pton_with_scope()` parses optional ports and dispatches by address family, with AF_UNSPEC trying IPv4 then IPv6. IPv6 link-local scopes are resolved by device name in the given net namespace or numeric scope ID.

Checksum helpers update L4 checksum fields and, for `CHECKSUM_COMPLETE` IPv4 pseudoheader updates, adjust `skb->csum` consistently. IPv6 16-byte address replacement deliberately avoids changing `skb->csum` because address and L4 checksum changes cancel for complete checksums.

Persistent state is limited to the ratelimit token bucket. Parsing and checksum helpers are stateless.

## Dependencies and Integration
Depends on ratelimit infrastructure, hex conversion, socket address structures, IPv6 address type helpers, netdevice lookup for scope IDs, byte-order/checksum primitives, skb checksum state, and kernel string conversion helpers. It integrates with modules that need address parsing without pulling in full protocol-stack code and with NAT/tunnel/classifier paths that adjust checksums after address rewrites.

## Risks and Test Signals
Risks include permissive `in_aton()` accepting malformed values, parser delimiter edge cases, IPv6 compression/backfill mistakes, scope-name lookup races or netns mismatches, and checksum corruption for partial versus complete skb states. Test signals include IPv4/IPv6 parser unit vectors, embedded IPv4 IPv6 forms, link-local scope by name and number, wildcard address checks, checksum replacement tests across `CHECKSUM_NONE`, `CHECKSUM_COMPLETE`, and `CHECKSUM_PARTIAL`, and ratelimit behavior through sysctl-adjusted `message_cost`/`message_burst`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/utils.c -->
