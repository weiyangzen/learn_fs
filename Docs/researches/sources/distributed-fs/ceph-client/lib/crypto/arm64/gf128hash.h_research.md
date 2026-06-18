# sources/distributed-fs/ceph-client/lib/crypto/arm64/gf128hash.h

## Purpose
This ARM64 header provides architecture hooks for GHASH and POLYVAL using ASIMD and PMULL acceleration, with generic fallbacks.

## Important APIs, Types, And Functions
It defines `NUM_H_POWERS`, static keys `have_asimd` and `have_pmull`, declares `pmull_ghash_update_p8`, `polyval_mul_pmull`, and `polyval_blocks_pmull`, and implements `polyval_preparekey_arch`, `polyval_mul_arm64`, `ghash_mul_arch`, `polyval_mul_arch`, `ghash_blocks_arch`, `polyval_blocks_arch`, and `gf128hash_mod_init_arch`.

## Control Flow
Initialization enables ASIMD and optionally PMULL. POLYVAL key preparation stores the raw key as the highest power and computes descending powers with PMULL or generic multiplication. Single multiply uses PMULL when available; with ASIMD but no PMULL it reuses the GHASH p8 routine on a zero block for equivalent POLYVAL multiplication. Block GHASH uses p8 ASIMD; block POLYVAL uses PMULL or generic fallback.

## State And Persistence
Feature static keys persist. `struct polyval_key` stores precomputed powers in caller-owned key memory; accumulators are updated in place.

## Dependencies And Integration Points
It depends on ARM64 cpufeature/SIMD APIs and common GF128 hash types. It integrates `ghash-neon-core.S` and POLYVAL PMULL core routines with generic GHASH/POLYVAL users such as AES-GCM and AES-GCM-SIV.

## Risks And Edge Cases
The equivalence trick for POLYVAL via GHASH p8 relies on format and zero-byte-swap assumptions. Key power order must match `polyval_blocks_pmull`. SIMD context and feature gating must distinguish ASIMD-only from PMULL-capable systems.

## Test Signals
GHASH, POLYVAL, AES-GCM, and AES-GCM-SIV vectors; PMULL and no-PMULL ASIMD feature testing; key precompute comparisons; and randomized generic-vs-arch tests validate this header.
