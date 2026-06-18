## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fintek.c

Purpose: Super I/O companion probe for Fintek LPC/eSPI multi-UART chips. It is invoked by 8250 PNP/legacy probing to identify the backing Fintek logical device, configure interrupt mode/FIFO/clocking, and attach RS485 and termios callbacks to an already discovered `uart_8250_port`.

Important APIs, types, and functions: `struct fintek_8250` stores chip ID, Super I/O base, LDN index, and unlock key. `fintek_8250_probe()` is the external entry point. `probe_setup_port()` scans common config ports (`0x4e`, `0x2e`) and keys, validates vendor/chip IDs, walks chip-specific LDN ranges, and matches the UART I/O base. `fintek_8250_rs485_config()` writes the `RS485` register. `fintek_8250_set_termios()` chooses a supported Fintek UART input clock to satisfy requested baud rates. `fintek_8250_set_irq_mode()` aligns Super I/O IRQ sharing/polarity with Linux IRQ trigger type.

Control flow: the probe temporarily enters Super I/O configuration mode with `request_muxed_region()`, matches the target UART, sets IRQ/FIFO features, exits config mode, then stores a devm-allocated private copy in `uart->port.private_data`. Handler installation is conditional on chip capabilities. Later termios and RS485 ioctls re-enter Super I/O mode briefly to update registers.

State and persistence: chip configuration is persisted in Super I/O registers until reset or firmware change. Driver runtime state is just the copied config tuple in `private_data`. The UART core owns baud, tty, and RS485 user-visible state.

Dependencies and integration points: depends on raw I/O port access (`inb`/`outb`), IRQ trigger metadata, PNP/PCI-era 8250 probing, `serial8250_do_set_termios()`, and serial RS485 core validation.

Risks: config-mode access is fragile; wrong key/base scanning could touch another Super I/O, though `request_muxed_region()` reduces races. RS485 validation has non-obvious polarity constraints and delay support differs for port 0 and chip family. Unsupported baud requests are silently reverted to the old baud. Test signals: chip-ID scan on each supported Fintek PID, IRQ mode verification for level and edge interrupts, FIFO depth behavior, baud clock switching at 115200/921600/1152000/1500000, RS485 delay clamping, and concurrent Super I/O users.
