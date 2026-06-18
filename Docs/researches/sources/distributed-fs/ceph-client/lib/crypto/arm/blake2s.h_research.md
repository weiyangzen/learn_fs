# sources/distributed-fs/ceph-client/lib/crypto/arm/blake2s.h

## Purpose
This minimal ARM header declares the architecture-provided BLAKE2s compression routine.

## Important APIs, Types, and Functions
It declares `void blake2s_compress(struct blake2s_ctx *ctx, const u8 *block, size_t nblocks, u32 inc);`.

## Control Flow
There is no code flow; the declaration causes generic BLAKE2s code to bind to the ARM assembly implementation when selected.

## State and Persistence
No state is defined here.

## Dependencies and Integration Points
It depends on the generic BLAKE2s context type being visible to the including translation unit and matches `arm/blake2s-core.S`.

## Risks and Test Signals
Risks are declaration/signature drift. Build/link tests and BLAKE2s known-answer tests are the signals.
