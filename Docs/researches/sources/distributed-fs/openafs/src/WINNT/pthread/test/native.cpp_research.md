# sources/distributed-fs/openafs/src/WINNT/pthread/test/native.cpp

## Purpose
Native Win32 interoperability test for the pthread shim.

## Important APIs, Types, And Functions
Defines three tests run by `main()`: `Test1()` checks `pthread_self()` on the main thread, `Test2()` checks a Win32 thread joining a pthread-created thread and receiving its return value, and `Test3()` checks that native Win32 threads registered through `pthread_self()` are removed from the active queue after termination.

## Control Flow
`Test2` creates a Win32 waiter thread and a pthread worker thread, coordinates with a shared DWORD, then verifies `pthread_join()`. `Test3` records initial active queue size using a helper pthread that walks the internal queue representation, starts two Win32 threads and two detached pthreads, advances a shared signal so each exits in order, and checks active queue size decreases after each termination.

## State And Persistence
Test state is process-local shared counters/handles. It intentionally inspects internal `pthread_t`/`rx_queue` layout, making it a white-box test of `pthread.c`.

## Dependencies And Integration Points
Depends on Win32 `CreateThread`, `WaitForSingleObject`, `InterlockedIncrement`, the pthread shim, `rx_queue`, and C++ exception handling around queue walking.

## Risks
Busy-wait loops and fixed `Sleep()` delays can be timing-sensitive on slow or highly loaded hosts. It casts pointers through DWORD-sized values, which is unsafe for 64-bit builds. White-box queue traversal couples the test to internal layout rather than public API.

## Test Signals
Passing output for all three tests indicates main/native thread registration, cross-API join, detached pthread cleanup, and native-thread watcher cleanup are working for 32-bit Windows assumptions.
