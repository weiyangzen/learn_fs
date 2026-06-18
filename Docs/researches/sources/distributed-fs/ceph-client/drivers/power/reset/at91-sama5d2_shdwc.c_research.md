# sources/distributed-fs/ceph-client/drivers/power/reset/at91-sama5d2_shdwc.c

## Purpose
SAMA5D2-compatible AT91 shutdown-controller poweroff driver with richer wake input/debounce support.

## Important APIs, Types, and Functions
`struct reg_config`, `struct shdwc`, global `at91_shdwc`, wake status, `at91_poweroff()`, debouncer/input parsing, SoC register configs, and platform probe/remove.

## Control Flow
probe maps SHDWC, enables slow clock, matches SoC config, optionally maps PMC/DDR controller for LPDDR poweroff, logs wake source, configures debounce/RTC/RTT/wakeup child inputs, and installs `pm_power_off`; callback writes PMC DDR sleep if needed, LPDDR powerdown, and SHDWC shutdown key.

## State and Persistence Behavior
global singleton backs legacy `pm_power_off`; per-SoC register offsets and DT wake configuration persist in SHDWC/PMC registers.

## Dependencies and Integration Points
AT91 clocks/PMC helpers, OF child nodes, DDRSDRC, platform driver, global poweroff hook.

## Risks and Edge Cases
global hook means only one active controller; child wake input parsing must match hardware input numbers; debounce conversion uses fixed 32.768 kHz table; inline assembly and DDR sequencing are hardware-critical.

## Test Signals
SAMA5D2/SAM9X60/SAMA7G5 DTs, wake child nodes, debounce boundaries, LPDDR and non-LPDDR shutdown, wake-source status, and remove cleanup.
