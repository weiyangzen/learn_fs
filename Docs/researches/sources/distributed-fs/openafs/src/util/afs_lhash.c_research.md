
# sources/distributed-fs/openafs/src/util/afs_lhash.c

Purpose: `afs_lhash.c` implements a linear hash table that expands incrementally instead of rehashing the entire table at once. It is intended for unknown-size collections with bounded average chain length and caller-managed keys.

Important APIs and functions: `afs_lhash_create()` initializes table state and a bucket allocator. `afs_lhash_enter()` inserts a key/data pair and triggers `afs_lhash_expand()` when load exceeds five records per logical bucket. `afs_lhash_search()` finds and moves a bucket to the head of its chain; `afs_lhash_rosearch()` searches without mutation; `afs_lhash_remove()` unlinks and recycles a bucket; `afs_lhash_iter()` visits entries; `afs_lhash_stat()` reports chain and operation counters; `afs_lhash_destroy()` frees table and buckets. Internal `afs_lhash_address()` implements Larson-style addressing with split pointer `p` and `maxp`; `afs_lhash_accomodate()` grows the physical bucket-pointer array.

Control flow: expansion splits bucket `p` into `p + maxp`, advances `p`, doubles `maxp` at the end of a round, increments logical table size, and relocates only records from the split bucket. Physical table allocation grows in fixed chunks around 1 KiB.

State and persistence: state includes equal callback, allocator hooks, split state, record count, logical/physical table sizes, bucket array, atomlist bucket allocator, and statistics counters. No external persistence.

Dependencies and integration: depends on `afs_atomlist` for bucket storage and optional user-space assertions for invariants. Callers own element lifetime and locking.

Risks: duplicate entries are allowed. If `afs_atomlist_create()` fails in create, an assertion catches it only when assertions are enabled; otherwise a NULL bucket allocator may later crash. No locking. Key quality is caller responsibility. Test signals should cover insert/search/remove, duplicate keys, incremental expansion, read-only search preserving order, stat counters, allocator failure, and invariant builds.
