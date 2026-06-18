# sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor-neon.c

Purpose: builds the ARM NEON inner XOR implementation by compiling the generic `xor-8regs.c` loop with vectorization enabled.

Important APIs and flow: requires `__ARM_NEON__` and, for GCC, enables `tree-vectorize`. It defines `NO_TEMPLATE`, includes `../xor-8regs.c` to reuse `xor_8regs_{2,3,4,5}`, then emits `xor_gen_neon_inner()` through `__DO_XOR_BLOCKS()`.

State and persistence: no persistent state; it mutates `dest` in place according to `srcs`.

Dependencies and integration: depends on NEON compiler flags from the build system, `xor_impl.h` wrapper macros, and the glue file that performs `kernel_neon_begin/end`.

Risks and test signals: correctness depends on compiler vectorization preserving the scalar XOR semantics and respecting alignment/length assumptions. Signals include compiler build failures when flags are missing, KUnit randomized XOR tests, and inspection of generated NEON code in architecture builds.
