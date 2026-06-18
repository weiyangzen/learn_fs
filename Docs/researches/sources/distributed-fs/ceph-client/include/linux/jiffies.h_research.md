# sources/distributed-fs/ceph-client/include/linux/jiffies.h

## Purpose
Defines jiffies timekeeping declarations, wrap-safe comparison macros, and conversion helpers between jiffies and common time units. It is the main kernel interface for low-cost tick-based timeouts.

## Important APIs, Types, And Functions
Exports `jiffies`, `jiffies_64`, `get_jiffies_64()`, `time_after*()`, `time_before*()`, range macros, jiffies-relative convenience macros, `INITIAL_JIFFIES`, `MAX_JIFFY_OFFSET`, conversion helpers such as `jiffies_to_msecs()`, `msecs_to_jiffies()`, `usecs_to_jiffies()`, `secs_to_jiffies()`, `timespec64_to_jiffies()`, clock_t conversions, and proc sysctl conversion handlers.

## Control Flow
Compile-time `HZ` ranges select `SHIFT_HZ` and scaled conversion constants. Constant arguments to `msecs_to_jiffies()` and `usecs_to_jiffies()` use `__builtin_constant_p()` so overflow and rounding logic can fold at compile time; dynamic arguments call external helpers. Wrap-safe comparisons subtract in signed space and only interpret the sign.

## State And Persistence
`jiffies` and `jiffies_64` are global tick counters. On 32-bit systems, reading `jiffies_64` requires `get_jiffies_64()` because the 64-bit value is not naturally atomic. There is no persistence across reboot.

## Dependencies And Integration Points
Depends on HZ from `asm/param.h`, generated time constants, vdso jiffies definitions, and time unit constants. It integrates with timers, scheduler timeouts, sysctl tunables, drivers, networking, and filesystem delayed work.

## Risks
Direct relational comparisons on `jiffies` break across wrap. Very large conversions saturate to `MAX_JIFFY_OFFSET`. `secs_to_jiffies()` is a macro suitable for static initializers but lacks the richer overflow checks of millisecond/microsecond helpers.

## Test Signals
Test signals include wrap-around comparisons, constant and runtime conversion parity, boundary saturation near `MAX_JIFFY_OFFSET`, multiple HZ configurations, 32-bit `get_jiffies_64()` correctness, and sysctl jiffies conversion behavior.
