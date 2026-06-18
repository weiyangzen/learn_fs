# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-mem-types.h

Purpose: defines memory accounting IDs for snapview-server allocations.

Important APIs/types: `enum snapview_mem_types` starts at `gf_common_mt_end + 1` and defines tags for private state, inode contexts, dirent arrays, fd contexts, and `gf_svs_mt_end`.

Control flow/state: no executable behavior; allocation tags are consumed by `GF_CALLOC` and initialized through `xlator_mem_acct_init(this, gf_svs_mt_end)`.

Dependencies/integration: includes `glusterfs/mem-types.h` and must match allocations in server, helper, and management code.

Risks/test signals: adding new persistent allocations without a tag weakens leak accounting. Compile and memory-accounting init tests are the main signals.
