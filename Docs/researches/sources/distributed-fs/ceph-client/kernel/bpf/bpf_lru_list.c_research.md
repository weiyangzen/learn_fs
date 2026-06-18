# sources/distributed-fs/ceph-client/kernel/bpf/bpf_lru_list.c

## Purpose
`bpf_lru_list.c` implements the allocator and eviction list machinery used by preallocated BPF LRU hash maps. It owns the movement of embedded `struct bpf_lru_node` objects between free, inactive, active, and per-CPU local lists, and delegates actual hash table removal to the map-specific `del_from_htab` callback.

## Important APIs, Types, and Functions
The external entry points are `bpf_lru_init()`, `bpf_lru_populate()`, `bpf_lru_pop_free()`, `bpf_lru_push_free()`, and `bpf_lru_destroy()`. The core internal operations are `__bpf_lru_node_move_to_free()`, `__bpf_lru_node_move_in()`, `__bpf_lru_node_move()`, `__bpf_lru_list_rotate_active()`, `__bpf_lru_list_rotate_inactive()`, and `__bpf_lru_list_shrink()`. Common-LRU mode uses per-CPU `struct bpf_lru_locallist` caches and a single global `struct bpf_lru_list`; per-CPU-LRU mode uses one `struct bpf_lru_list` per possible CPU. `LOCAL_FREE_TARGET`, `PERCPU_FREE_TARGET`, and `nr_scans` bound refill and scan work.

## Control Flow
Initialization allocates either per-CPU global lists or per-CPU local lists plus one shared LRU list, initializes all list heads and locks, records `hash_offset`, and stores the hash-table deletion callback. Population walks the preallocated element buffer, finds each embedded node by `node_offset`, clears its ref bit, and places the node on the initial free list.

On allocation, `bpf_lru_pop_free()` dispatches by mode. Per-CPU mode locks the CPU's list, rotates active/inactive lists, shrinks inactive/free lists if needed, writes the requested hash into the element at `hash_offset`, and moves the node to inactive. Common mode first tries the local free list under the local lock, refills it from the shared LRU by flushing pending nodes, rotating, taking global free nodes, and shrinking if needed, then puts the chosen node on the local pending list. If no local/global node is available, it round-robin steals from local free or pending lists on possible CPUs and rehomes the node as current CPU pending.

On deletion or replacement, `bpf_lru_push_free()` dispatches by mode. Common mode converts local pending nodes directly to local free when their original CPU local list still owns them; otherwise it falls back to moving an LRU-list node to the shared free list. Per-CPU mode locks the node CPU's LRU list and moves the node to free.

## State and Persistence Behavior
All state is in memory and tied to the lifetime of the owning BPF map. Node state is encoded in `node->type`, `node->cpu`, `node->ref`, the list linkage, and the hash stored at `hash_offset` inside the containing element. Active and inactive counts track only the two counted LRU lists, not free/local lists. `next_inactive_rotation` persists scan position across allocations so inactive promotion is spread over time. There is no disk persistence.

## Dependencies and Integration Points
This file depends on Linux list, raw spinlock, per-CPU allocation, CPU mask iteration, and atomic `READ_ONCE`/`WRITE_ONCE` helpers. It integrates directly with `kernel/bpf/hashtab.c`, which embeds `struct bpf_lru_node` in preallocated hash elements, sets ref bits on lookup/update, supplies `htab_lru_map_delete_node()` as `del_from_htab`, and calls pop/push around map update/delete paths.

## Risks
Correctness depends on holding the right local or global raw spinlock for every list transition. Type mismatches are guarded with `WARN_ON_ONCE`, but a corrupted type can still leak capacity or break list accounting. The forced shrink path deliberately ignores the ref bit when no inactive unreferenced victim can be deleted, so hot entries can be evicted under pressure. Common-LRU stealing touches remote CPU local lists and relies on stable possible-CPU iteration and local lock coverage. The callback must safely remove the node from the hash table and may fail, in which case the LRU scan continues or allocation fails.

## Test Signals
Useful signals are BPF selftests for `BPF_MAP_TYPE_LRU_HASH` and `BPF_MAP_TYPE_LRU_PERCPU_HASH`, stress tests that churn updates/lookups/deletes across many CPUs, lockdep/KCSAN coverage around LRU list operations, map update tests where `del_from_htab` refuses candidates, and accounting checks that active/inactive/free/local counts reconcile after allocation failure and map teardown.
