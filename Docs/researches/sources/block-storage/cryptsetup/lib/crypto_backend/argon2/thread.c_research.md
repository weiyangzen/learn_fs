# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/thread.c

## Purpose
Minimal cross-platform thread wrapper for Argon2 memory filling.

## Key Content
When threading is enabled, implements `argon2_thread_create()` and `argon2_thread_join()` using `_beginthreadex`/`WaitForSingleObject`/`CloseHandle` on Windows and `pthread_create`/`pthread_join` elsewhere.

## Dependencies and Coupling
Included by `core.c` multithreaded fill path via `thread.h`.

## Invariants and Risks
No abstraction beyond create/join is provided. Threading can be compiled out with `ARGON2_NO_THREADS`.
