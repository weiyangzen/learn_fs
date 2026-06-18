# sources/distributed-fs/ceph-client/arch/arm/lib/delay-loop.S

Purpose: provides loop-based delay primitives `__loop_delay`, `__loop_const_udelay`, and `__loop_udelay` used before or instead of timer-backed delay.

Control flow converts microseconds or constant delay units through `UDELAY_MULT` and `loops_per_jiffy`, rounds up, and spins decrementing a loop counter until elapsed. Persistent state is external `loops_per_jiffy`; this file owns none. Dependencies include calibration code and `asm/delay.h`. Risks are inaccurate delays before calibration, CPU frequency changes, and zero/overflow edge cases. Test signals include delay calibration, timer fallback absence, and timing sanity under early boot.
