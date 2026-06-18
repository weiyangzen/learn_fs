<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-i2c.c

## Purpose
`solo6x10-i2c.c` implements two Linux I2C adapters backed by the SOLO6x10 on-chip IIC controller, used mainly for Techwell TW28xx decoders and SAA7128 video encoder access.

## Important APIs, Types, and Functions
Convenience helpers `solo_i2c_readbyte()` and `solo_i2c_writebyte()` issue common register transactions. The hardware state machine is driven by `solo_i2c_start()`, `solo_i2c_flush()`, `solo_i2c_handle_read()`, `solo_i2c_handle_write()`, and `solo_i2c_stop()`. `solo_i2c_isr()` advances transactions from the top-level IRQ handler. `solo_i2c_master_xfer()` is the Linux I2C algorithm entry point and serializes transfers through `i2c_mutex`.

## Control Flow
`solo_i2c_init()` enables the controller with a fixed prescale, initializes wait state, and registers two adapters. A master transfer identifies which adapter is being used, stores the message array in `solo_dev`, enables `SOLO_IRQ_IIC`, emits the address phase, and waits up to half a second for `IIC_STATE_STOP`. Each hardware interrupt checks error bits, reads or writes the next byte, starts the next message when needed, or stops and wakes the waiter. Completion returns the count of messages consumed.

## State and Persistence
All in-flight transfer state is stored in `struct solo_dev`: `i2c_state`, `i2c_id`, current message pointer, message count, byte index, wait queue, and mutex. There is no persistent state. Hardware IIC control/data registers are reset around every transfer.

## Dependencies and Integration Points
This file depends on Linux I2C core, SOLO IRQ mask helpers, `SOLO_IIC_*` register definitions, and wait queue scheduling. TW28 setup/control and SAA7128 programming rely on these adapters.

## Risks and Edge Cases
The source itself warns that the implementation does too much in interrupt context and does not use hardware busy/status as robustly as it should. `solo_i2c_readbyte()` ignores `i2c_transfer()` failure and returns an uninitialized byte on hard failure. Interrupted or timed-out waits return a partial message count rather than a negative errno, which can mask bus problems for callers.

## Test Signals
Test adapter registration, TW and SAA bus transactions, repeated-start read sequences, `I2C_M_NOSTART` behavior, timeout/error handling, IRQ disable and wakeup on stop, and cleanup after partial adapter registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-i2c.c -->
