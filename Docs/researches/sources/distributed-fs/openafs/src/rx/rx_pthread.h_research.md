# sources/distributed-fs/openafs/src/rx/rx_pthread.h

## Purpose
Defines pthread-backed lock and condition-variable primitives for thread-safe user-mode RX builds.

## Important APIs, Types, And Functions
The header enables `RX_ENABLE_LOCKS`, includes `pthread_nosigs.h`, `opr.h`, and `opr/lock.h`, typedefs `afs_kmutex_t` and `afs_kcondvar_t` to pthread types, maps `pthread_yield` to platform equivalents, and defines `MUTEX_*`/`CV_*` macros onto OPR lock wrappers.

## Control Flow
There is no runtime flow in the header. Implementation files use the macros to initialize, enter, exit, wait, signal, and broadcast synchronization primitives.

## State And Persistence
No state is stored. The types it defines are embedded in RX globals, peers, calls, and server queue entries.

## Dependencies And Integration Points
This is included by pthread RX user-mode code and any header needing RX lock types. On Windows it includes WinSock/WinBase and pthread headers; on Unix it includes pthreads and platform yield alternatives.

## Risks And Test Signals
Risks are macro compatibility across platforms and assumptions that `opr_*` wrappers match pthread semantics. Build coverage on Windows, Solaris, AIX, and common Unix pthread builds plus condition-variable stress tests are useful signals.
