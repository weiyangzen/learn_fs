# sources/distributed-fs/openafs/src/WINNT/pthread/pthread.h

## Purpose
Declares the Windows pthread compatibility subset implemented by `pthread.c`.

## Important APIs, Types, And Functions
Defines `pthread_once_t`, `pthread_attr_t`, `pthread_condattr_t`, `pthread_mutexattr_t`, `pthread_rwlockattr_t`, `pthread_key_t`, `pthread_t`, `timespec_t`, mutex/condition/rwlock structs, `PTHREAD_CREATE_JOINABLE`, `PTHREAD_CREATE_DETACHED`, `PTHREAD_KEYS_MAX`, and `PTHREAD_ONCE_INIT`. Declares all supported pthread-like functions.

## Control Flow
No executable flow. Static initialization is represented by simple integer fields, enabling `pthread_once()` to work without a Win32 initializer.

## State And Persistence
The public structs expose implementation details: mutexes contain owner TID and `CRITICAL_SECTION`, conditions contain a waiter queue, and rwlocks compose shim mutex/condition objects.

## Dependencies And Integration Points
Includes Windows, time, OpenAFS NT errno mapping, and `rx_queue`. Any OpenAFS code including this header receives the shim definitions rather than system pthreads.

## Risks
Public struct layout couples consumers to this implementation and prevents ABI compatibility with real pthread libraries. `pthread_t` is `void *` to internal `thread_t`, which tests exploit by walking queue internals. `PTHREAD_KEYS_MAX` is fixed at 32.

## Test Signals
Compile OpenAFS Windows targets using pthread APIs, plus ABI/layout assumptions in native tests and TSD tests.
