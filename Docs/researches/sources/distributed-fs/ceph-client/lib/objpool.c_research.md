# sources/distributed-fs/ceph-client/lib/objpool.c

## Purpose
Provides initialization and teardown for the lockless object pool abstraction, allocating per-CPU ring slots with prebuilt objects for fast MPMC/FIFO pool operations defined by the public objpool API.

## APIs, Control Flow, and State
Exports `objpool_init()`, `objpool_free()`, `objpool_drop()`, and `objpool_fini()`. Init validates object count and size, aligns object size, rounds capacity to a power of two, allocates a CPU-slot pointer array, and distributes objects across possible CPUs. Each `objpool_slot` stores ring entries plus contiguous object storage; optional `objinit()` initializes each object. Allocation prefers `__vmalloc_node()` when not constrained to atomic GFP, falls back to `kmalloc_node()`, and keeps data node-local. Pool state includes capacity, object size, possible CPU count, refcount, context, release callback, and slot pointers. Finish drains remaining objects with `objpool_pop()`, decrements the pool ref, and frees slots when the last object is dropped.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/objpool.h`, vmalloc/slab allocation, atomics/refcounting, CPU masks, and log2 helpers. Risks include partial allocation failure cleanup, callback failure after some objects were initialized, capacity overflow, misuse after `objpool_fini()`, and delayed pool freeing until all checked-out objects call `objpool_drop()`. Test signals include init/fini under GFP variants, CPU distribution checks, object init failure injection, pop/push/drop lifecycle tests, and KASAN/KMSAN coverage for slot/object layout.
