# sources/distributed-fs/openafs/src/WINNT/pthread/test/tsd.c

## Purpose

`tsd.c` is a focused regression test for pthread thread-specific data in the OpenAFS Windows pthread layer. It verifies that each thread can store and retrieve a different value under the same key without cross-thread leakage.

## Important APIs, Types, and Functions

- Uses `pthread_key_t key`, `pthread_key_create()`, `pthread_setspecific()`, `pthread_getspecific()`, `pthread_create()`, and `pthread_join()`.
- `destruct(void *val)` is an empty destructor supplied to `pthread_key_create()`.
- `threadFunc(void *arg)` stores its argument in the global key and asserts the same pointer is returned by `pthread_getspecific()`.
- `main()` creates the key, starts `NTH` threads with distinct small integer values cast to `void *`, and joins every thread.

## Control Flow

The test creates one global key with `destruct`, starts ten worker threads, and passes each thread its loop index as the thread argument. Each worker sets that argument as key-specific data and immediately reads it back. The main thread joins all workers and returns zero if every API call succeeded and every assertion held.

## State and Persistence

State is entirely in-process: one pthread key and per-thread key values. The destructor does not mutate state and there is no persistent output.

## Dependencies and Integration Points

This file is a unit-style consumer of the OpenAFS Windows pthread compatibility API. It includes OpenAFS platform headers but does not call OpenAFS filesystem APIs.

## Risks and Edge Cases

- The loop index is cast directly to `void *`; this is common in small C tests but can trigger portability warnings and does not exercise pointer lifetime.
- The test does not call `pthread_key_delete()` and does not verify destructor invocation at thread exit.
- Because each thread sets and gets immediately, it validates key isolation but not long-lived TSD behavior across deeper call stacks.

## Test Signals

Passing behavior is silent exit zero. Assertion failures identify key creation, thread creation/join, or TSD isolation regressions.
