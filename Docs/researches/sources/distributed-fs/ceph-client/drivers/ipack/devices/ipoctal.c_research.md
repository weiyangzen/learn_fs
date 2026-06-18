# sources/distributed-fs/ceph-client/drivers/ipack/devices/ipoctal.c

Purpose: Implements the GE/SBS IP-OCTAL 232/422/485 IndustryPack serial board as eight dynamic raw TTY ports backed by SCC2698 DUART registers.

Important APIs/types/functions: `struct ipoctal`, `struct ipoctal_channel`, `ipoctal_probe()`, `ipoctal_inst_slot()`, `ipoctal_irq_handler()`, `ipoctal_irq_rx()`, `ipoctal_irq_tx()`, `ipoctal_write_tty()`, `ipoctal_set_termios()`, `ipoctal_hangup()`, `ipoctal_remove()`, `tty_operations ipoctal_fops`, and the IPACK device ID table.

Control flow: IPACK probe allocates board state, maps IO/INT/MEM8 spaces, resets each channel, programs default 9600 8N1 settings and block interrupt masks, allocates/registers a TTY driver, registers each channel device, and requests the carrier slot IRQ. The IRQ handler acknowledges the IPACK interrupt, scans all eight channels, drains RX FIFO into tty flip buffers with error flags, and pushes one TX byte per interrupt from the xmit buffer.

State and persistence: Per-channel state tracks stats, TX ring counters, tty port, register pointers, board ID, interrupt masks, and RX enable state. Carrier lifetime is pinned during tty install/cleanup through `ipack_get_carrier()` and `ipack_put_carrier()`. Removal frees the slot IRQ, unregisters TTY devices/driver, frees xmit buffers, and releases state.

Dependencies/integration: Depends on IPACK bus operations, TTY core, serial termios, `scc2698.h`, MMIO mapping, interrupt callbacks, and board IDs from IPACK headers.

Risks and test signals: Test all three board variants, half-duplex RS-485 RTS/RX transitions, termios changes while open, TX ring wrap/full behavior, RX error statistics, partial TTY registration failure cleanup, carrier removal with open ports, and the `i <= PAGE_SIZE - nb_bytes` copy condition near buffer-full boundaries.
