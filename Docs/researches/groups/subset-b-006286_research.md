<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svcsock.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/svcsock.c

Purpose: Implements the server-side SUNRPC socket transport for UDP and TCP, including listener creation, accepted TCP connection setup, UDP datagram receive/send, TCP record-fragment receive/send, socket callback installation, TLS handshake support, and socket teardown for `svc_xprt`.

Important APIs/types/functions: `svc_init_xprt_sock()` and `svc_cleanup_xprt_sock()` register/unregister the `tcp` and `udp` `svc_xprt_class` instances. `svc_addsock()` imports a user-provided listener fd into an RPC service. `svc_create_socket()` creates kernel sockets for service listeners. `svc_setup_socket()` allocates `struct svc_sock`, optional `bio_vec` send vectors, saves original socket callbacks, registers rpcbind state when needed, and dispatches to `svc_udp_init()` or `svc_tcp_init()`. UDP uses `svc_udp_recvfrom()`, `svc_udp_sendto()`, `svc_udp_has_wspace()`, and destination-address control-message helpers. TCP uses `svc_tcp_accept()`, `svc_tcp_recvfrom()`, `svc_tcp_sendto()`, `svc_tcp_read_marker()`, `svc_tcp_read_msg()`, page save/restore helpers, `receive_cb_reply()`, and TLS helpers `svc_tcp_handshake()` / `svc_tcp_handshake_done()`.

Control flow: Socket callbacks set transport flags and enqueue the `svc_xprt`: UDP/TCP data-ready sets `XPT_DATA`, listening TCP sets `XPT_CONN`, and TCP state changes schedule deferred close when a connected socket leaves `TCP_ESTABLISHED`. UDP receive first peeks for control messages, pulls an skb with `skb_recv_udp()`, records source/destination addresses, either decodes in place from linear skb data or copies nonlinear skb data into the request XDR buffer, then marks the request secure based on source port. UDP send releases the receive skb context, sets packet-info control data from the recorded destination address, converts the reply `xdr_buf` to bvecs, and sends with `MSG_SPLICE_PAGES`. TCP accept restores inherited callbacks on the child socket before wrapping it in a new temporary `svc_sock`. TCP receive reads the 4-byte RPC record marker, validates total fragment size against `sv_max_mesg`, restores pages saved from partial prior receives, reads the remaining fragment into request pages, preserves incomplete state back into `svsk`, and either returns a complete RPC Call or consumes callback replies via `receive_cb_reply()`. TCP send prepends an RPC record marker allocated from the page-frag cache, sends marker plus reply bvecs, and closes the transport on short write or error.

State and persistence behavior: State is in-memory per `svc_sock` and `svc_xprt`: saved socket callbacks, pending TCP marker bytes (`sk_tcplen`), partial TCP message bytes (`sk_datalen`), saved page pointers (`sk_pages`), send bvecs, TLS handshake completion, transport flags, reserved bytes, and socket credentials. No durable persistence exists. UDP skb ownership is carried in `rq_xprt_ctxt` until reply release. TCP partial receive pages are temporarily moved out of the request and into `svsk` across worker iterations; teardown calls `svc_tcp_clear_pages()` to drop any retained pages.

Dependencies and integration points: Depends on Linux socket, TCP/UDP/IP/IPv6, skb, page, bvec, TLS handshake, key, and net namespace APIs; SUNRPC service APIs in `svc_xprt`, stats, XDR helpers, and backchannel client transport APIs; tracepoints in `sock` and `sunrpc`; rpcbind registration through `svc_register()`. The class ops are consumed by SUNRPC service core and ultimately by NFS server transports.

Risks: Socket callback replacement relies on memory barriers and lock ordering; mistakes can lead to stale `sk_user_data` dereferences. TCP partial receive state is page-owning and must be cleared on all close paths to avoid leaks. `svc_tcp_accept()` returns `NULL` after failed `sock_alloc_file()` without explicitly releasing `newsock`, so callers must rely on kernel socket/file semantics for cleanup in that path. UDP control-message parsing drops datagrams if packet-info is missing or unexpected, which is correct for multihomed reply routing but sensitive to socket option setup. TLS handshake blocks an nfsd thread for up to `SVC_HANDSHAKE_TO`, as noted by the source comment. TCP callback reply handling copies only the head buffer, which is intentionally narrow and could be insufficient for future larger callback replies.

Test signals: Exercise UDP IPv4/IPv6 receive/send with packet-info and multihomed destination addresses, nonlinear skb copy and checksum failure paths, TCP fragmented records across multiple receives, oversized TCP fragment close, short TCP send close, accepted connection local/remote address capture, TLS handshake success/failure/timeout, backchannel reply matching by XID, buffer resizing after thread-count changes, and teardown with partial TCP pages retained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svcsock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysctl.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/sysctl.c

Purpose: Provides the optional `/proc/sys/sunrpc` sysctl interface for SUNRPC debug controls and a readable transport list when `CONFIG_SUNRPC_DEBUG` is enabled.

Important APIs/types/functions: Exports global debug flags `rpc_debug`, `nfs_debug`, `nfsd_debug`, and `nlm_debug`. `proc_dodebug()` implements read/write parsing for the debug flag sysctls. `proc_do_xprt()` formats registered service transports using `svc_print_xprts()`. `rpc_register_sysctl()` registers the `sunrpc` sysctl table and `rpc_unregister_sysctl()` removes it. `debug_table[]` defines `rpc_debug`, `nfs_debug`, `nfsd_debug`, `nlm_debug`, and read-only `transports`.

Control flow: On registration, the file installs the table once under `sunrpc`. Reads of debug flags format the stored integer as hex plus newline. Writes trim leading whitespace, copy a bounded input into a stack buffer, parse with base autodetection, validate trailing characters, store into the target global, and call `rpc_show_tasks(&init_net)` when `rpc_debug` is written. Reads of `transports` generate a bounded temporary report and copy it to userspace with `memory_read_from_buffer()`.

State and persistence behavior: State is only the four exported unsigned integer debug masks and the `sunrpc_table_header` registration pointer. Values persist only while the module/kernel is running. The interface is absent when `CONFIG_SUNRPC_DEBUG` is disabled, though the global debug symbols remain declared outside the conditional.

Dependencies and integration points: Integrates Linux sysctl helpers, uaccess-safe buffer copying, SUNRPC scheduler task display, stats/debug consumers, and service transport reporting. NFS, NFSD, NLM, and SUNRPC code can test the exported masks for conditional logging.

Risks: `proc_dodebug()` intentionally accepts numeric writes up to 19 bytes plus NUL; longer writes fail with `-EINVAL`. Debug state is global rather than per-network-namespace, while `rpc_show_tasks()` is hardwired to `init_net`. Heavy task dumping on every `rpc_debug` write can be noisy in production. The sysctl handlers are compiled out without `CONFIG_SUNRPC_DEBUG`, so tests must account for configuration-dependent presence.

Test signals: Validate debug sysctl read/write formatting, invalid trailing characters, oversized writes, empty/offset reads, `rpc_debug` task dump side effect, `transports` read truncation behavior, and idempotent register/unregister cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysfs.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/sysfs.c

Purpose: Exposes SUNRPC clients, transport switches, and individual transports under `/sys/kernel/sunrpc` with network-namespace-aware kobjects, read-only diagnostics, and write handlers for adding, redirecting, offlining, onlining, and deleting client transports.

Important APIs/types/functions: `rpc_sysfs_init()` creates the `sunrpc` kset plus `rpc-clients` and `xprt-switches` roots; `rpc_sysfs_exit()` tears them down. Setup/destroy APIs are `rpc_sysfs_client_setup/destroy()`, `rpc_sysfs_xprt_switch_setup/destroy()`, and `rpc_sysfs_xprt_setup/destroy()`. Show handlers expose client version/program/max_connect, xprt destination/source/xprtsec/info/state, and switch info. Store handlers include `rpc_sysfs_xprt_switch_add_xprt_store()`, `rpc_sysfs_xprt_dstaddr_store()`, `rpc_sysfs_xprt_state_change()`, and `rpc_sysfs_xprt_del_xprt()`. `struct xprt_addr` defers old destination string freeing through RCU.

Control flow: Initialization creates shared roots. When a transport switch is allocated, a `switch-%d` kobject is created in the appropriate net namespace; each transport becomes `xprt-%d-%s` under that switch; each RPC client gets `clnt-%d` with a sysfs link to its switch. Reads acquire stable references with `refcount_inc_not_zero()`, `xprt_get()`, or `xprt_switch_get()`, format state, and release. Adding a transport clones the main xprt’s class, net, address, server name, backchannel, security policy, and timeout settings, then inserts it into the switch. Writing `dstaddr` locks the xprt write bit, swaps the display address string through RCU, reparses the sockaddr while preserving port, and forces reconnect. Writing `xprt_state` permits non-main xprts to go offline, online, or be removed if offline. `del_xprt` offlines and deletes a non-main transport.

State and persistence behavior: Sysfs kobjects mirror live in-kernel RPC objects and hold back-pointers rather than owning the main object lifetime. Destination display strings can be replaced at runtime and old strings are released after an RCU grace period. Transport state changes affect live `rpc_xprt` flags and switch active counts only; there is no durable persistence across reboot or client recreation.

Dependencies and integration points: Depends on kobject/kset sysfs infrastructure, network namespace sysfs operations, SUNRPC client and transport refcounting, multipath switch APIs, address parsing helpers, xprtsock operations for source info, and xprt lifecycle functions in `xprt.c`/`xprtmultipath.c`.

Risks: The sysfs write handlers perform live transport mutation; correctness depends on `XPRT_LOCKED` serialization and matching `xprt_release_write()` calls. `dstaddr_store()` assigns the display string before checking whether `rpc_pton()` produced a valid address length, so invalid input can still alter display state and force reconnect. Several show handlers use `sprintf()` into a page-sized sysfs buffer and assume bounded field sizes. Non-main xprt protection prevents deleting the primary transport, but operational scripts must offline before remove. Namespace and object teardown ordering must avoid stale sysfs back-pointers.

Test signals: Validate kobject creation/removal and uevents, net namespace visibility, client link creation/removal, read formatting for connected and closed transports, adding an xprt from a switch, destination address rewrite with port preservation, unsupported class rejection for `dstaddr`, offline/online/remove transitions and active counts, refusal to mutate main xprt, interruptible lock waits, and RCU cleanup of replaced address strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysfs.h -->
# sources/distributed-fs/ceph-client/net/sunrpc/sysfs.h

Purpose: Declares the SUNRPC sysfs object wrappers and lifecycle hooks used by client transport and multipath code to publish live RPC client/xprt state under sysfs.

Important APIs/types/functions: `struct rpc_sysfs_xprt_switch` embeds a `kobject` and tracks `struct net *`, `struct rpc_xprt_switch *`, and an associated `struct rpc_xprt *`. `struct rpc_sysfs_xprt` embeds a `kobject` and links an individual `rpc_xprt` to its switch. Public functions cover global sysfs initialization/exit and setup/destroy for clients, switches, and xprts.

Control flow: `xprt_switch_alloc()` calls `rpc_sysfs_xprt_switch_setup()` and `rpc_sysfs_xprt_setup()`. `xprt_free()` calls `rpc_sysfs_xprt_destroy()`. RPC client creation/destruction calls the client setup/destroy APIs. The header does not implement logic; it defines the cross-file contract consumed by `sysfs.c`, `xprt.c`, and `xprtmultipath.c`.

State and persistence behavior: The declared structs are transient kobject containers with raw back-pointers to live RPC objects. Lifetime is coordinated externally by kobject reference counts and the RPC transport/switch teardown paths. No persistent state is defined here.

Dependencies and integration points: Requires SUNRPC client, xprt, xprt switch, kobject, and network namespace types from including translation units. It is the narrow include used to avoid exposing `sysfs.c` internals.

Risks: Because the header exposes back-pointer fields, users must preserve lifetime ordering and must not dereference after destroy. There are no stubs here for disabled sysfs configurations, so build coverage depends on the broader SUNRPC build selecting this file consistently.

Test signals: Compile-time checks that all setup/destroy declarations match `sysfs.c`, and runtime tests that xprt/switch/client allocation and free paths call the matching setup/destroy hooks exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/timer.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/timer.c

Purpose: Implements the datagram RPC round-trip-time estimator used to compute adaptive retransmission timeouts for frequently issued RPC procedures.

Important APIs/types/functions: `rpc_init_rtt()` initializes `struct rpc_rtt` arrays for five timer classes. `rpc_update_rtt()` updates smoothed RTT (`srtt`) and mean deviation (`sdrtt`) using Van Jacobson-style integer arithmetic. `rpc_calc_rto()` returns the retransmission timeout for a timer class. Constants are `RPC_RTO_MAX`, `RPC_RTO_INIT`, and `RPC_RTO_MIN`.

Control flow: Initialization stores the base timeout and seeds each timer bucket with either zero adjusted smoothed RTT or `(timeo - RPC_RTO_INIT) << 3`, plus initial deviation. Updates ignore timer index zero, negative samples from jiffies wrap, and coerce zero samples to one jiffy. The sample delta adjusts `srtt`, its absolute value adjusts `sdrtt`, and deviation is clamped to a minimum. Calculation returns the fixed base timeout for timer zero, otherwise `(srtt + 7) >> 3` plus deviation, capped at 60 seconds.

State and persistence behavior: State lives in caller-owned `struct rpc_rtt`, typically per RPC client. The estimator is memory-only and can be reset by client transport timeout logic after major timeouts.

Dependencies and integration points: Used by `xprt_wait_for_reply_request_rtt()` and `xprt_update_rtt()` in `xprt.c`, with procedure timer classes supplied by RPC procedure metadata. The code is intentionally scoped to datagram-style transports; stream transports generally use fixed/default timeout handling.

Risks: Timer indexes are one-based externally and decremented internally; callers passing zero deliberately bypass estimation. Bad timer indexes beyond the fixed array would be a caller bug. Conservative handling of infrequent/non-idempotent procedures avoids stale RTTs but can underutilize good network conditions.

Test signals: Verify initialization for timeouts below/equal/above `RPC_RTO_INIT`, update behavior for zero and negative samples, min/max timeout clamps, timer-zero bypass, retransmission count interactions through `rpc_set_timeo()` callers, and reset after major timeout in `xprt_adjust_timeout()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xdr.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xdr.c

Purpose: Provides generic SUNRPC XDR encoding, decoding, and `xdr_buf` manipulation utilities across head/page/tail storage, including stream cursors, page alignment, subsegments, zero/copy helpers, array processing, bio_vec conversion, and opaque-auth helpers.

Important APIs/types/functions: Basic encoders include `xdr_encode_netobj()`, `xdr_encode_opaque_fixed()`, `xdr_encode_opaque()`, and `xdr_encode_string()`. Buffer/page helpers include `xdr_buf_pagecount()`, `xdr_alloc_bvec()`, `xdr_free_bvec()`, `xdr_buf_to_bvec()`, `xdr_inline_pages()`, `_copy_from_pages()`, `read_bytes_from_xdr_buf()`, `write_bytes_to_xdr_buf()`, `xdr_decode_word()`, and `xdr_encode_word()`. Stream encode/decode APIs include `xdr_init_encode()`, `xdr_init_encode_pages()`, `xdr_reserve_space()`, `xdr_reserve_space_vec()`, `xdr_truncate_encode()`, `xdr_init_decode()`, `xdr_inline_decode()`, `xdr_read_pages()`, `xdr_set_pagelen()`, `xdr_enter_page()`, and `xdr_finish_decode()`. Structural helpers include `xdr_buf_subsegment()`, `xdr_stream_subsegment()`, `xdr_stream_move_subsegment()`, `xdr_stream_zero()`, `xdr_buf_trim()`, `xdr_decode_array2()`, `xdr_encode_array2()`, `xdr_process_buf()`, `xdr_stream_decode_string_dup()`, and opaque-auth encode/decode.

Control flow: Encoding starts with an initialized `xdr_stream` over an `xdr_buf`; reservations align byte counts to 4-byte units, advance head or page lengths, and use a scratch buffer when an encoded item crosses a page boundary. Decoding initializes a cursor over head, pages, or tail, advances inline when possible, or copies split objects into scratch. Page-oriented decode can realign data from the head into pages and move surplus into the tail via shrink/shift helpers. Buffer mutation routines perform left/right memmove-like operations across head, page list, and tail while handling highmem mappings and cache flushes. Subsegment helpers create views over portions of an `xdr_buf`; read/write/word/array helpers use those views to process data that may cross storage regions.

State and persistence behavior: State is caller-owned in `struct xdr_buf` and `struct xdr_stream`: current pointer, end pointer, page pointer, mapped highmem address, scratch iov, buffer lengths, and head/page/tail layout. The code allocates optional bvec arrays and temporary array elements, but has no durable state. `xdr_finish_decode()` must unmap any locally mapped page.

Dependencies and integration points: Used widely by SUNRPC clients/servers, NFS protocol encoders/decoders, socket send paths converting replies to bvecs, and RPC/RDMA chunk handling. Depends on Linux page mapping, highmem, scatterlist, bio_vec, XDR/RPC protocol constants, and SUNRPC tracepoints.

Risks: This is a high-blast-radius utility file; off-by-one mistakes in length, padding, page-base, or shift calculations can corrupt RPC messages or page data. Several helpers use `BUG_ON()`/`WARN_ON_ONCE()` for impossible states, so caller contract violations can crash or warn. `xdr_buf_pages_fill_sparse()` appears to skip allocation when a page pointer is NULL (`if (!buf->pages[i]) continue;`), so sparse-page behavior deserves scrutiny against expected semantics. `xdr_buf_to_bvec()` warns and truncates if caller-provided bvec capacity is too small. Callers must not use `xdr_truncate_encode()` on unsafe inlined page-cache replies except in the documented narrow tail case.

Test signals: Unit or KUnit-style coverage should exercise encode/decode alignment, objects split across page boundaries, highmem page decode/finish, head/page/tail subsegments, page realignment and truncation, `xdr_stream_move_subsegment()` in both directions, zeroing across all regions, bvec overflow handling, sparse page expansion, array elements crossing head/page/tail boundaries, opaque-auth size limits, and consumers such as TCP/UDP send and RDMA chunk registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprt.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprt.c

Purpose: Implements the generic client-side SUNRPC transport core: transport class registration, request slot allocation, write serialization, congestion control, timeout/retry handling, transmit and receive queue management, connection lifecycle, backchannel request initialization, sysfs/debugfs registration, and transport reference-counted teardown.

Important APIs/types/functions: Class APIs are `xprt_register_transport()`, `xprt_unregister_transport()`, `xprt_find_transport_ident()`, and `xprt_create_transport()`. Write/congestion APIs include `xprt_reserve_xprt()`, `xprt_reserve_xprt_cong()`, `xprt_release_xprt()`, `xprt_release_xprt_cong()`, `xprt_request_get_cong()`, `xprt_release_rqst_cong()`, and `xprt_adjust_cwnd()`. Connection APIs include `xprt_connect()`, `xprt_lock_connect()`, `xprt_unlock_connect()`, `xprt_force_disconnect()`, `xprt_disconnect_done()`, reconnect backoff helpers, and autodisconnect timer/work functions. Request APIs include `xprt_reserve()`, `xprt_retry_reserve()`, `xprt_alloc_slot()`, `xprt_free_slot()`, `xprt_request_enqueue_receive()`, `xprt_complete_rqst()`, `xprt_request_enqueue_transmit()`, `xprt_prepare_transmit()`, `xprt_transmit()`, and `xprt_release()`.

Control flow: Transports are registered globally by ident/netid and module references are taken while creating instances. A task reserves a slot, initializes an XID and timeouts, encodes into request buffers, enqueues for receive when expecting a reply, enqueues for transmit, reserves the transport write lock, drains the xmit queue, and then sleeps on pending until completion or timeout. Incoming transport implementations call `xprt_lookup_rqst()` under `queue_lock` by XID and complete with `xprt_complete_rqst()`, which updates received byte count, frees receive bvecs, removes the request from the rb-tree, and wakes the task. Timeout handlers distinguish minor retry timeouts from major timeouts, reset RTT/cwnd state, and let transport-specific timers run. Disconnect paths schedule close work under `XPRT_LOCKED`, clear connected/write-space/congestion waits, and wake pending tasks with `-ENOTCONN`.

State and persistence behavior: `struct rpc_xprt` holds locks (`transport_lock`, `reserve_lock`, `queue_lock`), request free/backlog/pending/sending queues, rb-tree receive queue keyed by XID, transmit list, congestion window and in-flight credit count, reconnect/idle timers, connect cookie, stats, slot counts, transport id, sysfs/debugfs objects, and kref lifetime. `struct rpc_rqst` tracks XID, connection cookie, send/receive buffers, retry counters, RTT sample, bytes sent/received, queue nodes, and pin count. All state is in-memory per transport.

Dependencies and integration points: Transport implementations provide `struct rpc_xprt_ops` for connect, close, send, destroy, request preparation, buffer allocation, and wait/timer policies. Integrates with RPC scheduler wait queues, auth (`rpcauth_xmit_need_reencode()`), RTT estimator in `timer.c`, sysfs in `sysfs.c`, debugfs, fail injection, backchannel support, and multipath switch state at the end of the file.

Risks: Concurrency is complex: write lock state, connect cookies, receive rb-tree pins, queue locks, and teardown work must stay ordered to avoid use-after-free or lost wakeups. Dynamic slot allocation can return `-ENOMEM` or backlog tasks, so callers must handle repeated `-EAGAIN`. Congestion control depends on balanced `rq_cong` get/put. `xprt_request_rb_insert()` only warns on duplicate XID and returns, so XID collision behavior depends on upstream randomization/incrementing and request lifecycle. Autodisconnect scheduling races are guarded by locks and timer deletion; regressions there can close active transports or leak timers.

Test signals: Exercise class registration and module autoload by netid, slot allocation/free and backlog wakeup, write-lock handoff with and without congestion, cwnd growth/halving on success/timeout, receive rb-tree lookup/completion/bad XID stats, pinned request dequeue waiting, transmit queue ordering for congestion credits and same-owner sequence requests, disconnect while sending/pending, connect cookie retransmission detection, idle autodisconnect, transport destroy with outstanding backchannel resources, and sysfs/debugfs lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtmultipath.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtmultipath.c

Purpose: Implements multipath support for SUNRPC client transports by managing `rpc_xprt_switch` lists, reference-counted switch lifetime, active/offline counts, switch IDs, sysfs publication, and iterator policies for selecting transports.

Important APIs/types/functions: Switch management APIs include `rpc_xprt_switch_add_xprt()`, `rpc_xprt_switch_remove_xprt()`, `rpc_xprt_switch_get_main_xprt()`, `xprt_switch_alloc()`, `xprt_switch_get()`, `xprt_switch_put()`, `rpc_xprt_switch_set_roundrobin()`, and `rpc_xprt_switch_has_addr()`. Iterator APIs include `xprt_iter_init()`, `xprt_iter_init_listall()`, `xprt_iter_init_listoffline()`, `xprt_iter_rewind()`, `xprt_iter_xchg_switch()`, `xprt_iter_destroy()`, `xprt_iter_xprt()`, and `xprt_iter_get_next()`. Static policies are singular, round-robin, list-all, and list-offline.

Control flow: A switch is allocated with one initial xprt, gets an ID, initializes lock/kref/list/queue counters, creates sysfs switch/xprt objects, and records a network namespace. Adding a transport takes a reference, appends it with RCU list operations if it belongs to the same net namespace, increments total and active counts, and publishes sysfs. Removing a transport updates counts, clears the net when the list becomes empty, deletes from the RCU list, and drops the transport reference. Iterators hold a switch reference and use RCU read-side sections to walk active or offline entries. Round-robin selection advances a cursor and skips transports whose queue length is above the switch average.

State and persistence behavior: `rpc_xprt_switch` maintains `xps_xprt_list`, `xps_nxprts`, `xps_nactive`, `xps_nunique_destaddr_xprts`, `xps_queuelen`, `xps_net`, `xps_iter_ops`, IDA id, kref, and sysfs pointer. Iterators maintain an RCU pointer to the switch, a cursor, and optional override ops. State is memory-only and freed with RCU after kref release.

Dependencies and integration points: Used by RPC clients to select transports, by `xprt.c` for online/offline/delete state changes, and by `sysfs.c` for live management. Depends on Linux RCU list traversal, kref, IDA, atomic counters, SUNRPC address comparison, and xprt refcounting.

Risks: Correctness depends on pairing RCU list updates with `xprt_get()`/`xprt_put()` and on readers taking references before leaving RCU. Active counts must stay in sync with `XPRT_OFFLINE` transitions from `xprt.c` and sysfs; double offline/remove mistakes can skew scheduling. Round-robin queue balancing uses approximate atomic counters and can be unfair under rapidly changing load. `xprt_switch_alloc()` does not visibly handle ID allocation failure before sysfs naming, so low-memory IDA failures merit review.

Test signals: Validate add/remove refcounts and RCU safety, net namespace rejection, active/offline count transitions, main transport lookup, duplicate address detection, singular vs round-robin vs list-all vs list-offline iteration, cursor rewind/exchange, queue-length based skipping, sysfs setup/destroy coupling, and cleanup of switch IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtmultipath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/Makefile -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/Makefile

Purpose: Defines the kernel build composition for the RPC/RDMA transport module `rpcrdma.o`.

Important APIs/types/functions: The Makefile adds `rpcrdma.o` when `CONFIG_SUNRPC_XPRT_RDMA` is enabled. `rpcrdma-y` links client transport, RPC/RDMA protocol, verbs, FRWR operations, IB client notifications, server RDMA transport/send/receive/RW/pcl code, and module initialization. `rpcrdma-$(CONFIG_SUNRPC_BACKCHANNEL)` conditionally adds `backchannel.o`.

Control flow: Kbuild compiles the listed objects into one module/built-in object according to kernel config. Backchannel support is included only when `CONFIG_SUNRPC_BACKCHANNEL` is set.

State and persistence behavior: No runtime state. Build-time configuration controls which object code is present.

Dependencies and integration points: Integrates xprtrdma with SUNRPC client/server RDMA support and the kernel Kbuild system. The object list must match symbols referenced by `module.c`, client/server RDMA paths, and optional backchannel ops.

Risks: Missing an object from `rpcrdma-y` produces link failures or feature omissions. Backchannel symbols must remain guarded consistently with `CONFIG_SUNRPC_BACKCHANNEL`. Object ordering is usually not semantically important but module init/exit symbols must be included exactly once.

Test signals: Build with `CONFIG_SUNRPC_XPRT_RDMA=m/y`, with and without `CONFIG_SUNRPC_BACKCHANNEL`, and run module load/unload or built-in boot smoke tests to catch unresolved symbols and init ordering issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/backchannel.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/backchannel.c

Purpose: Implements reverse-direction RPC callback support over RPC/RDMA for client transports, including backchannel setup, maximum payload/slot reporting, reply marshalling/sending, preallocated request recycling, and incoming callback Call delivery to the upper-layer callback service.

Important APIs/types/functions: `xprt_rdma_bc_setup()` records available backchannel server credits. `xprt_rdma_bc_maxpayload()` and `xprt_rdma_bc_max_slots()` report inline payload and slot limits. `xprt_rdma_bc_send_reply()` marshals and sends a backchannel reply through `rpcrdma_bc_marshal_reply()` and `frwr_send()`. `xprt_rdma_bc_destroy()` releases preallocated backchannel requests. `xprt_rdma_bc_free_rqst()` returns a request to the pool after ULP processing. `rpcrdma_bc_receive_call()` wraps an incoming RDMA receive buffer as an RPC request and enqueues it with `xprt_enqueue_bc_request()`.

Control flow: Setup currently sets `rb_bc_srv_max_requests` to half of `RPCRDMA_BACKWARD_WRS`. Reply sending checks connection state, obtains congestion credit, encodes a minimal RPC/RDMA header into the request header buffer, prepares send SGEs for inline data, and posts via FRWR; failures close the RDMA xprt and return `-ENOTCONN` unless marshalling failed permanently. Incoming calls borrow a request from `bc_pa_list` or allocate/setup a new one up to `RPCRDMA_BACKWARD_WRS`, point its receive `xdr_buf` at the RDMA receive buffer, attach the `rpcrdma_rep` to the request to keep the buffer alive, and enqueue the callback. Overflow logs a warning and forces disconnect.

State and persistence behavior: State lives in `rpc_xprt` backchannel fields (`bc_pa_list`, `bc_pa_lock`, `bc_alloc_count`) and in `rpcrdma_req`/`rpcrdma_rep` ownership links. Receive buffers are held by `req->rl_reply` until `xprt_rdma_bc_free_rqst()` returns the rep and request to their pools. No durable persistence.

Dependencies and integration points: Integrates SUNRPC backchannel APIs, RPC/RDMA request/reply buffers, XDR stream encoding, FRWR send, congestion helpers from `xprt.c`, and callback queueing in `bc_xprt`. It is conditionally built by the xprtrdma Makefile.

Risks: Backchannel receive buffer lifetime depends on the request holding `rep`; premature repost/free would corrupt callback decoding. Allocation is capped to prevent remote resource exhaustion, but overflow disconnects the whole transport. Reply marshalling supports inline backchannel replies only and depends on negotiated inline sizes. Congestion credit failures return `-EBADSLT`, which upper layers must treat correctly. The credit model explicitly ignores remote backchannel credits, relying on ULP replay/session behavior.

Test signals: Exercise setup credit reporting, max payload with different inline send/recv sizes, reply send success and disconnected/error paths, congestion failure, callback Call enqueue and XID propagation, request pool reuse, dynamic allocation cap/overflow disconnect, receive buffer hold/repost after free, and module builds with backchannel enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/backchannel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/frwr_ops.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/frwr_ops.c

Purpose: Implements RPC/RDMA Fast Registration Work Request memory registration for client RDMA chunks, including MR allocation/release, device capability sizing, XDR buffer to scatterlist mapping, send WR chaining, remote invalidation handling, synchronous/asynchronous local invalidation, and write-pad MR registration.

Important APIs/types/functions: MR lifecycle functions are `frwr_mr_init()`, `frwr_mr_release()`, `frwr_reset()`, `frwr_mr_put()`, and `frwr_mr_unmap()`. Capability setup is `frwr_query_device()`. Registration/mapping is `frwr_map()`. Send posting is `frwr_send()`. Invalidation paths include `frwr_reminv()`, `frwr_unmap_sync()`, `frwr_unmap_async()`, and completion callbacks `frwr_wc_fastreg()`, `frwr_wc_localinv()`, `frwr_wc_localinv_wake()`, and `frwr_wc_localinv_done()`. `frwr_wp_create()` registers the write-padding buffer.

Control flow: Device query verifies FRWR capabilities, chooses MR type (`IB_MR_TYPE_MEM_REG` or `IB_MR_TYPE_SG_GAPS`), computes max FR depth, send/recv WR budgets, receive batching, and max RDMA segments. Mapping walks an `xdr_buf` cursor through head, page list, and tail, building scatterlist entries up to provider depth and SG-gap constraints, DMA maps the SG list, maps it into an IB MR, tags the IOVA high bits with the RPC XID, rotates the rkey, records handle/length/offset, and prepares a REG_MR WR. Sending chains all registered MR WRs before the RDMA Send WR and chooses signaled sends based on request kref and send batch budget. Reply processing can consume a remotely invalidated MR by rkey. Local invalidation pops all registered MRs, chains LOCAL_INV WRs, and either waits synchronously for the last completion or lets the async last completion release the request after fencing.

State and persistence behavior: Per-MR state includes SG table, DMA mapping device/dir/nents, IB MR, completion, handle/length/offset, associated request, and prebuilt WR/CQE fields. Per-endpoint state includes max FR depth, MR type, send/recv queue budgets, send count, write-pad MR, and stats. All state is in-memory and reconstructed after disconnect; flushed in-flight MRs are destroyed during recovery.

Dependencies and integration points: Depends on RDMA core verbs (`ib_alloc_mr`, `ib_dma_map_sg`, `ib_map_mr_sg`, `ib_post_send`, LOCAL_INV/REG_MR WRs), RPC/RDMA buffer and endpoint types, XDR buffer layout, tracepoints, and disconnect recovery helpers. It is central to NFS/RDMA read/write chunk performance and safety.

Risks: DMA mappings must be unmapped exactly once; map failures after DMA mapping rely on later cleanup paths and deserve careful review. SG-gap handling changes how many MRs are needed and must match provider capabilities. Completion callbacks warn that only CQE and status are reliable, so touching other MR/request state must remain valid by construction. Async invalidation must unpin requests on post failure or completions can be lost. Queue-depth calculations must reserve enough WRs for forward, backward, and drain operations; underestimation can overflow provider queues, while overestimation reduces concurrency.

Test signals: Validate FRWR capability rejection and queue-depth sizing across RDMA devices, map of head/page/tail buffers with and without SG gaps, multi-MR cursor progression, DMA map and `ib_map_mr_sg` failures, rkey rotation and XID IOVA tagging, send WR chain ordering/signaling, remote invalidation match/miss, sync invalidation wait and post failure disconnect, async invalidation request completion/unpin, write-pad MR creation failure cleanup, and disconnect recovery with flushed WRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/frwr_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/ib_client.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/ib_client.c

Purpose: Registers RPC/RDMA as an RDMA core `ib_client` and provides per-IB-device removal notification tracking so transports can divest hardware resources before a device disappears.

Important APIs/types/functions: `struct rpcrdma_device` holds a kref, removing flag, `ib_device`, xarray of `rpcrdma_notification` registrants, and completion. Public APIs are `rpcrdma_rn_register()`, `rpcrdma_rn_unregister()`, `rpcrdma_ib_client_register()`, and `rpcrdma_ib_client_unregister()`. RDMA client callbacks are `rpcrdma_add_one()` and `rpcrdma_remove_one()`.

Control flow: Registering the ib_client causes RDMA core to call `rpcrdma_add_one()` for devices, allocating per-device data, initializing its xarray/completion/kref, and storing it with `ib_set_client_data()`. Transports register notifications by allocating an xarray index, taking a device kref, and storing a done callback. On device removal, the client sets a removing bit to reject new registrations, iterates all notifications and invokes each callback, then waits for outstanding registrants to unregister before destroying the xarray and freeing per-device data.

State and persistence behavior: Per-device state persists while the RDMA device is present and the rpcrdma ib_client is registered. Registrants hold a kref until `rpcrdma_rn_unregister()`. Removal completion gates final free. No durable persistence.

Dependencies and integration points: Integrates Linux RDMA core `ib_client`, xarray allocation, kref/completion lifetime management, RPC/RDMA notification structs from `rdma_rn.h`, and rpcrdma tracepoints. `module.c` registers this client before client/server RDMA transport initialization.

Risks: Removal callbacks must cause all registrants to unregister; otherwise `rpcrdma_remove_one()` waits indefinitely. `rpcrdma_rn_register()` ignores the exact negative errno from `xa_alloc()` and returns `-ENOMEM` for any allocation failure. Callback invocation occurs while iterating the xarray after setting the removing bit; callbacks must tolerate concurrent teardown and avoid re-registration on the same device.

Test signals: Register/unregister notifications on valid and NULL devices, registration rejected during removal, multiple registrants and xarray cleanup, remove waiting until delayed unregister, callback ordering, module unload with devices present, and RDMA hot-unplug under active RPC/RDMA traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/ib_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/module.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/module.c

Purpose: Provides `rpcrdma.ko` module metadata, tracepoint definition, initialization, and cleanup for the combined RPC/RDMA client and server transport module.

Important APIs/types/functions: Module metadata declares author, description, dual BSD/GPL license, and aliases `svcrdma`, `xprtrdma`, and `rpcrdma6`. `rpc_rdma_init()` registers the RDMA ib_client, initializes server-side RDMA, then initializes client xprt RDMA. `rpc_rdma_cleanup()` tears down client xprt RDMA, server RDMA, and the ib_client in reverse order. `CREATE_TRACE_POINTS` instantiates rpcrdma tracepoints.

Control flow: Module init first calls `rpcrdma_ib_client_register()`. If server RDMA init fails, it unregisters the ib_client. If client transport init fails, it cleans up server RDMA and unregisters the ib_client. Cleanup reverses successful initialization order: client transport cleanup, server cleanup, ib_client unregister.

State and persistence behavior: Module-global state is whatever the three subsystems allocate/register during init. No file-local mutable state beyond module registration exists. All state is expected to be released on module exit.

Dependencies and integration points: Integrates `xprt_rdma_cleanup/init()`, `svc_rdma_cleanup/init()`, `rpcrdma_ib_client_register/unregister()`, SUNRPC RDMA headers, and rpcrdma trace events. Kbuild includes this file in `rpcrdma.o`.

Risks: Initialization order matters: RDMA device notifications must exist before transport setup, and cleanup must stop transports before unregistering device callbacks. Any partial-init failure path must mirror cleanup precisely to avoid registered transports without an ib_client or leaked server/client resources. Tracepoint creation in this module means duplicate `CREATE_TRACE_POINTS` elsewhere would conflict.

Test signals: Build and load/unload `rpcrdma.ko`, inject failures in each init stage to verify rollback, confirm module aliases autoload expected transports, validate tracepoint availability, and run client/server RDMA smoke tests before and after module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/module.c -->
