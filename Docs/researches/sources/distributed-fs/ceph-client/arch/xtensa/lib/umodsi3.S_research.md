# sources/distributed-fs/ceph-client/arch/xtensa/lib/umodsi3.S

Purpose: Implements exported unsigned 32-bit modulo helper `__umodsi3`.

Important APIs, types, and functions: `__umodsi3`, hardware `remu` path, software normalization/subtract loop, `do_nsau`, divide-by-zero marker, and `EXPORT_SYMBOL`.

Control flow: Uses hardware remainder if available. Software path handles divisor zero/one, normalizes divisor to dividend, repeatedly subtracts shifted divisor where possible, performs final subtraction if needed, and returns the remainder.

State and persistence: Register-only arithmetic; divisor zero raises an illegal instruction for trap conversion.

Dependencies and integration: Compiler-emitted unsigned remainder and `traps.c` DIV0 recognition.

Risks: Boundary cases around divisor zero, divisor one, and high-bit operands; performance on cores lacking divide and loop instructions.

Test signals: Unsigned modulo tests for edge operands, divisor zero trap, powers of two, dividend<divisor, and no-DIV32/no-LOOPS builds.
