# sources/distributed-fs/ceph-client/drivers/tty/serial/milbeaut_usio.c

## Purpose

`milbeaut_usio.c` is the Socionext Milbeaut USIO UART driver. It manages a compile-time fixed array of platform UART ports, split RX/TX IRQs, FIFO setup, optional auto-flow-control property support, console and earlycon output, and clock-based baud generation.

## Important APIs, Types, and Functions

The driver uses static `mlb_usio_ports[]` and `mlb_usio_irq[][RX/TX]` arrays rather than a private wrapper type. `mlb_usio_ops` implements serial-core methods. Key functions include `mlb_usio_tx_chars()`, `mlb_usio_start_tx()`, `mlb_usio_rx_chars()`, `mlb_usio_rx_irq()`, `mlb_usio_tx_irq()`, `mlb_usio_startup()`, `mlb_usio_set_termios()`, `mlb_usio_probe()`, console helpers, and `mlb_usio_init()/exit()`.

## Control Flow

Module init registers the UART driver and platform driver. Probe enables the device clock, reads the `index` property to select the static port, maps registers, records named RX/TX IRQs, initializes serial-core fields, and adds the port. Startup requests separate RX and TX IRQs, applies optional auto-flow-control to ESCR, resets SCR/SSR/FCR/FBYTE, enables FIFOs, and enables TX/RX plus RX/TX buffer interrupts. RX IRQ drains up to a small count or FIFO-reported amount, handles parity/overrun/frame/break flags, resets error state, and pushes flip data. TX fills FIFO space from x_char or xmit FIFO and controls FCR/SCR TX interrupt bits.

## State and Persistence Behavior

State persists in static arrays keyed by DT `index`; the clock pointer is stored in `port->private_data`. Runtime status is mostly hardware register state and serial-core masks/counters. Removal uses `pdev->id` to select the port, while probe uses the `index` property, so platform IDs and DT indices must align.

## Dependencies and Integration Points

Dependencies include platform/OF, named IRQs, common clock framework, serial core, console/earlycon, and MMIO accessors. Compatible string is `socionext,milbeaut-usio-uart`; optional property `auto-flow-control` affects startup, termios, and console setup.

## Risks and Edge Cases

Probe does not validate negative results from `platform_get_irq_byname()` before storing them. Remove indexes by `pdev->id`, which may not equal the DT `index`. `mlb_usio_rx_chars()` only increments frame/parity/overrun counters for some statuses and uses nested conditionals that can leave `flag` from a previous iteration if not reset carefully. Startup/shutdown do not disable the clock until remove.

## Test Signals

DT index bounds and remove alignment, missing named IRQs, auto-flow-control property and CRTSCTS termios, RX parity/frame/overrun/break paths, TX FIFO refill and wakeup thresholds, console/earlycon output, clock enable failure, and multiple configured ports.
