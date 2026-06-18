# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr.h

## Purpose
`qedr.h` is the central private header for the QEDR driver. It defines device, CQ, QP, SRQ, PD, MR, user-context, mmap, and iWARP endpoint state shared by `main.c`, verbs, RoCE CM, and iWARP CM.

## Important APIs, Types, And Functions
Key types are `qedr_dev`, `qedr_device_attr`, `qedr_cnq`, `qedr_ucontext`, `qedr_userq`, `qedr_cq`, `qedr_pd`, `qedr_xrcd`, `qedr_qp_hwq_info`, `qedr_srq_hwq_info`, `qedr_srq`, `qedr_qp`, `qedr_ah`, `qedr_mr`, `qedr_user_mmap_entry`, `qedr_iw_listener`, and `qedr_iw_ep`. Inline helpers convert RDMA core objects to driver objects and provide queue helpers such as `qedr_inc_sw_cons`, `qedr_inc_sw_prod`, `qedr_qp_has_srq`, `qedr_qp_has_sq`, and `qedr_qp_has_rq`.

## Control Flow
The file has minimal executable flow through inline helpers. `qedr_get_dmac` validates a nonzero GRH destination GID and retrieves the resolved destination MAC from an AH. Queue helpers update circular producer/consumer indexes. Container helpers are used throughout operation tables to recover private objects from embedded RDMA core objects.

## State And Persistence Behavior
The structs describe all volatile QEDR runtime state. `qedr_dev` owns lower-layer handles, interrupt resources, doorbell/DPI mappings, SGID table, GSI QP/CQ references, xarrays, and iWARP workqueue. `qedr_qp` owns hardware queues, shadows for SQ/RQ WR IDs, RDMA state, PSNs, QED QP handles, and iWARP kref/completion state. User objects track umem, PBLs, mmap entries, and doorbell recovery metadata. There is no persistent storage.

## Dependencies And Integration Points
The header includes Linux PCI/xarray/completion, RDMA address helpers, QED public interfaces, QED chains, qede RDMA integration, RoCE common definitions, and local HSI layouts. It is the structural contract between QEDR source files and the lower-layer QED firmware interface.

## Risks And Test Signals
Because many objects embed RDMA core structs, layout assumptions are important; `struct qedr_qp` explicitly requires `ib_qp` first. Queue counters mix hardware chain indexes, software producers/consumers, and GSI-specific consumers, so wraparound bugs are a key risk. The header also centralizes reference-counted iWARP endpoint fields; incorrect ownership in users can leak or prematurely release QPs. Test signals include build coverage for all object-size registrations, lockdep/KASAN during object create/destroy stress, GSI traffic for `gsi_cons`, iWARP connect/disconnect refcount stress, and mmap/doorbell recovery tests for user contexts.
