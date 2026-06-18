<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.h

## Purpose

This header defines the ERDMA provider's verbs-layer private objects, protocol constants, state enums, conversion helpers, and exported verbs function prototypes. It is the contract between `erdma_verbs.c`, posting/polling code, connection-management code, and the device registration code that installs the ib_device operation table.

## Important APIs, types, and functions

Important limits include `ERDMA_MAX_PD`, `ERDMA_MAX_SEND_WR`, `ERDMA_MAX_ORD`, `ERDMA_MAX_IRD`, SGE limits, inline-data size, FRMR page-list length, MTT constants, MR type constants, and ERDMA access bits. Main object wrappers are `struct erdma_ucontext`, `struct erdma_pd`, `struct erdma_mtt`, `struct erdma_mem`, `struct erdma_mr`, `struct erdma_av`, `struct erdma_ah`, `struct erdma_uqp`, `struct erdma_kqp`, `struct erdma_qp`, and `struct erdma_cq`.

The header also defines iWARP and RoCEv2 QP states and attribute masks, `union erdma_mod_qp_params`, `struct erdma_qp_attrs`, xarray lookup helpers `find_qp_by_qpn()` and `find_cq_by_cqn()`, type-cast helpers such as `to_eqp()` and `to_ecq()`, `to_erdma_access_flags()`, protocol checks, and the full set of provider verbs prototypes.

## Control Flow

There is no standalone runtime flow in the header. The inline helpers shape control flow in implementation files by translating RDMA core objects to ERDMA containers, validating GID network types, choosing iWARP versus RoCEv2 behavior, and loading live QP/CQ objects from device xarrays. The prototypes expose create, destroy, query, modify, mmap, memory registration, CQ notification, posting, polling, stats, GID, pkey, and AH operations to other ERDMA modules.

## State and Persistence

The state described here is volatile kernel and hardware-facing state. `erdma_ucontext` stores doorbell mmap entries and a mutex-protected list of pinned user doorbell record pages. QPs carry a kref, completion for safe free, state semaphore, delayed reflush work, SQ/RQ backing state, CQ pointers, and protocol-specific attributes. CQs carry either kernel queue memory and doorbell record state or user MTT and doorbell record state. MRs store memory translation tables, page geometry, access flags, type, and validity.

## Dependencies and Integration Points

The header includes `erdma.h` and depends on RDMA core types, xarray-backed device fields, ERDMA protocol constants, Ethernet address sizes, and local hardware ABI structures. It is included by ERDMA verbs, CM, and send/receive completion paths. Public prototypes integrate with the ib_device ops registration and with RoCEv2 address/GID management paths.

## Risks

The header is a shared ABI inside the driver. Changing limits or struct fields can silently desynchronize command encoding, userspace ABI expectations, and posting/polling code. The iWARP and RoCEv2 state enums have different domains but share conversion tables in `erdma_verbs.c`; array dimensions and enum values must stay aligned. `find_qp_by_qpn()` and `find_cq_by_cqn()` return raw xarray pointers, so callers must pair lookups with the appropriate object lifetime rules. `to_erdma_access_flags()` intentionally omits local read as a hardware flag and always leaves local read handling to caller policy.

## Test Signals

Compile coverage is the first signal because this header fans out across the driver. Runtime signals include successful ib_device registration, object allocation through every exported op, QP lookup by async events or completions, CQ polling and notification, MR registration and fast-registration, and RoCEv2 AH/GID handling. ABI-sensitive changes should be tested with rdma-core userspace exercising context, QP, CQ, MR, AH, and mmap flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.h -->
