<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/spinlock.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/spinlock.h

## Purpose
`spinlock.h` maps kernel spinlock APIs to POSIX mutexes for tools.

## APIs And Flow
It typedefs `spinlock_t` and `arch_spinlock_t` to `pthread_mutex_t`, defines initializers, and maps `spin_lock*`, `spin_unlock*`, IRQ-save, bottom-half, nested, and arch lock helpers to pthread mutex operations. `arch_spin_is_locked()` always returns true.

## State, Dependencies, Risks, Tests
State is the pthread mutex object. Dependencies are `<pthread.h>` and `<stdbool.h>`. Risks are semantic mismatch with real spinlocks: operations can sleep, IRQ and bottom-half state is ignored, saved flags are unused, lockdep subclassing is absent, and `arch_spin_is_locked()` is not a real query. Tests should exercise initialization, lock/unlock, contention, IRQ-save macro compilation, and deadlock behavior expected by tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/spinlock.h -->
