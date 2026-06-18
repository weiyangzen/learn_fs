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
