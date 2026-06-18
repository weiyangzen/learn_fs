# sources/distributed-fs/ceph-client/drivers/input/keyboard/bcm-keypad.c

## Purpose

`bcm-keypad.c` drives Broadcom memory-mapped keypad matrix hardware. It programs row/column scan dimensions, debounce filters, edge interrupts, pull mode, optional clocking, and reports matrix key changes through the input subsystem.

## Important APIs, Types, and Functions

- Register constants describe KPCR, KPIOR, KPEMR, status, mask, clear, and ISR offsets.
- `struct bcm_kp` stores MMIO base, IRQ, optional clock, input device, previous status words, dimensions, and precomputed register values.
- `bcm_kp_matrix_key_parse_dt()` parses matrix keypad properties and Broadcom-specific debounce/output/pull properties into register values.
- `bcm_kp_start()` and `bcm_kp_stop()` enable/disable clock, interrupts, edge modes, and the hardware block.
- `bcm_kp_isr_thread()` reads both status registers, reports changed keys, and syncs input.

## Control Flow

Probe allocates state/input, parses device-tree matrix and Broadcom properties, builds the keymap, maps registers, configures the optional `peri_clk`, stops the hardware into a known state, requests a threaded IRQ, and registers input. Input open starts hardware; close stops it. The IRQ thread clears interrupt status, diffs current status against `last_state`, converts changed bits to row/column scan codes, reports key state adjusted for pull mode, then calls `input_sync()`.

## State and Persistence Behavior

The driver persists register configuration in `struct bcm_kp`, keeps `last_state[2]` for edge-to-state conversion, and relies on input open/close to control clock and hardware enable. No nonvolatile state is used.

## Dependencies and Integration Points

It depends on platform bus, OF, matrix keypad helpers, optional common clock framework, MMIO accessors, threaded IRQs, and Linux input. Device-tree properties include matrix row/column/keymap data, `autorepeat`, `status-debounce-filter-period`, `col-debounce-filter-period`, `row-output-enabled`, `pull-up-enabled`, and optional `clock-frequency`.

## Risks and Edge Cases

`bcm_kp_start()` assigns `last_state[0]` from both SSR0 and SSR1, leaving `last_state[1]` apparently uninitialized for the second status register. Invalid row/column counts or debounce values can produce bad register programming. Pull-up inversion must match board wiring. Clock rate rounding failures and shared hardware state across open/close are important failure points.

## Test Signals

Exercise row/column sizes up to 8x8, both pull modes, row-output vs column-output wiring, debounce bounds, optional/no clock configurations, input open/close cycles, IRQs from SSR0 and SSR1, autorepeat property, and keymap correctness for every matrix position.
