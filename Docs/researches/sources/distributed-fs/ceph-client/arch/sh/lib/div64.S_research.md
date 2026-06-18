# sources/distributed-fs/ceph-client/arch/sh/lib/div64.S

Purpose: implements the low-level 64-bit dividend divided by 32-bit divisor routine used by `__div64_32`.

Important symbol: `ENTRY(__xdiv64_32)`.

Control flow: performs multiword division in SH assembly, writes the quotient back through the dividend pointer, and returns the 32-bit remainder.

State and persistence: mutates caller memory for the dividend/quotient and uses registers for intermediate state.

Dependencies and integration: paired with `div64-generic.c` and generic kernel arithmetic macros.

Risks: carry/borrow and normalization mistakes affect time, block, network, and filesystem math. Division by zero must be prevented by callers.

Test signals: arithmetic selftests for boundary values such as 0, `U32_MAX`, high-bit dividends, and non-zero remainders.
