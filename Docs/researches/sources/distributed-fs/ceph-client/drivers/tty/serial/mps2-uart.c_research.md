# sources/distributed-fs/ceph-client/drivers/tty/serial/mps2-uart.c

## Purpose

`mps2-uart.c` is the serial-core driver for the ARM MPS2 UART exposed as `ttyMPS`. It provides platform/OF probing for `"arm,mps2-uart"`, normal and early console support, and a small interrupt-driven RX/TX implementation over a minimal register set: data, state, control, interrupt status/ack, and baud divider.

The hardware model is simple: fixed 8N1 framing, no modem-control hardware, a one-byte effective FIFO, and either one combined IRQ or separate RX/TX/overrun IRQs depending on platform description.

## Important APIs, Types, And Functions

`struct mps2_uart_port` wraps `struct uart_port` with a clock, TX/RX IRQ numbers, and a `flags` field containing `UART_PORT_COMBINED_IRQ`. `ports_idr` maps line numbers to port objects for console setup and write paths.

Register helpers `mps2_uart_write8()`, `mps2_uart_read8()`, and `mps2_uart_write32()` centralize MMIO access. The serial operations are in `mps2_uart_pops`: `tx_empty`, modem controls, `start_tx`, `stop_tx`, `stop_rx`, `startup`, `shutdown`, `set_termios`, type/config/request/verify hooks.

Interrupt handlers are split into `mps2_uart_rxirq()`, `mps2_uart_txirq()`, `mps2_uart_oerrirq()`, and `mps2_uart_combinedirq()`. Data movement is handled by `mps2_uart_rx_chars()` and `mps2_uart_tx_chars()`, the latter using `uart_port_tx()`.

Probe is composed of `mps2_of_get_port()`, `mps2_init_port()`, and `mps2_serial_probe()`. Console paths are `mps2_uart_console_write()`, `mps2_uart_console_setup()`, and early console handlers declared with `OF_EARLYCON_DECLARE()`.

## Control Flow

`mps2_uart_init()` registers the UART driver and the platform driver at `arch_initcall`. Probe allocates a managed port, chooses a line from the `serial` alias or cyclic IDR allocation, notes whether there is one combined IRQ, maps registers, prepares enough clock state to capture `uartclk`, records IRQs, and calls `uart_add_one_port()`.

Startup masks TX/RX groups, requests either the combined IRQ or the overrun/RX/TX IRQ trio, and then enables RX and TX plus their interrupt and overrun bits. Shutdown clears those enable bits and frees the corresponding IRQs.

TX begins by enabling TX interrupt and immediately calling `mps2_uart_tx_chars()` to prime the hardware. TX IRQ acknowledges `UARTn_INT_TX` and continues sending while `mps2_uart_tx_empty()` reports room. RX IRQ acknowledges `UARTn_INT_RX`, drains bytes while `UARTn_STATE_RX_FULL` is set, inserts them as `TTY_NORMAL`, and pushes the flip buffer. Overrun IRQ inserts `TTY_OVERRUN` for RX overruns and acknowledges unexpected TX overruns.

Termios enforces hardware limits by clearing CRTSCTS/CMSPAR, forcing CS8, no parity, and one stop bit. It computes a rounded baud divider from `uartclk`, writes `UARTn_BAUDDIV`, updates timeouts, and encodes the actual baud back into termios.

## State And Persistence Behavior

State is in the allocated `mps2_uart_port`, the IDR line mapping, and hardware registers. There is no persistent storage. The clock is enabled only temporarily in probe to read the rate; startup does not enable/disable it, so the platform clock topology must keep the UART usable after probe-time rate discovery.

Console lookup depends on `ports_idr` retaining the port object for a given index. The driver has no remove path, and the platform driver suppresses bind attributes, matching the assumption that these platform UARTs are not dynamically unbound.

## Dependencies And Integration Points

The driver uses Linux serial core, tty flip buffers, console/earlycon, OF/platform helpers, clocks, IDR allocation, and MMIO primitives. The device-tree binding supplies register resources, clock, interrupts, and optional serial alias. It registers `ttyMPS` with up to `MPS2_MAX_PORTS` ports.

## Risks And Edge Cases

The driver has no `remove` function and no IDR cleanup path, which is acceptable for non-hotpluggable platform devices but would be wrong for dynamic unbind. `mps2_uart_console_write()` assumes `idr_find()` succeeds and dereferences the result without a null check.

The separate-IRQ startup path requests the overrun IRQ as shared but RX/TX IRQs as non-shared; mismatched firmware IRQ descriptions will fail startup. Combined IRQ handling returns after the first handled source, so simultaneous RX/TX/overrun causes are serviced over multiple IRQ entries rather than one pass.

Because termios silently forces 8N1 and no flow control, tests expecting parity, stop-bit, or CRTSCTS behavior must assert that unsupported flags are cleared rather than applied.

## Test Signals

Boot with normal and early consoles on `"arm,mps2-uart"`, validate serial alias and cyclic IDR line assignment, test both one-IRQ and three-IRQ device-tree layouts, verify RX overrun reporting, confirm baud divider programming over the accepted range, and run TX/RX loopback under interrupt load. Static checks should flag the console null-dereference possibility and the missing remove/IDR cleanup if hot-unbind support is ever introduced.
