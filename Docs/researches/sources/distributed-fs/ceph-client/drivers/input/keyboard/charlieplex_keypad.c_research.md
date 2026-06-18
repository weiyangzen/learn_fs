# sources/distributed-fs/ceph-client/drivers/input/keyboard/charlieplex_keypad.c

## Purpose

`charlieplex_keypad.c` is a GPIO-polled charlieplex keypad driver. It scans shared GPIO lines by driving one line high at a time, reading the remaining lines, debouncing the detected matrix code, and reporting one active key at a time.

## Important APIs, Types, and Functions

- `struct charlieplex_keypad` stores input device, GPIO array, line count, settling time, debounce threshold/count, current code, and candidate code.
- `charlieplex_keypad_scan_line()` drives one output line, waits optional settling time, reads all lines, restores input mode, and returns a matrix scan code.
- `charlieplex_keypad_check_switch_change()` and `charlieplex_keypad_report_key()` implement debounce and release/press reporting.
- `charlieplex_keypad_probe()` parses polling/debounce/settling properties, builds a square keymap, sets polling, and registers input.

## Control Flow

Probe requires a nonzero `poll-interval`, defaults debounce to 5 ms, obtains `line` GPIOs as inputs, assigns consumer names, builds a keymap with `nlines` rows and columns, enables optional autorepeat, installs an input polling callback, and registers input. Each poll scans output lines until it finds an asserted input, then advances debounce state and emits release/press events once stable long enough.

## State and Persistence Behavior

The driver stores only volatile debounce and current-key state. GPIO directions change during each scan and are restored to input. It does not maintain persistent hardware configuration outside devm-managed GPIO descriptors.

## Dependencies and Integration Points

It integrates with platform/OF matching (`gpio-charlieplex-keypad`), GPIO descriptor arrays, matrix keypad keymap helpers, input polling, firmware properties, and optional `autorepeat`.

## Risks and Edge Cases

The scanner returns only the first detected asserted line pair, so simultaneous keys are not represented. `current_code` and `debounce_code` are initialized to `-1` while zero also means no key; report logic must avoid indexing negative codes. GPIO direction churn and settling time must match electrical characteristics. More than `MATRIX_MAX_ROWS` lines is rejected.

## Test Signals

Validate all line pairs, no-key transitions, debounce thresholds, simultaneous key behavior, zero and nonzero settling times, GPIO read errors, invalid/missing `poll-interval`, autorepeat, and keymap indexing for square matrices.
