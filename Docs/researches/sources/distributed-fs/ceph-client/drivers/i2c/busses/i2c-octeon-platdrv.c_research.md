# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-platdrv.c

## Purpose
Provides the platform-device glue for Cavium OCTEON TWSI I2C controllers. It maps device-tree resources, wires interrupts into the shared OCTEON core, initializes clocks/registers, and registers the I2C adapter.

## Important APIs, Types, And Functions
`octeon_i2c_probe()` is the main setup function. Interrupt helpers include standard CSR interrupt enable/disable, CN7890-style Linux IRQ enable/disable wrappers, and a separate HLC ISR for the secondary interrupt. The adapter algorithm calls `octeon_i2c_xfer()` from the shared core and reports functionality through `octeon_i2c_functionality()`.

## Control Flow
Probe detects CN7890-compatible hardware, selects IRQ numbers and callback implementations, allocates `struct octeon_i2c`, maps MMIO, reads `clock-frequency` or legacy `clock-rate`, gets IO clock rate, requests interrupts, initializes low-level hardware, programs clock divisors, attaches recovery info, and registers the adapter. Remove unregisters the adapter.

## State And Persistence
This file initializes the shared `struct octeon_i2c` with platform-specific offsets, IRQs, callbacks, `twsi_freq`, `sys_freq`, adapter timeout/retries, and OF node. Persistent state is only hardware register configuration during device lifetime.

## Dependencies And Integration Points
Depends on OF compatibles `cavium,octeon-3860-twsi` and `cavium,octeon-7890-twsi`, platform IRQ/resource APIs, `octeon_get_io_clock_rate()`, shared `i2c-octeon-core` exports, and the I2C core. The adapter supports I2C, SMBus emulation except quick, SMBus read block, and block process call.

## Risks
CN7890 uses separate HLC and core IRQ lines with manual `IRQ_NOAUTOEN` and atomic disable balancing; incorrect IRQ ordering or counts can deadlock waits. Missing clock properties fail probe. Adapter timeout is very short at 2 ms, so slow or clock-stretched devices may expose timing issues. OF register layout assumptions are fixed in probe.

## Test Signals
Boot/probe tests on both legacy and CN7890 compatibles, IRQ enable/disable balance under repeated transfers, fallback polling when shared core detects broken IRQs, clock-frequency and legacy clock-rate bindings, adapter functionality enumeration, and bus recovery after simulated stuck SCL/SDA.
