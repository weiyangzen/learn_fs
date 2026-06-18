# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm_bo.h

## Purpose
This header declares the buffer-object layer underneath AtomISP HMM. It manages ISP virtual address allocation, page allocation/import, MMU binding, vmap/mmap exposure, refcounts, and searchable allocation metadata.

## Important APIs, Types, And Functions
- `struct hmm_bo_device` owns the ISP virtual address arena (`start`, `pgnr`, `size`), an `isp_mmu`, list/rbtree indexes for all/free/allocated BOs, locks, a status flag, and a slab cache.
- `struct hmm_buffer_object` represents one allocation with page array, mutex, type (`HMM_BO_PRIVATE` or `HMM_BO_VMALLOC`), mmap/vmap counts, status flags, vmap address, rb-tree node, address range, page count, and duplicate-size free-list links.
- Status flags include `HMM_BO_ALLOCED`, `HMM_BO_PAGE_ALLOCED`, `HMM_BO_BINDED`, `HMM_BO_MMAPED`, `HMM_BO_VMAPED`, `HMM_BO_VMAPED_CACHED`, and `HMM_BO_ACTIVE`.
- Device lifetime APIs are `hmm_bo_device_init()`, `hmm_bo_device_exit()`, and `hmm_bo_device_inited()`.
- BO lifetime and state APIs include `hmm_bo_alloc()`, `hmm_bo_release()`, `hmm_bo_ref()`, `hmm_bo_unref()`, `hmm_bo_allocated()`, `hmm_bo_alloc_pages()`, `hmm_bo_free_pages()`, `hmm_bo_bind()`, `hmm_bo_unbind()`, `hmm_bo_vmap()`, `hmm_bo_vunmap()`, `hmm_bo_mmap()`, and search helpers by ISP start, ISP range, and vmap start.

## Control Flow
The intended lifecycle is initialize the device with an MMU client and address arena, allocate a BO range, allocate or import physical pages, bind those pages into the ISP MMU, optionally vmap or mmap them for CPU/user access, then unmap/unbind/free pages and unref/release the BO. Device search APIs let higher layers translate `ia_css_ptr` or vmap addresses back to BO metadata for data movement and teardown.

## State And Persistence
State persists in the BO device's linked list, allocated/free rbtrees, MMU mappings, page arrays, and per-BO status bits. `rbtree_mutex` protects virtual address tree updates, `list_lock` protects the full BO list, and each BO has its own mutex for object state. The data is in-memory only.

## Dependencies And Integration Points
The layer depends on Linux list/rbtree/kref/mutex/spinlock/mm APIs, `isp_mmu.h` for hardware address translation, `hmm_common.h` diagnostics, and CSS `ia_css_types.h`. It is the main bridge between high-level HMM calls and the ISP MMU driver.

## Risks
- Correctness depends on strict status-bit transitions; missing rollback after partial page allocation, binding, vmap, or mmap can leak pages or leave stale MMU entries.
- The free-rbtree duplicate-size linked-list scheme has nontrivial invariants (`prev`/`next` only for same-page-count free nodes).
- Cache mode is tracked by status flags; mixing cached and uncached mappings needs careful enforcement.
- `VM_RESERVED` is mentioned in comments but is obsolete in newer kernels, so implementation compatibility should be checked.
- Search-by-range APIs must be used carefully to avoid accepting invalid interior addresses for operations that require allocation starts.

## Test Signals
Validation should cover arena initialization/exit, allocation/free fragmentation, rbtree coalescing or duplicate-size behavior, refcount release paths, page allocation and vmalloc import, MMU bind/unbind plus TLB flushing by callers, vmap cached/uncached transitions, mmap count handling, and search correctness for start, interior, boundary, and missing addresses.
