<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/perf.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/perf.c

Purpose: Provides a Win32 test workload for OSI mutex sleep/wakeup performance and correctness by ping-ponging two threads through a shared flag.

Important APIs, types, and functions: `main_perfMutex` protects `flags`, `count`, and `done`. `main_Perf1` waits for `STARTA`, hands off to `STARTB`, increments count, sleeps on `flags`, and exits after `main_NITERS`. `main_Perf2` mirrors that for `STARTB` to `STARTA`. `main_PerfTest` initializes OSI, display, mutex, two threads, waits for `done == 2` with `osi_SleepM`, finalizes the mutex, closes handles, and returns status.

Control flow and state: The test starts with `STARTA`. Each worker obtains the mutex, waits if its flag is not set, toggles flags, wakes sleepers on `flags`, increments count, and then sleeps atomically with releasing the mutex. Completion wakes the main test waiting on `done`.

Persistence and dependencies: No persistence. Depends on Win32 threads, `main.h` display helpers, `perf.h`, and OSI lock/sleep APIs.

Integration points: Invoked from the client OSI test GUI/menu to stress synchronization.

Risks: Uses old implicit `int` declarations (`static done`, `main_PerfTest`). If `CreateThread` for the second thread fails, the first thread handle is not closed and the first thread may continue. The loop breaks while still holding the mutex, then increments `done` and releases, which is intentional but easy to misread.

Test signals: Confirm no deadlocks, count reaches expected threshold, both threads finish, display remains responsive, and repeated runs do not leak handles or leave stale mutex state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/perf.c -->
