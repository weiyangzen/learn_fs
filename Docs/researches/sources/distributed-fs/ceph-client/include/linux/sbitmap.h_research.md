# sources/distributed-fs/ceph-client/include/linux/sbitmap.h

Purpose: declares the scalable bitmap and bitmap-queue interfaces used by high-concurrency allocators, especially block multiqueue tag maps, where a single cacheline bitmap would become a contention point.

Important APIs and types: `struct sbitmap_word`, `struct sbitmap`, `struct sbitmap_queue`, `struct sbq_wait_state`, and `struct sbq_wait` define the bitmap, deferred-clear mask, per-CPU allocation hints, wait queues, and waiter accounting. Core APIs include `sbitmap_init_node()`, `sbitmap_resize()`, `sbitmap_get()`, `sbitmap_put()`, `sbitmap_weight()`, debug show helpers, `sbitmap_queue_init_node()`, `__sbitmap_queue_get()`, batch/shallow allocation helpers, `sbitmap_queue_clear()`, wake helpers, and wait-queue wrappers.

Control flow: allocation searches set bits across cacheline-separated words using per-CPU hints unless strict round-robin is requested. Freeing uses `cleared` masks first, then deferred clear/swap logic in the implementation returns bits to `word`; queue users sleep on rotating wait queues and are woken in batches after completions.

State and persistence: all state is in-memory and lifetime-bound to the initialized bitmap or queue. Persistent behavior is limited to counters and hints that affect allocation locality, fairness, and wake batching.

Dependencies and integration points: depends on bitops, atomics, percpu storage, raw spinlocks, wait queues, and seq_file debug output. It integrates with block-layer tag allocation and any subsystem needing scalable bounded-resource IDs.

Risks and test signals: risks include missed wakeups when shallow depth is not registered, stale per-CPU hints after resize, memory-ordering regressions around successful acquire allocation, deferred-clear races, and starvation with round-robin changes. Test with concurrent get/put stress, queue exhaustion/wakeup tests, resize tests, shallow-depth coverage, CPU hotplug/preemption scenarios, and debugfs bitmap output sanity.
