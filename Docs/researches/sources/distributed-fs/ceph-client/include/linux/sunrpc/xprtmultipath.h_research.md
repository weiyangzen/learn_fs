# sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtmultipath.h

Purpose: declares SUNRPC client transport-switch and iterator infrastructure for multipath/nconnect-style transport selection.

Important APIs and types: `struct rpc_xprt_switch` contains a lock, kref, ID, transport counts, active and unique-destination counts, queue length, xprt list, net namespace, iterator ops, sysfs object, and RCU head. `struct rpc_xprt_iter` stores an RCU switch pointer, cursor transport, and iterator ops. `struct rpc_xprt_iter_ops` provides rewind/current/next callbacks.

Control flow: clients allocate a switch around an initial transport, add/remove transports, select iterator policy such as round-robin, initialize iterators, exchange switches under RCU, and fetch current/next transports for RPC tasks.

State and persistence: multipath state is runtime client state with refcounts and RCU lifetime. Transport IDs can be cleaned up through `xprt_multipath_cleanup_ids()`.

Dependencies and integration points: integrates with `rpc_xprt`, net namespaces, sysfs transport switch objects, and client transport-management code in `clnt.h`.

Risks and test signals: risks include RCU cursor use-after-free, active count drift, duplicate address accounting errors, queue length mismatch, and offline removal races. Test nconnect/multipath mounts, round-robin selection, add/remove during I/O, offline transports, and namespace teardown.
