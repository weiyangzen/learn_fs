## sources/distributed-fs/ceph-client/lib/sbitmap.c

Purpose: scalable bitmap and waitqueue-backed bitmap queue implementation used for efficient tag/resource allocation, especially where per-CPU hints and batched wakeups reduce contention.

Important APIs/functions: bitmap APIs include `sbitmap_init_node()`, `sbitmap_resize()`, `sbitmap_get()`, `sbitmap_any_bit_set()`, `sbitmap_weight()`, and seq display helpers. Queue APIs include `sbitmap_queue_init_node()`, `sbitmap_queue_resize()`, `__sbitmap_queue_get()`, `__sbitmap_queue_get_batch()`, `sbitmap_queue_get_shallow()`, `sbitmap_queue_clear[_batch]()`, wake helpers, and waitqueue add/prepare/finish helpers.

Control flow: initialization computes bits-per-word, allocates words and optional per-CPU hints, and initializes swap locks. Allocation reads a CPU hint, searches for a zero bit in the target word, moves deferred clears into the visible word if needed, and updates the hint. Shallow allocation scales per-word depth to enforce class limits. Queue clear operations publish deferred or direct clears with memory barriers, update CPU hints, and wake waiters in batches across rotating waitqueue buckets.

State and persistence: `struct sbitmap` owns depth, shift, map words, deferred-clear masks, locks, round-robin flag, and per-CPU hints. `struct sbitmap_queue` adds wait states, wake counters, wake batch, active waiter count, completion counters, and shallow-depth limits.

Dependencies/integration: depends on random hints, percpu allocation, atomics/bitops, raw spinlocks, waitqueues, memory barriers, and seq_file.

Risks/test signals: memory ordering around clear/reallocation and waitqueue wakeups is subtle. Batch allocation has assumptions about non-round-robin maps. Seq output (`sbitmap_show`, `sbitmap_queue_show`, bitmap dump) provides operational diagnostics.
