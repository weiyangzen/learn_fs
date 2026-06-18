## sources/distributed-fs/ceph-client/drivers/input/keyboard/max7360-keypad.c

Purpose: MAX7360 MFD keypad child driver. It uses the parent regmap and `intk` IRQ to report matrix FIFO events with firmware-described keymap and dimensions.

Important APIs/types/functions: `struct max7360_keypad` holds input, row/col count, debounce, IRQ, regmap, and keycodes. `max7360_keypad_irq()` drains/handles a FIFO event. `max7360_keypad_parse_fw()` reads matrix dimensions, autorepeat, and debounce. `max7360_keypad_build_keymap()` reads the parent `linux,keymap`. Open/close manipulate `MAX7360_CFG_SLEEP`.

Control flow: probe gets parent regmap and named IRQ, parses parent firmware properties, allocates input, builds keymap, requests a threaded IRQ, registers input, initializes debounce and interrupt timing, then enables wakeup via `dev_pm_set_wake_irq()`. IRQ reads `MAX7360_REG_KEYFIFO`, skips overflow by polling for a non-overflow value, ignores empty FIFO, decodes row/col/release fields, and reports the mapped key.

State/dependencies/integration: state lives in regmap-backed hardware and input keycodes. It depends on MAX7360 MFD definitions, regmap, firmware properties on the parent node, input matrix helpers, threaded IRQ, and PM wake IRQ helpers.

Risks and test signals: keymap parsing deliberately reads from `dev->parent`, so child/parent firmware layout must match. Overflow recovery drops unknown events. Test parent property lookup, debounce bounds, sleep bit polarity, overflow and empty FIFO behavior, wake IRQ setup/clear, and unsupported dimensions.
