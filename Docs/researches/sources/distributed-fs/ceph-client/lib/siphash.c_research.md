# sources/distributed-fs/ceph-client/lib/siphash.c

## Purpose
Implements SipHash2-4 for keyed 64-bit pseudorandom hashing and HalfSipHash1-3 or SipHash1-3-derived 32-bit hashing for hash table use. These functions protect kernel hash tables and short keyed identifiers from collision attacks when callers use secret per-boot keys.

## APIs, Control Flow, and State
Exports include `__siphash_aligned()`, `__siphash_unaligned()`, `siphash_1u64()` through `siphash_4u64()`, `siphash_1u32()`, `siphash_3u32()`, `__hsiphash_aligned()`, `__hsiphash_unaligned()`, and `hsiphash_1u32()` through `hsiphash_4u32()`. Macros set up SipHash state from constants, xor the key, process full little-endian words with SipHash rounds, pack the tail bytes into the length-tagged final word, and run finalization rounds. Aligned variants are omitted on architectures with efficient unaligned access; unaligned variants use `get_unaligned_le*()`. On 64-bit, HalfSipHash uses the SipHash word engine for performance; on 32-bit, a native 32-bit HalfSipHash engine is used.

The file owns no persistent state. Security depends on caller-owned `siphash_key_t` or `hsiphash_key_t` lifetime and secrecy.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/siphash.h`, unaligned access helpers, endian conversion, and optional dcache word-at-a-time tail loading. Integration points include dcache, networking, hashtables, randomization-sensitive maps, and identifiers that need keyed hashing. Risks include using HalfSipHash where a secure PRF is required, reusing non-secret or predictable keys, endian/tail packing regressions, unaligned reads crossing inaccessible memory when architecture assumptions are wrong, and inconsistent 32-bit versus 64-bit expectations. Test signals include SipHash reference vectors, aligned/unaligned equivalence tests, tail-length coverage from 0 to 7 or 0 to 3 bytes, cross-endian builds, and collision-resistance stress on keyed hash tables.
