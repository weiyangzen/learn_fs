<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rwsem.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/rwsem.h

## Purpose
`rwsem.h` maps kernel read/write semaphore APIs onto POSIX read/write locks for tools.

## APIs And Flow
It defines `struct rw_semaphore` containing `pthread_rwlock_t` and inline helpers `init_rwsem()`, `exit_rwsem()`, `down_read()`, `up_read()`, `down_write()`, `up_write()`, plus nested variants mapped to the same operations. Flow delegates directly to pthread rwlock init, destroy, read lock, write lock, and unlock.

## State, Dependencies, Risks, Tests
State is the pthread rwlock object. Dependency is `<pthread.h>`. Risks include different fairness and signal behavior from kernel rwsems, ignored lockdep subclass arguments, and required destruction ordering. Tests should cover parallel readers, writer exclusion, init/destroy errors, nested macro compile paths, and tools linked with pthreads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rwsem.h -->
