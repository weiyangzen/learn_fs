# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/osdep.h

## Purpose
`osdep.h` provides Linux OS abstraction declarations and simple memory wrapper structures used by the IRDMA shared-control code.

## Important APIs, types, and functions
Important types are `struct irdma_dma_mem`, `struct irdma_virt_mem`, and `struct irdma_dma_info`. It forward-declares many core structs and prototypes OS-facing hooks for ibdev lookup, IEQ handling, virtual-channel state, device refcounting, CQP SDS/HMC commands, FPM buffers, termination timers, hardware stats timers, register access, and vmalloc page mapping.

## Control flow, state, and persistence
There is no executable flow. The memory wrapper structs carry virtual address, DMA physical address, and size through HMC, PBLE, CQP, queue, and context allocation paths.

## Dependencies and integration points
It includes Linux PCI, bitfield, RDMA verbs, and DSCP headers. It is included by most low-level files before hardware/control types are fully defined, allowing shared code to call OS-specific helpers implemented elsewhere.

## Risks and test signals
Risks include packed DMA memory wrappers causing unexpected alignment assumptions, stale prototypes, and divergent OS helper behavior. Tests should cover DMA mapping/unmapping, register access on 32-bit and 64-bit builds, virtual-channel timeout handling, and stats/termination timer lifetimes.
