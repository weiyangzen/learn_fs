# sources/distributed-fs/ceph-client/net/netfilter/nft_numgen.c

Purpose: implements nftables `numgen` expression variants for incremental and random bounded number generation.

Important APIs/types/functions: `struct nft_ng_inc` stores destination register, modulus, heap-allocated atomic counter, and offset. `nft_ng_inc_gen()` advances the counter with `atomic_cmpxchg()` and wraps at modulus. `struct nft_ng_random` stores destination register, modulus, and offset; `nft_ng_random_gen()` uses `get_random_u32()` and `reciprocal_scale()`. `nft_ng_select_ops()` dispatches by `NFTA_NG_TYPE`.

Control flow: select_ops requires dreg, modulus, and type. Incremental init parses optional offset, validates nonzero modulus and offset overflow, allocates the counter, initializes it to `modulus - 1` so first generated value is offset, and validates register store. Random init validates the same modulus/offset constraints and destination register but allocates no state. Eval writes the generated u32 to the destination register. Dump emits dreg, modulus, type, and offset.

State/persistence: incremental state is the shared atomic counter per expression; random has no mutable state. Dependencies include kernel random APIs, atomic operations, reciprocal scaling, and nf_tables register parsing. Risks include counter allocation failure, modulo distribution expectations, offset overflow, first-value semantics, and concurrent wrap behavior. Test signals: incremental sequence starting at offset, wrap at modulus, concurrent packet increments without duplicates beyond modulo cycle, random value range, invalid zero modulus/overflow rejection, dump/restore, and type dispatch errors.
