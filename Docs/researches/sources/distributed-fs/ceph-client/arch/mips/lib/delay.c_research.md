# sources/distributed-fs/ceph-client/arch/mips/lib/delay.c

Purpose: implements busy-wait delay loops for MIPS.

Important APIs/functions: exports `__delay`, `__udelay`, and `__ndelay`; internal arithmetic uses `lpj_fine`/`loops_per_jiffy`, `HZ`, `USEC_PER_SEC`, `NSEC_PER_SEC`, and `__delay`.

Control flow: `__delay()` loops until the requested loop count decrements to zero. Microsecond/nanosecond helpers scale time units into loop counts and call `__delay()`.

State and persistence: reads global loop calibration values; no local persistent state.

Dependencies and integration: used by `udelay`/`ndelay` architecture delay APIs and early platform code.

Risks: correctness depends on calibrated loops and overflow-safe arithmetic. CPU frequency changes can skew busy waits.

Test signals: delay calibration, timer-based delay measurements, and boot code using `udelay()` in hardware init.
