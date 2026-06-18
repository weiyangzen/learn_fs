# sources/distributed-fs/ceph-client/drivers/tty/serial/sb1250-duart.c

## Purpose

`sb1250-duart.c` supports the dual UART blocks integrated into Broadcom/SiByte BCM1250, BCM112x, BCM1480, and related SOCs. It registers legacy `duart` tty ports, handles up to two DUART chips with two channels each, provides interrupt-driven PIO RX/TX, modem control, optional console output, and SOC-dependent register/interrupt address selection.

## Important APIs, Types, and Functions

`struct sbd_duart` owns the two `sbd_port` channels for a DUART, the shared control-register physical base, and a `refcount_t` guarding the shared MMIO reservation. `struct sbd_port` embeds `uart_port`, points back to the DUART, stores the mapped shared-control base, and tracks whether TX is stopped and whether sane defaults have been initialized. Register access is split between per-channel helpers `read_sbdchn()`/`write_sbdchn()` and shared helpers `read_sbdshr()`/`write_sbdshr()`, with an optional SB1 pass-2 workaround that reads mode registers after each access.

The `sbd_ops` UART callbacks implement TX empty, modem control, TX/RX start/stop, modem-status enable, break, startup/shutdown, termios, resource management, config, and verify. `sbd_receive_chars()` drains up to 16 RX entries per pass and maps break/framing/parity/overrun status. `sbd_transmit_chars()` handles x_char and a single FIFO byte per TX-ready IRQ. `sbd_interrupt()` loops over RX, input-change, and TX status. `sbd_probe_duarts()` statically describes available channels from `soc_type`.

## Control Flow

Module and console init both call `sbd_probe_duarts()` once. It determines two or four lines based on SOC type, fills each active `uart_port` with IRQ, 80 MHz-style UART clock, FIFO size, MMIO base, line number, ops, and sysrq capability. Serial module init registers the UART driver and adds each populated port. Config/request paths reserve per-channel MMIO and the shared control region, map both areas, set port type, and run `sbd_init_port()` to reset TX/RX, program 8-bit defaults, clear OPCR/AUXCTL, and mask interrupts.

Startup requests the shared IRQ, drains RX, clears break/input-change state, configures RX/TX interrupt modes to FIFO-available behavior, disables TX, enables RX, marks TX stopped, and enables input-change plus RX interrupts. The interrupt handler reads shared ISR and IMR, filters all DUART status bits, dispatches RX, input-change, and TX handlers, and stops after 16 passes to avoid livelock. Termios drains active TX if needed, disables TX/RX, rewrites mode registers, baud generator, AUX CTS-change setting, read/ignore masks, and then re-enables RX and optionally TX based on current state.

## State and Persistence Behavior

There is no filesystem persistence. State is static in `sbd_duarts[]`, with per-port initialization flags, TX-stopped flags, shared-region reference counts, mapped MMIO pointers, and serial-core state. Hardware state includes mode registers, baud generator, interrupt masks, output port bits, AUX control, FIFOs, and break state. Console setup can map and initialize a port before normal serial registration.

## Dependencies and Integration Points

The driver depends on SiByte SOC headers for register addresses, interrupt numbers, UART bit definitions, and `soc_type`; raw 64-bit MMIO accessors; serial core; tty flip buffers; sysrq; console infrastructure; and legacy tty major/minor allocation. It has compile-time branches for BCM1480 versus SB1250/BCM112x register layouts and optional SB1 pass-2 workarounds.

## Risks and Edge Cases

The driver is highly platform-specific and relies on static SOC globals rather than platform devices. Shared control-region reservation is refcounted, so mismatched request/release paths can leak or prematurely release the shared region. The code uses bounded polling loops for RX/TX drain and console output; if hardware never reaches ready/empty, data can be dropped after timeout or console can stall for the loop duration. TX interrupt handling writes only one byte per pass, which is simple but may limit throughput. CS5/CS6 are unsupported and leave part of the previous mode unchanged. There is no runtime PM or hotplug discovery.

## Test Signals

Test SOC-type based two-line and four-line enumeration, request/release of two channels sharing one control region, SB1 workaround builds, startup/shutdown IRQ behavior, RX status mapping for break/frame/parity/overrun, modem input-change wakeups, DTR/RTS/loopback output bits, termios baud bounds and CS7/CS8 behavior, CREAD disable, CRTSCTS AUX updates, console setup/write/restore of TX interrupt state, and init/exit removing ports in reverse order.
