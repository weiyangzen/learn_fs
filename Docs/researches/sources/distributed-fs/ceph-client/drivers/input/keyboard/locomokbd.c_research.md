## sources/distributed-fs/ceph-client/drivers/input/keyboard/locomokbd.c

Purpose: LoCoMo keyboard driver for Sharp Zaurus Collie/Poodle PDAs. It scans a 16x8 keyboard matrix behind the LoCoMo companion chip.

Important APIs/types/functions: `struct locomokbd` stores keycodes, input, physical name, LoCoMo base, spinlock, release-detection timer, and cancel-key suspend counters. `locomokbd_scankeyboard()` drives each column and reports all row states. `locomokbd_interrupt()` acknowledges press interrupts and starts scanning. `locomokbd_timer_callback()` continues scanning until no keys remain.

Control flow: probe claims memory, initializes timer/lock/keymap, requests IRQ, and registers input. Open enables keyboard interrupt generation; close disables it. A hardware interrupt only indicates key press, so the driver scans immediately and schedules periodic scans while any key is held to detect release. Long pressing the cancel/ESC key emits `EV_PWR KEY_SUSPEND`.

State/dependencies/integration: state is the timer, suspend-jiffies/count, and LoCoMo register state. It depends on the LoCoMo bus driver, raw register helpers, input core, spinlocks, timers, and manually managed allocation/IRQ/mem-region cleanup.

Risks and test signals: `input_report_key()` is called for every matrix position, including keycode 0 entries, though key bit 0 is cleared. Long-press suspend timing depends on `SCAN_INTERVAL`. Test press-only IRQ release polling, open/close interrupt gating, memory-region conflicts, timer shutdown on remove, and cancel long press behavior.
