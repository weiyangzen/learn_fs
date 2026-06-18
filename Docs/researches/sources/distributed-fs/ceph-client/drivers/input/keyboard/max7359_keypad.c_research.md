## sources/distributed-fs/ceph-client/drivers/input/keyboard/max7359_keypad.c

Purpose: Maxim MAX7359 I2C key-switch controller driver for an 8x8 matrix. It reports FIFO events and manages controller autosleep.

Important APIs/types/functions: `struct max7359_keypad` stores keycodes, input, and client. `max7359_read_reg()`/`write_reg()` wrap SMBus accesses. `max7359_interrupt()` reads one FIFO byte and reports row/column press or release. `max7359_open()` and `max7359_close()` switch between short and long autosleep.

Control flow: probe requires a nonzero IRQ, reads the initial FIFO for device presence, allocates input, builds the keymap from platform data, requests a low threaded IRQ, registers input, initializes config/debounce/interrupt/autosleep registers, and enables device wakeup. IRQ decodes row bits, column bits, and release bit, emits `MSC_SCAN`, reports the mapped key, and syncs.

State/dependencies/integration: state is minimal and volatile; controller power state persists in hardware autosleep registers. Dependencies are I2C SMBus, matrix keymap platform data, threaded IRQ, input core, and PM wake.

Risks and test signals: the IRQ handler reads only one FIFO event per interrupt, so burst behavior depends on the chip retriggering. It does not check negative FIFO read before decoding. Test FIFO empty/error handling, press/release polarity, autosleep on open/close/suspend/resume, wake IRQ enable, and keymap bounds.
