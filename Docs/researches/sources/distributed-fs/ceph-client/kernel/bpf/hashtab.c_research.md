# sources/distributed-fs/ceph-client/kernel/bpf/hashtab.c

## Purpose
`hashtab.c` implements the kernel BPF hash-map family: normal hash, LRU hash, per-CPU hash, LRU per-CPU hash, and hash-of-maps. It provides allocation, lookup, update, delete, lookup-and-delete, batch operations, BPF iterators, callback iteration, memory accounting, BTF field destructors, and JIT lookup generation.

## Important APIs, types, and functions
`struct bpf_htab` embeds `struct bpf_map` and owns bucket array, allocators, preallocated element pool or LRU, optional extra per-CPU elements, counters, bucket count, element size, and hash seed. `struct bucket` combines a nulls hlist with `rqspinlock_t`. `struct htab_elem` stores hash/list/LRU/freelist state followed by aligned key and value or per-CPU pointer. Map ops are `htab_map_ops`, `htab_lru_map_ops`, `htab_percpu_map_ops`, `htab_lru_percpu_map_ops`, and `htab_of_maps_map_ops`.

## Control flow
Allocation validates flags, preallocation/LRU constraints, key/value sizes, zero-seed permission, NUMA restrictions, and per-CPU size limits. It allocates buckets, initializes hash seed, chooses per-CPU counter versus atomic count, and either preallocates all elements plus freelist/LRU state or initializes `bpf_mem_alloc` caches. Preallocated normal maps may allocate per-CPU extra elements so replacement can avoid pop/push while holding a bucket lock.

Lookup hashes the key with jhash, selects a bucket, and walks a nulls hlist under RCU; LRU lookups optionally mark the element referenced. Generated lookup paths call `__htab_map_lookup_elem()` directly and adjust the returned element pointer to the value, with special per-CPU and map-in-map variants.

Updates lock the target bucket after hashing. Normal non-per-CPU updates allocate a replacement element, insert it at the head, then unlink and free the old element after unlock for non-prealloc maps. `BPF_F_LOCK` can update an existing element in place under the element spin lock. LRU updates allocate/pop from LRU before taking the bucket lock to preserve lock ordering. Per-CPU and map-in-map updates modify values in place when the key already exists. Deletes unlink under the bucket lock and free or return the node to LRU/freelist afterward. Batch lookup/delete scans buckets, optionally locks non-empty buckets, stages keys/values outside user-copy regions, and defers freeing deleted nodes until after bucket unlock.

Iterator support walks buckets under RCU using seq-file callbacks, keeps bucket/skip state, copies per-CPU values into a temporary buffer, and runs attached BPF iterator programs. `bpf_for_each_hash_elem()` iterates under migration-disabled context and invokes a BPF callback with current-CPU value for per-CPU maps.

## State and persistence behavior
Persistent map state includes bucket chains, preallocated storage or allocator caches, LRU/freelist ownership, per-CPU value areas, map-in-map inner references, BTF special fields, and element counters. Free paths distinguish preallocated and dynamic maps, free special BTF fields, release inner map references, destroy allocators/counters, and release buckets/map storage. Dynamic maps rely on `bpf_mem_alloc` for RCU-safe freeing.

## Dependencies and integration points
This file integrates with BPF map core, BTF record management, BPF memory allocators, pcpu freelist, LRU list, map-in-map helpers, RCU/nulls hlist, rqspinlock/raw locking, syscall batch APIs, BPF iterators, JIT helper inlining via `map_gen_lookup`, and verifier map op contracts.

## Risks and test signals
Risks include bucket/LRU lock inversion, RCU lookup races, incorrect count accounting under prealloc vs dynamic allocation, per-CPU value leaks or wrong CPU selection, BTF field destructor omissions, map-in-map reference leaks, batch user-copy error handling, nulls-list restart bugs, and generated lookup mismatches. Tests should cover all map variants with prealloc and no-prealloc where allowed, update flags (`BPF_ANY`, `BPF_EXIST`, `BPF_NOEXIST`, `BPF_F_LOCK`, per-CPU CPU flags), LRU eviction, concurrent lookup/update/delete, lookup-and-delete, batch lookup/delete with small buffers and faults, iterator stop/resume, callback iteration early stop, memory accounting, zero-seed permission, BTF fields, and hash-of-maps fd lookup/update/free.
