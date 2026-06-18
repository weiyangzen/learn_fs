# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/core.c

## Purpose
Argon2 core engine: memory allocation/wiping, input validation, initial hashing, first-block generation, memory-fill scheduling, reference-index calculation, and final tag generation.

## Key Content
Implements block copy/xor/load/store helpers, allocator hooks, secure wipe fallbacks, global internal-memory clearing, `finalize()`, `index_alpha()`, single-threaded and multithreaded memory filling, full input validation, `initial_hash()`, `fill_first_blocks()`, and `initialize()`. Multithreaded fill launches lane workers per slice and enforces a thread limit.

## Dependencies and Coupling
Uses `core.h`, `thread.h`, BLAKE2b, and BLAKE2 endian helpers. The actual segment compression function is supplied by either `ref.c` or `opt.c`.

## Invariants and Risks
Memory cost is rounded down to equal lane/slice segments after enforcing the minimum. Custom allocators must be provided as a matching allocate/free pair. Sensitive memory is wiped when `FLAG_clear_internal_memory` is enabled, which defaults to true.
