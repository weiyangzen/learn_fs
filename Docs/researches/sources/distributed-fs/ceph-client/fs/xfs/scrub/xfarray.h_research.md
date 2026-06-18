<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfarray.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/xfarray.h

Purpose: declares the xfile-backed fixed-record array abstraction and its sort interface for scrub and repair modules that need large, pageable, mostly sequential collections.

Important APIs and types: `xfarray_idx_t` is a 64-bit index with `XFARRAY_NULLIDX` and `XFARRAY_CURSOR_INIT` sentinels. `struct xfarray` exposes backing `xfile`, logical length, max length, unset-slot count, object size, and object-size log. Public functions create/destroy arrays, load/store/unset elements, store into any unset slot, test for all-zero/null records, truncate, report backing bytes, get length, and load the next non-null entry. Inline helpers implement sparse load, append, and `xfarray_iter()` returning 1/0/errno. Sorting declarations include `xfarray_cmp_fn`, small-sort and pivot constants, `struct xfarray_sortinfo`, `XFARRAY_SORT_KILLABLE`, and `xfarray_sort()`.

Control flow: callers create an array with a required capacity and record size, append or store nonzero records, optionally use unset/store-anywhere for sparse lifecycle management, iterate with a cursor initialized to `XFARRAY_CURSOR_INIT`, and sort with a comparison function. The sortinfo structure documents its variable-sized tail allocation for quicksort low/high stacks and scratch/pivot records.

State and persistence: the header documents logical state stored in the implementation: backing xfile pages, `nr`, `max_nr`, `unset_slots`, and sort scratch/folio cache. Data is transient scrub working state, not filesystem metadata. All-zero records are reserved as the unset marker, which is a key contract for callers.

Dependencies and integration points: depends on `struct xfile`, scrub relaxation state, kernel comparison function type, and xfile-backed callers such as btree rebuilders, parent/directory scans, nlinks, counters, and other repair collectors. It hides xfile offset math from callers while allowing them to monitor bytes and sort records.

Risks and test signals: callers that need to store all-zero records must encode them differently or they will disappear during iteration. Because the header exposes struct fields, external users can accidentally mutate invariants. Test signals should include compile coverage for all inline helpers, sparse iteration API return values, sort flag behavior, and consumers that rely on `unset_slots` or `xfarray_bytes()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfarray.h -->
