# sources/distributed-fs/ceph-client/net/sunrpc/backchannel_rqst.c

Purpose: manages preallocated SUNRPC backchannel request objects and XDR buffers for transports that receive server-initiated callback RPCs, such as NFSv4 callbacks. It provides generic wrappers that dispatch to transport operations and a default implementation for request allocation, lookup, completion, enqueue, reuse, and destruction.

Important APIs/types/functions: exported functions are `xprt_bc_max_slots`, `xprt_svc_destroy_nullify_bc`, `xprt_setup_backchannel`, `xprt_destroy_backchannel`, and `xprt_enqueue_bc_request`. Core implementation helpers include `xprt_setup_bc`, `xprt_destroy_bc`, `xprt_lookup_bc_request`, `xprt_complete_bc_request`, `xprt_free_bc_request`, `xprt_free_bc_rqst`, `xprt_alloc_bc_req`, and `xprt_get_bc_request`. State lives in `rpc_xprt` fields such as `bc_pa_list`, `bc_pa_lock`, `bc_alloc_count`, `bc_alloc_max`, `bc_slot_count`, `bc_serv`, and request `rq_bc_pa_state`.

Control flow: setup clamps requested slots to `BC_MAX_SLOTS`, allocates `rpc_rqst` objects with one receive page and one send page, then splices them into the transport preallocation list under lock. Incoming callbacks use `xprt_lookup_bc_request()` to find a matching xid/connect-cookie request or allocate/reuse one, `xprt_complete_bc_request()` removes it from the free list, marks it in use, records copied bytes, and queues it to the backchannel service list. When processing finishes, `xprt_free_bc_rqst()` clears in-use state and either returns the request to the free list or frees it if all sessions were destroyed.

State and persistence behavior: all state is in-memory per transport. Preallocated request counts and slot counts are protected by `bc_pa_lock`; request in-use state uses bit operations and barriers. Requests hold a transport reference while queued to the service and release it when freed. No persistent state exists.

Dependencies/integration points: depends on `struct rpc_xprt` transport ops (`bc_setup`, `bc_destroy`, `bc_free_rqst`), XDR buffer helpers, service pools (`svc_pool_wake_idle_thread`), lightweight queues, and RDMA/socket receive paths that call lookup/complete helpers.

Risks: list/count consistency under `bc_pa_lock` is critical. `xprt_enqueue_bc_request()` takes a transport ref before checking `bc_serv`; if no service exists, the request is not enqueued here and correct later release depends on caller behavior. Allocation failure during setup must free both XDR pages. Connect-cookie matching prevents stale callbacks from reusing current slots; ordering barriers around `RPC_BC_PA_IN_USE` protect reuse.

Test signals: create/destroy backchannel sessions repeatedly with varying slot counts; inject allocation failures; receive duplicate xid callbacks; destroy sessions while requests are in use; verify requests are requeued or freed according to `bc_alloc_max`; and run NFSv4 callback traffic over TCP/RDMA with lockdep and refcount debug enabled.
