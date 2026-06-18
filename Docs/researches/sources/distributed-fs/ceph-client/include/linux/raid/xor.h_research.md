# sources/distributed-fs/ceph-client/include/linux/raid/xor.h

Purpose: declares the generic XOR generation entry point used by RAID parity code.

Important APIs and types: `xor_gen(void *dest, void **srcs, unsigned int src_cnt, unsigned int bytes)` XORs `src_cnt` source buffers into `dest` for `bytes` bytes.

Control flow: RAID code calls `xor_gen()` to build or update parity from data stripes; implementation selection lives outside this header.

State and persistence: no state is kept here. The output buffer contributes to persistent RAID parity only after higher layers write it.

Dependencies and integration points: integrates MD RAID parity paths with architecture-optimized XOR implementations.

Risks and test signals: risks include overlapping buffers, zero/one source edge cases, unaligned lengths, and optimized implementation mismatch. Test parity generation against a scalar reference, varied source counts, unaligned buffer/length combinations, and degraded RAID rebuilds.
