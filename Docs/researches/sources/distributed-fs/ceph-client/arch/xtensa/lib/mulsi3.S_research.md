# sources/distributed-fs/ceph-client/arch/xtensa/lib/mulsi3.S

Purpose: Implements exported signed 32-bit multiply helper `__mulsi3` across Xtensa cores with different multiply capabilities.

Important APIs, types, and functions: `__mulsi3`, hardware `mull`, MUL16 and MAC16 paths, software add/shift loop, `do_addx{2,4,8}` macros, ABI macros, and `EXPORT_SYMBOL`.

Control flow: Selects the best implementation at compile time: direct 32-bit multiply, split 16-bit partial products, MAC16 accumulator sequence, or software nibble-at-a-time multiplication after normalizing signs and choosing smaller multiplier.

State and persistence: Register-only arithmetic.

Dependencies and integration: Compiler-emitted multiplication on cores without full hardware support and module symbols; depends on core feature macros.

Risks: Software sign handling and partial-product carries are correctness hotspots; performance varies sharply by hardware feature set.

Test signals: Multiplication tests for signed extremes, zero, one, negative pairs, overflow wraparound behavior, and builds for MUL32/MUL16/MAC16/no-mul cores.
