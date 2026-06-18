# sources/distributed-fs/ceph-client/arch/sparc/lib/muldi3.S

Purpose: GCC runtime helper `__muldi3` for 64-bit integer multiplication on 32-bit SPARC-style register pairs. It is based on GNU CC support code and exported for kernel/module users that need compiler-emitted long-long multiplication support.

Important APIs/functions: `__muldi3` accepts high/low halves in the SPARC calling convention and returns a 64-bit product in `%i0/%i1` after `restore`. `EXPORT_SYMBOL(__muldi3)` exposes it.

Control flow: the routine uses `save`, writes one operand low word into `%y`, performs a 32-step `mulscc` multiply sequence to compute the low-half partial product, reads `%y`, computes cross terms with `umul`, adds them into the high result, then returns high/low halves.

State and persistence: no persistent state. It uses `%y`, local registers, integer condition codes, and the stack frame created by `save`.

Dependencies/integration: includes `linux/export.h`. Integrated as a libgcc replacement for builds where the compiler emits `__muldi3` instead of inline multiply sequences.

Risks: register-pair ABI must match compiler expectations exactly. The `%y` write/read delay and fixed `mulscc` sequence are SPARC-specific; scheduling or assembler rewrites can break arithmetic. Signedness assumptions matter because the helper name is used for two's-complement low 64-bit products.

Test signals: compiler runtime arithmetic tests for positive/negative operands, zero, all-ones, carry-heavy cross products, and randomized 64-bit multiplication compared with a reference. Build logs should show no unresolved libgcc multiply helper references.
