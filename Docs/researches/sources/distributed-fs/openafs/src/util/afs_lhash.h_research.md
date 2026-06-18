
# sources/distributed-fs/openafs/src/util/afs_lhash.h

Purpose: `afs_lhash.h` declares the linear hash table abstraction and its statistics structure.

Important APIs and types: opaque `afs_lhash`; `struct afs_lhash_stat` with min/max chain length, bucket/record counts, and cumulative search/remove counters. Public functions create/destroy, iterate, search, read-only search, remove, enter, and collect stats.

Control flow and integration: callers provide an equality predicate, allocation hooks, and precomputed unsigned keys. The header documents incremental growth and makes clear that duplicate entries are not rejected.

State and persistence: state is opaque and process-local. Caller owns data objects and synchronization.

Risks and test signals: misuse risks include poor key distribution, duplicate entries, freeing data before removal, or concurrent mutation without locks. Tests should validate API contracts and stats after representative workloads.
