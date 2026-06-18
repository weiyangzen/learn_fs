# sources/distributed-fs/ceph-client/drivers/input/keyboard/clps711x-keypad.c

## Purpose

`clps711x-keypad.c` drives the Cirrus Logic EP7209/CLPS711X keypad matrix using a syscon keyboard-scan register for columns and GPIOs for rows. It is a polled input driver for an 8-column matrix.

## Important APIs, Types, and Functions

- `struct clps711x_keypad_data` holds the syscon regmap, row count, row shift, and per-row GPIO state.
- `struct clps711x_gpio_data` stores a row GPIO descriptor and last column bitmap.
- `clps711x_keypad_poll()` asserts each column through `SYSCON1_KBDSCAN`, double-reads row GPIOs until stable, reports changed key states, and syncs input.
- `clps711x_keypad_probe()` obtains syscon/row GPIOs, parses poll interval, builds keymap, configures polling, and registers input.

## Control Flow

Probe looks up the `syscon` phandle, counts `row` GPIOs, allocates row state, gets each row GPIO as input, reads `poll-interval`, creates an input device, builds a matrix keymap with eight columns, sets all columns low, installs polling, and registers input. Polling iterates columns, asserts one scan code in syscon, reads every row twice for stability, compares against `last_state`, emits `MSC_SCAN` and key events for changes, deasserts columns, then syncs if anything changed.

## State and Persistence Behavior

Per-row `last_state` bitmaps persist across polls. Hardware column drive state is transient and reset low after every column. No nonvolatile state is used.

## Dependencies and Integration Points

The driver depends on platform/OF (`cirrus,ep7209-keypad`), syscon regmap, CLPS711X syscon definitions, GPIO descriptors, matrix keypad helpers, input polling, and `poll-interval`/`autorepeat` properties.

## Risks and Edge Cases

The double-read loop waits until two consecutive GPIO reads match; noisy hardware could spin for a long time, though `cond_resched()` mitigates scheduler impact. Missing or invalid `syscon`, row GPIOs, or poll interval prevents probe. Keycode zero entries suppress key reports but still track state changes.

## Test Signals

Test row counts, all eight columns, noisy GPIO simulation, poll interval parsing, autorepeat, keymap holes, syscon write failures, and repeated open/close/poll cycles under CPU load.
