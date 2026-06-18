# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_htab.h

Purpose: implements a small arena-backed hash table for BPF arena tests using arena linked lists and the page-fragment allocator.

Important APIs and types: `struct htab_bucket`, `struct htab`, `struct hashtab_elem`; `htab_lookup_elem()`, `htab_update_elem()`, `htab_init()`, `select_bucket()`, and `lookup_elem_raw()`.

Control flow: `htab_init()` allocates two pages for buckets and sets bucket count. Lookup selects a bucket by `hash & (n_buckets - 1)` and walks the arena list. Update allocates a new element, inserts it at the bucket head, and removes/frees the old matching element if present.

State and persistence: table buckets and elements live in arena memory. Updates replace elements rather than mutating in place. No persistent state outside the arena map.

Dependencies and integration points: depends on `bpf_arena_alloc.h`, `bpf_arena_list.h`, errno, and the global arena map symbol.

Risks: hash is identity and bucket count must be power-of-two for masking; no locking or atomicity; allocation failure returns `-ENOMEM`; duplicate handling depends on successful new allocation before old removal.

Test signals: arena hash-table tests should verify insert, replace, lookup miss/hit, and behavior under allocator failure.
