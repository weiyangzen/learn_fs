<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.c

## Purpose

Implements the PVRDMA non-QP/CQ/SRQ verbs surface: device/port/GID/PKey queries, port modification, user context allocation/mmap, protection domains, and address handles.

## Important APIs, Types, And Functions

Public handlers include `pvrdma_query_device()`, `pvrdma_query_port()`, `pvrdma_query_gid()`, `pvrdma_query_pkey()`, `pvrdma_port_link_layer()`, `pvrdma_modify_port()`, `pvrdma_alloc_ucontext()`, `pvrdma_dealloc_ucontext()`, `pvrdma_mmap()`, `pvrdma_alloc_pd()`, `pvrdma_dealloc_pd()`, `pvrdma_create_ah()`, and `pvrdma_destroy_ah()`.

## Control Flow

Device query copies capability fields from the shared region into RDMA core attributes and adds software-capability flags. Port and PKey queries post backend commands. GID query reads the driver's `sgid_tbl`. Ucontext allocation checks `ib_active`, allocates a UAR, posts create-ucontext with version-specific PFN width, stores `ctx_handle`, and returns QP table size. Mmap maps a single UAR page to userspace. PD allocation/deallocation post create/destroy commands and maintain counters. AH creation validates RoCE GRH and non-multicast destination, then builds a PVRDMA AV from AH attrs.

## State And Persistence Behavior

Device and port capabilities persist in `dev->dsr->caps`. User contexts own UAR indexes and backend context handles. PDs own backend PD handles and privileged/user state. AHs are local software objects with an AV and device AH count; no backend create command is used for AHs in this file.

## Dependencies And Integration Points

Depends on RDMA core query/mmap/ucontext/PD/AH APIs, PVRDMA command ABI, UAR allocator, GID table updates from `pvrdma_main.c`, and netdev/RoCE address semantics.

## Risks And Edge Cases

`pvrdma_query_device()` rejects non-empty user input/output buffers. Ucontext copyback failure calls dealloc, which posts destroy and frees UAR. `pvrdma_mmap()` only maps one page and rejects non-page-aligned offsets. AH creation rejects multicast addresses and requires GRH/RoCE attributes; multicast is not implemented through AH creation.

## Test Signals

Test capability reporting across device versions, query-port/pkey command failures, GID bounds, port shutdown state, ucontext allocation when inactive, UAR mmap validation, PD max accounting and copyback failure, AH validation for missing GRH/multicast/non-RoCE, and AH count limits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.c -->
