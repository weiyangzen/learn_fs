# subset-b-006285 Research

Grouped code research for the Ceph client copy of Linux SUNRPC pipefs, rpcbind client, RPC scheduler, socket helpers, statistics, module lifecycle, service dispatch, service transports, and server-side authentication files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/rpc_pipe.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/rpc_pipe.c

## Purpose
`rpc_pipe.c` implements the `rpc_pipefs` pseudo-filesystem used by SUNRPC clients and authentication helpers to exchange upcalls and downcalls with userspace. It creates the pipefs superblock, standard service directories, per-client directories, cache helper directories, and the dummy `gssd` pipe used to detect a running rpc.gssd.

## Important APIs, Types, And Functions
Important exported APIs include `rpc_pipefs_notifier_register()`, `rpc_queue_upcall()`, `rpc_mkpipe_data()`, `rpc_mkpipe_dentry()`, `rpc_unlink()`, pipe directory object helpers, `rpc_create_client_dir()`, `rpc_remove_client_dir()`, cache directory helpers, `rpc_get_sb_net()`, `rpc_put_sb_net()`, `gssd_running()`, `register_rpc_pipefs()`, and `unregister_rpc_pipefs()`. Key local structures are `rpc_pipe`, `rpc_pipe_msg`, `rpc_inode`, `rpc_filelist`, `rpc_pipe_dir_head`, and `rpc_pipe_dir_object`.

## Control Flow
Pipe users allocate `rpc_pipe` data, create a pipe dentry under rpc_pipefs, and queue messages with `rpc_queue_upcall()`. Readers open the FIFO, `rpc_pipe_read()` moves one queued message to `in_upcall`, calls the pipe operation's `upcall`, and destroys the message once fully copied or failed. Writers call the pipe operation's `downcall`. Last reader close purges pending upcalls with `-EAGAIN`; unlink/removal closes the pipe, purges queues with `-EPIPE`, cancels timeout work, and clears inode ownership. Mount setup builds the root directories and dummy gssd tree, stores the per-net superblock under `pipefs_sb_lock`, and sends mount notifications; unmount clears the superblock and sends unmount notifications.

## State And Persistence
State is in per-pipe queues, reader/writer counts, `pipelen`, delayed timeout work, and borrowed dentries; per-inode private data points to callers or pipe state. Per-network namespace state stores `pipefs_sb`, `pipefs_sb_lock`, `pipe_version`, and `gssd_dummy`. Data is runtime-only and lives until pipefs unmount, client directory removal, or netns teardown.

## Dependencies And Integration Points
The file integrates with VFS simple filesystem helpers, fs_context mounting, blocking notifier chains, rpciod delayed work, SUNRPC cache pipefs files, `rpc_clnt` lifecycle, network namespace storage from `netns.h`, and auth/GSS userspace daemons. Notifier hooks let clients create or destroy pipefs entries when a namespace's rpc_pipefs mount appears or disappears.

## Risks And Edge Cases
The main risks are lifecycle and locking races among open file descriptors, dentries, pipe queue timeout work, and unmount. `RPC_PIPE_WAIT_FOR_OPEN` queues messages without readers only for a bounded timeout. `rpc_get_sb_net()` deliberately returns with `pipefs_sb_lock` held, so every successful caller must pair it with `rpc_put_sb_net()`. Pipe ops must correctly destroy messages on all purge paths. Dummy gssd state is inferred only from open counts, so it is a liveness signal rather than proof that upcalls will be serviced.

## Test Signals
Useful signals include rpc_pipefs mount/unmount in multiple net namespaces, GSS upcall/downcall integration, reader close and unlink while messages are queued, timeout purge with no readers, notifier registration ordering, cache directory population, per-client `info` file refcount behavior, and lockdep/KASAN coverage for concurrent unmount, open, read, write, and client teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/rpc_pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/rpcb_clnt.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/rpcb_clnt.c

## Purpose
`rpcb_clnt.c` is the in-kernel rpcbind client. It creates per-net local rpcbind clients, registers and unregisters server program/version/transport tuples, and performs asynchronous remote port discovery for RPC clients that need autobinding.

## Important APIs, Types, And Functions
Important APIs include `rpcb_create_local()`, `rpcb_put_local()`, `rpcb_register()`, `rpcb_v4_register()`, and `rpcb_getport_async()`. Internal helpers create AF_LOCAL abstract/pathname or loopback TCP clients, build version-specific rpcbind clients, run synchronous SET/UNSET calls, select rpcbind protocol versions, and encode/decode rpcbind v2/v3/v4 XDR procedures. `struct rpcbind_args`, `struct rpcb_info`, `rpcb_procedures2/3/4`, and `rpcb_program` are the central data definitions.

## Control Flow
Local setup first tries `/run/rpcbind.sock` abstract AF_LOCAL, then `/var/run/rpcbind.sock`, then TCP loopback on port 111. A users count protects shared per-net local clients and `rpcb_put_local()` shuts them down when the last user exits. Server registration builds a mapping and calls either rpcbind v2 SET/UNSET or v4 SET/UNSET with universal addresses and netids. Client autobind puts the original task on the transport binding waitqueue, claims the transport binding bit, creates a temporary rpcbind client to the peer's rpcbind service, starts an async child task, and wakes all binding waiters when the child completes.

## State And Persistence
Per-net state in `sunrpc_net` stores `rpcb_local_clnt`, optional v4 `rpcb_local_clnt4`, `rpcb_users`, `rpcb_is_af_local`, and `rpcb_clnt_lock`. Remote autobind state lives briefly in `rpcbind_args`, the transport's `binding` waitqueue, `bind_index`, bound flag, and transport destination port. Procedure stats are stored in version count arrays and `rpcb_stats`.

## Dependencies And Integration Points
This file depends on the generic RPC client/task scheduler, xprtsock transports, `rpc_sockaddr2uaddr()` and `rpc_uaddr2sockaddr()`, tracepoints, credentials, and network namespace storage. It is called by server registration code in `svc.c` and by client transport connection code when an RPC service port is unknown.

## Risks And Edge Cases
Autobind concurrency is delicate: only one task should query rpcbind for a transport while others sleep on `xprt->binding`. Failed v4/v3 lookups advance `bind_index` to fall back, while IPv6 never uses v2. AF_LOCAL local rpcbind clients disable idle timeout because reconnect would require mount namespace context. Registration over v4 may be unavailable, requiring v2 fallback for IPv4 but not IPv6 service registration. XDR string lengths are bounded and overlong strings are truncated with a warning.

## Test Signals
High-value tests include local rpcbind startup fallback across abstract socket, pathname socket, and loopback TCP; v2 and v4 service registration/unregistration; IPv4 and IPv6 `GETPORT`/`GETADDR` lookup; concurrent autobind waiters; rpcbind unavailable or protocol-not-supported fallback; universal address parse failures; and trace/stat counters for rpcbind procedures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/rpcb_clnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sched.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/sched.c

## Purpose
`sched.c` implements SUNRPC task scheduling for synchronous and asynchronous RPC calls. It owns RPC wait queues, timeout handling, task wakeups, the task finite-state-machine executor, task and buffer allocation pools, and the `rpciod`/`xprtiod` workqueues.

## Important APIs, Types, And Functions
Important APIs include `rpc_task_gfp_mask()`, `rpc_task_timeout()`, waitqueue init/destroy, `rpc_sleep_on*()`, `rpc_wake_up*()`, `rpc_delay()`, `rpc_exit()`, `rpc_execute()`, `rpc_malloc()`, `rpc_free()`, `rpc_new_task()`, `rpc_put_task()`, `rpc_put_task_async()`, `rpciod_up()`, `rpciod_down()`, `rpc_init_mempool()`, and `rpc_destroy_mempool()`. Central types are `rpc_task`, `rpc_wait_queue`, delayed timer lists, `rpc_buffer`, and `rpc_task_setup`.

## Control Flow
Tasks are initialized with callback ops, credentials, owner, workqueue, optional client/transport references, and an initial prepare action. `rpc_execute()` marks a task active and runnable; synchronous tasks run the FSM in the caller while async tasks are queued to `rpciod`. `__rpc_execute()` repeatedly runs `tk_action` or pending callbacks until the task sleeps or completes. Sleeping puts a task on a protected waitqueue, optionally with a timeout. Waking removes it from the queue and either queues async work or wakes synchronous waiters. Completion releases xprt slots, credentials, clients, calldata, and finally frees or asynchronously frees dynamic task memory.

## State And Persistence
Global state includes the delay queue, task slab, buffer slab, task and buffer mempools, `rpciod_workqueue`, and `xprtiod_workqueue`. Per-task state includes runstate bits, refcount, RPC status, action/callback, timeout, waitqueue pointer, statistics timestamps, retry counters, transport, client, credentials, request pointer, and calldata. Wait queues keep priority buckets, fairness counters, queue length, and delayed timer work.

## Dependencies And Integration Points
The scheduler integrates with RPC clients, transports, credentials, I/O statistics, tracepoints, Linux workqueues, wait-bit APIs, memalloc flags, freezer-aware waits, mempools, and module lifetime. Transport code wakes tasks when slots, connections, or replies are available; client code provides callback operations and count-stat hooks.

## Risks And Edge Cases
Correctness depends on runstate ordering between `RPC_TASK_RUNNING` and `RPC_TASK_QUEUED`; comments call out barriers that prevent lockless executor loops or missed wakeups. Async task memory freeing is deferred through workqueue context to avoid false work item dependency loops. Synchronous tasks receiving signals make one more FSM pass so callbacks can clean up. `PF_MEMALLOC` and `memalloc_nofs` are used for swapper or reclaim-sensitive paths. Mempools protect small task/buffer allocation, but callers must handle `-ENOMEM` without blocking rpciod unsafely.

## Test Signals
Useful coverage includes synchronous and async RPC task lifecycle, waitqueue FIFO and priority fairness, timeout expiry, signal cancellation, delayed tasks, rpcbind/autobind waiters, mempool fallback under allocation failure, task refcount and callback release ordering, workqueue teardown, tracepoint events, and lockdep/KCSAN checks for queued/running state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/socklib.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/socklib.c

## Purpose
`socklib.c` provides common socket/XDR helpers shared by SUNRPC client and server transports. It copies received sk_buff data into XDR buffers while validating checksums, and sends an `xdr_buf` directly through a socket, including stream record markers and paged payloads.

## Important APIs, Types, And Functions
The exported APIs are `csum_partial_copy_to_xdr()` and `xprt_sock_sendmsg()`. Internal helpers include `xdr_skb_read_bits()`, `xdr_partial_copy_from_skb()`, `xprt_sendmsg()`, `xprt_send_kvec()`, `xprt_send_pagedata()`, and `xprt_send_rm_and_kvec()`. `struct xdr_skb_reader` tracks the source skb, copy offset, remaining byte count, checksum state, and accumulated checksum.

## Control Flow
Receive copy initializes an `xdr_skb_reader` over the skb. If the skb checksum is already unnecessary, it copies head, page, and tail data into the target XDR buffer and verifies all data was consumed. Otherwise it copies while accumulating checksum blocks, checks any remaining skb bytes, folds the checksum, and reports checksum faults for unchecked `CHECKSUM_COMPLETE` packets. Send flow walks the record marker plus XDR head, page data, and tail in order, advances over the caller's `base` offset, sets `MSG_MORE` until the final fragment, and returns queued bytes via `sent_p`.

## State And Persistence
The file keeps no persistent global state. All state is per-call: skb offset/count/checksum while receiving, iterator state in `msghdr`, and caller-visible sent byte accounting. Sparse XDR pages can be allocated lazily with `GFP_NOWAIT` during receive copy.

## Dependencies And Integration Points
The file depends on Linux skb copy/checksum APIs, page mapping helpers, XDR buffer layout, RPC record markers, socket `sock_sendmsg()`, `iov_iter` kvec/bvec setup, and network checksum fault reporting. It is used by socket transport implementations for UDP receive and TCP/stream send paths.

## Risks And Edge Cases
Partial skb copy failures return short counts or `-ENOMEM`, which callers treat as failed receive. Sparse page allocation is nonblocking and may return a partial copy. Send logic must handle nonzero `base` correctly across optional record marker, head, pages, and tail; off-by-one errors would retransmit or skip payload bytes. `MSG_MORE` must be cleared for the final segment to avoid delaying transmission. The checksum path must validate both copied XDR bytes and any uncopied skb remainder.

## Test Signals
Useful tests include UDP checksum-good and checksum-bad packets, CHECKSUM_COMPLETE fault reporting, sparse page allocation failure injection, XDR buffers with head/page/tail combinations, stream sends with and without record markers, partial sends with nonzero base offsets, and packetdrill or transport tests that verify `sent_p` and `MSG_MORE` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/socklib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/socklib.h -->
# sources/distributed-fs/ceph-client/net/sunrpc/socklib.h

## Purpose
`socklib.h` is the small internal header that exposes common SUNRPC socket helper routines to transport implementations.

## Important APIs, Types, And Functions
It declares `csum_partial_copy_to_xdr(struct xdr_buf *xdr, struct sk_buff *skb)` for receive-side skb-to-XDR copy/checksum validation and `xprt_sock_sendmsg(struct socket *sock, struct msghdr *msg, struct xdr_buf *xdr, unsigned int base, rpc_fraghdr marker, unsigned int *sent_p)` for send-side XDR buffer transmission.

## Control Flow
The header has no executable control flow. Including files call the declared helpers from transport receive or send paths after preparing an `xdr_buf`, socket, message header, stream marker, and resend base offset.

## State And Persistence
No state is stored in the header. It defines the compile-time contract between `socklib.c` and its users.

## Dependencies And Integration Points
The prototypes depend on SUNRPC/XDR data structures, Linux sockets, sk_buffs, and RPC stream record marker types supplied by including translation units. The header is included by socket transport code that needs shared client/server helper behavior.

## Risks And Edge Cases
Because this is a narrow declaration header, risks are ABI-style drift: mismatched prototypes, missing forward declarations in users, or changes to argument semantics that are not reflected in all transport callers. Callers must honor the ownership and offset semantics implemented in `socklib.c`.

## Test Signals
Compile coverage of all socket transport users is the main signal. Runtime validation comes from the `socklib.c` receive checksum and send-offset tests that exercise these declarations through real transport call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/socklib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/stats.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/stats.c

## Purpose
`stats.c` provides procfs and seq_file reporting for generic SUNRPC client and server statistics, plus per-operation RPC I/O metrics collection for completed client tasks.

## Important APIs, Types, And Functions
Important APIs include `svc_seq_show()`, `rpc_alloc_iostats()`, `rpc_free_iostats()`, `rpc_count_iostats_metrics()`, `rpc_count_iostats()`, `rpc_clnt_show_stats()`, `rpc_proc_register()`, `rpc_proc_unregister()`, `svc_proc_register()`, `svc_proc_unregister()`, `rpc_proc_init()`, and `rpc_proc_exit()`. Internal helpers print client procedure counters, aggregate per-op metrics up parent client chains, and create proc entries under `/proc/net/rpc`.

## Control Flow
Client proc reads call `rpc_proc_show()`, which prints network counters, RPC counters, and per-version procedure counts from `rpc_stat`. Server stats call `svc_seq_show()`, which sums per-CPU service procedure counters. When an RPC task completes, `rpc_count_iostats_metrics()` locks the operation metrics, increments operation/transaction/timeout/error counters, accumulates sent/received bytes and queue/RTT/execute times, and emits latency trace data. `rpc_clnt_show_stats()` prints transport stats and aggregated per-operation metrics.

## State And Persistence
Persistent state is owned by callers: `rpc_stat`, `svc_stat`, per-version count arrays, per-CPU server procedure counters, and per-client `rpc_iostats` arrays. This file allocates and frees metrics arrays and creates per-net proc directory entries through `sunrpc_net->proc_net_rpc`.

## Dependencies And Integration Points
The file integrates with procfs, seq_file, RPC client and server program metadata, transport stat printers, `rpc_clnt_iterate_for_each_xprt()`, per-CPU counters, spinlocks, ktime, tracepoints, and network namespace proc directories initialized by the SUNRPC pernet lifecycle.

## Risks And Edge Cases
The opening comment warns that proc output must fit within PAGE_SIZE when service-specific routines append generic stats. Metrics accounting assumes `om_ops` does not exceed `om_ntrans`, forcing at least one transaction per operation. Callers must pass a valid stat index and initialized metrics array. Parent-chain aggregation in `rpc_clnt_show_stats()` depends on sane `cl_parent` links and matching procedure layouts.

## Test Signals
Useful tests include `/proc/net/rpc` directory creation/removal per net namespace, client and server proc output formatting, per-procedure counter increments, metrics allocation/free, error/timeout/byte accounting after RPC completion, parent client metric aggregation, transport stat printing, and tracepoint validation for latency accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sunrpc.h -->
# sources/distributed-fs/ceph-client/net/sunrpc/sunrpc.h

## Purpose
`sunrpc.h` is an internal SUNRPC header for small shared definitions and cross-file prototypes that are not part of the public UAPI or exported Linux SUNRPC headers.

## Important APIs, Types, And Functions
It defines `struct rpc_buffer`, the inline helper `sock_is_loopback()`, and prototypes for `rpc_clients_notifier_register()`, `rpc_clients_notifier_unregister()`, `auth_domain_cleanup()`, `svc_sock_update_bufs()`, and `svc_authenticate()`.

## Control Flow
The only executable logic is `sock_is_loopback()`, which reads `sk->sk_dst_cache` under RCU and returns true when the cached destination device advertises `NETIF_F_LOOPBACK`. Other declarations are implemented in scheduler, pipefs, authentication, and server socket code.

## State And Persistence
`struct rpc_buffer` describes dynamically allocated RPC call/reply buffers with a stored allocation length followed by flexible data. The header owns no global state.

## Dependencies And Integration Points
The header depends on networking types and is included by core SUNRPC files such as scheduler, module lifecycle, pipefs, server dispatch, and authentication. `struct rpc_buffer` is used by `sched.c` allocation, notifier prototypes tie into client pipefs integration, and auth/server prototypes avoid circular includes.

## Risks And Edge Cases
`sock_is_loopback()` is only as current as the cached route and must remain RCU-safe. `struct rpc_buffer` layout is coupled to `rpc_malloc()`/`rpc_free()` using `container_of()` from the data pointer, so layout changes can break buffer freeing. Adding broad dependencies here can increase coupling across the SUNRPC core.

## Test Signals
Compile coverage across SUNRPC core files is the primary signal. Runtime signals include RPC buffer allocation/free under KASAN and route/loopback detection tests that exercise cached destination changes under RCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sunrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sunrpc_syms.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/sunrpc_syms.c

## Purpose
`sunrpc_syms.c` owns SUNRPC module and per-network-namespace initialization and teardown. It wires together memory pools, authentication, cache infrastructure, rpc_pipefs, procfs, sysfs/debugfs, client/server socket transports, and namespace-local SUNRPC state.

## Important APIs, Types, And Functions
The file exports `sunrpc_net_id`, defines pernet callbacks `sunrpc_init_net()` and `sunrpc_exit_net()`, registers `sunrpc_net_ops`, and implements module entry/exit through `init_sunrpc()` and `cleanup_sunrpc()`. It calls core subsystem initializers such as `rpc_init_mempool()`, `rpcauth_init_module()`, `cache_initialize()`, `register_pernet_subsys()`, `register_rpc_pipefs()`, `rpc_sysfs_init()`, `svc_init_xprt_sock()`, and `init_socket_xprt()`.

## Control Flow
Module init starts scheduler memory/workqueue infrastructure, initializes RPC auth and cache support, registers pernet state, registers rpc_pipefs, initializes sysfs/debugfs/sysctl when enabled, and finally registers server and client socket transports. Per-net init creates `/proc/net/rpc`, AUTH_UNIX IP and gid caches, rpc_pipefs namespace state, and client/rpcbind locks/lists. Teardown runs in reverse: per-net exit removes pipefs state and auth caches, module exit removes sysfs/client IDs/transport IDs/auth/socket/debugfs/pipefs/mempools/pernet state, checks auth domains, unregisters sysctls, and waits for outstanding RCU callbacks.

## State And Persistence
Global state includes the registered pernet subsystem ID and module-level subsystems. Per-net state is allocated as `struct sunrpc_net` and contains procfs roots, auth caches, rpc_pipefs state, all-client lists, and rpcbind client locking. State persists until the namespace or module exits.

## Dependencies And Integration Points
This file is the integration point for virtually all SUNRPC core subsystems: scheduler, auth, cache, pipefs, sysfs, debugfs, sysctl, procfs, xprtsock, svc socket transports, network namespaces, client tracking, and RCU cleanup. It uses `fs_initcall()` so SUNRPC initializes before NFS users.

## Risks And Edge Cases
Initialization ordering matters because later subsystems depend on earlier memory pools, auth, per-net state, and pipefs registration. Error labels must unwind only initialized components. Per-net teardown warns if clients remain on `all_clients`, and final `auth_domain_cleanup()` only warns because release callbacks may belong to modules already gone. `rcu_barrier()` is required to wait for delayed frees before module exit completes.

## Test Signals
Useful signals include module load/unload, namespace create/destroy, failure injection at each init step, `/proc/net/rpc` and rpc_pipefs availability per namespace, auth cache creation/destruction, transport registration presence, sysfs/debugfs/sysctl cleanup, and RCU/KASAN checks on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sunrpc_syms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svc.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/svc.c

## Purpose
`svc.c` implements high-level server-side SUNRPC service management and request dispatch. It creates services and worker pools, manages service threads, binds/unbinds services with rpcbind, allocates per-thread request buffers, decodes common RPC headers, authenticates requests, dispatches procedures, frames replies, and provides helper APIs for server payload handling.

## Important APIs, Types, And Functions
Important APIs include `sunrpc_set_pool_mode()`, `sunrpc_get_pool_mode()`, `svc_pool_for_cpu()`, `svc_bind()`, `svc_rpcb_cleanup()`, `svc_create()`, `svc_create_pooled()`, `svc_destroy()`, `svc_pool_wake_idle_thread()`, `svc_new_thread()`, `svc_set_pool_threads()`, `svc_set_num_threads()`, `svc_rqst_replace_page()`, `svc_rqst_release_pages()`, `svc_exit_thread()`, `svc_generic_rpcbind_set()`, `svc_register()`, `svc_generic_init_request()`, `svc_process()`, `svc_process_bc()`, `svc_max_payload()`, `svc_encode_result_payload()`, and `svc_fill_symlink_pathname()`. `struct svc_pool_map` drives global pool topology.

## Control Flow
Service creation computes version bounds and max XDR argument size, initializes permanent and temporary transport lists, creates one or more pools, and initializes per-pool work queues and counters. Thread creation allocates `svc_rqst`, page arrays, scratch folio, arg/response storage, and a kthread bound to a pool. `svc_process()` initializes the response buffer, validates RPC call direction, and calls `svc_process_common()`. The common path decodes RPC version/program/version/procedure, authenticates and lets the program apply additional auth checks, initializes procedure storage, reserves reply space, dispatches the procedure, handles bad RPC/auth/prog/version/proc replies, authorizes release, and returns whether to send or drop.

## State And Persistence
Persistent service state includes `svc_serv` program arrays, stats, max payload/message sizes, pools, thread counts, transport lists, temp transport timer, backchannel list, and pool map references. Per-thread `svc_rqst` state includes pages, response pages, bvecs, scratch folio, arg/resp structs, auth data, request flags, transport pointers, and RCU list membership. Pool mapping mode is global and cannot change while pooled services exist.

## Dependencies And Integration Points
The file integrates with rpcbind client code, service transports from `svc_xprt.c`, server socket buffer sizing, authentication from `svcauth.c`, XDR stream helpers, proc/stat counters, backchannel support, tracepoints, kthreads, NUMA/CPU affinity, cache deferred request cleanup, and program-specific dispatch tables such as NFS/NFSD.

## Risks And Edge Cases
Pool map changes are rejected once in use. Thread adjustment can partially succeed, leaving callers responsible for recovery. Request dispatch must always release auth/procedure resources on send, drop, and close paths. UDP is rejected for versions that require congestion control. `svc_rqst_replace_page()` has tight bounds requirements for response page arrays. Rpcbind unregister temporarily clears signal-pending state and recalculates it afterward, which is subtle process state manipulation.

## Test Signals
Useful tests include service create/destroy with global/percpu/pernode pool modes, dynamic thread scaling and victim exit, rpcbind register/unregister fallback, RPC header/auth/program/version/procedure error replies, procedure dispatch and release hooks, backchannel processing, response page replacement/release, symlink pathname construction with embedded NUL rejection, and lockdep/KASAN coverage for service shutdown with active transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svc_xprt.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/svc_xprt.c

## Purpose
`svc_xprt.c` implements server-side SUNRPC transport class registration, listener creation, transport scheduling, request receive/send coordination, temporary connection aging, shutdown, deferred request replay, listener lookup, and pool statistics.

## Important APIs, Types, And Functions
Important APIs include `svc_reg_xprt_class()`, `svc_unreg_xprt_class()`, `svc_print_xprts()`, `svc_xprt_deferred_close()`, `svc_xprt_put()`, `svc_xprt_init()`, `svc_xprt_received()`, `svc_xprt_create_from_sa()`, `svc_xprt_create()`, `svc_xprt_copy_addrs()`, `svc_print_addr()`, `svc_xprt_enqueue()`, `svc_reserve()`, `svc_wake_up()`, `svc_recv()`, `svc_send()`, `svc_age_temp_xprts_now()`, `svc_xprt_close()`, `svc_xprt_destroy_all()`, `svc_find_listener()`, `svc_find_xprt()`, `svc_xprt_names()`, and `svc_pool_stats_open()`.

## Control Flow
Transport classes register globally by name. Creating a listener finds the class, module-gets it, calls the provider's create op, attaches credentials, adds a permanent xprt, and enqueues it. Providers set `XPT_CONN`, `XPT_DATA`, `XPT_CLOSE`, `XPT_HANDSHAKE`, or `XPT_DEFERRED` and call `svc_xprt_enqueue()`. Service threads call `svc_recv()`, allocate argument pages, wait as idle workers, dequeue a busy xprt, and `svc_handle_xprt()` accepts new connections, performs TLS handshakes, receives deferred or fresh requests, reserves reply space, calls `svc_process()`, and releases the transport. Replies go through provider `xpo_sendto()`.

## State And Persistence
Global state is the registered transport class list and `svc_rpc_per_connection_limit` module parameter. Each `svc_xprt` tracks class/ops, refcount, flags, server, net namespace, credentials, local/remote addresses, ready-queue node, reserved reply bytes, active request count, deferred requests, users, auth cache, and optional backchannel xprt/switch. Service state tracks permanent and temporary lists, temporary connection count, aging timer, and per-pool ready queues/counters.

## Dependencies And Integration Points
The file depends on transport providers such as TCP/UDP svc sockets, service pools from `svc.c`, rpcbind unregister through `svc_register()`, auth cache release from `svcauth_unix.c`, cache deferral infrastructure, XDR buffers, socket address helpers, module loading via `request_module("svc%s")`, tracepoints, and optional backchannel transports.

## Risks And Edge Cases
`XPT_BUSY` is the key serialization bit; clearing it can allow another thread to close and put the transport, so references must be held around re-enqueue. Slot limiting and reserved bytes use memory barriers with readiness checks to avoid stalls. Temporary unauthenticated connections are hard-limited and aged with mark-and-sweep. Deferred requests only handle small non-paged buffers. Shutdown must close xprts even if no service threads are running, while avoiding deletion of transports owned by another net namespace.

## Test Signals
High-value tests include transport class duplicate registration, autoload of svc transport modules, listener create for IPv4/IPv6 and unsupported families, accept/data/handshake/close scheduling, per-connection RPC limit, reply reservation accounting, temp connection aging and address removal notifier path, deferred cache miss replay/drop, service shutdown with and without worker threads, listener lookup/names output, and pool stats seq output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svc_xprt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svcauth.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/svcauth.c

## Purpose
`svcauth.c` provides the generic server-side authentication dispatch layer for SUNRPC. It maps incoming RPC auth flavors to `auth_ops`, drives accept/set-client/release operations, supports dynamic auth flavor registration, maps local client credentials to service credentials, and manages shared `auth_domain` objects.

## Important APIs, Types, And Functions
Important APIs include `svc_authenticate()`, `svc_set_client()`, `svc_authorise()`, `svc_auth_register()`, `svc_auth_unregister()`, `svc_auth_flavor()`, `svcauth_map_clnt_to_svc_cred_local()`, `auth_domain_put()`, `auth_domain_lookup()`, `auth_domain_find()`, and `auth_domain_cleanup()`. The global `authtab` starts with NULL, UNIX, and TLS authenticators.

## Control Flow
`svc_authenticate()` decodes the credential flavor from the request stream, obtains the registered auth ops under RCU with a module reference, initializes `rq_cred`, stores `rq_authop`, and calls the flavor's `accept()`. Program dispatch can later call `svc_set_client()`, which delegates domain/client selection to the active flavor. `svc_authorise()` clears `rq_authop`, calls flavor release to emit/finalize verifiers and drop request resources, and releases the module reference. Auth domains are looked up by hashed name with RCU and kref protection; final put removes the domain and invokes the flavor's release method under the lock handoff.

## State And Persistence
Persistent state includes the RCU-protected `authtab` array and the global auth-domain hash table protected by `auth_domain_lock`. Per-request state includes auth status, auth slack, selected auth ops, service credentials, and optional auth domain/client. Local credential mapping creates transient `svc_cred` values and group-info references.

## Dependencies And Integration Points
The file integrates with `svc.c` request processing, `svcauth_unix.c` built-in auth operations, optional loadable auth flavors, RPC XDR opaque auth decoding, Linux credential and user namespace translation, module refcounts, RCU, krefs, and tracepoints.

## Risks And Edge Cases
Unknown or out-of-range auth flavors must produce proper RPC auth errors without leaking module refs. `svc_authorise()` must be called on all request paths after successful `svc_authenticate()` to release credentials and auth ops. `svc_auth_unregister()` removes pointers with RCU assignment, so users need grace-period-safe lifetime. `auth_domain_cleanup()` can only warn about leaks because domain release callbacks may live in unloaded modules.

## Test Signals
Useful tests include bad credential flavor, malformed credential stream, NULL/UNIX/TLS auth dispatch, dynamic auth flavor registration conflicts/unregistration, program-level `svc_set_client()` behavior, local credential user-namespace mapping, auth domain lookup/refcount/release, and leak warnings on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svcauth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svcauth_unix.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/svcauth_unix.c

## Purpose
`svcauth_unix.c` implements server-side AUTH_NULL, AUTH_SYS/AUTH_UNIX, and AUTH_TLS handling, plus the caches that map client IP addresses to UNIX auth domains and UIDs to expanded group lists. AUTH_NULL is treated like AUTH_UNIX mapped to anonymous credentials but still goes through the same client-domain IP checks for non-NULL procedures.

## Important APIs, Types, And Functions
Important APIs include `unix_domain_find()`, `svcauth_unix_purge()`, `svcauth_unix_info_release()`, `unix_gid_cache_create()`, `unix_gid_cache_destroy()`, `svcauth_unix_set_client()`, `ip_map_cache_create()`, and `ip_map_cache_destroy()`. Exported auth ops are `svcauth_null`, `svcauth_tls`, and `svcauth_unix`. Important structures are `unix_domain`, `ip_map`, and `unix_gid`, each backed by SUNRPC cache or auth-domain lifetimes.

## Control Flow
IP cache entries are requested from userspace as class/address and updated with an expiry and optional domain name. GID cache entries are requested by UID and updated with expiry plus a sorted group list. `svcauth_unix_set_client()` converts the remote address to IPv6 form, skips domain mapping for NULL procedure, looks up or uses the xprt cached IP map, calls `cache_check()`, assigns `rq_client`, then optionally replaces the request's group list with the expanded UID cache result. `svcauth_null_accept()` validates empty credential/verifier and creates anonymous empty groups. `svcauth_tls_accept()` validates AUTH_TLS on NULL procedure and either emits a STARTTLS verifier and queues handshake work or returns a NULL verifier. `svcauth_unix_accept()` parses machine name, uid, gid, supplementary groups, verifier, and reply verifier.

## State And Persistence
Per-net state stores `ip_map_cache` and `unix_gid_cache`. Transport state may cache one validated IP map under `XPT_CACHE_AUTH`. Auth domains persist in the global domain table until their kref drops, then free by RCU. Request credentials hold uid, gid, group_info, flavor, auth domain, and auth status until flavor release.

## Dependencies And Integration Points
The file depends on SUNRPC cache upcall/downcall infrastructure, pipefs cache files, `auth_domain` management from `svcauth.c`, service transport auth-cache lifetime from `svc_xprt.c`, network namespace state, sockaddr parsing/printing helpers, user namespace UID/GID conversion, group_info management, TLS-capable transport handshake ops, and NFS/NFSD export authorization through auth domains.

## Risks And Edge Cases
Cache miss handling can return DROP, CLOSE, DENIED, or OK, and callers must preserve request deferral state. Cached xprt IP maps must be invalidated when expired. IPv4 addresses are represented as v4-mapped IPv6 addresses, while IPv6 scope IDs are ignored. AUTH_SYS accepts invalid `-1` uid/gid values for backwards compatibility, leaving anonymous mapping to upper layers. GID cache updates allow up to 8192 groups, but wire AUTH_SYS still limits supplied groups to `UNX_NGROUPS`. AUTH_TLS is valid only on NULL procedure and depends on transport handshake support.

## Test Signals
Useful tests include AUTH_NULL, AUTH_SYS, and AUTH_TLS request parsing; malformed verifier and oversized machine/group lists; IP cache positive, negative, expired, and purge behavior; xprt auth-cache reuse and release; UID-to-GID cache upcall timeout and update; IPv4/v6 address mapping; STARTTLS verifier and handshake enqueue; and request deferral/close/deny behavior under cache miss or userspace timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/svcauth_unix.c -->
