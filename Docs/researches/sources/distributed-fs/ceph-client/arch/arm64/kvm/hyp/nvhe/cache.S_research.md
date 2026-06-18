# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/cache.S

## Purpose

This assembly file provides position-independent nVHE cache maintenance helpers copied from arm64 MM code.

## Important APIs, Types, And Functions

Symbols are `__pi_dcache_clean_inval_poc` with alias `dcache_clean_inval_poc`, and `__pi_icache_inval_pou` with alias `icache_inval_pou`.

## Control Flow

The data-cache helper runs a clean+invalidate by line to PoC and returns. The I-cache helper returns after an ISB when DIC makes explicit invalidation unnecessary; otherwise it invalidates I-cache by line to PoU.

## State And Persistence Behavior

It affects CPU caches for caller-provided address ranges and has no persistent variables.

## Dependencies And Integration Points

It is used by nVHE mapping/setup code that needs cache coherency without normal kernel helpers.

## Risks And Test Signals

Risks are wrong range arguments, missing barriers, and incorrect DIC alternative behavior. Test signals are self-modifying/vector mapping paths and pKVM code/data mapping coherency.
