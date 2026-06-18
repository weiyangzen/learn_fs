# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viperboard.c

## Purpose

`i2c-viperboard.c` exposes the Nano River Technologies Viperboard MFD's USB-backed I2C interface as a Linux I2C adapter. It translates I2C messages into Viperboard-specific USB bulk/control packets and supports a module-selected bus frequency.

## Important APIs, Types, and Functions

`struct vprbrd_i2c` stores the adapter and encoded bus frequency. Low-level helpers are `vprbrd_i2c_status()`, `vprbrd_i2c_receive()`, `vprbrd_i2c_addr()`, `vprbrd_i2c_read()`, and `vprbrd_i2c_write()`. `vprbrd_i2c_xfer()` implements message transfer under the parent `vprbrd` mutex.

## Control Flow

Module init maps `i2c_bus_freq` values to firmware frequency constants and registers a platform driver. Probe gets the parent Viperboard MFD data, allocates adapter state, sets adapter algorithm/quirks, sends a control request to configure bus frequency, then registers the adapter. Transfers lock the parent USB buffer, send read or write data packets, send an address/length packet, query status, and abort on USB or protocol errors.

## State and Persistence Behavior

The adapter shares `vb->buf` and `vb->lock` with the MFD parent. Frequency is fixed at probe and stored in a DMA-capable byte field for the control transfer. There is no data cache. Adapter quirks cap read/write lengths at 2048 bytes.

## Dependencies and Integration Points

It depends on the Viperboard MFD structures and USB endpoint definitions, platform-driver binding from the MFD, USB bulk/control APIs, I2C core, and hwmon class scanning.

## Risks

Read length encoding is complex, with split transfers around 512/1024-byte boundaries. Write chunks use firmware-specific maximum payloads. Probe uses a range check that appears inverted for frequency constants, making valid-frequency validation sensitive to enum ordering. `i2c_add_adapter()` return value is ignored. Shared USB buffer misuse would corrupt concurrent MFD operations, so mutex coverage is critical.

## Test Signals

Test all supported module frequencies, invalid frequency fallback/rejection, reads/writes at 1, 255, 510, 512, 767, 1024, 2048 bytes, USB short transfer errors, protocol status failures, mutex serialization, adapter quirk enforcement, and platform remove cleanup.
