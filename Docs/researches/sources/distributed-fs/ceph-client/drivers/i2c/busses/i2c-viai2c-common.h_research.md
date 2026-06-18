# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-common.h

## Purpose

`i2c-viai2c-common.h` defines the register map, bitfields, shared state structure, platform identifiers, transfer modes, timeout, and exported function prototypes for the VIA/WMT/Zhaoxin I2C controller family.

## Important APIs, Types, and Functions

The key type is `struct viai2c`, which embeds an `i2c_adapter`, completion, device pointer, MMIO base, optional clock, transfer-control value, IRQ number, current message pointer, byte counters, return code, last-message flag, mode, platform ID, and platform-private pointer. Register constants cover CR, TCR, CSR, ISR, IMR, CDR, TR, and MCR.

## Control Flow

The header has no executable control flow, but it defines the contract shared by `i2c-viai2c-common.c`, `i2c-viai2c-wmt.c`, and `i2c-viai2c-zhaoxin.c`. Platform drivers initialize `struct viai2c`, then delegate transfer work to the common functions and call `viai2c_irq_xfer()` from ISRs.

## State and Persistence Behavior

State fields in `struct viai2c` are mutable during transfers and must be coordinated with interrupt handlers. The `tcr` field stores persistent bus-speed/mode bits to OR into each transfer.

## Dependencies and Integration Points

It includes kernel delay, I2C, interrupt, MMIO, module, OF IRQ, and platform headers. The public prototypes are exported by the common C file for modular reuse.

## Risks

The shared structure is part of an implicit ABI among three source files. Type changes, especially `u16 xfered_len`, can affect zero-length and FIFO paths. Common register names hide variant-specific width differences because users call both word and byte accessors on the same offsets.

## Test Signals

Build coverage for both WMT and Zhaoxin consumers is the main signal. Runtime tests should verify that platform-specific private data and mode fields remain coherent across byte and FIFO transfers.
