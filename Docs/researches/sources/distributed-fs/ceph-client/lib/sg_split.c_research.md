# sources/distributed-fs/ceph-client/lib/sg_split.c

## Purpose
Splits an input scatterlist into multiple newly allocated scatterlists covering consecutive byte ranges. It supports both physical SG metadata and already DMA-mapped SG metadata, making it useful when a larger I/O vector must be divided into protocol or device-sized pieces.

## APIs, Control Flow, and State
The exported API is `sg_split()`. Internal `struct sg_splitter` tracks the first input SG for a split, number of output entries, skip offset in the first input entry, final-entry length, and allocated output SG pointer. `sg_calculate_split()` scans the input list, consumes an initial skip, walks split sizes, and records how many source entries each output needs. `sg_split()` first calculates physical layout with `sg_nents(in)`, allocates each output array, copies and adjusts physical SG fields in `sg_split_phys()`, then, if `in_mapped_nents` is non-zero, recalculates against `sg_dma_len()` and fills DMA address/length fields in `sg_split_mapped()`.

State is transient: allocated output SG arrays are returned to the caller, which must free them with `kfree()`. No global state exists.

## Dependencies, Integration, Risks, and Tests
Depends on scatterlist traversal, `sg_dma_address()`, `sg_dma_len()`, and slab allocation. Integration points include DMA-aware drivers and crypto/block/network paths that need segmented views of a larger SG list. Risks include invalid split sizes returning `-EINVAL`, mismatched physical and DMA segment counts after DMA mapping coalesces entries, off-by-one errors when a split boundary lands inside an SG entry, caller leaks on partial failure if outputs are not cleared, and callers forgetting that outputs are shallow copies of page references. Test signals include split-at-entry-boundary tests, split-inside-entry tests, skip beyond available data, mapped versus unmapped DMA length comparisons, and allocation failure injection.
