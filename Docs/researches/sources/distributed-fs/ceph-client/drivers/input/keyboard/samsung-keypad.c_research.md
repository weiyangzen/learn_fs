# sources/distributed-fs/ceph-client/drivers/input/keyboard/samsung-keypad.c

## Purpose

This platform driver supports Samsung S3C/S5P matrix keypad controllers. It scans rows and columns through MMIO registers, reports Linux input key events, supports platform data and DT bindings, handles runtime/system PM, and configures wakeup for keypad interrupts.

## Important APIs, Types, and Functions

`struct samsung_keypad` contains chip metadata, input device, clock, MMIO base, wait queue, stopped/wake flags, dimensions, cached row state, and keycodes. `samsung_keypad_scan()` drives each column and reads rows. `samsung_keypad_report()` compares new state with cached state. `samsung_keypad_irq()` loops while keys remain pressed. `samsung_keypad_start()` and `samsung_keypad_stop()` manage clock and interrupts. PM paths include runtime suspend/resume and system suspend/resume with wake toggling.

## Control Flow

Probe parses platform data or DT child key nodes, validates dimensions, optionally configures GPIOs, maps MMIO, obtains a prepared clock, builds the keymap, requests a threaded IRQ, enables runtime PM, registers input, and frees temporary DT platform data. Opening the input device starts the controller. The IRQ thread clears pending bits, scans the matrix, reports changed keys, and if any key is down waits up to 50 ms before rescanning; this continues until release or stop.

## State and Persistence Behavior

`row_state[]` is the persistent software snapshot of pressed keys. `stopped` coordinates close/suspend with the IRQ polling loop. Wake enable state is tracked separately for runtime PM. Hardware interrupt, wake, and column registers persist only while the clock and controller are active.

## Dependencies and Integration Points

The driver depends on platform/OF data, `matrix_keypad_build_keymap()`, Samsung keypad register layout, clocks, runtime PM, and input `open`/`close` callbacks. Chip variants differ by column bit shift and are selected from OF data or platform IDs.

## Risks and Edge Cases

The IRQ thread actively polls while keys are held, so stuck keys can keep the device busy. DT parsing reads child properties without checking individual property read errors. Start/stop and runtime PM both manipulate clocks and wake bits, so clock balance and stopped-state transitions are important. S5PV210 row/interrupt masks are defined but the scan path only uses generic row masks through dimension limits.

## Test Signals

Tests should cover S3C and S5PV210 variants, DT and platform-data keymaps, held-key polling, close during IRQ wait, no-autorepeat, runtime suspend/resume while open and closed, wakeup suspend/resume, invalid dimensions, and clock/IRQ failure unwind.
