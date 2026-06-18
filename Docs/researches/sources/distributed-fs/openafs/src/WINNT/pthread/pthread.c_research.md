# sources/distributed-fs/openafs/src/WINNT/pthread/pthread.c

## Purpose
Implements a deliberately limited POSIX pthread compatibility layer for Windows NT, intended to support OpenAFS code without being a complete pthread implementation.

## Important APIs, Types, And Functions
Implements `pthread_once`, mutex, read/write lock, condition variable, thread create/join/self/equal/exit, attributes, and thread-specific data APIs declared in `pthread.h`. Internal `thread_t` records active threads, join state, Win32 handles/IDs, native-thread marker, and per-thread TSD. Waiter and thread structures are cached in `rx_queue` lists.

## Control Flow
`pthread_once()` uses `InterlockedExchange()` and sleep polling. Mutexes wrap `CRITICAL_SECTION` while rejecting recursive self-locks with `EDEADLK`. RW locks combine write/read mutexes and a condition variable. `pthread_create()` allocates a `thread_t`, adds it to `active_Q`, then starts a Win32 thread running `afs_pthread_create_stub()`. The stub initializes TLS, calls the user routine, catches the custom `pthread_exit` exception, runs TSD destructors, then either signals joiners or caches detached thread state. `pthread_self()` creates pseudo-pthread records for native Win32 threads and starts a watcher thread that removes those records when native handles terminate. Condition variables maintain a queue of per-waiter events and convert absolute POSIX waits to relative Win32 waits.

## State And Persistence
All state is process-local: active/cache queues, waiter cache, TLS indexes, key table/destructors, watcher thread/event/list, and initialization once-controls. `DllMain()` initializes caches on attach and cleans waiter/TSD/thread caches on detach.

## Dependencies And Integration Points
Depends on Win32 synchronization/threading/TLS APIs, MSVC structured exception handling, `rx_queue`, C runtime allocation/time, and OpenAFS Windows build macros. Tests in `pthread/test` exercise key behavior.

## Risks
The file explicitly diverges from full POSIX. Busy waiting in `pthread_once`, non-robust native-thread watcher, named event creation with static counters, incomplete cond-destroy waiter validation, and manual cache cleanup are sensitive. `pthread_rwlock_unlock()` infers write ownership by expecting `pthread_mutex_trylock()` to return `EDEADLK`, which depends on this shim’s mutex semantics. `pthread_exit()` on a native thread raises an unhandled exception by design. `WaitForMultipleObjects()` has maximum handle limits not checked here.

## Test Signals
Existing tests include general pthread behavior, TSD, and native-thread interaction. Additional signals should cover recursive mutex errors, timed waits including timeout race paths, detached/joinable cleanup, native thread TSD destructor cleanup, RW lock contention, DLL detach cleanup, and handle-count limits.
