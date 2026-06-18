# sources/distributed-fs/ceph-client/include/rdma/rdma_cm_ib.h

Purpose: InfiniBand-specific RDMA CM extension for manually supplying path records and sharing a UDP/multicast Q_Key constant.

Important APIs/types/functions: `rdma_set_ib_path(struct rdma_cm_id *, struct sa_path_rec *)` and `RDMA_UDP_QKEY`.

Control flow: Client-side code can call `rdma_set_ib_path` after address resolution to replace `rdma_resolve_route`; subsequent connection setup uses the supplied path record.

State and persistence behavior: The path record becomes runtime route state inside the CM ID. `RDMA_UDP_QKEY` is a static protocol constant.

Dependencies and integration points: Depends on `rdma_cm.h` and IB SA path records. Integrates with IB ULPs and tests that already have route/path data.

Risks: Stale or mismatched path records can cause wrong MTU, P_Key, GID, SL, or unreachable connections. Call ordering matters because this is not a replacement for address binding.

Test signals: Manual path connection setup, invalid path rejection, QP attr propagation, and UDP/multicast Q_Key behavior.
