# sources/distributed-fs/ceph-client/drivers/input/keyboard/tc3589x-keypad.c

## Purpose

This platform child driver supports the TC35893/TC3589x MFD keypad controller. It configures keypad size, debounce, settle timing, GPIO pull-ups, block clocks/reset, interrupt masks, and FIFO event decoding for matrix key input.

## Important APIs, Types, and Functions

`struct tc3589x_keypad_platform_data` stores parsed keypad dimensions, timing, IRQ trigger, wake/autorepeat flags, and optional keymap data. `struct tc_keypad` stores parent MFD, input device, platform data, keymap pointer, and stopped flag. `tc3589x_keypad_init_key_hardware()` writes size/config/pull-up registers. `tc3589x_keypad_irq()` drains event FIFO and decodes row/column/up records. Enable/disable paths manipulate reset, MFS, clock, IRQ clear, and mask registers.

## Control Flow

Probe parses OF properties, gets IRQ, allocates state/input, builds a matrix keymap using the maximum hardware matrix, disables the keypad block, requests a threaded IRQ, registers input, and configures wake capability. Input open enables the block and initializes hardware. IRQ handling reads up to eight FIFO entries, skips empty/clear codes, reports each valid event, clears keyboard interrupts, and re-enables event/loss masks. Suspend disables non-wakeup devices or enables IRQ wake; resume reverses that state.

## State and Persistence Behavior

`keypad_stopped` tracks whether the block is disabled and drives PM behavior. The keymap pointer is the input core keycode array. Hardware state includes keypad size, pull-up configuration, debounce/settle registers, interrupt masks, and block clock/reset state.

## Dependencies and Integration Points

The driver depends on the TC3589x MFD API (`tc3589x_reg_write/read`, `tc3589x_set_bits`), matrix-keypad bindings, platform IRQ resources, and input device open/close. Wake policy is exposed through device wakeup flags.

## Risks and Edge Cases

The OF parser checks for `linux,keymap` but never fills `plat->keymap_data`; actual keymap loading relies on `matrix_keypad_build_keymap()` reading from input parent properties. Resume returns immediately when `keypad_stopped` is false, so a wakeup-enabled active keypad may skip disabling IRQ wake. FIFO overflow/loss is only masked/re-enabled, not surfaced as input loss. Pull-ups are programmed broadly for row/column groups.

## Test Signals

Test OF dimension parsing, missing keymap, open/close block enable, FIFO press/release decoding, overflow/loss interrupts, wake and non-wake suspend/resume, IRQ trigger behavior, MFD register errors, and keymap holes.
