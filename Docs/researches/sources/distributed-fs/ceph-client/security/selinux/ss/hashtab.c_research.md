<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.c

## Purpose
Implements a generic sorted-bucket hash table used by SELinux policy structures such as symbol tables. It provides allocation, insertion node allocation, destruction, mapping, duplication, optional debug statistics, and slab cache initialization.

## Important APIs, Types, and Functions
Public functions are `hashtab_init()`, `__hashtab_insert()`, `hashtab_destroy()`, `hashtab_map()`, `hashtab_duplicate()`, optional `hashtab_stat()`, and `hashtab_cache_init()`. Internal helper `hashtab_compute_size()` rounds element hints to a power-of-two table size.

## Control Flow
Initialization zeroes the table and allocates the bucket array when the hint is nonzero. Inline insertion/search in the header use caller-provided hash/compare functions to maintain sorted chains; `__hashtab_insert()` allocates and links a node at the requested position. Duplication allocates a same-sized table and invokes a caller copy callback for every node, preserving bucket order and cleaning partial copies through a destroy callback on failure.

## State and Persistence
State is `struct hashtab` with bucket array, size, and element count. Nodes are slab allocated from `hashtab_node_cachep`. The table is not serialized directly here, but policydb symbol readers/writers persist data stored in hashtabs.

## Dependencies and Integration Points
Depends on SELinux allocation helpers from `security.h`, slab caches, and caller-supplied key functions declared in `hashtab.h`. Used by policydb and conditional duplication paths.

## Risks
`hashtab_destroy()` frees only nodes and bucket arrays; callers must free keys/data separately where required. Duplication failure cleanup relies on the caller destroy callback matching the copy callback's ownership. Zero-sized tables are valid but reject insert/search as appropriate.

## Test Signals
Test insert/search ordering through header APIs, duplicate with deep and shallow copy callbacks, duplicate failure cleanup, destroy after partial construction, debug statistics, and policy load/unload leak tests for symbol tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.c -->
