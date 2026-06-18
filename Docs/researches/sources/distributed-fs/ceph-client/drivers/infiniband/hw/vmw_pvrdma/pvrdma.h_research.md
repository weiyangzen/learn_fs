<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma.h

## Purpose

Central private header for the VMware PVRDMA driver. It defines all driver-private object wrappers, core device state, conversion helpers, MMIO accessors, enum translation helpers, and cross-file function prototypes.

## Important APIs, Types, And Functions

Major types include `struct pvrdma_dev`, `pvrdma_page_dir`, `pvrdma_cq`, `pvrdma_ucontext`, `pvrdma_pd`, `pvrdma_user_mr`, `pvrdma_srq`, `pvrdma_qp`, `pvrdma_ah`, `pvrdma_wq`, `pvrdma_uar_map`, and `pvrdma_id_table`. Inline helpers convert generic IB objects to PVRDMA objects, write/read device registers, ring CQ/QP UAR doorbells, convert MTU/port/QP/MR/access/opcode/completion values, and compute page-directory pointers.

Prototypes link together command posting, UAR management, page-directory management, MR/CQ/QP/SRQ helpers, and AH/GID conversion helpers.

## Control Flow

All PVRDMA verbs handlers receive generic RDMA core objects and use the `to_v*()` helpers to reach private state. Most host operations build command structures from `pvrdma_dev_api.h`, post them through `pvrdma_cmd_post()`, then update local tables and counters. Work queues and completion queues share ring state in page directories and notify the device through UAR MMIO writes.

## State And Persistence Behavior

`struct pvrdma_dev` is the persistent per-PCI-device state: register mapping, shared device region, command/response slots, async/CQ rings, QP/CQ/SRQ lookup tables, GID table, UAR allocator, counters, netdev association, and RDMA registration state. Object wrappers persist for the lifetime of their RDMA core object and often hold umem pins or coherent page directories.

## Dependencies And Integration Points

Depends on Linux PCI, interrupts, workqueues, semaphores, RDMA core verbs, RDMA user ABI, PVRDMA device ABI, and the local ring/device/verbs headers. It is included by all PVRDMA implementation files.

## Risks And Edge Cases

Several translation helpers assume 1:1 enum values with RDMA core for many fields, while switch statements handle opcodes and network types explicitly. Table indexing commonly uses handles modulo capability sizes when receiving events, but some destroy paths clear by raw handle; tests should watch for handle semantics across device versions. MMIO writes require ordering barriers in callers where host-visible state is prepared.

## Test Signals

Compile coverage verifies structure layout and cross-file prototypes. Runtime signals include successful probe, ucontext/PD/CQ/QP/MR/SRQ lifecycle, correct work-completion decoding, and stable behavior across PVRDMA version 17 through 20 feature gates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma.h -->
