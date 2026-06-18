## sources/distributed-fs/openafs/src/lwp/lock.c

Purpose: Implements the wait and wake slow paths for `struct Lock` declared in `afs_lock.h`.

Important APIs and functions: `Lock_Init`, `Lock_Destroy`, `Afs_Lock_Obtain`, `Afs_Lock_WakeupR`, `Afs_Lock_ReleaseR`, `Afs_Lock_ReleaseW`, and non-pthread atomic wait helpers `LWP_WaitProcessR`, `LWP_WaitProcessW`, and `LWP_WaitProcessS`.

Control flow: `Afs_Lock_Obtain` handles four modes. Read waits while a write lock is present, write waits while any exclusive or reader state exists, shared waits while any exclusive lock exists, and boosted waits while readers remain. In pthread builds it waits on read or write condition variables under the caller-held mutex. In LWP builds it waits on event addresses. Release helpers choose whether to wake readers or exclusive waiters, with `ReleaseR` preferring readers and `ReleaseW` preferring exclusive lockers.

State and persistence: Mutates only the supplied `struct Lock`.

Dependencies and integration: Bridges `afs_lock.h` macros to pthread opr condition variables or LWP wait/signal calls. Used by userspace OpenAFS code that needs kernel-style lock semantics outside the kernel.

Risks: Wait-state bits are coarse, so broadcasts can wake more waiters than can proceed. Fairness depends on which release helper is used. Non-pthread atomic wait helpers are only atomic because LWP is cooperative, not because a real mutex is held. Caller misuse of lock mode can corrupt state.

Test signals: All obtain/release modes under contention, pthread and LWP builds, boost with active readers, wake preference differences, no-block macro compatibility, and lock destroy after waiters drain.
