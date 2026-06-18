# sources/distributed-fs/ceph-client/drivers/input/keyboard/spear-keyboard.c

## Purpose

This platform driver supports the ST SPEAr keyboard controller. It exposes a 16x16 matrix through a hardware FIFO-style data register, reports one active key at a time, manages scan start/stop through input open/close, and supports wake-aware suspend behavior.

## Important APIs, Types, and Functions

`struct spear_kbd` owns the input device, MMIO base, clock, IRQ, mode, suspended clock rate, saved control register, last pressed key, keycode matrix, and IRQ wake flag. `spear_kbd_interrupt()` reads status/data and reports release of the prior key plus press of the new key. `spear_kbd_open()` programs clock frequency, mode, scan rate, and starts scanning. `spear_kbd_close()` stops scanning and disables the clock. PM functions save/restore mode control and optionally reprogram suspend rate.

## Control Flow

Probe requires an IRQ and `st,mode`, optionally reads `suspended_rate`, maps MMIO, obtains a prepared clock, builds the fixed 16x16 keymap from firmware, requests IRQ, registers input, and marks the device wake-capable. Open enables the clock, computes the peripheral clock divider in MHz minus one, writes scan configuration, clears status, and sets start-scan. Interrupt flow validates data availability, releases `last_key` if set, reads row/column from `DATA_REG`, maps it to a keycode, emits scan/key press, caches the key, and clears status.

## State and Persistence Behavior

Only one active `last_key` is tracked, reflecting the hardware model. Saved `mode_ctl_reg` is used across suspend/resume. Wake mode may leave scanning active and changes frequency programming for low-power clock assumptions.

## Dependencies and Integration Points

It depends on platform resources, clock rate, matrix keymap bindings, input open/close callbacks, and OF compatible `st,spear300-kbd`.

## Risks and Edge Cases

The interrupt handler always releases the previous key before pressing a new one, so true multi-key rollover is unsupported. A `KEY_RESERVED` key can become `last_key` if the keymap leaves holes. The driver uses a nonstandard `suspended_rate` property name without vendor prefix. Clock enable/disable in suspend is explicit and can become unbalanced if input open state changes unexpectedly.

## Test Signals

Test mode parsing, keymap bounds, single-key press/release replacement, no data interrupt returning `IRQ_NONE`, clock divider calculations, autorepeat property, suspend with wake and custom suspended rate, and close/resume interactions.
