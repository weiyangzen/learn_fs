<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/core.c -->
# sources/distributed-fs/ceph-client/kernel/futex/core.c

Purpose: provides futex keying, hashing, queue primitives, robust-list exit cleanup, PI-state exit cleanup, per-mm private futex hash management, fault-injection hooks, and global futex hash initialization. It is the substrate used by all futex wait, wake, PI, requeue, and syscall layers.

Important APIs/types/functions: central functions are `get_futex_key()`, `futex_hash()`, `futex_setup_timer()`, `fault_in_user_writeable()`, `futex_top_waiter()`, `futex_q_lock()`, `futex_queue()`, `futex_unqueue()`, `futex_unqueue_pi()`, `futex_exec_release()`, `futex_exit_release()`, `futex_exit_recursive()`, `futex_mm_init()`, `futex_hash_free()`, `futex_hash_allocate_default()`, `futex_hash_prctl()`, and `futex_init()`. Internal structures include the global NUMA-sharded bucket array and optional `struct futex_private_hash`.

Control flow: futex operations first call `get_futex_key()` to validate alignment/access and translate user addresses into either private `(mm,address,node)` keys or shared inode/page-offset keys. `futex_hash()` maps keys to per-mm private buckets when enabled or to global NUMA buckets otherwise. Queue helpers increment waiter counters before locking, enqueue priority-sorted `futex_q` entries, and unqueue safely under RCU because `q->lock_ptr` can change during requeue. Exit paths call `futex_cleanup_begin()`, walk robust lists, repair owner-died futex words, clean PI state lists, and publish `FUTEX_STATE_DEAD` or reset to OK for exec.

State and persistence behavior: state is runtime-only: hash buckets, waiter counts, plist queues, futex keys, per-task robust-list pointers, per-task PI-state lists, and optional per-mm private hash tables. Private hash replacement uses RCU, per-cpu-to-atomic ref transitions, `mm->futex_hash_lock`, and `mmput_async()` to protect old hashes until no futex operation can reference them.

Dependencies and integration points: integrates with `mm_struct` initialization/free in `fork.c`, user memory access/GUP, shmem/inode mapping, mempolicy/NUMA node hints, rtmutex PI state, robust-list syscalls, task exit/exec, `prctl(PR_FUTEX_HASH_*)`, debugfs fault injection, and the exported helpers in `futex.h`.

Risks: incorrect key generation can alias unrelated futexes or split waiters for the same futex. Shared mapping races with truncation, swapcache movement, COW, and inode reuse are sensitive. Queue waiter barriers must preserve the no-lost-wakeup guarantee. Robust-list traversal is user-controlled and must avoid loops and bad pointers. Private hash resizing risks stale bucket pointers, missed wakeups, refcount underflow, and mm lifetime bugs.

Test signals: futex selftests for private/shared mappings, shmem/file-backed futexes, robust mutex owner death, PI owner exit, private-hash prctl resizing, NUMA/MPOL futex2 keys, fault injection, module-free builds with/without MMU, lockdep/sparse annotations, and stress tests combining clone, exit, exec, and requeue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/core.c -->
