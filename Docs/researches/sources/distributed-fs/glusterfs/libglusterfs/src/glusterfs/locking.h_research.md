# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/locking.h

Purpose: `locking.h` centralizes GlusterFS mutex naming and Darwin spinlock compatibility. It gives the rest of libglusterfs a stable `gf_lock_t` alias and `LOCK_*` macros over pthread mutex calls.

Important APIs and types: `gf_lock_t` is `pthread_mutex_t`. `LOCK_INIT`, `LOCK`, `TRY_LOCK`, `UNLOCK`, and `LOCK_DESTROY` map directly to pthread calls. On Darwin, `pthread_spinlock_t` and spinlock operations are mapped to `OSSpinLock` primitives.

Control flow and state: the header has no runtime control flow besides macro expansion. All state is owned by the lock objects embedded in structures such as call stacks, rbthash buckets, memory pools, rotating buffers, and token buckets.

Dependencies and integration: every subsystem that uses `gf_lock_t` depends on this stable wrapper. `mem-pool.h`, `rbthash.h`, `rot-buffs.h`, and `stack.h` include it either directly or transitively.

Risks: the macros expose raw pthread return values only if callers inspect them; many call sites ignore failures. The Darwin `OSSpinLock` mapping is legacy and has priority-inversion concerns on modern Darwin systems. There is no debug ownership tracking at this layer.

Test signals: concurrency tests should focus on higher-level users. Portability builds should compile on Linux and Darwin paths. Static analysis should flag unbalanced `LOCK`/`UNLOCK` and destroyed-while-held patterns.
