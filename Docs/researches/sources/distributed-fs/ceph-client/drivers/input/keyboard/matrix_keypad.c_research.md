## sources/distributed-fs/ceph-client/drivers/input/keyboard/matrix_keypad.c

Purpose: generic GPIO-driven matrix keypad platform driver. It scans row/column GPIO matrices with debounce and optional wakeup support.

Important APIs/types/functions: `struct matrix_keypad` stores input, row shift, timing properties, row/column GPIO descriptors, row IRQs, wake IRQ bitmap, last column state, delayed work, spinlock, and stopped/scan flags. `matrix_keypad_scan()` performs the column scan and reports diffs. `matrix_keypad_interrupt()` gates row IRQs and schedules debounce work. `matrix_keypad_start()`/`stop()` manage scan lifecycle.

Control flow: probe reads timing and drive-mode properties, gets GPIOs, normalizes active-low settings, requests row IRQs initially disabled, builds keymap, registers input, and initializes wakeup. Opening schedules an immediate scan that activates columns and enables row IRQs. Row IRQs disable all row IRQs and schedule delayed work. The worker reads initial rows, scans each column, reports changed key states with `MSC_SCAN`, reactivates all columns, re-enables IRQs, and reschedules if rows changed during scanning.

State/dependencies/integration: state is delayed work, GPIO directions/values, row IRQ enabled state, last key matrix, and wake IRQ bitmap. Dependencies are gpiod, IRQ core, input matrix helpers, firmware properties, and PM wake hooks.

Risks and test signals: active-low normalization and `drive-inactive-cols` determine electrical behavior; wrong firmware polarity can invert all keys. The worker enables IRQs before checking post-scan row changes, so tests should cover rapid transitions. Validate suspend wake IRQs, debounce timing, sparse keymaps, GPIO acquisition failures, and row/column count limits.
