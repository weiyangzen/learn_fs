# sources/distributed-fs/ceph-client/lib/raid/xor/xor-32regs.c

Purpose: generic scalar XOR template optimized around explicit register temporaries.

Important APIs and flow: `xor_32regs_{2,3,4,5}` process eight `long` values per iteration. They load destination words into locals, XOR source words according to operand count, store back, and advance pointers. `DO_XOR_BLOCKS()` builds `xor_gen_32regs()`.

State and persistence: no persistent state; destination is mutated.

Dependencies and integration: core generic template exported as `xor_block_32regs` for fallback and calibration.

Risks and test signals: assumes byte counts are suitable for eight-`long` loop granularity, which is satisfied by the public `xor_gen()` contract. Signals include KUnit randomized length/source tests and boot calibration.
