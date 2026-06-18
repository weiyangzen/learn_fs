# sources/distributed-fs/ceph-client/lib/crypto/blake2b.c

## Purpose
Generic BLAKE2b hash and PRF implementation with optional architecture compression override.

## Important APIs, Types, And Functions
Key functions are `blake2b_update()`, `blake2b_final()`, `blake2b_compress_generic()`, `blake2b_increment_counter()`, and `blake2b_set_lastblock()`. It exports update and final symbols and includes `blake2b.h` for an arch `blake2b_compress` when configured.

## Control Flow
The compression loop increments the 128-bit byte counter, loads a 128-byte block as little-endian words, initializes the 16-word work vector from chaining state, IV, counters, and finalization flags, runs 12 BLAKE2b rounds using the sigma table, and XORs results into `ctx->h`. Update buffers partial data, compresses complete non-final blocks, and leaves the last block buffered. Final marks the last block, pads with zeroes, compresses with the actual byte count, writes little-endian output, and zeroes the context.

## State, Persistence, And Dependencies
State is in `struct blake2b_ctx`: chaining words, counters, flags, output length, buffer, and buffer length. No filesystem persistence exists. It depends on kernel endian helpers, `unrolled_full`, module exports, and optional arch compression.

## Integration Points
Provides exported crypto-lib BLAKE2b streaming primitives used by in-kernel keyed hashing and PRF callers. Optional `blake2b_mod_init_arch()` is invoked at subsys init if an arch header defines it.

## Risks
Finalization consumes and zeroes the context, so callers must not reuse it. Multi-block compression requires `inc == BLAKE2B_BLOCK_SIZE`; debug warns on misuse. Output length must have been initialized correctly by the caller.

## Test Signals
BLAKE2b known-answer vectors, keyed and unkeyed PRF cases, empty input, one-block and multi-block messages, variable digest sizes, and generic-vs-arch comparisons validate this file.
