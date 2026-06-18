# sources/distributed-fs/ceph-client/lib/crypto/s390/gf128hash.h

## Purpose

This s390 architecture header accelerates GHASH through CPACF while retaining the generic GF(2^128) fallback. It was read as a complete 54-line file.

## Important APIs, Types, and Functions

It defines `have_cpacf_ghash`, `ghash_preparekey_arch`, `ghash_blocks_arch`, and `gf128hash_mod_init_arch`. The key preparation stores both POLYVAL-convention key material for fallback and raw GHASH key material for CPACF.

## Control Flow

Key preparation always fills both representations. `ghash_blocks_arch` checks the static key; the accelerated path converts the accumulator from POLYVAL to GHASH convention, builds the CPACF context buffer with accumulator and key, calls `cpacf_kimd(CPACF_KIMD_GHASH)`, converts the accumulator back, and zeroizes the temporary context. Otherwise it calls `ghash_blocks_generic`.

## State and Persistence Behavior

The static key persists after init. Prepared GHASH keys persist in caller-owned key structs in two representations. The CPACF context buffer is local and explicitly zeroized.

## Dependencies and Integration Points

It depends on CPACF, s390 CPU feature probing, and generic GF128 conversion helpers. It integrates with GHASH and POLYVAL library code.

## Risks and Edge Cases

The main risks are representation conversion mistakes, failure to zero temporary key material, CPACF feature misquery, and keeping raw key storage synchronized with generic key storage.

## Test Signals

GHASH and POLYVAL KUnit vectors, all-ones guarded-key tests in the broader test suite, CPACF-enabled s390 runs, and forced generic fallback comparison validate behavior.
