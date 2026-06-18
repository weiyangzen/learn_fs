# sources/compression/lz4/lib/xxhash.c

## Purpose
`xxhash.c` implements xxHash 0.6.5 for LZ4: fast non-cryptographic 32-bit and 64-bit hashes, streaming hash state, and canonical big-endian encodings.

## Important APIs, Types, And Functions
The exported functions are `XXH_versionNumber`, `XXH32`, `XXH32_createState`, `XXH32_freeState`, `XXH32_copyState`, `XXH32_reset`, `XXH32_update`, `XXH32_digest`, `XXH32_canonicalFromHash`, `XXH32_hashFromCanonical`, and equivalent `XXH64*` functions when 64-bit support is enabled. Internal primitives include endian-aware reads, rotate/swap helpers, prime constants, per-lane rounds, merge rounds, and final avalanche functions.

## Control Flow
One-shot hashing selects aligned or unaligned paths, normalizes endian behavior unless native format is forced, processes 16-byte chunks for XXH32 or 32-byte chunks for XXH64, then finalizes tail bytes with switch fallthrough. Streaming reset initializes accumulators from the seed, update buffers partial chunks in `mem32` or `mem64`, and digest finalizes without consuming state.

## State, Persistence, And Dependencies
`XXH32_state_t` tracks total length, large-length marker, four accumulators, a 16-byte scratch buffer, and `memsize`. `XXH64_state_t` tracks total length, four 64-bit accumulators, a 32-byte scratch buffer, and `memsize`. There is no persistent storage. Allocation and memory copy are wrapped locally around `malloc`, `free`, and `memcpy`.

## Integration Points
The CLI benchmark uses `XXH64` for data-integrity checks. Fuzz helpers use `XXH32` to seed deterministic random choices. The OSS-Fuzz Makefile namespaces symbols with `-DXXH_NAMESPACE=LZ4_` to avoid collisions.

## Risks
Compile-time switches can permit non-standard unaligned reads. By default, null input is an error for streaming update and unsafe for one-shot calls unless `XXH_ACCEPT_NULL_INPUT_POINTER` is enabled. These hashes are not cryptographic and should not be used for adversarial integrity or authentication.

## Test Signals
Important signals are known xxHash vectors, streaming versus one-shot equivalence, chunk-boundary updates around 16 and 32 bytes, canonical round trips, big-endian behavior, namespaced builds, and sanitizer builds with `XXH_FORCE_MEMORY_ACCESS=0`.
