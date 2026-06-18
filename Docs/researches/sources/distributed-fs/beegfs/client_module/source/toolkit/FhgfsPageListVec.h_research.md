## sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsPageListVec.h

**Purpose:** Defines a fixed-size page-vector block containing `FhgfsPage` entries, linked into larger chunk page vectors.

**Important APIs/types/functions:** Defines `BEEGFS_LIST_VEC_MAX_PAGES`, `struct FhgfsPageListVec`, and inline create/destroy/init/uninit, `pushPage`, `getMaxPages`, and `getFhgfsPage`.

**Control flow:** Creation first tries slab-cache allocation and, if provided and necessary, falls back to a mempool allocation for guaranteed first vector availability. Debug builds intentionally simulate allocation failure on odd `jiffies`. `pushPage` maps the page with `kmap`, stores page/data/length, and increments `usedPages`.

**State and persistence behavior:** Each block stores up to 16 pages in debug builds or 32 normally, plus list linkage. It owns allocation of the block object but not final page release; page lifecycle is completed by chunk/page IO helpers.

**Dependencies and integration points:** Used exclusively by `FhgfsChunkPageVec` and page IO paths. Depends on kernel mempool, slab cache, list, and kmap APIs.

**Risks:** Destroy chooses mempool free if a pool pointer is supplied, not per-object allocation provenance; the parent must pass the correct allocator context. `getFhgfsPage` has no bounds check. Debug allocation failure changes timing and must not trigger false production assumptions.

**Test signals:** Test slab and mempool allocation paths, push up to capacity and refusal after capacity, kmap/unmap lifecycle through parent cleanup, and debug failure simulation.
