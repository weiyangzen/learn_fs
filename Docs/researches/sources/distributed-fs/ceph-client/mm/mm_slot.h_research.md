# sources/distributed-fs/ceph-client/mm/mm_slot.h

## Purpose
Provides a small shared helper abstraction for subsystems that keep per-`mm_struct` records in both a hash table and an ordered/list structure. It defines the common `struct mm_slot`, allocation/free wrappers, and hash lookup/insert macros used by MM features that need to associate metadata with an address space.

## Important APIs, Types, and Functions
`struct mm_slot` contains `hash` for a hash bucket, `mm_node` for a list, and `mm` pointing to the address space the slot describes. `mm_slot_entry()` wraps `container_of()` so embedding subsystems can recover their larger object. `mm_slot_alloc()` allocates zeroed cache objects with `kmem_cache_zalloc(GFP_KERNEL)` and returns `NULL` if cache initialization failed. `mm_slot_free()` frees objects through the same slab cache. `mm_slot_lookup()` and `mm_slot_insert()` are statement-expression macros over Linux hash-table helpers.

## Control Flow
There is no standalone runtime flow. Callers allocate an embedding object from a subsystem slab cache, initialize or embed `struct mm_slot`, insert it with `mm_slot_insert()`, later find it with `mm_slot_lookup()`, and free it with `mm_slot_free()`. Lookup hashes the `mm_struct *` value and linearly scans the selected bucket for pointer equality.

## State and Persistence Behavior
The header owns no global state. Persistent state lives in caller-owned hash tables, lists, and slab caches. `mm_slot_insert()` writes the slot's `mm` pointer before adding it to the supplied hash table. The macros perform no locking or lifetime management, so callers must protect hash/list access and ensure the referenced `mm_struct` remains valid for the slot lifetime.

## Dependencies and Integration Points
The header depends on `<linux/hashtable.h>` and `<linux/slab.h>`. It is a utility interface for MM subsystems such as KSM-style or scanner-style code that need efficient lookup from `mm_struct` to subsystem metadata while also iterating all slots through a list.

## Risks and Edge Cases
The main risks are caller-side: missing external locking, stale `mm` pointers after address-space teardown, inserting duplicate slots for one `mm`, freeing through the wrong cache, and relying on `mm_slot_alloc()` without handling a `NULL` cache or allocation failure. Because the hash key is the raw pointer cast to `unsigned long`, correctness assumes stable `mm_struct` addresses during slot lifetime.

## Test Signals
Compile coverage for embedding users is the primary signal. Runtime tests should exercise insertion, duplicate prevention at the caller layer, lookup miss and hit paths, teardown ordering during process exit, slab allocation failure handling, and lockdep coverage around whatever subsystem lock protects the hash table and list.
