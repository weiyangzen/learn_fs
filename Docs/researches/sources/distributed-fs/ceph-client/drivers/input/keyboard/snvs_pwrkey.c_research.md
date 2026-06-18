# sources/distributed-fs/ceph-client/drivers/input/keyboard/snvs_pwrkey.c

## Purpose

This platform driver reports the i.MX SNVS ON/OFF key as an input power key. It configures SNVS low-power control bits through a syscon regmap, handles short/long press status, emulates press/release behavior for early silicon, and supports wakeup through the PM wake IRQ framework.

## Important APIs, Types, and Functions

`struct pwrkey_drv_data` stores the SNVS regmap, IRQ, selected keycode, current key state, wakeup flag, timer, input device, and minor revision. `imx_snvs_pwrkey_interrupt()` handles the SPO interrupt and clears `SNVS_LPSR_SPO`. `imx_imx_snvs_check_for_events()` polls `SNVS_HPSR_BTN` after debounce and during long presses. `imx_snvs_pwrkey_probe()` parses `regmap`, `linux,keycode`, `wakeup-source`, and `power-off-time-sec`, enables debounce/power-off configuration, and registers input/IRQ.

## Control Flow

Probe gets the parent SNVS regmap, optional clock, keycode, IRQ, and optional power-off timing, reads the silicon minor revision, enables debounce power-key detection, clears stale SPO status, initializes a timer, registers an input device, requests IRQ, enables device wakeup, and installs the IRQ as a wake IRQ. On interrupt it records a wakeup event, reads LP status, and either emits a synthetic press/release for minor revision 0 or schedules the debounce timer. The timer reads live button state and reports only changes, rescheduling while pressed.

## State and Persistence Behavior

The driver persists `keystate` and the timer while bound. SNVS LPCR bits for debounce and power-off timing persist in the shared SNVS block. Wakeup state is managed by device core and PM wake IRQ. A devm action deletes the timer during teardown.

## Dependencies and Integration Points

It depends on OF, `syscon_regmap_lookup_by_phandle()`, SNVS register layout, optional clock control, input key events, timers, and `dev_pm_set_wake_irq()`. Compatible string is `fsl,sec-v4.0-pwrkey`.

## Risks and Edge Cases

The timer callback ignores regmap read errors and treats unread state as whatever was left in `state`. Revision-specific behavior is critical: first-generation i.MX6 only interrupts on release. `power-off-time-sec` accepts only 0, 5, 10, or 15 seconds. Wake IRQ setup errors are logged but not fatal.

## Test Signals

Test revision 0 synthetic events, newer revision debounce and long-press polling, keycode override, invalid power-off timing, regmap failure, wake from suspend, timer cleanup on unbind, optional clock paths, and repeated press/release races around IRQ clear.
