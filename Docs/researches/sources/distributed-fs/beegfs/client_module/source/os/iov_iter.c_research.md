## sources/distributed-fs/beegfs/client_module/source/os/iov_iter.c

**Purpose:** Implements `BeeGFS_ReadSink`, a helper that converts difficult read destinations, especially pipe iterators, into safe bvec-backed iterators for parallel BeeGFS storage reads.

**Important APIs/types/functions:** Provides `beegfs_readsink_reserve` and `beegfs_readsink_release`, with internal `beegfs_readsink_reserve_no_pipe`, `compute_max_pagecount`, and `beegfs_readsink_reserve_pipe` when pipe iterators are supported.

**Control flow:** Non-pipe iterators are copied and truncated to the requested size. Pipe iterators allocate page and bio_vec arrays, call `iov_iter_get_pages` or `iov_iter_get_pages2`, build a `bio_vec` view over returned pages, and initialize `sanitized_iter` as an `ITER_BVEC`. Release puts every reserved page, frees arrays, and zeroes the struct.

**State and persistence behavior:** The read sink temporarily owns page references and metadata arrays between reserve and release. It does not advance the original iterator; callers advance the original after completed reads.

**Dependencies and integration points:** Used by `FhgfsOpsRemoting_readfileVec` before splitting reads across stripe targets. Depends on kernel `iov_iter`, pages, bvecs, slab allocation, and feature macros for pipe and `iov_iter_get_pages2`.

**Risks:** Low-memory allocation failure leaves a sanitized iterator with count zero, so callers must handle empty state. A failed second allocation leaks the first allocation until release is called, which the intended call pattern does. Pipe iterator APIs can auto-advance in newer kernels, so the code copies the iterator for `get_pages2` to avoid double-advancement.

**Test signals:** Read into normal iovec, kvec, bvec, and pipe destinations; force allocation failures; verify page refs are released; validate no double advancement with `iov_iter_get_pages2`; and exercise partial reserve sizes.
