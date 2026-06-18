## sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsChunkPageVec.h

**Purpose:** Defines `FhgfsChunkPageVec`, a chunk-bounded list of page-vector blocks used to batch consecutive pages for BeeGFS buffered read/write operations.

**Important APIs/types/functions:** Inline APIs include create/destroy, init/uninit, `addPageListVec`, `getFirstPageListVec`, `pushPage`, `getSize`, `getInode`, `getFirstPageFileOffset`, iterator get/reset, iterator index, data-size helpers, and `_getChunkPageOffset`.

**Control flow:** Initialization creates the first `FhgfsPageListVec`, using a mempool for the first allocation if supplied. `pushPage` rejects full vectors and non-consecutive page indexes, appends to the current list-vector, allocates another list-vector if full, initializes first-page offsets/chunk offset, and tracks last-page size. Iteration walks list-vector entries and resets only when explicitly requested.

**State and persistence behavior:** State is transient in-memory page references, mapped page data pointers held in child `FhgfsPageListVec` entries, file/page indexes, chunk offset, and iterator cursors. Uninit destroys all list-vector blocks but page release/unmap is handled by IO completion helpers rather than this destructor alone.

**Dependencies and integration points:** Integrates `FhgfsPage`, `FhgfsPageListVec`, kernel mempools/slab caches, inode/page APIs, and remoting page-vector IO.

**Risks:** `_getChunkPageOffset` assumes `numChunkPages` is a power of two. `getDataSize` and `getRemainingDataSize` assume `size`/remaining pages are nonzero. The mempool pointer is stored only when first allocation used it; destroy must free all blocks through the right allocator. Non-consecutive pages are refused, so callers must split batches correctly.

**Test signals:** Test page pushing across list-vector boundaries, full chunk refusal, non-consecutive refusal, first-page offset/chunk offset, iterator reset, error cleanup, debug-mode forced allocation failures, and power-of-two chunk assumptions.
