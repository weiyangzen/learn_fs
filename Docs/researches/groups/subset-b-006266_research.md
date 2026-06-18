# subset-b-006266

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/sendmsg.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/sendmsg.c

Purpose: implements AF_RXRPC data transmission from userspace `sendmsg()` and from in-kernel services. It creates client calls from control messages, appends user data into encrypted Tx buffers, queues DATA packets, handles final-packet notification, and exposes kernel helpers for send, abort, and declared transmit length.

Important APIs/functions: `rxrpc_do_sendmsg()` is the socket entry point; `rxrpc_kernel_send_data()`, `rxrpc_kernel_abort_call()`, and `rxrpc_kernel_set_tx_length()` are exported kernel APIs. Internally, `rxrpc_sendmsg_cmsg()` parses `SOL_RXRPC` control messages, `rxrpc_new_client_call_for_sendmsg()` constructs client calls, `rxrpc_send_data()` performs the copy/encrypt/queue loop, `rxrpc_queue_packet()` publishes packets into the call Tx queue, and `rxrpc_propose_abort()` schedules abort packets with release ordering. Key types include `rxrpc_sock`, `rxrpc_call`, `rxrpc_send_params`, `rxrpc_txqueue`, and `rxrpc_txbuf`.

Control flow: `rxrpc_do_sendmsg()` requires a user call ID cmsg, handles accept-charge requests for listening server sockets, looks up an existing call or creates a new client call, applies optional timeout and total-length controls, then either proposes an abort or sends data. `rxrpc_send_data()` waits for client connection establishment, initializes client security when needed, validates call state and total length, allocates queue pages in `RXRPC_TXQ_MASK` chunks, obtains security-specific Tx buffers, copies from the message iterator, secures full/final buffers, and queues them. If the call transmit window is full, it drops `user_mutex`, waits according to interruptibility and `MSG_WAITALL`, then reloads any pending partial buffer.

State and persistence: state is per socket/call, not durable. The file mutates `send_top`, `tx_bottom`, `send_queue`, `tx_pending`, `tx_total_len`, call timeout fields, `RXRPC_CALL_TX_NO_MORE`, and abort fields. Memory ordering matters: abort code uses `smp_store_release()`, and queue publication stores `send_top` after the Tx buffer pointer/content. Partial unsent data persists in `call->tx_pending` across calls.

Dependencies and integration: depends on RxRPC call, peer, connection, security, timer, trace, and wakeup internals from `ar-internal.h`; uses Linux socket locking, wait queues, message iterators, signals, and skbuff-style allocation. Security integration occurs through `conn->security->alloc_txbuf()` and `call->security->secure_packet()`.

Risks: lock dropping around Tx-window waits means call state must be revalidated after reacquiring `user_mutex`. Total-length accounting rejects under/over send and can strand a caller if `MSG_MORE` usage is wrong. Queue ring assertions and `WARN_ON_ONCE` guard duplicate slots but do not recover a corrupted sequencing bug. Interruptible waits and `MSG_DONTWAIT` return partial progress if bytes were copied.

Test signals: useful signals include sendmsg cmsg validation tests, client-call creation with missing addresses, blocking/nonblocking Tx-window behavior, partial writes with `MSG_MORE`, declared length mismatch, abort cmsg behavior, kernel service send/abort paths, tracepoints `rxrpc_txqueue`, `rxrpc_tq`, `rxrpc_txbuf`, and fault injection for copy/security allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/sendmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/server_key.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/server_key.c

Purpose: provides RxRPC server-side key type handling and server socket security-keyring configuration. It validates descriptions for `rxrpc_s` keys, delegates security-class-specific key parsing/destruction, and lets user or kernel services attach a keyring to a server socket.

Important APIs/functions: defines `key_type_rxrpc_s` with `vet_description`, `preparse`, `free_preparse`, `instantiate`, `destroy`, and `describe` hooks. `rxrpc_server_keyring()` consumes a userspace keyring name from a sockopt, `rxrpc_sock_set_security_keyring()` attaches a kernel-provided keyring before bind/connect, and `rxrpc_sock_set_manage_response()` toggles challenge-response management. Helpers `rxrpc_vet_description_s()`, `rxrpc_preparse_s()`, `rxrpc_free_preparse_s()`, `rxrpc_destroy_s()`, and `rxrpc_describe_s()` bridge to `struct rxrpc_security` callbacks.

Control flow: key descriptions must parse as `<service>:<security-class>[:...]` with service <= 65535 and security class 1..255. During preparse, the security class is looked up and stored in payload slot 1, then `preparse_server_key` handles class-specific payload material. Socket keyring setup rejects replacement, copies a NUL-terminated userspace string, requests a kernel keyring by description, and stores it in `rx->securities`.

State and persistence: the key subsystem persists instantiated keys and payloads. Socket state stores a referenced keyring in `rx->securities`; manage-response is a bit in `rx->flags`. Class-specific key payload lifetime is owned by key hooks and released through security callbacks.

Dependencies and integration: integrates Linux keyrings, RxRPC security class registry, sock locking, and exported AF_RXRPC kernel service APIs. Security modules such as RxKAD/RxGK provide the concrete server-key parser and cleanup methods.

Risks: key descriptions are parsed partly with `simple_strtoul()` and partly with `sscanf()`, so malformed descriptions must remain covered by both validation stages. Keyring attachment is intentionally one-shot and state-dependent; callers attempting setup after binding receive `-EISCONN`. Manage-response only has an effect for security classes that consult userspace.

Test signals: key-add/request tests with valid and invalid descriptions, missing security classes returning `-ENOPKG`, sockopt keyring setup with bad lengths/names, kernel keyring setup before and after bind, and challenge-response behavior for classes supporting managed responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/server_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/skbuff.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/skbuff.c

Purpose: centralizes RxRPC socket-buffer reference/accounting trace helpers. It wraps skb lifecycle events so the subsystem can track outstanding Rx skbs and emit consistent trace records.

Important APIs/functions: `rxrpc_new_skb()` records a newly allocated or received skb, `rxrpc_see_skb()` traces an skb observed in a queue without changing ownership, `rxrpc_get_skb()` increments the accounting counter and takes an skb reference, `rxrpc_free_skb()` decrements accounting and consumes one reference, and `rxrpc_purge_queue()` drains a `sk_buff_head`.

Control flow: all mutating helpers update `rxrpc_n_rx_skbs` through `select_skb_count()` and emit `trace_rxrpc_skb()` with the skb pointer, Linux skb refcount, RxRPC accounting count, and trace reason. `rxrpc_purge_queue()` repeatedly dequeues until empty and consumes each skb.

State and persistence: the only persistent state is the global atomic skb count used for diagnostics. Actual packet memory lifetime remains owned by Linux skb refcounting; these helpers must be paired correctly with real `skb_get()`/`consume_skb()` ownership changes.

Dependencies and integration: used by RxRPC receive/input queues and cleanup paths; depends on Linux skbuff APIs, `rxrpc_skb_trace` values, and subsystem tracepoints.

Risks: because the diagnostic counter is manually maintained, missing a helper call or calling the wrong one creates misleading leak accounting even when the skb refcount is correct. `rxrpc_see_skb()` intentionally does not validate or retain the skb.

Test signals: trace-based leak checks, queue purge tests on non-empty receive queues, refcount debugging, and subsystem shutdown tests expecting `rxrpc_n_rx_skbs` to return to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/skbuff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/sysctl.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/sysctl.c

Purpose: registers `/proc/sys/net/rxrpc` tunables for RxRPC timing, connection reap, backlog, receive window, receive MTU, jumbo packet, and optional receive-delay injection parameters.

Important APIs/functions: `rxrpc_sysctl_init()` registers the static table under `init_net`, and `rxrpc_sysctl_exit()` unregisters it. The `rxrpc_sysctl_table` maps proc names to global variables such as `rxrpc_soft_ack_delay`, `rxrpc_idle_ack_delay`, `rxrpc_conn_idle_client_expiry`, `rxrpc_max_backlog`, `rxrpc_rx_window_size`, `rxrpc_rx_mtu`, and `rxrpc_rx_jumbo_max`.

Control flow: initialization calls `register_net_sysctl()` and returns `-ENOMEM` on failure. Exit unregisters only when a table header was registered. Individual sysctls use kernel min/max handlers: millisecond values use `proc_doulongvec_minmax`, jiffy-backed expiry values use `proc_doulongvec_ms_jiffies_minmax`, and integer tunables use `proc_dointvec_minmax`.

State and persistence: sysctl writes mutate global RxRPC variables at runtime; values are not persisted by this file across reboot. Bounds constants enforce minimum Rx MTU 500, backlog range 4..`RXRPC_BACKLOG_MAX - 1`, receive window <= 255, jumbo max <= `RXRPC_MAX_NR_JUMBO`, and time delays within configured ranges.

Dependencies and integration: integrates Linux sysctl infrastructure and RxRPC global tunable definitions from `ar-internal.h`. Optional `CONFIG_AF_RXRPC_INJECT_RX_DELAY` exposes `inject_rx_delay` for fault/test behavior.

Risks: global tunables affect all RxRPC users in `init_net`; there is no per-net namespace registration here. Incorrect bounds could destabilize flow control, MTU handling, or connection expiry. Runtime changes can alter behavior under active calls.

Test signals: module init/exit sysctl registration tests, proc read/write validation at min/max/out-of-range values, conversion tests for ms-to-jiffies fields, and feature-gated presence of `inject_rx_delay`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/txbuf.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/txbuf.c

Purpose: allocates, traces, and frees RxRPC transmit data buffers used by the send path before packets are secured and queued.

Important APIs/functions: `rxrpc_alloc_data_txbuf()` creates a `struct rxrpc_txbuf` and associated page-fragment data area, `rxrpc_see_txbuf()` emits a trace without changing lifetime, and `rxrpc_put_txbuf()` drops a reference and frees on last put. `rxrpc_free_txbuf()` performs final release. Globals `rxrpc_txbuf_debug_ids` and `rxrpc_nr_txbuf` provide debug identity and live-count accounting.

Control flow: allocation creates the metadata object, computes a data offset after a jumbo header aligned to the security data alignment, allocates aligned data from `conn->tx_data_alloc` under `tx_data_alloc_lock`, initializes refcount/debug fields/space/sequence/client flag, traces allocation, and increments the live count. Put uses `__refcount_dec_and_test()`, traces the new refcount, and frees the page fragment plus metadata when dead.

State and persistence: buffers are transient per call. Persistent state includes live debug counters and connection-level page-frag allocator state. `txb->seq` is set to `call->send_top + 1`, so allocation assumes caller serializes sequencing with the call send path.

Dependencies and integration: called through security-class `alloc_txbuf()` paths and consumed by `sendmsg.c` queueing. Uses page-frag allocation, refcount APIs, tracepoints, and RxRPC connection/call structures.

Risks: data is freed via `page_frag_free(txb->data)` even though `data` points past an internal offset; this relies on page-frag free semantics accepting the returned address. Alignment, offset, and data-size calculations must remain consistent with security headers and jumbo header assumptions. Missing puts leak page-frag memory and `rxrpc_nr_txbuf`.

Test signals: allocation failure injection, alignment-sensitive security modes, send/abort paths that drop pending txbufs, trace count returning to zero, and stress tests around concurrent calls sharing a connection page-frag allocator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/txbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/utils.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/utils.c

Purpose: contains a small RxRPC utility for deriving a `sockaddr_rxrpc` peer address from an incoming skb.

Important APIs/functions: `rxrpc_extract_addr_from_skb()` zeroes the destination address and fills the UDP source endpoint for IPv4 or, when enabled, IPv6. It sets `transport_type`, `transport_len`, family, port, and address fields.

Control flow: the function switches on `skb->protocol`. For `ETH_P_IP`, it reads `udp_hdr(skb)->source` and `ip_hdr(skb)->saddr`; for `ETH_P_IPV6` under `CONFIG_AF_RXRPC_IPV6`, it reads `ipv6_hdr(skb)->saddr`; unsupported protocols log a rate-limited warning and return `-EAFNOSUPPORT`.

State and persistence: no persistent state. The caller-provided `sockaddr_rxrpc` is overwritten; skb contents are read only.

Dependencies and integration: used by RxRPC receive paths that need to identify or create peers from UDP packets. Depends on network header pointers already being valid and on Linux IPv4/IPv6/UDP header helpers.

Risks: it assumes the skb is already parsed far enough that IP and UDP header accessors are valid. Unsupported L2 protocol values are not recoverable here. IPv6 support is compile-time gated.

Test signals: IPv4 receive path address extraction, IPv6 builds with `CONFIG_AF_RXRPC_IPV6`, malformed or unexpected protocol skbs, and rate-limited warning coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/Kconfig -->
# sources/distributed-fs/ceph-client/net/sched/Kconfig

Purpose: defines Linux traffic-control scheduler, classifier, ematch, action, and related feature configuration symbols. It controls which qdisc, classifier, action, and metadata modules are built into or as modules for `net/sched`.

Important symbols: top-level `NET_SCHED` enables QoS/fair queueing and selects FIFO support. Scheduler symbols include HTB, HFSC, PRIO, MULTIQ, RED/GRED/SFB/SFQ, TEQL, TBF, CBS, ETF, TAPRIO, NETEM, DRR, MQPRIO, SKBPRIO, CHOKE, QFQ, CODEL/FQ_CODEL, CAKE, FQ, HHF, PIE/FQ_PIE, INGRESS, PLUG, ETS, BPF qdisc, and DUALPI2. Classifier symbols include BASIC, ROUTE4, FW, U32 with optional perf/mark, FLOW, CGROUP, BPF, FLOWER, MATCHALL, and EMATCH variants. Action symbols include POLICE, GACT with optional probability, MIRRED, SAMPLE, NAT, PEDIT, SIMP, SKBEDIT, CSUM, MPLS, VLAN, BPF, CONNMARK, CTINFO, SKBMOD, IFE with metadata plugins, TUNNEL_KEY, CT, GATE, and `NET_TC_SKB_EXT`.

Control flow: Kconfig dependency logic exposes options only under `if NET_SCHED`. Many action configs depend on `NET_CLS_ACT`; netfilter-backed actions add `NETFILTER`, `NF_CONNTRACK`, mark, NAT, and flow-table dependencies. Defaults for queue discipline are selected through `NET_SCH_DEFAULT` choice and materialized in `DEFAULT_NET_SCH`.

State and persistence: selected symbols persist in the kernel `.config` and drive compilation, module names, and runtime feature availability. No runtime state is directly managed.

Dependencies and integration: consumed by the build system and C preprocessor. It aligns with `net/sched/Makefile`, user-facing `tc`/iproute2 features, and optional subsystems such as BPF, netfilter, CAN, textsearch, cgroups, and skb extensions.

Risks: dependency mistakes can allow uncompilable combinations or hide needed modules. Help text advertises module names and should remain synchronized with Makefile objects. Some options select helper libraries, so missing `select` lines can cause link errors.

Test signals: `allmodconfig`, `allyesconfig`, randconfig, module build coverage for each symbol, and iproute2 `tc` feature tests matching enabled symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/Makefile -->
# sources/distributed-fs/ceph-client/net/sched/Makefile

Purpose: maps traffic-control Kconfig symbols to the scheduler, classifier, ematch, and action object files compiled for `net/sched`.

Important build mappings: unconditional core objects are `sch_generic.o` and `sch_mq.o`; `CONFIG_NET_SCHED` adds `sch_api.o` and `sch_blackhole.o`; `CONFIG_NET_CLS_ACT` adds `act_api.o`. The listed action files map directly from action configs, including `act_gact.o`, `act_bpf.o`, `act_connmark.o`, `act_csum.o`, `act_ct.o`, `act_ctinfo.o`, `act_gate.o`, and `act_ife.o`. IFE metadata plugins map to `act_meta_mark.o`, `act_meta_skbprio.o`, and `act_meta_skbtcindex.o`.

Control flow: kbuild evaluates `obj-$(CONFIG_...) += file.o` lines. Built-in `y` symbols link into the kernel or parent object; module `m` symbols become loadable modules with names implied by the object basename.

State and persistence: no runtime state. The file persists the source-to-object build contract used by kernel builds and module packaging.

Dependencies and integration: must remain consistent with `Kconfig`, source file module aliases, and any helper objects such as `sch_mqprio_lib.o`. It also includes classifier and ematch object lists, so it is the build join point for much of `net/sched`.

Risks: missing or misspelled object mappings create configured-but-unbuilt features. Objects added without matching Kconfig can be unexpectedly built or never built. Module names in Kconfig help should track these object names.

Test signals: per-symbol module builds, `make M=net/sched`, randconfig coverage, and checking that `modprobe act_*`, `sch_*`, `cls_*`, and `em_*` aliases match selected config outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_api.c -->
# sources/distributed-fs/ceph-client/net/sched/act_api.c

Purpose: implements the shared Linux traffic-control action API. It owns action registration, per-net IDR lifetime management, netlink create/delete/get/dump handling, action execution graph semantics, statistics, cookies, and hardware offload add/delete/stats integration.

Important APIs/functions: exported core APIs include `tcf_register_action()`, `tcf_unregister_action()`, `tcf_action_check_ctrlact()`, `tcf_action_set_ctrlact()`, `tcf_action_exec()`, `tcf_action_init()`, `tcf_action_destroy()`, `tcf_action_dump()`, `tcf_action_update_stats()`, `tcf_action_copy_stats()`, `tcf_idr_check_alloc()`, `tcf_idr_create()`, `tcf_idr_release()`, `tcf_idr_insert_many()`, `tcf_idrinfo_destroy()`, and `tcf_action_update_hw_stats()`. `tc_ctl_action()` and `tc_dump_action()` are registered for `RTM_NEWACTION`, `RTM_DELACTION`, and `RTM_GETACTION`.

Control flow: action modules register `tc_action_ops` and per-net operations before becoming visible in `act_base`. Netlink create requests parse up to `TCA_ACT_MAX_PRIO` nested actions, load modules by action kind if needed, initialize each action through its ops, validate flags and cookies, offload standalone actions when requested, then atomically replace temporary IDR `ERR_PTR(-EBUSY)` slots with live actions. Execution iterates an action array, skips software when `SKIP_SW`, handles `PIPE`, bounded `REPEAT`, bounded `JUMP`, and `GOTO_CHAIN`, and stops at the first non-pipe result. Dump/delete walkers iterate action IDRs under locks and produce netlink notifications.

State and persistence: per-net `tc_action_net` IDRs hold actions by index, with refcount and bind count tracking. Global `act_base` stores registered action kinds under `act_mod_lock`; `act_pernet_id_list` stores pernet IDs for reoffload. Actions hold cookies, stats, goto-chain RCU pointers, flags, module refs, and hardware offload counts.

Dependencies and integration: integrates rtnetlink, netlink attributes, classifier/filter chains, per-net namespaces, module autoloading (`act_<kind>` aliases), `flow_offload`/indirect block callbacks, gnet stats, RCU, IDR, and qdisc/skb helpers. `tcf_dev_queue_xmit()` bridges optional fragmentation transmit hooks.

Risks: lifetime is subtle: IDR placeholders prevent duplicate allocation, module refs must be dropped on all paths, and bind/ref counts determine whether deletion is legal. Offload flags `SKIP_HW` and `SKIP_SW` are mutually exclusive and must match classifier flags. Action graph control opcodes are bounded but malformed jump graphs intentionally degrade to `TC_ACT_OK`.

Test signals: rtnetlink add/get/delete/flush/dump tests, concurrent create/delete on the same index, module autoload retry returning `-EAGAIN`, action cookie dump/free, skip flag validation, chain goto behavior, hardware offload add/delete/reoffload/stats paths, and KASAN/RCU/refcount checks for action teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_bpf.c -->
# sources/distributed-fs/ceph-client/net/sched/act_bpf.c

Purpose: implements the `bpf` traffic-control action, allowing a classic BPF instruction array or an eBPF `BPF_PROG_TYPE_SCHED_ACT` program to decide packet action results.

Important APIs/functions: `tcf_bpf_act()` runs the program; `tcf_bpf_init()` parses and installs/replaces programs; `tcf_bpf_dump()` reports program parameters, ID/tag/name or classic instructions; `tcf_bpf_cleanup()` releases program resources. `tcf_bpf_init_from_ops()` creates classic BPF with `bpf_prog_create()`, while `tcf_bpf_init_from_efd()` gets an eBPF program by fd.

Control flow: init validates `TCA_ACT_BPF_PARMS`, allocates or finds an action index, checks the configured control action, requires exactly one of classic ops or eBPF fd, installs new config under the action lock, assigns the filter with RCU, and synchronizes before freeing replaced programs. Runtime updates stats, adjusts skb data pointers at ingress by pushing/pulling MAC header, runs the program, normalizes the returned opcode, drops prefetched sockets for non-OK results, and counts drops on `TC_ACT_SHOT`.

State and persistence: action state stores the RCU `bpf_prog *filter`, optional copied classic instructions, optional eBPF name, instruction count, action opcode, stats, and IDR-managed action lifetime. eBPF program refs are held with `bpf_prog_get_type()`/`bpf_prog_put()`.

Dependencies and integration: integrates TC action API, Linux BPF verifier/program subsystem, rtnetlink attributes, module/pernet registration, and ingress skb data-pointer conventions.

Risks: replacing programs requires RCU synchronization to avoid freeing code still executing. Classic and eBPF encodings are mutually exclusive; accepting both would make lifetime ambiguous. Ingress MAC push/pull must remain balanced. Unknown BPF return codes intentionally become `TC_ACT_UNSPEC`.

Test signals: classic BPF and eBPF install/dump/delete, invalid fd/type rejection, replacement while packets run, ingress versus egress program execution, return-code mapping, drop statistics, and module autoload via `act_bpf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_connmark.c -->
# sources/distributed-fs/ceph-client/net/sched/act_connmark.c

Purpose: implements the `connmark` TC action, copying a netfilter connection mark into `skb->mark` so classifier/qdisc policy can use conntrack state.

Important APIs/functions: `tcf_connmark_act()` performs lookup and mark copy; `tcf_connmark_init()` creates/replaces action parameters; `tcf_connmark_dump()` reports action and zone; `tcf_connmark_cleanup()` releases RCU parameters. Parameters are stored in `struct tcf_connmark_parms` with net namespace, zone, and action.

Control flow: runtime updates lastuse/basic stats, determines IPv4 or IPv6 protocol, first tries `nf_ct_get()` from the skb, and if absent builds a conntrack tuple from the packet and looks it up in the configured zone. On success it assigns `skb->mark = ct->mark`, releases any lookup reference, increments overlimit stats as a "marked packet" counter, and returns the configured action.

State and persistence: action instances live in the shared TC IDR. Mutable parameters are replaced under the action lock and freed with `kfree_rcu()`. Packet state is changed by writing `skb->mark`; conntrack table state is read only.

Dependencies and integration: depends on `NETFILTER`, `NF_CONNTRACK`, and `NF_CONNTRACK_MARK`; integrates TC action registration/pernet state, RCU parameter lookup, and nf_conntrack tuple APIs.

Risks: packets without valid IPv4/IPv6 headers or conntrack entries pass through without mark changes. Zone mismatch or tuple extraction failure silently leaves the old skb mark. The action uses overlimits as a semantic counter, so stats readers need to know this convention.

Test signals: IPv4/IPv6 packets with attached ct, ingress packets requiring tuple lookup, non-IP packets, configured zones, mark copy correctness, replacement cleanup under traffic, and statistics indicating marked packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_connmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_csum.c -->
# sources/distributed-fs/ceph-client/net/sched/act_csum.c

Purpose: implements the `csum` TC action, recalculating selected packet checksums after earlier actions edit packet headers or payload.

Important APIs/functions: `tcf_csum_act()` is the action body. Init/dump/cleanup functions manage `struct tcf_csum_params` containing `update_flags` and action opcode. Protocol helpers update IPv4 header, ICMP/IGMP, IPv4/IPv6 TCP, UDP, UDPLite, ICMPv6, and SCTP checksums; `tcf_csum_skb_nextlayer()` validates pull/writability for next-layer headers. `tcf_csum_offload_act_setup()` maps to `FLOW_ACTION_CSUM`.

Control flow: init parses `TCA_CSUM_PARMS`, allocates or replaces the action, checks control action, and RCU-swaps params. Runtime updates stats, honors immediate `TC_ACT_SHOT`, resolves the packet protocol including stacked VLAN headers, calls IPv4 or IPv6 checksum handlers based on `update_flags`, restores any pulled VLAN headers, and drops on validation or writability failure. IPv6 handling walks hop/routing/destination headers, detects jumbo hop options, and ignores fragments or unsupported next headers.

State and persistence: action parameters are RCU-managed and per-action; packet state is mutated in headers and `skb->ip_summed`/checksum fields. No external persistent state is created.

Dependencies and integration: uses TC action API, skbuff pull/write helpers, IP/IPv6/TCP/UDP/SCTP checksum helpers, VLAN handling, and flow offload action translation.

Risks: checksum correctness depends on packet linearization, header offsets, VLAN restoration, and GSO exceptions. Some malformed UDP/UDPLite length cases are treated as "ignore obscure skb" rather than drop after partial preparation. Fragmented IPv4 and IPv6 packets are intentionally not deep-recalculated. Any packet dropped by this action increments qstats.

Test signals: packet-edit plus csum pipelines for IPv4/IPv6 TCP/UDP/UDPLite/ICMP/SCTP, VLAN and QinQ encapsulation, GSO packets, malformed/truncated headers, jumbo IPv6 hop option handling, offload translation, and drop-stat assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_csum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_ct.c -->
# sources/distributed-fs/ceph-client/net/sched/act_ct.c

Purpose: implements the `ct` TC action, integrating traffic control with netfilter conntrack, NAT, helpers, zones, labels/marks, defragmentation, and flow-table hardware offload.

Important APIs/functions: `tcf_ct_act()` is the runtime action; `tcf_ct_init()` parses and installs parameters; `tcf_ct_fill_params()` builds conntrack templates, marks, labels, helpers, zones, and NAT ranges; `tcf_ct_act_nat()` applies NAT; `tcf_ct_flow_table_get()` manages per-net/per-zone flow tables; `tcf_ct_flow_table_lookup()` accelerates established flows; `tcf_ct_flow_table_process_conn()` adds eligible TCP/UDP/GRE flows; `tcf_ct_offload_act_setup()` maps TC action offload. A global `zones_ht` rhashtable indexes `tcf_ct_flow_table` by net and zone, and `act_ct_wq` handles RCU cleanup.

Control flow: init rejects binding to unsupported non-ingress/non-clsact qdiscs, parses netlink attributes, allocates or replaces an IDR action, validates control action, fills params, obtains a zone flow table, then RCU-swaps params. Runtime handles `CLEAR` by removing skb ct state. Otherwise it identifies IPv4/IPv6, temporarily pulls to L3, handles fragments through nf defrag, trims network data, reuses cached ct only if net/zone/helper/direction match, tries flow-table lookup, associates a template for zone tracking, calls `nf_conntrack_in()`, applies NAT, assigns helpers and sequence adjustment when committing, runs helpers when needed, applies mark/label updates, confirms unconfirmed connections on commit, optionally promotes flow-table offload, restores skb headers, and records post-ct metadata.

State and persistence: per-action params are RCU-managed and may hold helper refs, label namespace refs, conntrack templates, NAT ranges, and a ref to a shared zone flow table. Conntrack table entries, marks, labels, NAT status, helper state, and flow offload entries persist outside the action. Global zone flow tables are refcounted and removed asynchronously.

Dependencies and integration: deeply integrates TC action API, netfilter conntrack/NAT/helper/label/zone/accounting/event APIs, nf_flow_table, IPv6 defrag, skb control blocks, flow offload, rhashtable, ordered workqueues, and the `tcf_frag_xmit_count` static branch.

Risks: lifetime and concurrency are high risk: params, templates, helper refs, flow tables, and ct references cross RCU, refcounting, and netfilter ownership. Header pull/push around L3 processing must balance on every path. NAT/helper combinations can require seqadj extensions. Flow offload only supports restricted protocols and no helpers/seqadj; stale/offloaded state must be refreshed or torn down safely. Confirmed conntrack clashes can drop the ct pointer, which the code explicitly reloads.

Test signals: ct clear, lookup-only, commit, force, zone, mark, label, SNAT/DNAT IPv4/IPv6, helper assignment, fragmented packets, cached ct reuse/mismatch, ingress-only binding rejection, flow-table promotion and teardown, hardware offload actions, concurrent action replacement, module unload cleanup, and nf_conntrack event/accounting verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_ctinfo.c -->
# sources/distributed-fs/ceph-client/net/sched/act_ctinfo.c

Purpose: implements the `ctinfo` TC action, copying selected information from conntrack marks into packet DSCP and/or `skb->mark` for qdisc classification.

Important APIs/functions: `tcf_ctinfo_act()` performs lookup and mutation; `tcf_ctinfo_dscp_set()` writes IPv4/IPv6 DSCP while preserving ECN; `tcf_ctinfo_cpmark_set()` copies masked connmark to skb mark; `tcf_ctinfo_init()` validates masks and installs params; `tcf_ctinfo_dump()` reports config plus counters; `tcf_ctinfo_cleanup()` frees params.

Control flow: init requires `TCA_CTINFO_ACT`, validates that DSCP mask is exactly six contiguous bits and does not overlap the optional state mask, parses zone and copy-mask options, then RCU-swaps params. Runtime pulls IPv4/IPv6 headers, gets attached conntrack or performs tuple lookup in the configured zone, conditionally applies DSCP when no state mask is configured or the state bit is present, optionally copies mark, releases lookup refs, and returns the configured action.

State and persistence: per-action params are RCU-managed. Atomic counters track DSCP set, DSCP errors, and cpmark set. Packet state changes are DS field writes and `skb->mark`; conntrack mark is read only.

Dependencies and integration: depends on conntrack and connmark support, TC action API, IPv4/IPv6 DS field helpers, `skb_try_make_writable()`, and netfilter tuple lookup.

Risks: DSCP writes can fail if the skb cannot be made writable; this increments an error counter but still returns the configured action. Misconfigured masks are rejected, but runtime conntrack absence leaves packets unchanged. IPv6/IPv4 header pull length must be correct before DS field mutation.

Test signals: DSCP restore from mark with and without state mask, cpmark copy, invalid mask validation, IPv4/IPv6 writability failure counters, zone lookups, dump counter accuracy, and replacement cleanup under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_ctinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_gact.c -->
# sources/distributed-fs/ceph-client/net/sched/act_gact.c

Purpose: implements the generic TC action `gact`, returning configured control actions such as pass, drop, trap, goto chain, pipe, reclassify, or probabilistic alternatives.

Important APIs/functions: `tcf_gact_init()` creates/replaces an action; `tcf_gact_act()` returns the runtime action and updates stats; `tcf_gact_dump()` reports configuration; `tcf_gact_stats_update()` merges hardware stats; `tcf_gact_offload_act_setup()` maps supported actions to flow offload entries. Optional `CONFIG_GACT_PROB` adds random and deterministic probability functions.

Control flow: init parses `TCA_GACT_PARMS`, optionally validates probability parameters, allocates or finds an IDR action, validates the primary control action and goto chain, then updates action and probability state under lock. Runtime reads the configured action, optionally substitutes a probability fallback based on random or packet-count modulo, updates bstats/lastuse, counts drops for `TC_ACT_SHOT`, and returns the result.

State and persistence: action state is stored in the TC IDR and includes primary action, optional probability action/type/value, packet counter for deterministic mode, stats, and goto-chain pointer. No external durable state is created.

Dependencies and integration: shared TC action API, optional random number generation, flow offload mapping for accept/drop/trap/goto, module/pernet registration.

Risks: probability fallback does not allow goto-chain fallback. Memory barriers pair probability value/type updates with runtime reads. Offload supports only a subset of software control actions; unsupported actions return `-EOPNOTSUPP`.

Test signals: basic pass/drop/trap/goto execution, bind and replace semantics, probability random/deterministic distribution, dump output, hardware offload acceptance/rejection, and stats update behavior for drop actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_gact.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_gate.c -->
# sources/distributed-fs/ceph-client/net/sched/act_gate.c

Purpose: implements the `gate` TC action, allowing packets only during configured time slots and optionally enforcing per-entry byte limits.

Important APIs/functions: `tcf_gate_init()` parses schedule parameters and starts the timer; `tcf_gate_act()` enforces current gate state; `gate_timer_func()` advances schedule entries; `parse_gate_list()`/`parse_gate_entry()` build entry lists; `tcf_gate_dump()` reports schedule; `tcf_gate_cleanup()` cancels timers and frees params; `tcf_gate_offload_act_setup()` maps schedules to `FLOW_ACTION_GATE`.

Control flow: init parses base time, cycle time, clock ID, flags, priority, and entry list. Replacement can reuse old entries and defaults. It resolves clock IDs to timekeeper offsets, cancels/reinitializes the hrtimer when timing base changes, computes cycle time from entries if omitted, RCU-swaps params, marks gate pending/open, selects the first entry, and starts the soft hrtimer at the next cycle boundary. The timer sets open/closed status, max octets, close time, advances to the next entry, and restarts. Runtime drops packets when pending is clear but gate is closed, or when byte count exceeds max octets; otherwise it returns the configured action.

State and persistence: per-action state includes RCU schedule params, an hrtimer, current/next entry pointers, current close time, gate status flags, octet counters, clock offset, stats, and goto-chain pointer. Schedule state is runtime-only.

Dependencies and integration: TC action API, hrtimer/timekeeping offsets, netlink nested attributes, qdisc packet length, flow offload gate entries, RCU cleanup, and pernet registration.

Risks: timer and action path share mutable gate state under `tcf_lock`; replacements must cancel timers when clock/base changes to avoid stale callbacks. Empty entry lists are invalid for new actions. Time arithmetic depends on nonzero cycle time and valid intervals. Offload entry duplication allocates memory that must be destroyed through the flow action entry destructor.

Test signals: open/closed slot behavior, max-octet drops/overlimits, base time in past/future, clock ID validation, replacement reusing entries, timer cancellation on timing changes, dump roundtrip, offload gate entry creation/destruction, and cleanup under active timer load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_ife.c -->
# sources/distributed-fs/ceph-client/net/sched/act_ife.c

Purpose: implements the Inter-FE (`ife`) TC action, encoding selected packet metadata into an outer Ethernet/IFE header or decoding received IFE metadata back into skb fields.

Important APIs/functions: exported metadata helpers include `register_ife_op()`, `unregister_ife_op()`, generic u16/u32 encode/get/check/alloc/validate/release functions, and internal metadata list builders. `tcf_ife_init()` installs encode/decode params, `tcf_ife_act()` dispatches runtime encode/decode, `tcf_ife_encode()` prepends IFE metadata, `tcf_ife_decode()` parses TLVs and applies metadata ops, `tcf_ife_dump()` reports config, and `tcf_ife_cleanup()` releases metadata ops.

Control flow: metadata ops register globally by metaid/name. Init parses action params, optional destination/source MAC, ethertype, and metadata allow/use list; it autoloads missing metadata modules by known meta ID, validates values, allocates or replaces the action, validates control action, populates the metadata list or installs all registered metadata ops, and RCU-swaps params. Encode computes the total TLV size by asking each op whether metadata is present, checks MTU on egress, prepends an IFE header, encodes each TLV, and fills outer Ethernet addresses/type. Decode pushes MAC header at ingress if needed, calls `ife_decode()`, iterates TLVs, dispatches matching metadata decode ops, counts unknown metadata as overlimits, resets protocol with `eth_type_trans()`, and returns action.

State and persistence: action params contain encode/decode flag, outer Ethernet fields, ethertype, and a list of `tcf_meta_info` entries with module references and optional configured values. The global `ifeoplist` stores metadata operation providers under a rwlock. Packet metadata and headers are mutated at runtime; action state is RCU-managed.

Dependencies and integration: depends on `NET_IFE`, TC action API, IFE TLV helpers, Ethernet header helpers, module autoload aliases `ife-meta-*`, and metadata provider modules for skb mark, priority, and tcindex.

Risks: metadata op registration exports appear swapped in this source (`register_ife_op` near `EXPORT_SYMBOL_GPL(unregister_ife_op)` and vice versa), which is a review-sensitive signal. Encoding must not exceed MTU on egress and must balance ingress header push/pull. Metadata list lookup is linear. Unknown or malformed TLVs can drop packets or increment overlimit stats.

Test signals: encode/decode roundtrips for skb mark/prio/tcindex, metadata module autoload, configured versus allow-all metadata lists, egress MTU drop, malformed TLVs, missing metadata ops, dump output, module unregister/refcount behavior, and ingress header handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_ife.c -->
