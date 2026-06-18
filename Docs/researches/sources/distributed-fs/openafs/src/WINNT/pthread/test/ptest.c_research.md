# sources/distributed-fs/openafs/src/WINNT/pthread/test/ptest.c

## Purpose

`ptest.c` is a no-output-on-success regression test for the OpenAFS Windows pthread compatibility layer. It exercises thread creation/join, thread identity, one-time initialization, mutex locking and trylocking, condition wait/signal/broadcast, timed condition waits, object destruction, and explicit invalid-argument paths. It is intended to fail through `assert()` if the NT pthread implementation diverges from the expected API contract.

## Important APIs, Types, and Functions

- Uses OpenAFS platform headers `afs/param.h` and `afs/stds.h`, the Win32 `Sleep()` call, and pthread types/functions from `pthread.h`.
- Global synchronization state includes `pthread_once_t once_c`, counters `should_be_one`, `should_be_NTH`, `should_be_NTH_minus_1`, mutexes `g_mutex`, `try_mutex`, `cond_mutex`, and condition variable `g_cond`.
- `once_me()` is the `pthread_once` initializer. It increments `should_be_one` and initializes the mutex and condition objects that later tests rely on.
- `threadFunc()` verifies `pthread_equal(*me, pthread_self())`, runs `pthread_once`, increments a shared count under `g_mutex`, then tests `pthread_mutex_trylock()` contention by letting one thread hold `try_mutex` during `Sleep(SLEEP_TIME)`.
- `condWaitFunc()`, `condSignalFunc()`, `condBroadcastFunc()`, and `condTimeWaitFunc()` exercise condition-variable wakeup and timeout behavior.
- `main()` is the test orchestrator and contains the final invalid-argument assertions.

## Control Flow

The first phase creates `NTH` threads, each receiving a pointer to its `pthread_t` slot. All threads call `pthread_once`; only one should run `once_me()`. Every thread increments `should_be_NTH` under `g_mutex`; one thread should acquire `try_mutex` and sleep, while the other nine increment `should_be_NTH_minus_1`. The main thread joins all workers, destroys `g_mutex`, and validates the counters.

The second phase verifies condition variables. One waiter blocks until a signaler sleeps and sets `cond_flag`, then signals. A broadcast run resets `cond_flag`, starts `NTH - 1` waiters and one broadcaster, and joins all threads. A timed-wait run resets `cond_flag`, starts one waiter using an absolute timeout of `time(NULL) + COND_WAIT_TIME`, expects `ETIME`, and checks elapsed wall-clock time.

The final phase destroys the remaining synchronization objects and calls pthread APIs with null pointers or invalid attribute pointers, asserting that each returns a nonzero error instead of succeeding.

## State and Persistence

All state is process-local. The test depends on zero-initialized static globals and modifies only counters, mutexes, condition variables, and the `cond_flag`. It does not persist files, registry keys, or logs. Timing state comes from `time()` and Win32 `Sleep()`.

## Dependencies and Integration Points

The file integrates with the OpenAFS Windows pthread library and intentionally includes OpenAFS standard headers before libc/pthread headers. It assumes the pthread implementation maps timed condition wait failure to `ETIME` and supports Win32-style sleeping. It is a test binary rather than a library module.

## Risks and Edge Cases

- The trylock test is timing-sensitive: it assumes all non-owning threads reach `pthread_mutex_trylock()` while one thread still holds `try_mutex` for two seconds.
- `condSignalFunc()` and `condBroadcastFunc()` write `cond_flag` without holding `cond_mutex`, which can hide or introduce condition-variable ordering races in stricter implementations.
- Timed wait uses wall-clock seconds and allows a one-second tolerance, so clock changes or slow scheduling can affect the elapsed check.
- The invalid attribute tests pass literal pointer value `4`; that is useful for validation but is intentionally unsafe outside a test process.

## Test Signals

Successful execution emits no diagnostic text and exits zero. Any pthread behavior mismatch terminates through `assert()`. The strongest signals are the final counter checks, successful condition joins, `ETIME` from timed wait, and nonzero error returns for null/invalid arguments.
