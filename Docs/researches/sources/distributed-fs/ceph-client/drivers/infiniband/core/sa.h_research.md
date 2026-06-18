# sources/distributed-fs/ceph-client/drivers/infiniband/core/sa.h

## Purpose
`sa.h` is the private header for Subnet Administration support. It provides client reference helpers and declares multicast and multicast-member query entry points used across SA core code.

## Important APIs, types, and functions
- `ib_sa_client_get()` increments an SA client usage count.
- `ib_sa_client_put()` decrements the count and completes `client->comp` when the last user leaves.
- `ib_sa_mcmember_rec_query()` starts a multicast member record query.
- `mcast_init()` and `mcast_cleanup()` initialize and tear down multicast handling.

## Control flow and behavior
The inline reference helpers provide a small lifetime protocol: registration initializes `users` to one, each active query gets a reference, query completion drops it, and unregister waits for the completion after dropping the registration reference. The multicast-member query prototype follows the common SA pattern of client, device, port, method, record, component mask, timeout, allocation mask, callback, context, and cancellable query handle.

## State, persistence, and dependencies
The persistent state is external in `struct ib_sa_client`, especially its atomic `users` and completion. The header depends on `<rdma/ib_sa.h>` for SA public types, component masks, and query handle definitions.

## Integration points
Included by `sa_query.c` and multicast implementation files. It ties the generic SA query engine to multicast join/leave support.

## Risks and test signals
Risks are unbalanced client get/put around asynchronous queries and callbacks after client unregister. Test signals are client unregister while queries are outstanding, multicast join/leave cancellation, and lockdep/KASAN checks for completion ordering.
