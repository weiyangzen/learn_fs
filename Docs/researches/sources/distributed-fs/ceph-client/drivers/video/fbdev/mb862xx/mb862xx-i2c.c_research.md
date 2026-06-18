# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xx-i2c.c

## Purpose
Implements an I2C master adapter for MB862xx GDC hardware, used by Coral-P(A)/Lime style framebuffer devices when `CONFIG_FB_MB862XX_I2C` is enabled.

## Important APIs, Types, and Functions
- `mb862xx_i2c_wait_event()` polls bus control/status for interrupt or bus error completion.
- `mb862xx_i2c_do_address()` emits address phases and manages repeated-start state in `par->i2c_rs`.
- `mb862xx_i2c_read_byte()` and `mb862xx_i2c_write_byte()` transfer one data byte through GDC I2C registers.
- `mb862xx_xfer()` implements `i2c_algorithm.master_xfer`.
- `mb862xx_i2c_init()` attaches a static `i2c_adapter` to the framebuffer private data and registers it.
- `mb862xx_i2c_exit()` unregisters the adapter.

## Control Flow
I2C core calls `mb862xx_xfer()` with message arrays. For each non-empty message, the driver writes the address, then calls the read or write loop. After at least one message it emits STOP and disables the bus. Reads request ACK for all but the final byte. Writes return `-EIO` on NACK or bus error.

## State and Persistence
The adapter uses `struct mb862xxfb_par` as `algo_data`, primarily for register base access and `i2c_rs` repeated-start tracking. `par->adap` records whether the adapter is registered.

## Dependencies and Integration Points
Uses MB862xx register macros from `mb862xx_reg.h`, `inreg/outreg` from `mb862xxfb.h`, Linux I2C core, and udelay polling. Called by the PCI/CoralP initialization and removal paths.

## Risks
`mb862xx_i2c_wait_event()` has no timeout and can spin forever if hardware never sets completion or bus error. The adapter object is static, so multiple device instances would share one adapter and `algo_data`. `functionality()` advertises only `I2C_FUNC_SMBUS_BYTE_DATA` even though the transfer path is raw master_xfer-like.

## Test Signals
Validation includes successful adapter registration, transfers returning the number of completed messages, STOP after multi-message operations, repeated-start behavior for combined transactions, and error propagation on bus error/NACK. Hardware lockup tests should expose the missing timeout.
