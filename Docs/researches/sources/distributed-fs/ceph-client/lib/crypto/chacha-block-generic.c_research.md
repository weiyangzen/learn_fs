# sources/distributed-fs/ceph-client/lib/crypto/chacha-block-generic.c

## Purpose
Generic ChaCha core permutation and HChaCha block functions.

## Important APIs, Types, And Functions
Defines internal `chacha_permute()` and exports `chacha_block_generic()` plus `hchacha_block_generic()`. It operates on `struct chacha_state` and constants from `<crypto/chacha.h>`.

## Control Flow
`chacha_permute()` validates that the round count is 20 or 12, then runs alternating column and diagonal quarter rounds in two-round increments. `chacha_block_generic()` copies input state, permutes it, adds the original state, writes 64 little-endian keystream bytes, increments counter word 12, and wipes the temporary state. `hchacha_block_generic()` permutes without feed-forward addition and outputs words 0-3 and 12-15 for XChaCha subkey derivation.

## State, Persistence, And Dependencies
The caller's ChaCha state is mutated only by the stream block counter increment. Temporary state is zeroized. Dependencies include bit rotation, unaligned little-endian stores, export symbols, and crypto headers.

## Integration Points
Used by `chacha.c` as the generic backend and by XChaCha initialization in `chacha20poly1305.c`.

## Risks
Counter overflow behavior is only word-12 increment here; higher-level nonce/counter policy must prevent keystream reuse. HChaCha output must not be used as normal stream keystream. Round count warning does not prevent execution if invalid in non-fatal debug configurations.

## Test Signals
RFC ChaCha20 and HChaCha/XChaCha vectors, 12-round test cases if supported, counter increment tests, and generic-vs-arch comparisons verify behavior.
