## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/delay.h

Purpose: declares and defines PowerPC busy-wait delay helpers.

Important APIs/types/functions: exports `__delay()`, `udelay()`, `ndelay()`, `mulhwu_scale_factor()`, and loop-per-jiffy scaling inputs used by generic delay code.

Control flow: delay helpers convert requested microseconds or nanoseconds to timebase/loop counts using architecture scaling and call the low-level delay loop. Exact implementation details are in companion architecture code.

State and persistence: reads calibration state such as loops-per-jiffy/timebase conversion data. No persistent state is changed by the header.

Dependencies and integration: integrates with generic delay APIs, timebase calibration, device drivers that require short busy waits, and early boot code where timers may be unavailable.

Risks and test signals: overflow or scaling errors make delays too short or too long, breaking hardware sequencing. Test signals include timer calibration, driver probe timing, `udelay`/`ndelay` selftests where available, and 32/64-bit build coverage.
