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
