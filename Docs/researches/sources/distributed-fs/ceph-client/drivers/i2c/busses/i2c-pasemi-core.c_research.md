# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-core.c

## Purpose
Provides the shared PA Semi PWRficient SMBus/I2C controller implementation. It handles FIFO programming, controller reset/clear, optional IRQ completion, raw I2C messages, SMBus protocol operations, functionality reporting, and common adapter registration for glue drivers.

## Important APIs, Types, And Functions
The file operates on `struct pasemi_smbus` from the header. `pasemi_i2c_common_probe()` initializes the adapter and controller and is exported to glue. `pasemi_i2c_xfer()` and `pasemi_i2c_xfer_msg()` implement raw I2C transfers. `pasemi_smb_xfer()` implements SMBus quick, byte, byte/word data, block, process call, and block process call. `pasemi_irq_handler()` completes IRQ-driven waits.

## Control Flow
Before each transfer, `pasemi_smb_clear()` waits for idle and resets FIFOs on stale error/data conditions. Raw I2C writes address/data commands into `REG_MTXFIFO`, waits at STOP for completion, and reads data from `REG_MRXFIFO` for reads. SMBus transfer constructs protocol-specific FIFO sequences, waits for completion, then pulls response data as required. Error paths reset the controller.

## State And Persistence
State is contained in glue-owned `struct pasemi_smbus`: MMIO base, clock divisor, hardware revision, IRQ-use flag, and completion. Hardware status flags in `REG_SMSTA` are cleared after use. There is no durable state.

## Dependencies And Integration Points
Depends on Linux I2C/SMBus core, MMIO accessors, polling helpers, completions, and exported symbols for glue modules. The adapter advertises both I2C and a broad SMBus capability set.

## Risks
FIFO command ordering is protocol-sensitive, especially block reads where the length byte is read before issuing the remaining read count. `use_irq` defaults to false in common probe, so glue must opt in if IRQ completion is desired. Hardware timeout assumptions are based on a documented 25 ms controller timeout but use a 100 ms software timeout. Empty RX FIFO after completion maps to `-ENODATA`.

## Test Signals
Exercise all advertised SMBus protocols, raw multi-message I2C with and without repeated starts, NACK/timeout/arbitration status handling, block length clamping, reset after error, polling and IRQ completion modes, and common-probe reuse from PCI or other glue.
