# sources/distributed-fs/ceph-client/include/linux/sunserialcore.h

Purpose: declares shared Sun serial, keyboard, mouse, and console helper interfaces for SPARC/Sun UART drivers.

Important APIs and types: keyboard constants identify reset and L1-A key sequence values. APIs include `suncore_mouse_baud_cflag_next()`, `suncore_mouse_baud_detection()`, `sunserial_register_minors()`, `sunserial_unregister_minors()`, `sunserial_console_match()`, and `sunserial_console_termios()`.

Control flow: serial drivers register UART minors, detect mouse baud changes from received bytes, match Open Firmware console nodes, and derive console termios settings.

State and persistence: state lives in UART drivers, console objects, and device tree nodes; this header stores none.

Dependencies and integration points: depends on device, serial core, console, and device tree support. It integrates legacy Sun keyboard/mouse serial behavior with the generic UART layer.

Risks and test signals: risks include minor allocation mismatches, OF console matching mistakes, keyboard escape sequence handling, and baud detection false positives. Test on Sun/SPARC serial console hardware or emulation, console handoff, keyboard L1-A handling, and mouse baud changes.
