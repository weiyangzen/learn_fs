# sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor_arch.h

Purpose: defines arm64 XOR algorithm registration.

Important APIs and flow: `arch_xor_init()` registers generic `8regs` and `32regs`; if `cpu_has_neon()` is true, it registers `xor_block_eor3` when the named SHA3 feature is present, otherwise `xor_block_neon`.

State and persistence: only init-time registration state in the XOR core.

Dependencies and integration: depends on `<asm/simd.h>` and arm64 CPU feature helpers. It is included by `xor-core.c` under `CONFIG_XOR_BLOCKS_ARCH`.

Risks and test signals: choosing EOR3 skips registering plain NEON, so SHA3 detection must be reliable. Signals include boot template logs and KUnit XOR validation on arm64 hardware variants.
