# sources/distributed-fs/ceph-client/arch/microblaze/lib/divsi3.S

Purpose: provides signed 32-bit division helper `__divsi3` for MicroBlaze cores or builds lacking hardware divide.

Important APIs and state: arguments are dividend r5 and divisor r6; result is r3. It saves r28-r31.

Control flow: zero divisor or zero dividend returns 0. Negative operands are made positive while saving result sign. A shift/subtract loop builds quotient bit by bit, then negates the result if needed.

State and persistence: pure arithmetic aside from callee-saved register preservation.

Dependencies and integration: exported to modules and used by compiler-generated division. Paired with `modsi3.S` and unsigned variants.

Risks and test signals: division by zero silently returns 0 instead of trapping. Edge case `INT_MIN / -1` follows two's-complement behavior of the routine. Test signed sign combinations, zero, INT_MIN, and builds without hardware div.
