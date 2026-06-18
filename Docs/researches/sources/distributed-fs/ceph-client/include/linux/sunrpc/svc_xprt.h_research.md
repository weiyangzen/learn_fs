# sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_xprt.h

Purpose: declares the SUNRPC server transport abstraction used by socket, RDMA, and other service transports.

Important APIs and types: `struct svc_xprt_ops` defines create, accept, space check, receive, send, result-payload handling, context release, detach, free, temp-kill, and handshake hooks. `struct svc_xprt_class` registers a transport class with max payload and identifier. `struct svc_xpt_user` provides deletion callbacks. `struct svc_xprt` stores class/ops, kref, queue time, list/ready nodes, flags, service pointer, reservation/request counts, locks, auth cache, deferred list, local/remote addresses, users, net namespace, credentials, and optional backchannel client transport/switch.

Control flow: service code registers transport classes, creates/listens on transports, enqueues ready transports, receives into `svc_rqst`, sends replies, closes/deferred-closes, and tears down all transports during service destruction. Inline helpers manage peer-valid temp connection accounting and user callbacks.

State and persistence: transport state is runtime service/connection state with refcounts, flags, reservations, address buffers, deferred requests, and optional auth cache.

Dependencies and integration points: depends on `svc.h`, networking address types, krefs, lwq, net namespaces, credentials, and rpcbind unregister behavior.

Risks and test signals: risks include temp connection count leaks, close/user callback races, auth cache lifetime, address length assumptions, and transport class unregister while active. Test with TCP/UDP/RDMA listeners, temp connection aging, TLS handshake flags, deferred close, and service teardown.
