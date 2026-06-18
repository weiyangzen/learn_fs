# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr.c

Purpose: implements version selection for MFC hardware operations and shared private/generic DMA buffer allocation helpers.

Important APIs and functions: `s5p_mfc_init_hw_ops` selects v5 or v6+ `struct s5p_mfc_hw_ops` and sets the warning-code base. `s5p_mfc_init_regs` initializes register pointer tables for v6+ hardware. `s5p_mfc_alloc_priv_buf` and `s5p_mfc_release_priv_buf` allocate/free firmware-private buffers either from a pre-reserved bitmap-backed memory region or via coherent DMA allocation. `s5p_mfc_alloc_generic_buf` and `s5p_mfc_release_generic_buf` always use coherent DMA allocation.

Control flow: probe or device initialization calls `s5p_mfc_init_hw_ops` and then v6+ register setup. Codec operation backends call allocation helpers for instance buffers, context buffers, scratch buffers, and codec-private memory. Reserved-memory allocation searches `dev->mem_bitmap` for 64 KiB-aligned zero areas, records virtual and DMA addresses relative to `dev->mem_base`, and clears the bitmap on release. DMA allocation records the memory context and validates that the returned address is not below the configured base.

State and persistence: persistent driver-lifetime state includes `dev->mfc_ops`, `dev->mfc_regs`, `dev->warn_start`, the reserved-memory bitmap, and `struct s5p_mfc_priv_buf` fields (`ctx`, `virt`, `dma`, `size`). Buffer contents are zeroed by callers where required, not by these generic helpers.

Dependencies and integration points: depends on v5/v6 operation providers, MFC variant version macros, bitmap allocation, coherent DMA APIs, and per-bank memory devices/base addresses. It is the shared memory-management layer used by both decoder and encoder operation backends.

Risks: reserved-memory release assumes `b->dma` belongs to the reserved range and `b->size` is page-aligned. The bitmap allocation check uses `start > bits`; exact-end edge behavior depends on `bitmap_find_next_zero_area` semantics. DMA allocations below the configured base are rejected, but generic allocations do not perform that base validation. Release helpers assume the buffer was allocated and still has a valid size/context.

Test signals: boot/probe tests for v5 and v6+ variants; allocation failure injection; reserved-memory and IOMMU/coherent-DMA memory modes; repeated open/close to verify bitmap reuse; and DMA address sanity checks on platforms with multiple MFC memory banks.
