<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/delay.h

## Purpose
This header implements busy-wait delay loops for m68k using `loops_per_jiffy`, with variants for ColdFire alignment and CPUs lacking 32x32-to-64 multiply/divide.

## Important APIs, Types, And Functions
- `__delay()` runs an inline decrement loop, with `DELAY_ALIGN` padding for ColdFire.
- `__bad_udelay()` catches excessive constant microsecond delays.
- `__const_udelay()` is implemented by scaled arithmetic, either with simplified 32-bit math or `mulul`.
- `__udelay()` and `udelay()` provide microsecond delays with compile-time range checking for constants.
- `ndelay()` computes loop counts for nanosecond delays.

## Control Flow
Callers invoke `udelay()` or `ndelay()`. Constant microsecond delays above 20000 route to `__bad_udelay()`. Otherwise the code scales by HZ and `loops_per_jiffy`, then spins in `__delay()`.

## State And Persistence Behavior
The header does not store state. It reads `loops_per_jiffy` and consumes CPU cycles; interrupts are not disabled by these helpers.

## Dependencies And Integration Points
It depends on `asm/param.h`, HZ, `loops_per_jiffy`, CPU config flags, and compiler constant detection. It is used by drivers and early hardware sequencing requiring short waits.

## Risks And Edge Cases
Busy waits depend on calibrated `loops_per_jiffy` and CPU alignment behavior. Long `udelay()` calls are discouraged and constant-checked. Nanosecond scaling is approximate, especially on no-64-multiply CPUs.

## Test Signals
Delay calibration, serial/device reset timing, timer-based measurements of `udelay()`/`ndelay()`, and cross-builds for ColdFire and full m68k multiply support validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/delay.h -->
