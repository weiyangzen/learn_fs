# sources/distributed-fs/ceph-client/arch/s390/lib/delay.c

## Purpose
Implements s390 busy-wait delay primitives used by generic kernel delay APIs.

## Important APIs, Types, And Functions
Exports `__delay()`, `__udelay()`, and `__ndelay()`. `__delay()` executes a simple branch-count loop and explicitly does not promise wall-clock duration. `delay_loop()` waits against the monotonic TOD clock. `__udelay()` and `__ndelay()` convert microseconds/nanoseconds into TOD deltas and call `delay_loop()`.

## Control Flow And State
`__delay()` uses inline assembly `brct` over roughly half the supplied loop count plus one. `delay_loop()` computes an end TOD value and spins with `cpu_relax()` until `tod_after()` reports the current monotonic TOD has passed it. `__ndelay()` uses `do_div()` after scaling to avoid floating point.

## Dependencies And Integration
Depends on s390 TOD clock helpers, `cpu_relax()`, kernel delay exports, and s390 division helper definitions.

## Risks And Test Signals
Risks include overflow in time conversion, assumptions about loops being calibrated, and busy-wait behavior under virtualization. Signals include boot stability, timer/delay selftests, driver behavior requiring short delays, and compile coverage for exported symbols.
