# sources/distributed-fs/ceph-client/drivers/tty/serial/men_z135_uart.c

## Purpose

`men_z135_uart.c` drives MEN 16z135 high-speed UART MCB cores. It registers MCB devices as serial-core UARTs with large memory-mapped FIFOs, configurable TX/RX trigger levels, modem-status handling, and module parameters for FIFO alignment and RX timeout.

## Important APIs, Types, and Functions

`struct men_z135_port` wraps `uart_port` with MCB device/resource pointers, an RX bounce page, cached status register, lock, and automode flag. `men_z135_ops` supplies serial-core methods. Important functions are `men_z135_handle_rx()`, `men_z135_handle_tx()`, `men_z135_intr()`, `men_z135_request_irq()`, `men_z135_set_mctrl()`, `men_z135_get_mctrl()`, `men_z135_startup()`, `men_z135_set_termios()`, `men_z135_request_port()`, `men_z135_probe()`, and `men_z135_remove()`.

## Control Flow

Module init registers the UART driver and MCB driver. MCB probe allocates the port and a page-sized RX buffer, fills UART metadata, and calls `uart_add_one_port()`. Serial-core config/request maps the MCB memory resource. Startup requests a shared IRQ, enables all IRQs except TX-space-available, programs trigger levels from module params, and optionally sets RX timeout. The interrupt handler reads a destructive status/IIR register, acknowledges IRQ bits, then handles receiver line status, RX data/timeout, TX-space available, and modem status under the port lock.

## State and Persistence Behavior

Global `line` assigns monotonically increasing port lines and is decremented on remove. Per-port state includes MCB memory ownership, `rxbuf`, cached `stat_reg`, and `automode` for CRTSCTS behavior. Hardware register state includes CONF, BAUD, TIMEOUT, FIFO control pointers, and modem/LCR fields.

## Dependencies and Integration Points

The driver integrates with the MEN Chameleon Bus (`mcb_register_driver`, `mcb_request_mem`, `mcb_get_irq`), serial core, TTY flip buffers, module parameters, MMIO bulk copy helpers, and modem-control callbacks.

## Risks and Edge Cases

`men_z135_set_termios()` ORs new LCR bits into the previous value without clearing word/parity/stop fields first, so changing formats can leave stale bits. RX is capped at `MEN_Z135_FIFO_WATERMARK` to avoid crossing into TX FIFO space. `verify_port()` always rejects user serial_struct changes. The global `line` counter can reuse line numbers incorrectly if removes are not strictly LIFO.

## Test Signals

MCB probe/remove with multiple cores, RX FIFO watermark and flip-buffer truncation, TX FIFO alignment mode, configurable trigger levels and timeout, modem DCD/CTS change notifications, CRTSCTS automode, termios format changes, destructive IRQ status handling with multiple bits set, and IRQ request failure.
