# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-usbio.c

## Purpose

`i2c-usbio.c` exposes Intel USBIO I2C buses as auxiliary-bus-backed Linux I2C adapters. It translates I2C messages into USBIO bulk protocol commands and applies ACPI-selected bus speed and device-specific quirks.

## Important APIs, Types, and Functions

`struct usbio_i2c` stores the adapter, auxiliary device, shared read/write buffer, quirks, speed, and TX/RX buffer sizes. `usbio_i2c_init()` and `usbio_i2c_uninit()` bracket each transfer. `usbio_i2c_read()` and `usbio_i2c_write()` split messages around USBIO packet buffer limits. `usbio_i2c_xfer()` acquires the USBIO device, initializes the bus, runs messages, uninitializes, and releases it.

## Control Flow

Probe obtains platform bus descriptors, binds ACPI HIDs, discovers endpoint buffer sizes, allocates a maximum-size RW buffer, reads quirks, computes a maximum speed from capability bits and quirks, clamps ACPI speed, configures adapter metadata and quirks, and registers the adapter. Transfers are serialized by `usbio_acquire()`/`usbio_release()`, with every message converted to `USBIO_I2CCMD_READ` or `USBIO_I2CCMD_WRITE`.

## State and Persistence Behavior

The driver keeps one reusable RW buffer per adapter. Speed and quirks are fixed at probe. It has no cache. Each transfer starts with an INIT packet using the first message address and ends with UNINIT using the same address context.

## Dependencies and Integration Points

It depends on the USBIO namespace/API, auxiliary bus, ACPI helpers, I2C core, and USBIO protocol structures. Adapter quirks declare no zero-length transfers, no repeated starts, and either 4 KiB or 52-byte maximum read/write lengths.

## Risks

Chunked reads do not validate exact return lengths for intermediate chunks, only negative errors. Chunked writes use `txchunk` as the copied length before shrinking it for the last iteration, so edge-case message sizes near chunk boundaries are important. INIT behavior changes under `USBIO_QUIRK_I2C_NO_INIT_ACK`. Since repeated starts are prohibited, clients requiring combined transactions may fail.

## Test Signals

Validate ACPI HID binding, speed clamping, both adapter-quirk variants, reads and writes at 0, 1, 52, 53, 4096, and over-buffer lengths, quirk paths for chunk size and missing INIT ACK, acquire/release balancing on failures, and dependency clearing for ACPI companion devices.
