# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-core.c

## Purpose
Contains the shared Cavium/Marvell OCTEON/ThunderX TWSI I2C implementation used by platform and PCI glue. It implements low-level controller transfers, high-level-controller optimized transfers, block FIFO transfers, clock programming, interrupt/poll waits, status translation, and bus recovery.

## Important APIs, Types, And Functions
Exports `octeon_i2c_isr()`, `octeon_i2c_xfer()`, `octeon_i2c_init_lowlevel()`, `octeon_i2c_set_clock()`, and `octeon_i2c_recovery_info`. Low-level helpers include `octeon_i2c_start()`, `octeon_i2c_stop()`, `octeon_i2c_read()`, and `octeon_i2c_write()`. HLC paths include pure read/write, composite read/write, and block composite functions. `octeon_i2c_check_status()` maps TWSI status codes to Linux errors.

## Control Flow
The transfer path first tries HLC for low-speed messages that match supported shapes: single messages up to eight bytes, two-message same-address internal-address operations up to eight bytes, or block operations up to 1024 bytes when block registers exist. Otherwise it falls back to low-level START, address, byte-by-byte read/write, STOP sequencing. Wait helpers use interrupts unless broken IRQ detection switches the device to polling.

## State And Persistence
State lives in the shared `struct octeon_i2c` supplied by the glue driver: wait queue, adapter, register offsets, IRQ hooks, frequency, MMIO base, HLC/block flags, and broken-IRQ flags. The code toggles hardware HLC/block modes and clock divisors but persists nothing outside device registers.

## Dependencies And Integration Points
Depends on the definitions in `i2c-octeon-core.h`, Linux I2C core, PCI helper for OcteonTX2 clock behavior, generic SCL bus recovery, and glue-provided interrupt enable/disable callbacks. The exported recovery info is attached by platform glue.

## Risks
HLC status is read from a different register than low-level status, so mode transitions must be clean. Broken IRQ fallback is runtime-detected and changes wait behavior. Block FIFO paths require correct byte ordering and length limits. Watchdog timeout handling resets the bus monitor. Low-level fallback rejects zero-length messages and may return `-EOPNOTSUPP` when the core is addressed as a slave.

## Test Signals
Exercise HLC pure and composite transfers at <=400 kHz, block composite reads/writes above eight bytes, high-speed fallback, `I2C_M_RECV_LEN`, NACK/arbitration/watchdog status paths, broken IRQ polling fallback, clock divisor calculation on OcteonTX2 and older platforms, and generic SCL recovery after a forced stuck bus.
