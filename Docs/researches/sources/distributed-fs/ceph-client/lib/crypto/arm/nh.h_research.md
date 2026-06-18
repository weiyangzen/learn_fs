# sources/distributed-fs/ceph-client/lib/crypto/arm/nh.h

## Purpose
This ARM32 header connects the NEON NH assembly implementation to the common NH library. It opportunistically accelerates only workloads large enough to benefit.

## Important APIs, Types, And Functions
It declares `nh_neon`, defines `have_neon`, implements `nh_arch`, and defines `nh_mod_init_arch`. `nh_arch` returns a boolean indicating whether the architecture path handled the request.

## Control Flow
Initialization enables `have_neon` when `HWCAP_NEON` is present. `nh_arch` checks `have_neon`, `message_len >= 64`, and `may_use_simd()`. If true, it enters `scoped_ksimd()`, calls `nh_neon`, stores the digest words, and returns true; otherwise it returns false so generic code handles the hash.

## State And Persistence
Only the static key persists. Key, message, and hash buffers are caller-owned and not retained.

## Dependencies And Integration Points
It includes ARM NEON/SIMD headers and relies on common NH constants such as `NH_NUM_PASSES`. It integrates with the generic NH implementation through the `nh_arch` hook.

## Risks And Edge Cases
The size threshold avoids overhead for small inputs; changing it can affect performance but not correctness if the assembly supports the sizes. SIMD context gating and static-branch initialization are the main safety risks.

## Test Signals
Compare generic and NEON outputs for boundary lengths, especially 0, short, 64, and multi-stride messages. Build tests should cover ARM32 without NEON and with `CONFIG_KERNEL_MODE_NEON`.
