## sources/distributed-fs/ceph-client/mm/kasan/quarantine.c

Purpose: implements Generic KASAN's quarantine for freed slab objects, delaying reuse so use-after-free accesses remain detectable.

Important APIs and data: public hooks are `kasan_quarantine_put()`, `kasan_quarantine_reduce()`, and `kasan_quarantine_remove_cache()`. Internal structures include `qlist_head`, per-CPU `cpu_quarantine`, global round-robin quarantine batches, `quarantine_lock`, SRCU domain `remove_cache_srcu`, per-CPU `shrink_qlist`, and CPU hotplug callbacks.

Control flow: freed objects with valid free metadata are appended to a per-CPU queue with IRQs disabled. When a per-CPU queue exceeds `QUARANTINE_PERCPU_SIZE`, it moves into the global batch ring under lock and advances the tail when a batch reaches target size. Reduction recomputes max size from total RAM and online CPUs, removes the oldest global batch if over budget, and frees objects outside the lock. Cache removal first drains per-CPU queues on all CPUs, scans global batches for matching cache objects, frees them, and waits for SRCU readers so concurrent reductions cannot miss objects.

State and persistence: state is in per-CPU and global linked lists of `kasan_free_meta.quarantine_link`, global byte counters, batch indices, offline flags, and size limits. It is runtime-only.

Dependencies and integration: integrates with Generic KASAN free metadata, slab `___cache_free()`, CPU hotplug, SRCU, raw spinlocks, local IRQ control, total RAM accounting, and cache shutdown/shrink hooks.

Risks and test signals: risks include missing objects during cache teardown, IRQ races with per-CPU queues, quarantine memory growth, wrong object-to-cache reconstruction, and init-on-free metadata leakage. Tests should stress UAF detection before reuse, cache destruction with quarantined objects, CPU hotplug, memory pressure reduction, and init-on-free configurations.
