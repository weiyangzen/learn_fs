# sources/distributed-fs/ceph-client/drivers/input/serio/apbps2.c

## Purpose

`apbps2.c` implements a serio driver for the GRLIB APBPS2 PS/2 controller. It exposes the big-endian MMIO APBPS2 core as a `SERIO_8042` port for keyboard or mouse devices.

## Important APIs, Types, and Functions

`struct apbps2_regs` describes the data/status/control/reload registers. `struct apbps2_priv` stores the serio port and mapped registers. `apbps2_isr()` drains received data and maps parity/frame status to serio flags. `apbps2_write()`, `apbps2_open()`, and `apbps2_close()` implement serio callbacks. `apbps2_of_probe()` maps resources, requests IRQ, reads core frequency, programs reload, and registers serio.

## Control Flow

Probe maps the MMIO resource, disables the controller, parses/maps the OF IRQ, requests it shared, reads the `freq` property, programs the reload register to `freq_hz / 10000`, allocates and registers a serio port, and stores driver data. Open clears error flags, drains stale data with a limit, and enables receiver plus receive interrupt. Interrupt handling loops while data-ready is set, reads data, clears error bits if needed, and reports the byte. Write waits for TX FIFO space, writes the byte, and enables receive/transmit controls.

## State and Persistence Behavior

Persistent state is the MMIO register mapping and serio port. Hardware state includes reload timing, control bits, FIFO contents, and status/error bits. The driver itself does not buffer data outside IRQ processing.

## Dependencies and Integration Points

The file depends on OF platform devices, big-endian MMIO accessors, IRQ mapping/request, and serio core. It integrates with standard PS/2 protocol drivers through `SERIO_8042`.

## Risks and Edge Cases

`irq_of_parse_and_map()` result is not explicitly checked before `devm_request_irq()`. Write timeout returns `-ETIMEDOUT`; open drain uses a fixed 1024-iteration limit. The OF match table uses legacy `.name` entries rather than compatible strings. Correct operation depends on the `freq` property being present and accurate.

## Test Signals

Tests should cover OF probe with valid and missing `freq`, IRQ receive with parity/frame errors, open FIFO drain, write timeout and success, reload timing, remove cleanup, and standard keyboard/mouse attach.
