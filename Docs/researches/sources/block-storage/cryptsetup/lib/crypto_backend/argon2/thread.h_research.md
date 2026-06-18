# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/thread.h

## Purpose
Thread abstraction header for Argon2.

## Key Content
Defines platform-specific thread function and handle types, and declares `argon2_thread_create()` and `argon2_thread_join()` when `ARGON2_NO_THREADS` is not set. Uses Win32 process/thread APIs on Windows and pthreads otherwise.

## Dependencies and Coupling
Consumed by `core.c` and implemented by `thread.c`.

## Invariants and Risks
The API intentionally only supports creation and joining. Callers own scheduling and error handling.
