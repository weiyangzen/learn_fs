# sources/distributed-fs/ceph-client/kernel/dma/dummy.c

## Purpose
This file defines a fail-closed DMA ops table for devices or architectures that expose `struct dma_map_ops` but cannot perform DMA mappings. Every mapping capability fails, and unexpected unmap calls warn.

## Important APIs, Types, And Functions
`dma_dummy_mmap()` returns `-ENXIO`. `dma_dummy_map_phys()` returns `DMA_MAPPING_ERROR`. `dma_dummy_unmap_phys()` warns. `dma_dummy_map_sg()` returns `-EINVAL`. `dma_dummy_unmap_sg()` warns. `dma_dummy_supported()` returns false. `dma_dummy_ops` publishes these callbacks.

## Control Flow
Callers attempting mmap, physical mapping, SG mapping, or mask support get immediate failure. Unmap functions should be unreachable because corresponding map operations cannot succeed; they emit `WARN_ON_ONCE(true)` to flag misuse.

## State, Persistence, And Dependencies
There is no state. Dependencies are limited to DMA map ops types, scatterlists, VMAs, and warning support.

## Integration Points
Built when `CONFIG_ARCH_HAS_DMA_OPS` is enabled, this ops table can be assigned to devices that should not DMA or as a safe default before real ops are installed.

## Risks
Assigning dummy ops to a device that requires DMA causes all DMA setup to fail. Conversely, the fail-closed behavior is useful because it prevents accidental physical mappings on unsupported hardware. Unexpected unmap warnings indicate caller accounting bugs.

## Test Signals
Test that map calls return failure, DMA mask support reports false, mmap returns `-ENXIO`, and unmap callbacks warn only if a caller incorrectly unmaps a never-mapped buffer.
