# sources/distributed-fs/ceph-client/drivers/input/keyboard/stmpe-keypad.c

## Purpose

This platform child driver supports keypad blocks in STMPE multi-function expanders. It configures variant-specific keypad pins, row/column masks, debounce, scan count, and FIFO reads, then reports matrix key press/release events through input.

## Important APIs, Types, and Functions

`struct stmpe_keypad_variant` captures per-chip FIFO width, auto-increment behavior, pull-up requirements, max rows/cols, and GPIO masks. `struct stmpe_keypad` stores parent STMPE, input, variant, timing settings, row/column masks, and keymap. `stmpe_keypad_read_data()` reads FIFO bytes. `stmpe_keypad_irq()` decodes row/column/up records. `stmpe_keypad_altfunc_init()` assigns pins to keypad alternate function. `stmpe_keypad_chip_init()` enables the block and programs registers.

## Control Flow

Probe gets the parent `struct stmpe`, selects the variant by `partnum`, parses debounce/scan/autorepeat and matrix properties, builds a keymap, derives used row/column masks from non-reserved keymap entries, initializes chip hardware, requests a threaded IRQ, registers input, and stores driver data. IRQ flow reads the variant's data bytes, skips no-key markers, decodes row/column and release bit, emits `MSC_SCAN` and key state, and syncs for each FIFO entry.

## State and Persistence Behavior

The software row/column masks are derived once from the keymap and persist for the device lifetime. Hardware block enable, alternate-function pin selection, pull-ups, scan count, debounce, and row/column registers remain active until remove disables the keypad block.

## Dependencies and Integration Points

It depends on the STMPE MFD core (`stmpe_enable()`, `stmpe_block_read()`, `stmpe_set_altfunc()`), matrix-keypad bindings, platform IRQs, and I2C-backed input devices. Supported variants are STMPE1601, STMPE2401, and STMPE2403.

## Risks and Edge Cases

Variant pin masks are consumed with `__ffs()` while clearing bits; incorrect variant metadata can corrupt pin selection. Some variants require pull-ups and different FIFO read behavior. IRQ handling returns `IRQ_NONE` on read error, which may matter for shared/level IRQs. There is no explicit PM path, so parent MFD suspend must preserve or restore keypad block state.

## Test Signals

Test all variants, auto-increment and non-auto-increment reads, row counts above eight, pull-up programming, debounce/scan-count limit failures, keymap-derived pin masks, FIFO no-key markers, release events, remove disabling the block, and parent MFD suspend/resume.
