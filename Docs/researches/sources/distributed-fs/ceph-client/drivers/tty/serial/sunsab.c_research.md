# sources/distributed-fs/ceph-client/drivers/tty/serial/sunsab.c

## Purpose
This driver supports Siemens SAB82532 DUSCC asynchronous serial controllers on Sun systems. Each chip exposes two channels, registered as `ttyS` ports through the shared Sun minor allocator.

## Important APIs, Types, And Functions
`struct uart_sunsab_port` wraps `uart_port`, mapped SAB register union, IRQ flags, DSR state, command timeouts, interrupt masks, DTR/DSR PVR bit assignments, GIS shift, chip version, and cached register values. `sunsab_pops` provides the uart-core callbacks.

`receive_chars()` handles RPF/TCD/TIME/RFO/BRK events, reads FIFO bytes, acknowledges receive completion, updates counters, processes sysrq/break, applies read/ignore masks, and returns a tty port for flip push. `transmit_chars()` reacts to ALLS/XPR interrupts, applies pending cached register updates via `sunsab_tx_idle()`, fills the transmit FIFO, issues `CMDR_XF`, wakes writers, and masks XPR when idle. `check_status()` handles DCD/CTS/DSR deltas.

`calc_ebrg()` computes SAB baud generator values. `sunsab_convert_to_sab()` translates termios into DAFO, EBRG, timeout, read/ignore masks, receiver enable, and deferred register updates.

## Control Flow
Init counts matching OF nodes, allocates channel state, registers the required minor count, then registers the platform driver. `sab_probe()` initializes both channels in one device, matches console nodes for each line, and adds both uart ports. `startup()` requests a shared IRQ, waits for command engines, resets RX/TX, clears interrupt registers, programs async mode, powers the channel, masks/unmasks selected interrupts, and marks TX idle. `shutdown()` masks interrupts, disables break and receiver, avoids power-down due known reboot crashes, and frees the IRQ.

## State And Persistence
State is per channel in `sunsab_ports`. Register programming is intentionally cached in `cached_ebrg`, `cached_mode`, `cached_pvr`, and `cached_dafo`; `SAB82532_REGS_PENDING` delays writes until transmitter idle to avoid emitting garbage. Global state includes the allocated `sunsab_ports` array and uart driver registration. No disk persistence exists.

## Dependencies And Integration Points
The driver depends on OF/platform resources, SPARC IRQ data, serial core, console core, tty flip buffers, sysrq, `suncore` minor/console helpers, and the register definitions in `sunsab.h`. It matches OF nodes named `se` or compatible `sab82532`.

## Risks
Deferred register updates are essential; writing mode/baud/data-format while TX is active can corrupt output. The stop-RX path writes `interrupt_mask1` to `imr0`, which is suspicious and should be regression-tested. Probe uses a static `inst` counter and expects init-time counting to match actual probe count. Shutdown intentionally leaves power enabled due historical crash behavior, so power-state expectations are unusual.

## Test Signals
Test dual-channel probe/remove, shared IRQ dispatch for ISR0/ISR1, RX FIFO counts for RPF/TCD/TIME/RFO, break/sysrq and `sun_do_break()`, modem status waits, termios baud and parity/stop/data changes while TX active, console setup from firmware termios, and cleanup when the second channel fails to add.
