# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ocores.c

## Purpose
Implements an I2C adapter for the OpenCores I2C controller and GRLIB variant. It supports MMIO or I/O port resources, multiple register widths and endianness, interrupt-driven and polling transfers, platform-data device creation, and noirq suspend/resume.

## Important APIs, Types, And Functions
`struct ocores_i2c` stores register accessors, clocks, bus/core rates, transfer state, wait queue, and process lock. `ocores_process()` is the byte-level state machine. `ocores_xfer_core()` starts a transfer and waits via IRQ or polling; `ocores_xfer()` and `ocores_xfer_polling()` expose normal and atomic paths. `ocores_init()` programs the prescaler and enables the core. Probe configures accessors, resources, OF/platform data, IRQ mode, and adapter registration.

## Control Flow
Probe maps resources, derives clock and register layout from platform data or OF, selects accessors, optionally disables IRQ use for broken FU540 hardware, requests the IRQ if needed, initializes the controller, then registers the adapter. Transfers set the interrupt enable bit according to mode, seed state with the first address byte, issue START, and either wait on `wait` or repeatedly poll status and invoke the ISR path. `ocores_process()` handles NACK/arbitration loss, repeated starts, read ACK/NACK decisions, writes, STOP, and final wakeup.

## State And Persistence
All transfer state is in `struct ocores_i2c`: current message pointer, byte position, remaining message count, and state enum. Hardware state is the prescaler/control/command/status register set. No durable state is persisted.

## Dependencies And Integration Points
Depends on platform device resources, optional clocks, OF bindings (`opencores,i2c-ocores`, GRLIB, SiFive compatibles), `i2c-ocores` platform data, I2C core, and IRQ or polling support. Platform data can instantiate known child devices after adapter registration.

## Risks
The file mutates the global `ocores_algorithm.xfer` when one probed device needs polling, which can affect later adapters using the same static algorithm. Timing depends on accurate `ip_clock_khz` and `bus_clock_khz`; unsupported clock error threshold is strict. Broken IRQ handling and polling mode must not race with `ocores_process_timeout()`, hence the process lock. OF clock fallback includes deprecated properties and must avoid drift.

## Test Signals
Test by probing OpenCores and GRLIB variants with 8/16/32-bit and big/little-endian registers, transfer with and without IRQs, exercise atomic polling transfers, inject NACK and arbitration loss, validate prescaler output against requested bus rate, suspend/resume with clock changes, and confirm FU540-compatible devices operate in polling mode.
