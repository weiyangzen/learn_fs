# sources/distributed-fs/ceph-client/include/rdma/mr_pool.h

Purpose: Small QP-scoped memory-region pool API for reusable kernel MRs.

Important APIs/types/functions: `ib_mr_pool_init`, `ib_mr_pool_get`, `ib_mr_pool_put`, and `ib_mr_pool_destroy`.

Control flow: Initialize a caller-owned list with preallocated MRs, get an MR for a transfer, map/register/use it through normal verbs paths, return it, then destroy the pool before QP resources disappear.

State and persistence behavior: Runtime state is in the caller-provided `list_head` and each pooled `ib_mr`. Lifetime is tied to the owning QP.

Dependencies and integration points: Depends on `ib_verbs.h`, `struct ib_qp`, `struct ib_mr`, and `enum ib_mr_type`. Integrates with fast registration and integrity MR use.

Risks: List access needs external serialization if shared. Returning an MR still visible to hardware or with stale keys can expose memory. Destroying with checked-out MRs leaks or races.

Test signals: Init failure unwind, get/put balance, exhausted pool behavior, destroy ordering, integrity MR parameters, and teardown with outstanding transfers.
