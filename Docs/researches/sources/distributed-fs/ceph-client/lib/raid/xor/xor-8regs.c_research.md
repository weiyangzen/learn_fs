# sources/distributed-fs/ceph-client/lib/raid/xor/xor-8regs.c

Purpose: simplest generic scalar XOR template.

Important APIs and flow: `xor_8regs_{2,3,4,5}` process eight `long` words per iteration and directly apply `p1[i] ^= p2[i] ...`. `DO_XOR_BLOCKS()` emits `xor_gen_8regs()` unless `NO_TEMPLATE` is defined; ARM NEON reuses the helper bodies with `NO_TEMPLATE`.

State and persistence: no persistence; destination is updated in place.

Dependencies and integration: exported as `xor_block_8regs` for generic fallback and architecture calibration.

Risks and test signals: low complexity, but public contract still requires aligned buffers and 512-byte-multiple lengths. Signals include KUnit, boot calibration, and use as fallback when architecture SIMD is disabled.
