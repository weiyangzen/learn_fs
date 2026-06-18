# sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor_arch.h

Purpose: defines ARM XOR template registration policy.

Important APIs and flow: declares `xor_block_arm4regs`, `xor_block_neon`, and `xor_gen_neon_inner()`. `arch_xor_init()` always registers ARM scalar `arm4regs` and generic `8regs`/`32regs`; with kernel-mode NEON and `cpu_has_neon()`, it also registers `xor_block_neon`.

State and persistence: registration feeds the core's init-only template list; no other persistence.

Dependencies and integration: depends on `<asm/neon.h>` and is included by `xor-core.c` for ARM builds with architecture XOR blocks.

Risks and test signals: CPU feature detection and SIMD gating determine whether NEON participates in calibration. Signals are boot XOR measurement output, KUnit, and NEON build/config combinations.
