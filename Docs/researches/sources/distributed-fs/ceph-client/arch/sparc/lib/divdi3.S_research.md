# sources/distributed-fs/ceph-client/arch/sparc/lib/divdi3.S

Purpose: SPARC32 libgcc-compatible signed 64-bit division helper.

Important APIs/functions: Exports `__divdi3`.

Control flow: Normalizes operand signs, performs multiword division using shift/subtract loops for several operand-size cases, then reapplies result sign. It handles 64-bit numerator/divisor values split across registers.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h`; built for `CONFIG_SPARC32` to satisfy compiler helper calls.

Risks/test signals: Division by edge values, sign handling, and overflow-like `INT64_MIN / -1` behavior are sensitive. Test positive/negative combinations, small/large divisors, and compare with C 64-bit division.
