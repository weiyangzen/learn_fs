
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.c

## Purpose

`nft_set_pipapo_avx2.c` provides x86-64 AVX2 vectorized lookup routines for the PIPAPO set backend. It accelerates bucket intersection and refill loops for common field widths while preserving the same mapping-table semantics as the generic implementation.

## Important APIs, Types, and Functions

Public functions are `nft_pipapo_avx2_estimate()`, `pipapo_get_avx2()`, and `nft_pipapo_avx2_lookup()`. Internal helpers include AVX2 load/AND/store/test macros, `nft_pipapo_avx2_refill()`, specialized lookup bodies for 4-bit and 8-bit grouping with 1, 2, 4, 6, 8, 12, 16, or 32 groups, and `nft_pipapo_avx2_lookup_slow()` for uncommon sizes.

## Control Flow

Datapath lookup disables BH, verifies FPU usability, RCU-dereferences active match data, and calls `pipapo_get_avx2()` or falls back to generic lookup. `pipapo_get_avx2()` locks the per-CPU scratch map, starts kernel FPU usage with a minimal mask, clears a YMM zero register, runs one specialized field function per field, and maps/refills results until it reaches a final element. Expired or inactive final elements are skipped by continuing refill on the remaining result bitmap.

## State and Persistence Behavior

The implementation uses the same `nft_pipapo_match`, field tables, mapping tables, and per-CPU scratch maps as generic PIPAPO. It does not own persistent state, but it depends on lookup tables being aligned to `NFT_PIPAPO_ALIGN` and bucket sizes being multiples of YMM-width longs.

## Dependencies and Integration Points

Dependencies include x86 FPU APIs, AVX2 CPU feature checks, inline assembly, `nft_set_pipapo.h`, and nf_tables set lookup contracts. Backend selection is exposed through `nft_set_pipapo_avx2_type` in the generic file when the architecture supports it.

## Risks and Test Signals

Risks include FPU use in invalid contexts, missing `kernel_fpu_end()` on error paths, alignment or bucket-size assumptions, inline assembly clobber mistakes, and divergence from generic semantics for expired/inactive elements. Test AVX2-capable and non-AVX2 systems, `irq_fpu_usable()` fallback paths, common IPv4/IPv6/port/MAC concatenations, timeout expiry during lookup, and comparison against generic backend results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.c -->
