# sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read.h

Purpose: declares the data structures shared by the quick-read implementation.

Important APIs, types, and functions: defines `qr_inode_t` for cached bytes, size, priority, mtime/ctime, stat buffer, last refresh, LRU node, generation, and invalidation time; `qr_priority_t` for pattern priority rules; `qr_conf_t` for cache limits/timeouts/options; `qr_inode_table_t` for cache usage and LRU buckets; `qr_statistics`; and `qr_private_t`.

Control flow: no functions are declared here beyond data contracts; `quick-read.c` uses these structures for lookup population, read serving, pruning, and lifecycle.

State and persistence: describes all quick-read runtime state, which is in-memory and per-process.

Dependencies and integration: includes Gluster logging, dict, list, compat/defaults, POSIX headers, `fnmatch`, and quick-read memory types.

Risks and test signals: changes to `qr_inode_t` affect locking and LRU accounting in `quick-read.c`. Because cached content is a raw `void *`, callers must preserve size and stat invariants. Compile tests and cache-behavior tests validate this contract.
