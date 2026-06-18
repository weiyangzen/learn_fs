# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-common.c

## Purpose

`i2c-viai2c-common.c` provides shared transfer and initialization logic for VIA/WonderMedia/Zhaoxin I2C controller variants. Platform-specific files supply IRQ handlers, clock setup, and adapter registration while this file handles byte-mode message sequencing.

## Important APIs, Types, and Functions

The exported functions are `viai2c_wait_bus_not_busy()`, `viai2c_xfer()`, `viai2c_irq_xfer()`, and `viai2c_init()`. Internal `viai2c_write()` and `viai2c_read()` program control/data/transfer registers and wait for `complete`. State is held in `struct viai2c` from the companion header.

## Control Flow

`viai2c_xfer()` sets byte mode, optionally waits for bus ready on WMT, records the current message and byte index, then calls read or write helper per message. The helpers set initial CDR/CR/TCR state, issue CPU ready when required by platform semantics, wait up to `VIAI2C_TIMEOUT`, and return the IRQ-computed result. `viai2c_irq_xfer()` is called by platform ISRs after byte-end events; it reads or writes the next byte, handles quick commands, sets RX/TX end bits, and returns completion status.

## State and Persistence Behavior

Per-transfer state lives in `i2c->msg`, `xfered_len`, `ret`, `last`, and `mode`. `complete` is reinitialized per message. The shared init function allocates and maps `struct viai2c`, sets platform kind, initializes completion, and stores driver data.

## Dependencies and Integration Points

The file exports symbols for WMT and Zhaoxin modules. It depends on MMIO word/byte register access, completions, platform devices, and platform-specific IRQ status clearing. It distinguishes WMT and Zhaoxin repeated-start/CPU-ready requirements.

## Risks

Zero-length write support relies on setting `xfered_len = -1` in a `u16` field, an intentional wraparound that is fragile. ACK/NACK handling maps write NAK to `-EIO` rather than `-ENXIO`. Platform-specific CR/TCR behavior is interleaved with common code, so new variants can easily break existing timing.

## Test Signals

Exercise byte-mode reads/writes, SMBus quick zero-length writes, WMT `I2C_M_NOSTART`, Zhaoxin non-first read CPU-ready behavior, timeout handling, NAK handling, repeated message sequences, and exported-symbol consumers.
