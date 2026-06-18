# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/timer.h

Purpose: Timer register layout and bit definitions for RC32434. It describes three counters plus a real-time counter block.

Important APIs/types/functions: `TIMER0_BASE_ADDR` is `0x18028000`; `TIMER_COUNT` is `3`. `struct timer_counter` provides `count`, `compare`, and `ctc`. `struct timer` contains an array of counters plus real-time `rcount`, `rcompare`, and `rtc`. Bit and mask macros include `RC32434_CTC_EN_BIT`, `RC32434_CTC_TO_BIT`, `RC32434_RTC_CE_BIT`, `RC32434_RTC_TO_BIT`, `RC32434_RTC_RQE_BIT`, `RC32434_RCOUNT_MSK`, and `RC32434_RCOMP_MSK`.

Control flow, state, and persistence: The header has no functions; platform timer code maps the register block, writes enable/compare fields, and consumes timeout bits. State persists in hardware counters and compare registers.

Dependencies and integration: It includes `mach-rc32434/rb.h` for `BIT_TO_MASK`. It integrates with clocksource/clockevent setup and interrupt handling for RC32434 timer IRQs.

Risks and test signals: Incorrect masks or counter array sizing will break timer interrupts and scheduling. Test by booting the platform, confirming periodic tick or clockevent programming, and checking timeout bits clear as expected under interrupt load.
