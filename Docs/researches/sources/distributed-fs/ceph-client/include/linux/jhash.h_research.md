# sources/distributed-fs/ceph-client/include/linux/jhash.h

## Purpose
Provides Linux inline wrappers for Bob Jenkins lookup3-style 32-bit non-cryptographic hashes. It is intended for hash table indexing of bytes or 32-bit words where speed and avalanche behavior matter more than adversarial security.

## Important APIs, Types, And Functions
`jhash_size()` and `jhash_mask()` support power-of-two hash table sizing. `jhash()` hashes arbitrary byte sequences using unaligned 32-bit loads and byte tail handling. `jhash2()` hashes arrays of `u32`. `jhash_1word()`, `jhash_2words()`, and `jhash_3words()` handle fixed word counts. Internal macros `__jhash_mix()` and `__jhash_final()` implement reversible mixing and final avalanche with `rol32()`.

## Control Flow
The byte hash initializes three accumulators from `JHASH_INITVAL`, length, and caller seed, then mixes 12-byte chunks until the tail. A fallthrough switch folds the final 0 to 12 bytes before final mixing. The word hash follows the same pattern over groups of three words.

## State And Persistence
No state is retained. Hash stability depends on input bytes, length, seed, word order, and architecture endianness for the generic byte path.

## Dependencies And Integration Points
Depends on `linux/bitops.h` for rotates and `linux/unaligned.h` for unaligned loads. It integrates broadly with kernel hash tables, network code, and filesystem caches that need deterministic seeded 32-bit hashes.

## Risks
This is not a cryptographic or hash-flooding-resistant function. `jhash()` results are endian-dependent. Callers using `jhash_mask()` must ensure the table size is a power of two. Seeds should be chosen carefully for exposed hash tables.

## Test Signals
Tests should verify known vectors per architecture, tail lengths 0 through 12, unaligned inputs, fixed-word helpers matching equivalent `jhash2()` inputs, and distribution across power-of-two masks.
