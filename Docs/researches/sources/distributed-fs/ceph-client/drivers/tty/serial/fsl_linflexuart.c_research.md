# sources/distributed-fs/ceph-client/drivers/tty/serial/fsl_linflexuart.c

Purpose: Freescale/NXP LINFlexD UART driver for up to four `ttyLF` ports. It supports interrupt-driven UART mode, termios reconfiguration through LINFlex init mode, normal console, OF early console, suspend/resume, and early-console handoff buffering.

Important APIs/types/functions: `linflex_ports[]`, `linflex_pops`, `linflex_setup_watermark()`, `linflex_startup()`, `linflex_shutdown()`, `linflex_set_termios()`, `linflex_int()`, `linflex_rxint()`, `linflex_txint()`, `linflex_transmit_buffer()`, `linflex_put_char()`, `linflex_console_write()`, `linflex_console_setup()`, and `linflex_early_console_setup()`.

Control flow: probe matches `fsl,s32v234-linflexuart`, allocates `uart_port`, reads DT serial alias, maps MMIO, gets IRQ, fills serial-core fields, stores the port, and adds it. Startup enters init mode, configures UART mode/RX/TX/interrupts, and requests IRQ. IRQ dispatches RX on data-ready and TX on transmit-empty. RX drains bytes, tracks break/frame/parity/overrun, handles SysRq, and pushes flip data. TX writes through `BDRL` and waits for completion.

State/persistence: state is hardware registers plus `uart_port`. Console builds add `earlycon_port`, `linflex_earlycon_same_instance`, `init_lock`, `during_init`, and `earlycon_buf` to preserve early output while the real console reinitializes the same hardware.

Dependencies/integration: DT compatible, platform IRQ/MMIO, serial core, TTY flip buffers, console/OF earlycon, and PM sleep helpers.

Risks: init-mode and TX-completion waits lack timeouts. Early handoff buffering can drop characters on atomic allocation failure or cap. Modem and break control are stubs. Error flag propagation is less complete than termios masks imply.

Test signals: same-instance earlycon handoff, console setup without options, CS7/CS8/parity combinations, unsupported mode mutation, RX break/error paths, suspend/resume, and IRQ TX/RX.
