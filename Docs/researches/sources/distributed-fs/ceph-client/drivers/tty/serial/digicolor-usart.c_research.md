# sources/distributed-fs/ceph-client/drivers/tty/serial/digicolor-usart.c

Purpose: Conexant Digicolor USART platform serial driver for up to three `ttyS` ports. It provides interrupt-driven TX/RX, console support, and a delayed-work RX polling workaround for hardware whose RX interrupt threshold cannot be lowered below half FIFO.

Important APIs/types/functions: `struct digicolor_port` embeds `uart_port` and `delayed_work rx_poll_work`; `digicolor_ports[]` backs console lookup; `digicolor_uart_ops` supplies callbacks. Key routines are `digicolor_uart_rx()`, `digicolor_uart_tx()`, `digicolor_uart_int()`, `digicolor_rx_poll()`, `digicolor_uart_startup()`, `digicolor_uart_shutdown()`, `digicolor_uart_set_termios()`, and `digicolor_uart_probe()`.

Control flow: init optionally attaches console, registers UART/platform drivers. Probe requires DT and a `serial` alias, maps MMIO, gets clock and IRQ, initializes the port/work item, requests IRQ, and adds the port. Startup enables the peripheral, soft-resets it, configures FIFO mode/thresholds, enables RX/TX interrupts, and schedules 100 ms polling. Poll work forces RX interrupt if bytes are waiting below threshold. IRQ clears flags and dispatches RX/TX.

State/persistence: state is per-port memory, delayed work, and hardware registers. Termios is encoded in config/divisor registers and serial-core masks. No disk persistence.

Dependencies/integration: DT compatible `cnxt,cx92755-usart`, platform resources, clocks, workqueues, serial core, TTY flip buffers, and console core.

Risks: low-rate RX latency depends on 100 ms polling. Modem control is effectively stubbed with CTS always reported. Break control is empty. Error classification uses `else if`, so one dominant error flag wins. `ttyS` naming can collide if platform numbering is wrong.

Test signals: low-rate RX below FIFO threshold, work cancellation on shutdown/remove, TX interrupt disable on idle, console output/setup, baud limits, parity/frame/overrun reporting, DT alias bounds, and missing-DT failure.
