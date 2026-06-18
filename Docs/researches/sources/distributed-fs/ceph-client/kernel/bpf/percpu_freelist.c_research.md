# sources/distributed-fs/ceph-client/kernel/bpf/percpu_freelist.c

Purpose: implements a simple per-CPU freelist used by BPF maps for preallocated elements. It provides IRQ-safe public push/pop wrappers and lower-level variants for callers that already disabled IRQs. The source was read as a complete 137-line file.

Important APIs/functions: `pcpu_freelist_init`, `pcpu_freelist_destroy`, `pcpu_freelist_push`, `pcpu_freelist_pop`, `__pcpu_freelist_push`, `__pcpu_freelist_pop`, and `pcpu_freelist_populate`. Internal helpers manipulate `struct pcpu_freelist_head` and `struct pcpu_freelist_node`.

Control flow: initialization allocates one head per possible CPU, initializes resilient spinlocks, and clears heads. Populate distributes a buffer of fixed-size elements across CPU heads without locking before publication. Push first tries the current CPU list; if locking fails, it scans other possible CPUs until it can insert. Pop scans from the current CPU across possible CPUs, skips empty heads, and removes the first node from a lock it can acquire. Public wrappers disable/restore local IRQs around the lower-level operations.

State and persistence: freelist state is held in per-CPU `first` pointers protected by `rqspinlock_t`. Nodes are embedded in caller-owned preallocated elements and persist until popped or the freelist is destroyed.

Dependencies/integration: uses percpu allocation, `for_each_possible_cpu`, `for_each_cpu_wrap`, `raw_res_spin_lock`, and local IRQ control. It is included by prealloc map implementations that need low-overhead allocation without general kmalloc.

Risks and edge cases: `__pcpu_freelist_push` spins forever until some CPU list lock is acquired, so resilient spinlock behavior matters. Pop can return NULL when all lists are empty or locks are contended. Public and double-underscore variants have different IRQ preconditions. Populate assumes the buffer is not yet concurrently visible.

Test signals: preallocated hash/array map stress tests, empty/full freelist behavior, IRQ-disabled caller coverage, CPU hotplug-like possible CPU configurations, and lockdep/resilient-spinlock diagnostics.
