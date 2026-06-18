# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha256-ce.S

## Purpose
ARMv8 Crypto Extensions SHA-224/SHA-256 transform plus a two-buffer SHA-256 finalization fast path.

## Important APIs, Types, And Functions
Exports `sha256_ce_transform` and `sha256_ce_finup2x`. Uses `.Lsha2_rcon`, `load_round_constants`, `add_only`, `add_update`, `do_4rounds_2x`, and `do_16rounds_2x`. Assumes `struct __sha256_ctx` offsets for `state`, `bytecount`, and `buf`.

## Control Flow
`sha256_ce_transform()` loads round constants and state, loops over 64-byte blocks, byte-swaps input words, runs SHA256 CE rounds with schedule updates, adds chaining state, and stores state. `sha256_ce_finup2x()` clones an initial context into two states, folds any buffered bytes, interleaves rounds for two equal-length message tails, constructs padding and count blocks, then byte-swaps and stores both digests.

## State, Persistence, And Dependencies
The block transform mutates caller state. The finup path reads an immutable context and writes two digest buffers. It depends on ARM SHA2 instructions, vector registers, and exact C struct layout verified by `sha256.h`.

## Integration Points
Selected by `sha256.h` when SHA2 CE is available. The two-buffer finup hook accelerates callers that finalize two same-length SHA-256 streams from the same base context.

## Risks
`sha256_ce_finup2x()` has tight preconditions: `len >= SHA256_BLOCK_SIZE`, `len <= INT_MAX`, equal tail lengths, and accessible 64-byte reads for padding construction. Offset drift in `struct __sha256_ctx` would be severe, hence the header assertions. The stack scratch area and final-step state machine are high-risk for boundary lengths 56, 64, and buffered contexts.

## Test Signals
Generic-vs-CE comparison, SHA256 and SHA224 vectors, two-way finup tests for buffered and unbuffered contexts, lengths around 56/63/64/65 bytes, and KMSAN output initialization checks are important.
