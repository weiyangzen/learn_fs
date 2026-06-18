# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd_glue.c

Purpose: publishes LoongArch LSX and LASX raw SIMD routines as safe XOR templates.

Important APIs and flow: `MAKE_XOR_GLUES(flavor)` emits an inner grouped-source generator, a public `xor_gen_flavor()` wrapper around `kernel_fpu_begin()` and `kernel_fpu_end()`, and a `struct xor_block_template`. Enabled flavors are controlled by `CONFIG_CPU_HAS_LSX` and `CONFIG_CPU_HAS_LASX`.

State and persistence: no durable state; it protects CPU FPU/vector state while mutating parity buffers.

Dependencies and integration: depends on `<asm/fpu.h>`, `xor_simd.h`, and the LoongArch registration header.

Risks and test signals: missing FPU bracketing would corrupt task state. Signals include preemption-sensitive stress tests, KUnit XOR coverage, and boot logs measuring `lsx` or `lasx`.
