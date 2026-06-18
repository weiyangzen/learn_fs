# sources/distributed-fs/ceph-client/kernel/livepatch/shadow.c

## Purpose
`shadow.c` implements the livepatch shadow variable API: an RCU-safe global hash table mapping an arbitrary parent object pointer and caller-defined ID to a patch-owned data buffer. It lets livepatches attach auxiliary state to existing kernel objects without changing those object layouts.

## Important APIs, Types, and Functions
The internal `struct klp_shadow` contains an hlist node, RCU head, parent `obj`, numeric `id`, and flexible `data[]`. Global state is `klp_shadow_hash` and `klp_shadow_lock`.

Exported APIs are `klp_shadow_get()`, `klp_shadow_alloc()`, `klp_shadow_get_or_alloc()`, `klp_shadow_free()`, and `klp_shadow_free_all()`. Internal helpers are `klp_shadow_match()`, `__klp_shadow_get_or_alloc()`, and `klp_shadow_free_struct()`.

## Control Flow
Lookups run under `rcu_read_lock()` and scan the hash bucket keyed by the object pointer. Allocation first checks locklessly, speculatively allocates zeroed storage, rechecks under `klp_shadow_lock`, optionally invokes the constructor under that spinlock, then publishes the entry with `hash_add_rcu()`. `klp_shadow_alloc()` warns and returns `NULL` on duplicates; `klp_shadow_get_or_alloc()` returns the existing data pointer.

Freeing acquires the spinlock, removes matching entries with `hash_del_rcu()`, runs an optional destructor, and defers memory release with `kfree_rcu()`. `klp_shadow_free_all()` scans every bucket and removes all entries with a given ID.

## State and Persistence Behavior
Shadow variables are runtime-only and persist until explicitly freed by the livepatch or until system shutdown. The data payload is owned by the caller. The implementation guarantees the shadow structure remains alive for concurrent readers via RCU but does not serialize access to caller payload contents.

## Dependencies and Integration Points
The file integrates with the public livepatch shadow API in `<linux/livepatch.h>`, kernel hashtable helpers, spinlocks, RCU, and slab allocation. Livepatch replacement code and callbacks can use it to migrate or annotate state across patched object lifetimes.

## Risks and Test Signals
Constructors run under a spinlock and must not sleep. Callers must handle payload locking and lifetime after free; a returned data pointer is not protected after the caller leaves its own synchronization. Duplicate allocation behavior differs between `alloc` and `get_or_alloc`. Tests should stress concurrent get/free, duplicate allocation, constructor failure, destructor execution, free-all by ID, and invalid sleeping constructors under lockdep.
