# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa.h

## Purpose

`efa.h` is the main internal header for the Amazon EFA RDMA driver. It defines driver constants, device/object wrapper structures, statistics, IRQ/EQ state, and function prototypes for the verbs, mmap, address-handle, memory-registration, query, and stats operations implemented by the EFA driver.

## Important APIs, Types, and Functions

- Constants: `DRV_MODULE_NAME`, `DEVICE_NAME`, IRQ naming limits, and MSI-X vector index layout.
- `struct efa_dev`: top-level RDMA/PXI device wrapper containing `ib_device`, `efa_com_dev`, PCI BAR metadata, IRQ vectors, device attributes, stats, EQ array, and interrupt-enabled CQ xarray.
- Object wrappers: `efa_ucontext`, `efa_pd`, `efa_mr`, `efa_cq`, `efa_qp`, `efa_ah`, and `efa_eq`.
- `struct efa_stats`: atomic error/keepalive counters used by device stats.
- Function prototypes: query, PD, QP, CQ, MR, ucontext, mmap, AH, QP modify, link-layer, and hardware stats entry points.

## Control Flow

The header has no executable control flow. It defines the object model used when RDMA core allocates embedded driver objects via `ib_device_ops`; operation implementations cast from `ib_*` objects to these wrappers and call EFA admin commands through `efa_com_cmd.h`/`efa_com`.

## State and Persistence Behavior

`efa_dev` persists for the PCI device lifetime. User contexts store a UAR number. PDs store a device PD number. CQs own DMA or umem-backed completion memory plus mmap entries and optional EQ association. QPs own RQ DMA memory, doorbell/LLQ mmap entries, admin `qp_handle`, capacities, and software `state`. MRs retain `ib_umem` and optional interconnect IDs returned by firmware. Stats are atomic64 and intended for concurrent updates from verbs/error paths and async keepalive handling.

## Dependencies and Integration Points

The header depends on Linux PCI/interrupt APIs, RDMA core/uverbs ABI (`rdma/efa-abi.h`, `ib_verbs.h`), and EFA admin command wrappers. It is included by EFA main, verbs, communication command, and interrupt code. Userspace-visible mmap entries and response fields must remain coordinated with the EFA userspace ABI.

## Risks and Edge Cases

- Structure fields such as mmap entries and DMA buffers encode ownership contracts; destroy paths must release every optional entry exactly once.
- `efa_qp.state` is a software IB state cache and must stay consistent with firmware state transitions issued by admin commands.
- `cqs_xa` stores only interrupt-enabled CQs, so lookup code must not assume all CQs are present.
- Atomic stats avoid locking but provide no grouping consistency across counters.
- BAR address/length fields must be validated by PCI probe before use by mmap and doorbell paths.

## Test Signals

Compile all EFA objects after RDMA core signature changes, create/destroy each RDMA object type, exercise CQ interrupt and polling modes, map/free all mmap entry types, verify stats increments on failure paths, and run ABI tests with rdma-core EFA userspace.
