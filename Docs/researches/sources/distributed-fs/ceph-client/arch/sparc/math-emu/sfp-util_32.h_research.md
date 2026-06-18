# sources/distributed-fs/ceph-client/arch/sparc/math-emu/sfp-util_32.h

Purpose: SPARC32 machine-dependent support macros for the generic Linux soft-fp package.

Important APIs/types/macros: `add_ssaaaa` and `sub_ddmmss` implement double-word add/subtract with carry/borrow. `umul_ppmm` expands to a `%y`/`mulscc` 32x32-to-64 multiply. `udiv_qrnnd` expands to a 32-iteration quotient/remainder division loop. `UDIV_NEEDS_NORMALIZATION` is `0`, `abort()` maps to `return 0`, and `__BYTE_ORDER` is set from kernel endian macros.

Control flow: all behavior is macro-expanded into soft-fp callers. Arithmetic macros use inline assembly and condition codes; `abort()` returns failure from the containing emulation function.

State and persistence: no standalone state. Expanded code uses `%g1`, `%g2`, `%y`, condition codes, and local C variables. It can alter control flow of callers through `return 0`.

Dependencies/integration: includes kernel/sched/types and `asm/byteorder.h`. Consumed by `math_32.c` and generic `math-emu` headers, especially multiplication/division-heavy soft-fp operations.

Risks: inline asm constraints and clobbers must match GCC expectations. `%y` scheduling comments are important on SPARC; moving delay instructions can break multiplication. `abort()` being a return macro couples this header to functions returning integer success/failure.

Test signals: compile soft-fp with multiple GCC versions and run FP emulation arithmetic that exercises add/sub/mul/div internals, especially quad division. Static build checks should catch asm constraint regressions.
