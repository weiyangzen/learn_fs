
# sources/distributed-fs/ceph-client/include/linux/objpool.h

Purpose: defines a fixed-capacity, preallocated, lockless-ish per-CPU object pool optimized for contexts where allocation is prohibited or expensive, such as probes and interrupt/thread mixed consumers.

Important APIs/types/functions: `struct objpool_slot` is a per-CPU ring with `head`, `tail`, `last`, mask, and object entries. `struct objpool_head` stores object size/count, CPU count, per-slot capacity, GFP flags, refcount, flags, slot array, release callback, and caller context. `objpool_init()` allocates and initializes objects. `objpool_pop()` disables local IRQs and scans per-CPU slots for an object. `objpool_push()` returns an object to the current CPU slot. `objpool_drop()`, `objpool_free()`, and `objpool_fini()` handle asynchronous teardown. Internal helpers use acquire/release loads, stores, and cmpxchg on ring indexes.

Control flow: callers initialize a pool with a fixed number of objects and optional per-object init callback. Allocation pops from the local CPU slot first, then other possible CPUs. Reclamation pushes to the current CPU slot and publishes via `last`. Teardown releases unused objects and waits for outstanding objects to be dropped in asynchronous use cases.

State and persistence: all state is in-memory preallocated object and ring metadata. Capacity is fixed after initialization. The pool may outlive `objpool_fini()` until outstanding borrowed objects call `objpool_drop()`.

Dependencies and integration points: depends on refcounts, atomics, cpumasks, IRQ flag helpers, SMP CPU iteration, memory barriers, and GFP allocation. It integrates with kretprobe/rethook-style users that need safe object reuse from constrained contexts.

Risks and test signals: risks include double-push or wrong-object push corrupting rings, wraparound assumptions, insufficient barriers causing stale entries, teardown while `objpool_push()` is in flight, and memory overhead from per-CPU rings. Test signals include `test_objpool`, high-concurrency push/pop stress, IRQ/thread mixed use, CPU hotplug/possible CPU configurations, asynchronous outstanding-object teardown, and KCSAN/KASAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objpool.h -->
