# sources/distributed-fs/ceph-client/drivers/tty/serial/suncore.c

## Purpose
This file is the shared Sun serial support layer used by multiple SPARC serial drivers. It centralizes dynamic minor allocation, firmware console matching and termios extraction, and legacy Sun mouse baud-rate detection.

## Important APIs, Types, And Functions
`sunserial_register_minors()` assigns a contiguous minor range starting at `sunserial_current_minor`, grows `drv->nr`, registers the uart driver on first use, and adjusts `tty_driver->name_base`. `sunserial_unregister_minors()` shrinks the range and unregisters when the last user leaves. `sunserial_console_match()` wires a console into a driver, compares the device node to `of_console_device`, optionally validates A/B line selection, and adds a preferred console when the command line did not already select one.

`sunserial_console_termios()` parses firmware properties such as `ttyX-mode`, `ssp-console-modes`, and LOM defaults into `console->cflag`. `suncore_mouse_baud_cflag_next()` rotates mouse baud rates through 1200, 2400, 4800, and 9600. `suncore_mouse_baud_detection()` watches break patterns and the 0x87 byte to decide whether mouse baud should advance.

## Control Flow
Sun serial drivers call `sunserial_register_minors()` during module init once they count firmware nodes, call `sunserial_console_match()` during per-device probe, and call `sunserial_console_termios()` from console setup. Keyboard/mouse drivers call the mouse helpers in their RX interrupt paths when breaks indicate mismatched baud.

## State And Persistence
`sunserial_current_minor` is process-global in kernel memory and tracks assigned minors across Sun serial driver registrations. Mouse detection stores `mouse_got_break` and `ctr` as static state shared across calls. There is no persistent storage.

## Dependencies And Integration Points
The file depends on serial core, console core, OF PROM data, `of_console_device`, `of_console_options`, and `linux/sunserialcore.h` exports. It is consumed by `sunsu`, `sunsab`, `sunzilog`, and `sunhv`.

## Risks
Minor accounting is global and assumes balanced register/unregister calls with the original count. Console matching depends on firmware naming and A/B line offset conventions. `sunserial_console_termios()` performs minimal validation and ignores handshake fields. Mouse baud detection is global static state, so concurrent mouse-like streams could interfere.

## Test Signals
Validation should include multiple Sun serial drivers registering in one boot, console node matching with and without command-line console, A/B line offset handling, RSC/LOM/default termios parsing, and mouse break-driven baud rotation.
