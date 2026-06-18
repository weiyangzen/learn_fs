# sources/distributed-fs/ceph-client/drivers/input/keyboard/st-keyscan.c

## Purpose

This platform driver supports the STMicroelectronics STI keyscan controller. It programs matrix dimensions and debounce timing, reads a compact 16-bit matrix state on interrupts, and reports key transitions through a matrix keymap.

## Important APIs, Types, and Functions

`struct st_keyscan` stores MMIO base, IRQ, clock, input device, last 16-bit matrix state, row/column counts, and debounce time. `keyscan_isr()` reads `KEYSCAN_MATRIX_STATE_OFF`, computes changed bits, reports key transitions using the input keycode array, and syncs. `keyscan_start()` enables the clock and programs debounce, dimensions, and enable. `keyscan_stop()` disables scanning and the clock. Probe parses matrix properties and `st,debounce-us`.

## Control Flow

Probe requires DT, allocates input/state, parses rows/columns, builds a keymap, maps registers, gets a clock, briefly enables the clock to stop/reset the controller, requests IRQ, registers input, stores driver data, and marks wakeup capable. Input open starts hardware; close stops it. Interrupts are edge/simple state-change notifications, with all changed bits in the 16-bit matrix reported from the cached state comparison.

## State and Persistence Behavior

`last_state` is the only event-state cache. Hardware debounce and dimension registers persist while the controller is enabled. Suspend either enables IRQ wake or stops scanning if the input device is open; resume reverses that behavior.

## Dependencies and Integration Points

The driver depends on OF compatible `st,sti-keyscan`, the matrix-keypad binding, platform MMIO/IRQ, a clock, and input `open`/`close` callbacks.

## Risks and Edge Cases

The controller maximum is 16 keys, but matrix parsing does not explicitly reject row/column products greater than 16 before building a keymap. `for_each_set_bit(..., BITS_PER_LONG)` iterates beyond the 16 hardware bits if high bits somehow change. Probe enables the clock and calls `keyscan_stop()`, which disables it; failures after that must not assume the clock is still active. Wakeup capability is set, but policy depends on userspace enabling wake.

## Test Signals

Test valid and oversized matrices, debounce conversion from microseconds and clock rate, open/close clock balance, interrupt deltas, all release behavior after suspend, wake-enabled suspend/resume, missing DT, and keymap holes.
