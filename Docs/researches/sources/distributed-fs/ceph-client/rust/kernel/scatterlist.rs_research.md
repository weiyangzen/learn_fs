## sources/distributed-fs/ceph-client/rust/kernel/scatterlist.rs

Purpose: wraps kernel scatter-gather tables and entries for DMA, supporting borrowed externally managed `sg_table`s and owned Rust-created tables built from vmalloc-backed page iterators.

Important APIs/types/functions: `SGEntry` exposes `dma_address` and `dma_len`. `SGTable<Borrowed>` can be constructed from raw `sg_table *` with `from_raw` and iterated. `Owned<P>` stores a `Devres<DmaMappedSgt>`, `RawSGTable`, and backing pages, with drop order intentionally unmapping DMA before freeing the SG table and pages. `SGTable<Owned<P>>::new` constructs a pinned table from `Device<Bound>`, pages, DMA direction, and flags. `SGTableIter` yields DMA-mapped entries.

Control flow: owned construction collects `struct page *` values from a `VmallocPageIter`, allocates an sg table with `sg_alloc_table_from_pages_segment`, computes max segment from `dma_max_mapping_size`, then maps with `dma_map_sgtable`. Iteration starts at `sgl`, uses `nents`, and advances with `sg_next`. Drops call `dma_unmap_sgtable` and `sg_free_table`.

State/persistence: state is in-memory DMA mapping state associated with a bound device. The backing page owner `P` is held to keep pages alive. No persistent storage exists.

Dependencies/integration: integrates with `Device`, `Devres`, DMA direction/address types, vmalloc page iteration, `ARef<Device>`, allocation flags, and C scatterlist/DMA bindings.

Risks: borrowed `from_raw` requires no concurrent modification and external lifetime validity. Owned construction rejects empty page lists to avoid C-side null dereference. The iterator warns that entries can become unmapped on device unbind despite table borrowing. Drop order is safety-critical. DMA direction and device must match unmap parameters.

Test signals: doctest covers constructing an owned table from `VVec`. Runtime tests should validate empty-buffer rejection, nents iteration boundaries, unmap-on-drop, and device-unbind devres interaction.
