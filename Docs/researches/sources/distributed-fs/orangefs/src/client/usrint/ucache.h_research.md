## sources/distributed-fs/orangefs/src/client/usrint/ucache.h

Purpose: Defines the shared-memory layout, constants, sentinel values, lock abstraction, stats, and public API for OrangeFS usrint's experimental user cache.

Important APIs, types, and functions: Constants set table sizes, block size, shared-memory keys, modes, cache size, sentinel values, and lock type. Core structures are `ucache_stats_s`, `ucache_aux_s`, `mem_ent_s`, `mem_table_s`, `cache_block_u`, `file_ent_s`, `file_table_s`, `ucache_u`, and `ucache_ref_s`. Public declarations expose cache initialization, file open/close, memory-table lookup, block lookup/insert, info/flush, daemon-only initialization, test wiping, and lock helpers.

Control flow: Header-only inline declarations define the contract: callers must initialize/attach the cache, open a file to obtain a `file_ent_s`, then lookup/insert cache blocks by file offset and close/flush when done.

State and persistence: Describes System V shared-memory state: one large cache segment and one auxiliary segment containing process-shared locks and stats. Data survives individual process exits until the daemon or system removes shared memory.

Dependencies and integration points: Includes `<stdint.h>`, `<pthread.h>`, `<sys/shm.h>`, and `gen_mutex_t` through including code for `LOCK_TYPE == 3`. Shared constants must match daemon and client builds.

Risks and test signals: Layout is compile-time sensitive to `BLOCKS_IN_CACHE`, `LOCK_TYPE`, platform word size, and struct padding. Changing constants can strand incompatible shared-memory segments. Inline prototypes without definitions in the header rely on `ucache.c` linkage choices. Test ABI/layout consistency across daemon/client, 32-bit vs 64-bit sentinels, all lock types, and cache-size arithmetic overflow.
