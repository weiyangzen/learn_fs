# sources/distributed-fs/ceph-client/drivers/power/reset/at91-poweroff.c

## Purpose
legacy Atmel AT91 SAM9/SAMA5 shutdown-controller poweroff driver.

## Important APIs, Types, and Functions
global `at91_shdwc`, wakeup mode parser, `at91_poweroff()` ARM assembly, DT wakeup configuration, and platform probe/remove.

## Control Flow
probe maps SHDWC, enables slow clock, reports wake source, programs wakeup mode/counter/RTC/RTT bits, optionally maps LPDDR2/3 DDR controller, and assigns `pm_power_off`; callback powers down DDR then writes the shutdown key.

## State and Persistence Behavior
global base pointers, slow clock, optional MPDDRC mapping, and `pm_power_off` persist until remove; wake mode and DDR low-power writes persist in hardware.

## Dependencies and Integration Points
AT91 clocks, OF address lookup, SHDWC registers, DDRSDRC definitions, platform driver, legacy global poweroff hook.

## Risks and Edge Cases
inline assembly is ARM-specific and must run from cache-aligned code; global singleton prevents multiple controllers; wakeup strings outside known values only warn; MPDDRC lookup is compatible-string-specific.

## Test Signals
DT wakeup property tests, LPDDR and non-LPDDR boards, slow-clock failure, wake-source logging, remove clearing `pm_power_off`, and real shutdown.
