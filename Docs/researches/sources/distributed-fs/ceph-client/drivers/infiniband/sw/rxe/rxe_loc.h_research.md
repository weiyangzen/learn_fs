# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_loc.h

## Purpose
`rxe_loc.h` is the main RXE internal function declaration hub. It ties together AV, CQ, multicast, mmap, MR, MW, net, QP, SRQ, completer/requester/responder, ICRC, and ODP interfaces.

## Important APIs, types, and functions
The header declares most non-static RXE implementation functions. It also defines `struct rxe_mmap_info`, QP helper inlines `qp_num()`, `qp_type()`, `qp_state()`, `qp_mtu()`, `is_odp_mr()`, and `rxe_advance_resp_resource()`. It declares `atomic_ops_lock`, timer callbacks, packet queueing functions, and ODP functions or stubs depending on `CONFIG_INFINIBAND_ON_DEMAND_PAGING`.

## Control flow
No direct flow beyond small inline helpers. The ODP section selects real declarations when ODP is enabled and `-EOPNOTSUPP`/unsupported response stubs otherwise.

## State and persistence
The only defined structure here is mmap metadata, containing pending-list linkage, context, kref, mapped object pointer, and user-visible mmap info. Other state is declared and owned by implementation files.

## Dependencies and integration points
This header is included by RXE source files to avoid circular declarations. It binds object pools, workqueue tasks, memory access helpers, packet paths, and optional ODP support into one internal API.

## Risks
Because it is broad, changes here can trigger large rebuild impact. Stub return values must match callers' expectations when ODP is disabled. The `is_odp_mr()` inline checks `mr->umem` and `is_odp`; callers must still handle non-ODP and DMA MR paths correctly.

## Test signals
Build RXE with ODP enabled and disabled, run sparse-style checks for prototype drift, and exercise each declared subsystem path through verbs and packet tests.
