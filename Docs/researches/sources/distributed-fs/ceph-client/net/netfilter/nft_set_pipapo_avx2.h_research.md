
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.h -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.h

## Purpose

`nft_set_pipapo_avx2.h` is the architecture gate and public declaration header for the PIPAPO AVX2 implementation.

## Important APIs, Types, and Functions

When building for x86-64 outside UML, it includes xstate definitions, sets `NFT_PIPAPO_ALIGN` to the YMM save-area size in bytes, forward-declares `struct nft_pipapo_match`, and declares `nft_pipapo_avx2_estimate()` and `pipapo_get_avx2()`.

## Control Flow

The header has no runtime control flow. Its compile-time condition controls whether generic PIPAPO sees AVX2 alignment requirements and whether AVX2 declarations are available.

## State and Persistence Behavior

No state is stored here. The alignment macro affects allocation layout for lookup tables and scratch maps in the generic implementation.

## Dependencies and Integration Points

It integrates with `nft_set_pipapo.c`, `nft_set_pipapo_avx2.c`, x86 `xstate.h`, and nf_tables set estimation. Non-x86 or UML builds compile without declarations and use generic PIPAPO only.

## Risks and Test Signals

Risks are compile-time: wrong architecture gating, missing alignment propagation, or declaration drift from the C implementation. Test x86-64 AVX2 builds, UML builds, non-x86 builds, and object files with and without `CONFIG_X86_64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo_avx2.h -->
