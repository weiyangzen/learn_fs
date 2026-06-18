# sources/distributed-fs/ceph-client/arch/mips/lib/multi3.c

Purpose: supplies `__multi3` for GCC 9 and older on 64-bit MIPS R6 when the compiler may emit suboptimal 128-bit multiply helper calls.

Important APIs/functions: conditional exported `__multi3`, with inline `dmulu` and `dmuhu` wrappers.

Control flow: splits operands into high/low 64-bit halves with `TWunion`, computes low product, high product, and cross terms, and returns the low 128 bits.

State and persistence: stateless.

Dependencies and integration: depends on `libgcc.h`, MIPS R6 `dmulu/dmuhu`, 64-bit mode, and GCC version guard.

Risks: conditional compilation must match compiler behavior. Endian union layout and signedness of low/high operations must remain correct.

Test signals: 128-bit multiplication tests on MIPS64R6 GCC < 10 and symbol absence on unsupported configs.
