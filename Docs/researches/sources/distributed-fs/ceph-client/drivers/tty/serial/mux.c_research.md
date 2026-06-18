# sources/distributed-fs/ceph-client/drivers/tty/serial/mux.c

## Purpose

`mux.c` is the PA-RISC Serial MUX driver for Mux console hardware found in some HP PA-RISC servers. It registers `ttyB` ports on `MUX_MAJOR`, maps up to 256 MUX lines, and uses a polling timer rather than hardware IRQs to move data between the MUX FIFOs and the tty layer.

The file comments note that the driver currently supports console functionality on MUX port 0 and that full MUX functionality would need additional work. In practice the code registers all detected ports, but the implementation remains minimal: no real termios changes, modem controls, start/stop operations, or hardware IRQ integration.

## Important APIs, Types, And Functions

`struct mux_port` contains a `uart_port` and an `enabled` flag. Global state is `mux_ports[MUX_NR]`, `port_cnt`, `mux_driver`, and `mux_timer`. MMIO access is via `UART_PUT_CHAR()` and `UART_GET_FIFO_CNT()` plus direct raw reads of the data register.

`get_mux_port_count()` reads PA-RISC IODC data to determine port count and special-cases K-Class built-in MUX hardware to one connected port. `mux_read()` drains RX data/status words and handles break/sysrq. `mux_write()` uses `uart_port_tx_limited()` and waits for `mux_tx_done()` after writes. `mux_poll()` periodically services enabled ports.

Serial-core operations are in `mux_pops`, with many no-op hooks because the hardware/driver does not support modem control, termios, stop/start, or break control. Console support is `mux_console_write()` and `mux_console_setup()`.

Platform integration uses PA-RISC device tables `builtin_mux_tbl` and `mux_tbl`, drivers `builtin_serial_mux_driver` and `serial_mux_driver`, and lifecycle functions `mux_probe()`, `mux_remove()`, `mux_init()`, and `mux_exit()`.

## Control Flow

`mux_init()` registers the built-in MUX driver first, then the generic add-in MUX driver, preserving desired detection order. If any ports were probed, it starts `mux_timer` to run every `MUX_POLL_DELAY` and registers the console when configured.

`mux_probe()` determines port count, requests the MUX memory region, registers the UART driver on the first detected device, then initializes and maps each port line at `dev->hpa.start + MUX_OFFSET + i * MUX_LINE_OFFSET`. Each port is added with `uart_add_one_port()`, `PORT_MUX`, `UPF_BOOT_AUTOCONF`, FIFO size 255, and no IRQ.

Open/startup sets `mux_ports[line].enabled = 1`; shutdown clears it. The timer loops through `port_cnt`, skips disabled lines, calls `mux_read()` and then `mux_write()`, and rearms itself.

RX reads the data register until an EOFIFO marker appears. Status words are skipped. Break markers update break counters and invoke `uart_handle_break()`. Normal bytes pass through sysrq handling and enter the tty flip buffer. TX writes as much as fits based on FIFO count and then waits for FIFO drain in `mux_tx_done()`.

Removal finds the first port for the device by matching `mapbase`, removes each UART port, unmaps the line, and releases the memory region. Exit deletes the timer, unregisters console if needed, unregisters both PA-RISC drivers, and unregisters the UART driver.

## State And Persistence Behavior

State is entirely in static kernel memory and mapped device registers. `port_cnt` monotonically increases during probe and is used as both the number of registered lines and the next insertion index. `enabled` gates timer servicing for opened ports. There is no disk persistence.

The poll timer is global across all MUX devices. The driver assumes `port_cnt` and the static `mux_ports` layout remain coherent for the module lifetime. Remove does not compact `mux_ports` or reduce `port_cnt`, which is consistent with rare/non-hotplug PA-RISC hardware but important for any dynamic-unbind assumptions.

## Dependencies And Integration Points

This driver depends on PA-RISC platform APIs (`struct parisc_device`, `pdc_iodc_read()`, PA-RISC device tables), serial core, tty flip buffers, sysrq, console, timers, raw MMIO, and memory-region APIs. It exposes `ttyB` devices and a console when `CONFIG_SERIAL_MUX_CONSOLE` is enabled.

## Risks And Edge Cases

`get_mux_port_count()` calls `BUG_ON(status != PDC_OK)`, so malformed firmware reads panic the kernel rather than failing probe. `mux_probe()` calls `BUG_ON(status)` after `uart_add_one_port()`, making add failures fatal.

`request_mem_region()` return value is ignored. `ioremap()` result is not checked before use. Removal does not decrement `port_cnt`, clear mappings in the global array, or unregister the UART driver when the last device is removed outside module exit.

TX is polling and can busy-wait in `mux_tx_done()` until FIFO count reaches zero. The global timer services all enabled ports serially, so one slow or wedged port can delay others. Termios and modem controls are no-ops, so serial settings are effectively fixed.

## Test Signals

Test on PA-RISC systems with built-in and add-in MUX hardware, verifying built-in detection order and K-Class one-port override. Exercise console output on `ttyB0`, RX break/sysrq handling, timer polling under sustained RX/TX, open/close toggling of `enabled`, and module unload cleanup. Static review should focus on unchecked resource acquisition, fatal `BUG_ON()` paths, and behavior after device removal.
