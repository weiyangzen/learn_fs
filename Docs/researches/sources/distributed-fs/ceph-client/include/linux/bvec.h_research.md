## sources/distributed-fs/ceph-client/include/linux/bvec.h

**Purpose:** This header defines `bio_vec` memory segment descriptors and iterator helpers used by block I/O and page/folio-backed data movement.

**Important APIs/types/functions:** `struct bio_vec` stores page, length, and page offset. `bvec_set_page()`, `bvec_set_folio()`, and `bvec_set_virt()` initialize segments. `struct bvec_iter` tracks sector, remaining bytes, vector index, and per-vector offset. Access macros produce single-page and multipage views. Iterators include `bvec_iter_advance()`, `bvec_iter_advance_single()`, `for_each_bvec`, `for_each_mp_bvec`, `bvec_init_iter_all()`, and `bvec_advance()`. Mapping/copy helpers include `bvec_kmap_local()`, `memcpy_from_bvec()`, `memcpy_to_bvec()`, `memzero_bvec()`, `bvec_virt()`, and `bvec_phys()`.

**Control flow, state, persistence:** Iterators mutate only in-memory cursor state; `bi_size` shrinks as bytes are consumed. Segment descriptors are views over existing pages/folios, not owners of storage.

**Dependencies/integration:** Depends on highmem, pages/folios, warning helpers, min/max, and memory copy helpers. It integrates tightly with `bio`, block layer splitting, and filesystem I/O.

**Risks and test signals:** Risks include advancing past end, assuming multipage bvecs are single-page, using `bvec_virt()` on highmem, offset overflow, and losing sector updates because bare bvec helpers do not maintain `bi_sector`. Test signals are bio splitting/merging tests, highmem builds, KASAN bounds checks, WARN coverage for over-advance, and block I/O corruption tests.
