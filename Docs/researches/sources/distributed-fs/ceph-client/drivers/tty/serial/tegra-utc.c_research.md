# sources/distributed-fs/ceph-client/drivers/tty/serial/tegra-utc.c

## Purpose
This is the NVIDIA Tegra UART Trace Controller driver. It exposes up to 16 `ttyUTC` ports backed by separate RX and TX MMIO client register blocks and supports interrupt-driven tty IO, console polling, earlycon, and nbcon console output.

## Important APIs, Types, And Functions
`struct tegra_utc_port` contains optional console object, `uart_port`, RX/TX base mappings, IRQ masks, FIFO size, and RX/TX thresholds. `tegra_utc_uart_ops` implements TX empty, start/stop TX, stop RX, startup/shutdown, fixed termios, and optional poll operations.

`tegra_utc_init_tx()` and `tegra_utc_init_rx()` configure enable, FIFO thresholds, command reset/flush, interrupt clear/mask/set, and client enable. `tegra_utc_tx_chars()` uses `uart_port_tx()` to feed bytes until TX FIFO full. `tegra_utc_rx_chars()` drains up to 256 RX chars, accounts overflow, handles sysrq outside the port lock, inserts tty chars, and pushes flip buffers. `tegra_utc_isr()` loops over masked RX and TX interrupt status until drained.

## Control Flow
Module init registers a global uart driver and platform driver. Probe reads required `tx-threshold` and `rx-threshold`, obtains SoC FIFO size from match data, maps named `tx` and `rx` resources, calls `tegra_utc_setup_port()` and `uart_read_port_properties()`, stores drvdata, adds the port, and registers console if configured. `startup()` initializes hardware then requests a dedicated IRQ. `shutdown()` disables RX and frees the IRQ. Remove unregisters console and removes the port; module exit unregisters drivers.

Console flow includes earlycon setup for `nvidia,tegra264-utc`, atomic nbcon writes that burst by FIFO occupancy, threaded nbcon writes that poll FIFO space byte-by-byte, and console device lock/unlock wrappers around the uart port lock.

## State And Persistence
Per-device state is in `tegra_utc_port`, especially IRQ masks and thresholds. Hardware state is initialized on startup, poll init, console setup, and earlycon setup. No persistent storage exists.

## Dependencies And Integration Points
The driver depends on platform/OF matching `nvidia,tegra264-utc`, named resources `tx` and `rx`, device properties for thresholds and uart port properties, serial core, tty flip buffers, console/nbcon/earlycon, and MMIO polling helpers.

## Risks
Probe logs setup errors but does not return immediately after `tegra_utc_setup_port()` failure before registering the port, which may be a real bug. Termios forcibly clamps to 8-N-1 with no flow control, so user-requested settings are ignored. RX/TX interrupt loops rely on correct mask/set/clear semantics. Early/console paths must not overflow FIFO; atomic write bursts depend on accurate occupancy. `port.type` uses `PORT_TEGRA_TCU`, which may be intentional reuse or a type-reporting mismatch.

## Test Signals
Test probe with missing threshold properties, named resource failures, `uart_read_port_properties()` failure, IRQ request failure, RX/TX interrupt drain, overflow accounting, sysrq, stop_rx mask behavior, fixed termios enforcement, poll get/put, earlycon output, nbcon atomic/threaded output under FIFO pressure, suspend-like shutdown/startup cycles, and remove/module-exit cleanup.
