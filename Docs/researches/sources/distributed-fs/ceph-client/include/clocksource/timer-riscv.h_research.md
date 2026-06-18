# sources/distributed-fs/ceph-client/include/clocksource/timer-riscv.h

Purpose: RISC-V clocksource multiplier/shift helper declaration.

Important APIs/types/functions: `riscv_cs_get_mult_shift(u32 *mult, u32 *shift)`.

Control flow: callers request precomputed clocksource conversion values for RISC-V timer cycles to nanoseconds.

State and persistence: no state in header; implementation supplies current conversion state.

Dependencies and integration points: includes Linux types and integrates with RISC-V timer/clocksource code.

Risks: invalid mult/shift values cause time drift or scheduler tick errors.

Test signals: RISC-V boot/timekeeping tests and clocksource conversion validation.
