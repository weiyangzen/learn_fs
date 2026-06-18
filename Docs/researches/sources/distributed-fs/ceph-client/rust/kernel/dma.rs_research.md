# sources/distributed-fs/ceph-client/rust/kernel/dma.rs

## Purpose
`dma.rs` provides Rust abstractions for Linux DMA configuration and coherent memory allocation. It covers DMA masks, mapping attributes, data directions, CPU-staged coherent allocations, shared coherent allocations, no-kernel-mapping handles, and projection macros for hardware-shared structures.

## Important APIs, Types, and Functions
`DmaAddress` aliases `dma_addr_t`. The `dma::Device` trait exposes `dma_set_mask`, `dma_set_coherent_mask`, `dma_set_mask_and_coherent`, and `dma_set_max_seg_size`. `DmaMask`, `Attrs`, `attrs::*`, and `DataDirection` model C DMA constants. `CoherentBox<T>` owns CPU-only staged coherent memory. `Coherent<T>` exposes a DMA handle and unsafe CPU access. `CoherentHandle` represents hardware-only coherent memory with `DMA_ATTR_NO_KERNEL_MAPPING`. Macros `dma_read!` and `dma_write!` project into `Coherent` buffers.

## Control Flow
Drivers set DMA masks from probe before allocating. `CoherentBox` allocates a `Coherent`, lets the CPU safely initialize it before the DMA address is exposed, and then converts into `Coherent`. `Coherent` allocation calls `dma_alloc_attrs`, stores the CPU pointer, DMA address, attrs, and an owning device reference, then frees via `dma_free_attrs` on drop. Binary debugfs reads call `writer.write_dma` for coherent buffers. `CoherentHandle` adds `DMA_ATTR_NO_KERNEL_MAPPING` and exposes only size and DMA address.

## State and Persistence
DMA allocation state is in memory and device/IOMMU state. `Coherent` and `CoherentHandle` hold a refcounted device reference so free calls have a valid device pointer. No durable persistence exists, but hardware may access memory until the driver stops the device.

## Dependencies and Integration Points
The module depends on `Device<Core>` for mask setup, `Device<Bound>` for allocation, debugfs binary writer support, `KnownSize`, `AsBytes`, `FromBytes`, userspace slice writers, and DMA mapping bindings. It is intended for bus drivers and can be exported through debugfs.

## Risks
The file explicitly notes a soundness gap: DMA allocations can carry device/IOMMU resources and ideally need devres-style revocation without making CPU memory access cumbersome. Safe CPU references from `Coherent` are unsafe because callers must prevent device races. Drops require hardware to be halted. Size overflow, zero-length allocations, ZSTs, and architecture-dependent DMA address width are handled but need tests.

## Test Signals
Test mask setup, coherent scalar and slice allocation, zero-length and overflow rejection, initialization failure cleanup, no-kernel-mapping allocation/free, debugfs binary reads with offsets, `dma_read!`/`dma_write!` projections, and remove paths where hardware is stopped before allocations drop.
