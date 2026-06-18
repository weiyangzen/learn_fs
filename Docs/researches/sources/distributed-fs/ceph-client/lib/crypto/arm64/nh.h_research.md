# sources/distributed-fs/ceph-client/lib/crypto/arm64/nh.h

## Purpose
This header connects the ARM64 ASIMD NH implementation to the generic NH library.

## Important APIs, Types, And Functions
It declares `nh_neon`, defines `have_neon`, implements `nh_arch`, and defines `nh_mod_init_arch`.

## Control Flow
Init enables `have_neon` when `cpu_have_named_feature(ASIMD)` is true. `nh_arch` checks `have_neon`, `message_len >= 64`, and `may_use_simd()`, then calls `nh_neon` inside `scoped_ksimd()` and returns true. Otherwise it returns false for generic processing.

## State And Persistence
Only the feature static key persists. The key, message, and hash buffers are caller-owned.

## Dependencies And Integration Points
It depends on ARM64 hwcap/SIMD and cpufeature helpers plus common NH constants and types. It is the arch hook consumed by generic NH code.

## Risks And Edge Cases
The threshold and SIMD gating determine when assembly is used. Incorrect feature detection would cause illegal instructions or missed acceleration. Short inputs must continue to use the generic path.

## Test Signals
Generic-vs-ASIMD NH comparisons, lengths below/at/above 64 bytes, CPU feature masking, and builds on non-ASIMD configurations validate this header.
