## sources/distributed-fs/ceph-client/drivers/input/keyboard/hilkbd.c

Purpose: basic HP Human Interface Loop keyboard driver for HP300 and selected PA-RISC HP700 systems. It exposes a single `input_dev` named `HIL keyboard` on `BUS_HIL` and translates HIL set-1 scancodes through `hphilkeyb_keycode`.

Important APIs/types/functions: the central state is the file-static `hil_dev` with input device, current HIL device id, 16-byte packet buffer, spinlock, and native bus `dev_id`. `hil_interrupt()` decodes status/data/command response nibbles, `handle_status()` and `handle_data()` assemble poll blocks, `poll_finished()` reports key state, and `hil_do()` serializes HIL command writes. Platform integration is split between a PA-RISC `parisc_driver` and HP300 direct I/O region setup.

Control flow: init claims the IRQ, enables HIL interrupts, sends `HIL_READKBDSADR`, attempts to discover the keyboard, switches keyboard addressing to raw mode, registers input capabilities, then registers the input device. Runtime is interrupt driven: status bytes mark block start/end, data bytes fill the circular packet buffer, and block completion reports a key press/release from packet type `0x40`.

State/dependencies/integration: persistent state is only in RAM plus HIL hardware interrupt/config state. It depends on architecture-specific HIL MMIO accessors, `linux/hil.h` keycode tables, the input core, and PA-RISC/HP300 bus discovery.

Risks and test signals: `hil_keyb_init()` waits on a local wait queue that the IRQ path never wakes, so discovery can always wait for the timeout even if `hil_dev.valid` changes. `poll_finished()` calls `input_report_key()` without a local `input_sync()`, so event delivery depends on later synchronization. Tests should cover IRQ block framing, raw-mode command ordering, module unload interrupt disable/free, and architecture-specific init paths.
