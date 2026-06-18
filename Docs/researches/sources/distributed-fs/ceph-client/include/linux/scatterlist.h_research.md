# sources/distributed-fs/ceph-client/include/linux/scatterlist.h

Purpose: defines Linux scatter-gather list entries and helpers for representing non-contiguous memory as DMA, block I/O, crypto, networking, or driver transfer segments.

Important APIs and types: `struct scatterlist`, `struct sg_table`, `struct sg_append_table`, `struct sg_page_iter`, `struct sg_dma_page_iter`, and `struct sg_mapping_iter` are the main types. Helpers include `sg_set_page()`, `sg_set_folio()`, `sg_set_buf()`, `sg_page()`, `sg_next()`, chain/end marker helpers, DMA accessors, allocation/free routines, table-from-pages builders, split/copy/zero helpers, page iterators, and mapping iterators.

Control flow: callers initialize entries or tables, optionally chain multiple chunks, pass them through DMA mapping, then iterate either by SG entry, mapped DMA entry, page, or temporary mapped page window. Low bits of `page_link` encode chain and end markers, so access must go through helpers.

State and persistence: SG state is transient in-kernel transfer metadata: page pointer, offset, length, DMA address/length, optional DMA flags, and table entry counts. It does not persist data; it describes memory ownership and mapping state that callers must unmap/free correctly.

Dependencies and integration points: depends on MM page/folio helpers, DMA address types, architecture I/O, SWIOTLB/bus-address flags, and optional SG pools. It is a central contract between memory buffers and DMA-capable subsystems.

Risks and test signals: risks include direct page pointer assignment corrupting marker bits, using `orig_nents` instead of DMA `nents` after mapping, chained-list termination bugs, highmem mapping misuse, bounced segment cleanup mistakes, and length truncation in folio helpers. Test with chained and unchained tables, DMA-map/unmap users, highmem mappings, SG copy/zero operations, page iterator offsets, and DEBUG_SG builds.
