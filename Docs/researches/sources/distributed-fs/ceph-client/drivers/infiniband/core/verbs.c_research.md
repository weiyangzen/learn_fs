<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/verbs.c

## Purpose
This file is a central RDMA/InfiniBand core verbs implementation. It wraps provider driver operations with common validation, reference counting, resource tracking, security hooks, GID/GRH ownership rules, RoCE address resolution, QP state-machine checks, CQ/MR/multicast/XRC/WQ helpers, drain helpers, RDMA netdev allocation, and hardware stats allocation.

## Important APIs, Types, And Functions
- Message helpers: `ib_event_msg()`, `ib_wc_status_msg()`, `ib_rate_to_mult()`, `mult_to_ib_rate()`, `ib_rate_to_mbps()`, and `ib_port_attr_to_speed_info()` translate enums and port attributes into stable strings or numeric rates.
- Transport helpers: `rdma_node_get_transport()`, `rdma_port_get_link_layer()`, `ib_get_eth_speed()`, `ib_get_rdma_header_version()`, and `ib_get_gids_from_rdma_hdr()` classify RDMA devices, ports, and packet headers.
- Protection-domain lifecycle: `__ib_alloc_pd()` allocates a driver PD, optionally creates an internal DMA MR, and registers restrack state; `ib_dealloc_pd_user()` releases the internal MR, calls provider deallocation, removes restrack, and frees memory.
- Address-handle lifecycle: `rdma_copy_ah_attr()`, `rdma_replace_ah_attr()`, `rdma_move_ah_attr()`, `rdma_destroy_ah_attr()`, `rdma_create_ah()`, `rdma_create_user_ah()`, `ib_create_ah_from_wc()`, `rdma_modify_ah()`, `rdma_query_ah()`, and `rdma_destroy_ah_user()` manage AH objects and SGID attribute references.
- RoCE address path: `rdma_fill_sgid_attr()`, `rdma_unfill_sgid_attr()`, `rdma_update_sgid_attr()`, `ib_resolve_unicast_gid_dmac()`, and `ib_resolve_eth_dmac()` ensure GRH SGID attributes and destination MACs are available before provider calls.
- SRQ/QP/CQ/MR lifecycle: `ib_create_srq_user()`, `ib_destroy_srq_user()`, `create_qp()`, `ib_create_qp_user()`, `ib_create_qp_kernel()`, `ib_destroy_qp_user()`, `__ib_create_cq()`, `ib_destroy_cq_user()`, `ib_reg_user_mr()`, `ib_alloc_mr()`, `ib_alloc_mr_integrity()`, and `ib_dereg_mr_user()` allocate core objects, call `ib_device->ops`, and maintain use counts and restrack entries.
- QP state rules: `qp_state_table` and `ib_modify_qp_is_ok()` encode required and optional attribute masks for transitions between RESET, INIT, RTR, RTS, SQD, SQE, and ERR.
- QP mutation and sharing: `_ib_modify_qp()`, `ib_modify_qp_with_udata()`, `ib_modify_qp()`, `ib_query_qp()`, `ib_open_qp()`, `ib_close_qp()`, and `__ib_destroy_shared_qp()` handle real/shared QPs, XRC target lookup, security hooks, counter binding, and SGID/LAG updates.
- Other exported helpers: multicast attach/detach, XRC domain allocation, WQ lifecycle, VF management wrappers, MR SG mapping, queue drain, RDMA netdev allocation/initialization, and `rdma_alloc_hw_stats_struct()` / `rdma_free_hw_stats_struct()`.

## Control Flow
Most public functions follow a common pattern: validate core invariants and provider capability, allocate or initialize the core object, call the provider operation in `device->ops`, then add resource tracking and increment dependent object use counts only after success. Destroy paths reject busy objects, call the provider destroy/dealloc operation, drop dependent references, delete restrack entries, release SGID or umem resources, and free memory.

AH creation first validates the port and GRH requirements, fills or verifies the SGID attribute, optionally resolves RoCE destination MACs or LAG transmit slave netdevices, calls the provider create method, then unwinds the temporary SGID fill so the caller's input attribute is not silently mutated. AH/QP modify uses the same SGID-fill pattern and transfers persistent SGID references to object fields only after provider/security modification succeeds.

QP creation builds the core QP object, initializes completion/event routing and MR lists, calls the provider create method, installs security state, and registers restrack. XRC target QPs add a second shared-open object stored in an xarray under `xrcd->tgt_qps`. QP modification is funneled through `_ib_modify_qp()`, which resolves AH data, rejects unsupported alternate paths for RoCE, masks oversized PSNs, auto-binds counters during reset-to-init port assignment, runs `ib_security_modify_qp()`, and then updates cached port and SGID references.

CREATION and teardown of CQ, SRQ, WQ, MR, XRCD, multicast membership, and VF wrappers are thin but important adapters around provider callbacks. Drain helpers move a QP to error and post sentinel WRs or poll SRQ completions so callers can wait until outstanding work is observed by the CQ path.

## State And Persistence
Persistent kernel state includes allocated RDMA core objects, provider-private driver objects embedded via `rdma_zalloc_drv_obj*()`, restrack records, use counters on PD/CQ/SRQ/XRCD/WQ/RWQ objects, SGID attribute references, QP security state, RDMA counter bindings, MR address/length/page size metadata, and optional CQ umem. State is in-memory only and tied to kernel object lifetime; provider hardware state is created and destroyed through `ib_device->ops`.

AH and QP attributes hold SGID references that must be explicitly released. QP shared-open state is persisted in `real_qp->open_list` and, for XRC targets, `xrcd->tgt_qps`. MR mapping helpers update `mr->iova`, `mr->length`, and `mr->page_size` while converting scatterlists to provider page vectors.

## Dependencies And Integration Points
The file depends on Linux networking headers, IPv4/IPv6 helpers, ethtool, security hooks, `rdma/ib_verbs.h`, `rdma/ib_cache.h`, `rdma/ib_addr.h`, `rdma/ib_umem.h`, `rdma/rw.h`, `rdma/lag.h`, core private RDMA helpers, and RDMA tracepoints. Its primary integration contract is `struct ib_device_ops`, with provider drivers supplying alloc/create/modify/query/destroy callbacks. It also integrates with netdevice lifetime through `ib_device_get_netdev()` / `dev_put()`, rtnl locking for ethtool speed, LAG slave selection, RDMA counters, uverbs `ib_udata`, and Linux resource tracking.

## Risks And Edge Cases
Reference ownership is the largest risk: failed paths must undo SGID fills, LAG netdevice references, provider-created resources, restrack entries, use counts, umem, and security state in the exact reverse order. QP alternate-path handling explicitly notes incomplete migration-state tracking. Some provider contracts are assumed, such as kernel CQ creation not setting `cq->umem` and drivers preserving CQ pointers during QP creation. `__ib_create_cq()` leaks the just-allocated CQ if `cq_attr->cqe` is zero because it returns directly after allocation. `ib_get_eth_speed()` calls `dev_put(netdev)` before a warning that may print `netdev->name`, so that diagnostic path depends on a pointer after ref release. Generic drain helpers rely on the caller ensuring CQ/SQ/RQ capacity and no concurrent posting.

## Test Signals
Useful signals are RDMA core build coverage, provider driver module builds, uverbs and kernel-verbs create/modify/destroy tests, RoCE AH/QP tests with IPv4, IPv6, multicast, VLAN, and LAG, QP transition negative tests against `ib_modify_qp_is_ok()`, MR scatterlist mapping boundary tests, XRC shared-QP open/close tests, CQ/SRQ drain behavior, KASAN/KCSAN/leak checking for error paths, and tracepoint or restrack validation showing objects are added and removed exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/verbs.c -->
