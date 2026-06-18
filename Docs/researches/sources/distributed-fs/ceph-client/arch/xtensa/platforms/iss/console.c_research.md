# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/console.c

Purpose: Provides a single-line ISS serial TTY and optional console backed by simulator host I/O simcalls.

Important APIs, types, and functions: `rs_open()`, `rs_close()`, `rs_write()`, `rs_poll()`, `rs_write_room()`, `rs_init()`, `rs_exit()`, `iss_console_write()`, `iss_console_device()`, `iss_console_init()`, `serial_driver`, `serial_port`, and `serial_timer`.

Control flow: Late init allocates/registers a raw tty driver named `ttyS`, links one port, and starts polling when opened. The poll timer repeatedly calls `simc_poll()`/`simc_read()` on fd 0, pushes received chars into the TTY flip buffer, and reschedules while reads remain valid. Writes call `simc_write()` on fd 1. Console init registers a `ttyS` console if enabled.

State and persistence: Maintains global tty driver/port and polling timer. No hardware FIFO state; host stdio is the backend.

Dependencies and integration: TTY core, console core, timers, ISS `simcall.h`, and simulator host read/write/poll services.

Risks: Polling is timer-driven rather than interrupt-driven; console `device` returns `serial_driver`, which must be initialized for later console use; write path assumes host accepts all bytes.

Test signals: ISS console output during boot, login/input on `ttyS0`, close/open timer behavior, and serial console registration with `CONFIG_SERIAL_CONSOLE`.
