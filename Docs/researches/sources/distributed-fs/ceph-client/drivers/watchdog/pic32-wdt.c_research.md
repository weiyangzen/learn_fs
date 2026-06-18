# sources/distributed-fs/ceph-client/drivers/watchdog/pic32-wdt.c

## Purpose
`pic32-wdt.c` drives the Microchip PIC32 watchdog timer. It exposes a fixed timeout derived from hardware prescaler/postscaler configuration and services the watchdog with a 16-bit key write.

## Important APIs, types, and functions
`struct pic32_wdt` stores watchdog registers, reset-control base, and clock. Helpers include `pic32_wdt_is_win_enabled`, `pic32_wdt_get_post_scaler`, `pic32_wdt_get_clk_id`, `pic32_wdt_bootstatus`, `pic32_wdt_get_timeout_secs`, and `pic32_wdt_keepalive`. Ops are `pic32_wdt_start`, `stop`, and `ping`.

## Control flow
Probe maps registers and reset-control space, enables the clock, rejects windowed-clear mode, computes timeout from clock/32 and postscaler terminal count, reads/clears WDT reset cause, forces nowayout, and registers the global watchdog device. Start sets `ON` and writes the clear key; stop clears `ON` and executes `nop`; ping writes the clear key to the high halfword of WDTCON.

## State and persistence
Hardware configuration controls timeout and window mode. Reset cause survives until probe clears it. The software watchdog object is global and has no set-timeout path.

## Dependencies and integration points
It depends on OF compatible `microchip,pic32mzda-wdt`, PIC32 platform data macros, clock framework, watchdog core, and MMIO reset base mapping.

## Risks and test signals
Risks include unsupported windowed mode causing probe failure, fixed nowayout, global singleton watchdog, zero timeout if clock/postscaler math underflows, and direct reset-cause clearing during probe. Test signals include windowed-mode rejection, timeout calculation for all postscaler values, bootstatus clear, start/stop/ping key write, and clock/map failures.
