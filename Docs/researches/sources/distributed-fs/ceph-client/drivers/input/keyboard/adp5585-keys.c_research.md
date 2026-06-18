# sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5585-keys.c

Purpose: implements keypad support for ADP5585/ADP5589-family MFD devices, using firmware-described keypad pins, matrix keymaps, regmap setup, and parent event notifiers.

Important APIs/types/functions: `struct adp5585_kpad_chip` describes event ranges and matrix dimensions. `struct adp5585_kpad` stores chip info, notifier, input, keycode map, device, keypad pin bitmap, and row shift. Key functions are `adp5585_keys_parse_fw`, `adp5585_keys_validate_events`, `adp5585_keys_setup`, `adp5585_keys_ev_handle`, and `adp5585_keys_probe`.

Control flow: probe requires an IRQ-capable parent ADP5585 device, reads revision, allocates input, attaches the parent OF node, parses `adi,keypad-pins`, reserves pins against the parent `pin_usage` bitmap, derives effective rows/columns, builds the matrix keymap, optionally enables repeat, validates unlock/reset special events, writes keypad pin configuration registers through regmap, registers a blocking notifier for parent key events, and registers input. Event handling filters events to the chip key range, maps hardware event numbers to row/column scan codes, reports the mapped keycode with press state carried in notifier data, and syncs.

State and persistence: reserved keypad pins are tracked in the parent device until devm cleanup. Keymap, row shift, and bitmap persist in memory. Hardware pin configuration persists until device reset/reconfiguration.

Dependencies and integration: depends on MFD_ADP5585, regmap, matrix keypad helpers, firmware properties, parent blocking notifier chain, and Linux input.

Risks: keypad pin parsing must avoid collisions with other child functions; invalid special event keys are rejected only if they fall in key event ranges. Sparse row/column selections are supported but produce matrix dimensions up to the highest used row/column. Event notifier data is cast through `unsigned long`, so parent contract matters.

Test signals: firmware parsing tests for invalid/duplicate pins, sparse matrices, unlock/reset event validation, regmap write failures, parent notifier press/release events, and ADP5585 versus ADP5589 ID table coverage.
