# sources/distributed-fs/ceph-client/include/linux/sunrpc/svc.h

Purpose: declares the SUNRPC server framework: service thread pools, request context, program/version/procedure descriptors, buffer sizing, request processing, and server-side XDR stream setup.

Important APIs and types: `struct svc_pool` tracks per-pool thread counts, pending transports, idle/all thread lists, counters, and flags for work/victim management. `struct svc_serv` holds program tables, stats, locks, thread counts, transport lists, temp-socket timer, pool array, thread function, and optional backchannel queue. `struct svc_rqst` is the per-thread/per-RPC context with transport, addresses, service/procedure/auth state, XDR arg/reply buffers/streams, page arrays, folio batching, RPC header fields, decoded args/results, auth slack, cache request handle, client domains, task pointer, and private data. `struct svc_program`, `svc_version`, and `svc_procedure` describe dispatch, auth, rpcbind, decode, encode, release, and size contracts.

Control flow: a service is created and bound, threads receive transport work, initialize decode streams, authenticate and dispatch to a procedure, encode replies into page-backed XDR buffers, reserve auth slack, send responses, release pages, and possibly stop when pool victim flags are set.

State and persistence: service, pool, request, temp socket, and page buffer state are in-memory and service-lifetime. RPC payload pages are dynamically refilled and released per request; no persistent storage is managed here.

Dependencies and integration points: depends on XDR, auth/svcauth, lwq, wait queues, mm/pages/folios, kthreads, net namespaces, rpcbind, service transports, and optional backchannel support. NFSd and lockd are principal users.

Risks and test signals: risks include page-array ownership bugs, auth slack underflow, thread stop races, temp socket accounting, request deferral loops, buffer length mismatches, and backchannel context confusion. Test with NFSd/lockd workloads, UDP/TCP/RDMA payload sizes, thread pool resizing, auth flavors, deferral caches, and KASAN on page release paths.
