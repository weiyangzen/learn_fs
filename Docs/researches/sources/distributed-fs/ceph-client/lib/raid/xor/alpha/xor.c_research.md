# sources/distributed-fs/ceph-client/lib/raid/xor/alpha/xor.c

Purpose: provides Alpha EV5/EV6 hand-scheduled RAID XOR implementations for the generic XOR dispatch framework. It exports two templates, `xor_block_alpha` and `xor_block_alpha_prefetch`, wrapping assembly entry points for 2 through 5 operands.

Important APIs and flow: external assembly symbols `xor_alpha_{2,3,4,5}` and `xor_alpha_prefetch_{2,3,4,5}` process 64-byte chunks with Alpha `ldq`, `xor`, and `stq` instructions. `DO_XOR_BLOCKS()` builds `xor_gen_alpha()` and `xor_gen_alpha_prefetch()` so the core can feed arbitrary source counts in groups of up to four source buffers.

State and persistence: no durable state; only in-place mutation of the destination parity buffer. Template speed is later filled by XOR calibration unless Alpha architecture code forces a template.

Dependencies and integration: depends on `xor_impl.h` for template shape and wrapper generation, and on `alpha/xor_arch.h` for registration policy. It integrates with `xor-core.c` through `struct xor_block_template`.

Risks and test signals: risks are assembly ABI register assumptions, 64-byte alignment, and read-past/write-past mistakes in unrolled loops. Signals include `CONFIG_XOR_KUNIT_TEST`, boot-time XOR speed logs, Alpha EV6 selection of prefetch code, and RAID5 parity checks under large aligned buffers.
