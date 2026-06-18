<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/dist-dir-utils.h -->
# sources/distributed-fs/orangefs/src/common/misc/dist-dir-utils.h

Purpose: declares distributed-directory utility APIs and debug/bitmap macros. It is used by code that creates, splits, routes, and inspects distributed directory data.

Important macros: `PINT_debug_dist_dir_attr`, `PINT_debug_dist_dir_bitmap`, `PINT_debug_dist_dir_handles`, and `PINT_debug_dist_dir` emit state through gossip debugging. `SET_BIT`, `CRL_BIT`, and `TST_BIT` manipulate bitmap words using 32-bit indexing conventions. `PINT_dist_dir_attr_copyto()` copies all fields in `PVFS_dist_dir_attr`.

APIs: declarations cover initialization, active-bucket checks, bucket lookup by hash, split-node selection, bitmap merge, name hashing, and server-number assignment.

State behavior: callers own the attr structure and bitmap allocation returned by `PINT_init_dist_dir_state()`. Macros mutate bitmaps in place and do not bounds-check. Debug macros assume valid attr/bitmap/handle arrays.

Dependencies include `pvfs2-types.h` for distributed-directory types and `gossip.h` for logging. Integration points include directory metadata layout, directory entry placement, and split logic.

Risks: the typo `CRL_BIT` likely means clear bit, but callers must know the exact name. Macro arguments can be evaluated multiple times in debug macros, so pass stable lvalues. Tests should include macro bit positions around word boundaries, attr copy correctness, and ABI consistency with serialized distributed-directory attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/dist-dir-utils.h -->
