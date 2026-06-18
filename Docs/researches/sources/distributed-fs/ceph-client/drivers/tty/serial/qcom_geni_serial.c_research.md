# sources/distributed-fs/ceph-client/drivers/tty/serial/qcom_geni_serial.c

## Purpose

`qcom_geni_serial.c` is the UART driver for Qualcomm GENI/QUP serial engines. It exposes two UART personalities through serial core: a FIFO-mode debug console device named `ttyMSM` for `qcom,geni-debug-uart` compatibles, and DMA-mode high-speed UART devices named `ttyHS` for `qcom,geni-uart` compatibles. It also handles SA8255P variants where baud/performance selection is driven through power-domain performance levels rather than direct GENI clock programming.

## Important APIs, Types, and Functions

`struct qcom_geni_serial_port` is the main per-port state: `uart_port`, `geni_se`, FIFO geometry, DMA addresses, setup flag, clock/poll timeout, RX buffer, swap/flow-control flags, RS485 state helpers, active TX accounting, wake IRQ, private serial-driver data, device match data, and optional power-domain list. `struct qcom_geni_device_data` selects console versus UART mode, GENI transfer mode, resource initialization, rate-setting, and power-state callbacks. `struct qcom_geni_private_data` carries the associated `uart_driver` and byte caches for poll/console paths.

Key UART operations are split by mode. Console ports use `qcom_geni_console_pops` with FIFO `start_tx`, `stop_tx`, `start_rx`, `stop_rx`, poll callbacks, and console write support. Non-console ports use `qcom_geni_uart_pops` with DMA `start_tx`, `stop_tx`, `start_rx`, and `stop_rx`. `qcom_geni_serial_port_setup()` loads UART firmware if needed, stops RX, discovers FIFO depths, configures RX stale count, optional pin swaps, packing, watermarks, and selected FIFO/DMA mode. `qcom_geni_serial_set_termios()` programs baud, parity, word length, stop bits, CTS masking/manual flow, loopback, timeout accounting, and clock/interconnect votes. `qcom_geni_serial_isr()` is the shared interrupt path for FIFO and DMA events.

## Control Flow

Probe resolves OF match data, chooses the console or high-speed UART driver, obtains a stable line number through serial aliases/IDA allocation, maps resources through serial core request/config callbacks, initializes GENI resources or SA8255P power domains, allocates a DMA RX buffer for high-speed ports, requests the IRQ with `IRQ_NOAUTOEN`, parses optional wake IRQ and pin-swap properties, gets RS485 defaults, enables runtime PM, and registers the UART port.

Startup lazily runs port setup, starts RX using the selected mode, and enables the main IRQ. FIFO RX starts a secondary GENI command and enables RX FIFO watermark/last interrupts. DMA RX starts the secondary command with RFR open and prepares a fixed 2048-byte DMA buffer. TX uses either FIFO watermark interrupts and `uart_fifo_out()` chunks or a DMA mapping prepared from the linear xmit FIFO tail. The ISR clears GENI/DMA statuses first, updates error counters and break/parity/drop state, completes DMA TX/RX, restarts RX DMA, drains RX FIFO for console paths, and feeds TX FIFO until the active command is complete.

Console write disables GENI master/secondary interrupts, handles any active transmit command by waiting or draining, cancels the command, writes the full console string through FIFO words with newline expansion, waits for completion, restores interrupt enables, and releases the port lock. Early console setup assumes firmware is already UART, cancels stale TX/RX state, configures packing/FIFO mode and 8N1-like defaults, and installs early read/write callbacks when configured.

## State and Persistence Behavior

There is no filesystem persistence. Long-lived state is the allocated `qcom_geni_serial_port`, IDA line ownership, GENI hardware state, FIFO/DMA accounting, optional wake IRQ state, selected clock/performance level, and runtime PM/interconnect votes. Hardware state persists across open/close while the device is powered: sequencer commands, watermarks, transfer configuration, pin swap, loopback, manual RFR, and baud clock selection. Suspend routes through serial core; console suspend also changes interconnect tagging to allow lower-power suspend even with `no_console_suspend`.

## Dependencies and Integration Points

The driver depends on platform devices, OF match data, Qualcomm GENI serial-engine helpers, QUP wrapper state from the parent, clocks or OPP/performance domains, interconnect bandwidth APIs, runtime/system PM, wake IRQ infrastructure, serial core, tty flip buffers, DMA helpers in the GENI SE layer, and optional console/earlycon/poll support. It integrates with RS485 via `uart_port.rs485_config`, with DT properties `rx-tx-swap` and `cts-rts-swap`, and with serial aliases `serial`/`hsuart`.

## Risks and Edge Cases

The FIFO console path can lose the current console payload if a TX watermark never appears; it cancels/aborts the command after timeout. DMA RX uses a fixed buffer and immediately re-prepares it after each completion, so bad DMA residue or missing `RX_EOT` can stall reception. `qcom_geni_serial_stop_rx_dma()` polls for `RX_EOT` and falls back to sequencer abort/reset, but failure to see reset completion is not strongly surfaced. Error handling intentionally drops RX data on parity/general-purpose error IRQs, which is safe but coarse. Probe error paths detach power domains but line IDA cleanup is only explicit in some wake-IRQ failure/remove paths, so line allocation paths should be reviewed when adding new failures. Polling paths rely on bounded udelay loops and may be used before full timer infrastructure during early console.

## Test Signals

Useful tests include OF probe for console, UART, and SA8255P compatibles; alias and IDA line allocation; FIFO console boot/earlycon/poll read/write; DMA TX/RX under sustained traffic; RX timeout/EOT/parity/break/overrun paths; RS485 RTS polarity before and after send; CRTSCTS/manual flow transitions; loopback and pin-swap properties; runtime suspend/resume; system suspend/resume with and without console; wake IRQ behavior; DMA preparation failure; firmware load failure; and high baud rates that drive OPP and interconnect vote changes.
