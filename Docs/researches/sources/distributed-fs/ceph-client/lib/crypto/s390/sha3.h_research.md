# sources/distributed-fs/ceph-client/lib/crypto/s390/sha3.h

## Purpose

This s390 header accelerates SHA-3 absorb, Keccak permutation, and one-shot SHA3 hashing through CPACF. It was read as a complete 151-line file.

## Important APIs, Types, and Functions

It defines static keys `have_sha3` and `have_sha3_init_optim`, overrides `sha3_absorb_blocks`, `sha3_keccakf`, and one-shot functions `sha3_224_arch`, `sha3_256_arch`, `sha3_384_arch`, and `sha3_512_arch`. Helper `s390_sha3` uses `cpacf_klmd`.

## Control Flow

Block absorb dispatches by SHA3 block size to the corresponding KIMD function, with SHA3-256 also covering SHAKE256's block size. `sha3_keccakf` invokes KIMD SHA3-512 with a zero block to obtain a plain permutation when accelerated. One-shot hashing uses KLMD and optionally sets `CPACF_KLMD_NIP | CPACF_KLMD_DUFOP` when facility 86 allows optimized initialization. Init checks all required KIMD and KLMD SHA3 functions and enables acceleration only if the complete set is present.

## State and Persistence Behavior

Static keys persist after init. One-shot helper state is stack-local and zeroized. Streaming state remains in caller-owned `sha3_state`.

## Dependencies and Integration Points

It integrates with `sha3.c` via architecture hook macros and depends on CPACF, KMSAN unpoisoning for optimized output, and generic SHA3 fallbacks.

## Risks and Edge Cases

Risks include treating SHA3 facilities as all-or-nothing, block-size dispatch confusion with SHAKE, KMSAN state marking, and ensuring zero-input KIMD semantics really match Keccak-f.

## Test Signals

SHA3 and SHAKE KUnit vectors, NIST SHAKE vectors, all-length squeeze tests, FIPS SHA3-256 self-test, and CPACF fallback comparison validate behavior.
