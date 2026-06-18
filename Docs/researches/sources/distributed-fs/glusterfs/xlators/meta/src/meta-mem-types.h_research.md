# sources/distributed-fs/glusterfs/xlators/meta/src/meta-mem-types.h

Purpose: defines memory-accounting identifiers for the `meta` translator. These identifiers let Gluster attribute allocations for private state, fd caches, generated strings, dirents, and frame-local state.

Important APIs/types/functions: `enum gf_meta_mem_types_` starts at `gf_common_mt_end + 1` and defines `gf_meta_mt_priv_t`, `gf_meta_mt_fd_t`, `gf_meta_mt_fd_data_t`, `gf_meta_mt_strfd_t`, `gf_meta_mt_dirents_t`, `gf_meta_mt_local_t`, and `gf_meta_mt_end`.

Control flow: `meta.c::mem_acct_init()` passes `gf_meta_mt_end` to `xlator_mem_acct_init()`. Allocation sites in helper and hook code use these enum values with `GF_MALLOC()`/`GF_CALLOC()`.

State and persistence behavior: no runtime state is stored here; the enum indexes runtime allocation counters. Values must remain in range and unique for accounting accuracy.

Dependencies and integration points: includes `<glusterfs/mem-types.h>` for `gf_common_mt_end`. Integrated by all `meta` source files that allocate translator-specific memory.

Risks and edge cases: adding new allocation categories after `gf_meta_mt_end` or reordering values can break accounting interpretation. Missing use of these types makes leak diagnostics less precise.

Test signals: successful `mem_acct_init()`, leak reports grouped under the expected meta categories, and allocation/failure-path tests for fd and dirent caches.
