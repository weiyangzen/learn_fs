# sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-mmx.c

Purpose: implements legacy x86 MMX XOR templates for Pentium II and Pentium-style scheduling.

Important APIs and flow: `xor_pII_mmx_{2,3,4,5}` process 128-byte chunks with macro-expanded `movq` and `pxor`. `xor_p5_mmx_{2,3,4,5}` process 64-byte chunks with a different instruction schedule. Both sets use `DO_XOR_BLOCKS()` and wrappers `xor_gen_pII_mmx()` and `xor_gen_p5_mmx()` inside `kernel_fpu_begin/end`.

State and persistence: no durable state; MMX/FPU state is temporarily owned and destination memory is mutated.

Dependencies and integration: registered by `x86/xor_arch.h` only when MMX exists and SSE/AVX choices are unavailable.

Risks and test signals: risks include old inline assembly constraints, operand-register limits, and FPU state cleanup. Signals include x86 32-bit build coverage, KUnit XOR tests on legacy configs, and boot calibration output.
