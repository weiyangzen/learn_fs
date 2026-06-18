# sources/distributed-fs/ceph-client/drivers/input/keyboard/ep93xx_keypad.c

## Purpose

`ep93xx_keypad.c` drives the Cirrus EP93xx 8x8 matrix keypad controller. It configures hardware debounce/prescale, decodes one-key or two-key capture registers, reports key state, and supports clock gating plus wake IRQ setup.

## Important APIs, Types, and Functions

- Register constants describe `KEY_INIT`, `KEY_DIAG`, and `KEY_REG` fields.
- `struct ep93xx_keypad` stores input, clock, debounce, prescale, MMIO base, 64-key keymap, last two active keys, IRQ, and enabled flag.
- `ep93xx_keypad_irq_handler()` decodes capture status and reports transitions for up to two simultaneous keys.
- `ep93xx_keypad_config()`, open/close, suspend/resume, probe, and remove manage hardware configuration, clocking, input registration, and wake IRQ.

## Control Flow

Probe obtains IRQ/MMIO/clock, reads optional debounce and prescale properties, builds an 8x8 keymap, requests the IRQ, registers input, stores drvdata, enables wakeup, and registers the IRQ as a wake source. Input open configures registers and enables the clock; close disables the clock. IRQ handling reads capture state and compares captured keys to `key1`/`key2` to emit releases for keys no longer present and presses for current keys.

## State and Persistence Behavior

The driver persists the keymap, last active keycodes, debounce/prescale values, and enabled flag in `struct ep93xx_keypad`. Clock state follows input open/close and PM. Wake IRQ registration persists until remove.

## Dependencies and Integration Points

It depends on platform/OF compatible `cirrus,ep9307-keypad`, MMIO, common clock framework, matrix keypad helpers, input core, PM sleep ops, and `dev_pm_set_wake_irq()`.

## Risks and Edge Cases

The hardware reports only up to two keys; larger combinations cannot be represented. Keycode zero handling can produce redundant reports if capture registers contain unmapped positions. Suspend uses `clk_disable()` while close uses `clk_disable_unprepare()`, so clock prepare/enable balance relies on open/PM ordering. Wake IRQ setup failures are warnings, not fatal.

## Test Signals

Test one-key, two-key, and no-key transitions; key replacement releases; debounce/prescale values; clock open/close/suspend/resume balance; wake from keypad IRQ; keymap holes; and probe failures for missing IRQ/MMIO/clock.
