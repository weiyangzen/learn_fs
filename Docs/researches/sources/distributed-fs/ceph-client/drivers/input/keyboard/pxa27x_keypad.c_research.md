# sources/distributed-fs/ceph-client/drivers/input/keyboard/pxa27x_keypad.c

## Purpose

This platform driver supports the Marvell/PXA27x keypad controller, including matrix keys, direct GPIO-like keys, and up to two rotary encoders. It exposes all detected inputs through the Linux input subsystem and uses firmware properties to describe matrix dimensions, direct-key masks, rotary behavior, keymaps, and debounce timing.

## Important APIs, Types, and Functions

`struct pxa27x_keypad` owns the clock, MMIO base, IRQ, keycode table, current matrix/direct state, and rotary descriptors. Property parsing is split across `pxa27x_keypad_matrix_key_parse()`, `pxa27x_keypad_direct_key_parse()`, and `pxa27x_keypad_rotary_parse()`. Event paths are `pxa27x_keypad_scan_matrix()`, `pxa27x_keypad_scan_direct()`, `pxa27x_keypad_scan_rotary()`, and `pxa27x_keypad_irq_handler()`. `pxa27x_keypad_config()` programs `KPC`, `KPREC`, and debounce registers; input `open`/`close` gate the controller clock.

## Control Flow

Probe obtains IRQ, MMIO, clock, and an input device, builds keymaps from matrix-keypad bindings, requests the IRQ, registers input, and marks the device wake-capable. Opening the input device enables the clock and writes controller configuration. The IRQ handler reads `KPC`, dispatches direct/rotary and matrix scanners based on pending bits, and reports `MSC_SCAN` plus key or relative events. Matrix scanning decodes either the single-key `KPAS` fields or multi-key `KPASMKP*` registers and compares them with cached column state.

## State and Persistence Behavior

The driver persists only runtime input state: prior matrix columns, prior direct-key mask, rotary default counter value, and firmware-derived keycode arrays. Hardware configuration persists while the clock remains enabled. Suspend keeps the clock active only for wake-capable use; otherwise it disables and later reprograms the controller if the input device is still open.

## Dependencies and Integration Points

It depends on platform devices, MMIO registers, a clock, IRQ delivery, generic firmware properties, and `matrix_keypad_build_keymap()`. DT matching uses `marvell,pxa27x-keypad`; direct and rotary properties are Marvell-specific.

## Risks and Edge Cases

Direct-key default mask calculation uses `GENMASK(direct_key_num - 1, 0)`, so a malformed configuration with no direct/rotary keys must not reach that branch. Rotary reporting has both relative and synthetic press/release modes, and invalid property combinations can silently change event semantics. Matrix multi-key registers expose eight columns regardless of configured columns, so bounds and state comparison matter. The rotary scan loop always calls `report_rotary_event(keypad, 0, ...)`, which makes the second encoder path suspicious.

## Test Signals

Useful tests include DT/property validation for matrix-only, direct-only, and mixed layouts; keymap bounds failures; low-active direct keys; relative and keycode rotary modes; multi-key matrix changes; suspend/resume with and without wakeup; open/close clock balancing; and IRQ storms with no state changes.
