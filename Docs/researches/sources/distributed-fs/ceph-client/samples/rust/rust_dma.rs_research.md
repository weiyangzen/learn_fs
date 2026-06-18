# sources/distributed-fs/ceph-client/samples/rust/rust_dma.rs

## Purpose

This Rust PCI driver sample demonstrates DMA mask setup, coherent DMA allocation, typed DMA reads/writes, scatter-gather table construction, and cleanup-time verification against QEMU's `pci-testdev`.

## Important APIs, Types, and Functions

It implements `pci::Driver` for `DmaSampleDriver`, uses `pci_device_table!`, `Coherent<[MyStruct]>`, `dma_write!`, `dma_read!`, `DmaMask::new::<64>()`, `SGTable<Owned<VVec<u8>>>`, and `PinnedDrop`. `MyStruct` is marked `AsBytes` and `FromBytes`.

## Control Flow

Probe sets a 64-bit DMA mask, allocates a coherent slice sized for `TEST_VALUES`, writes test pairs through DMA access macros, allocates a virtual vector for a 4-page scatterlist, and stores all resources in the driver. On pinned drop, it checks coherent memory values and logs DMA addresses of SG entries.

## State and Persistence Behavior

Driver state holds an `ARef` to the PCI device, coherent allocation, and pinned SG table. Coherent data persists for the device lifetime. Drop asserts that the coherent values remain intact.

## Dependencies and Integration Points

It depends on PCI, QEMU `pci-testdev` vendor/device ID, kernel DMA API, scatterlist wrappers, and Rust pin-init.

## Risks and Edge Cases

The comment says DMA allocation/mapping calls are not concurrent before using unsafe `dma_set_mask_and_coherent`. Drop uses assertions; unexpected corruption can trigger kernel assertion behavior in a sample. The SG table is created for `ToDevice` without actual device DMA.

## Test Signals

Run under QEMU with `-device pci-testdev`, load the module, confirm probe/unload logs, coherent value assertions, and printed SG DMA addresses.
