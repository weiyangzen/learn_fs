# sources/distributed-fs/ceph-client/lib/raid/xor/xor-8regs-prefetch.c

Purpose: generic scalar XOR template using direct memory XORs plus prefetch.

Important APIs and flow: `xor_8regs_p_{2,3,4,5}` process eight `long` words per line, prefetch destination/source pointers one line ahead, and use a `once_more` label to process the final line after the prefetch loop. `DO_XOR_BLOCKS()` exposes `xor_gen_8regs_p()`.

State and persistence: no persistence; in-place destination mutation.

Dependencies and integration: depends on `linux/prefetch.h` and is registered as `xor_block_8regs_p`.

Risks and test signals: risks are tail-loop correctness and prefetch safety at page ends. KUnit guard-page tests and boot speed calibration are the main signals.
