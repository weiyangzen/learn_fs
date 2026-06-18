# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_tegra.c

## Purpose
Implements 8250 glue for NVIDIA Tegra UARTs, including Tegra-specific break handling, clock/reset management, DT/ACPI matching, and console-aware suspend/resume.

## Important APIs, Types, And Functions
`struct tegra_uart` stores the clock, optional shared reset control, and 8250 line number. `tegra_uart_handle_break()` drains RX while FIFO/error/break bits remain set to clear Tegra break/error conditions. `tegra_uart_probe()` builds a `PORT_TEGRA` `uart_8250_port`, maps memory, reads firmware port properties, gets optional reset and clock resources, deasserts reset, and registers the port. Remove and PM callbacks unregister/suspend/resume through 8250 and manage reset/clock state.

## Control Flow
Probe allocates private state, initializes the embedded `uart_port` lock, sets `UPF_BOOT_AUTOCONF | UPF_FIXED_PORT | UPF_FIXED_TYPE`, installs `handle_break`, maps the MMIO resource with `devm_ioremap()`, reads port properties, configures `UPIO_MEM32`/`regshift = 2`, gets an optional shared reset, and either uses firmware-provided `uartclk` or enables a clock and derives it. Reset is deasserted before `serial8250_register_8250_port()`. Suspend delegates to 8250 and disables the clock unless the port is an active console with console suspend disabled; resume mirrors that order.

## State And Persistence
Runtime state is in `tegra_uart` and the 8250 core's port. Clock enablement may persist across suspend for active consoles. Reset state is asserted on remove and probe failure after registration failure. There is no file-backed persistence.

## Dependencies And Integration Points
Depends on platform devices, OF compatible `nvidia,tegra20-uart`, ACPI ID `NVDA0100`, reset controls, clocks, console state helpers, `uart_read_port_properties()`, and the 8250 core's `PORT_TEGRA` entry.

## Risks And Test Signals
Risks include break-drain timeout behavior, clock handling when `uartclk` is firmware-provided but `uart->clk` is NULL, console suspend corner cases, and reset assertion ordering. Test signals include DT and ACPI probe, RX break handling without interrupt storms, suspend/resume with console and non-console ports, remove after registration, and baud correctness when the clock is supplied by firmware versus the clock framework.
