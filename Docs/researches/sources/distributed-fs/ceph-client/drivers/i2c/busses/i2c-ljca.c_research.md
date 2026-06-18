# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ljca.c

Purpose: implements the Intel La Jolla Cove Adapter USB-to-I2C auxiliary driver. It exposes LJCA firmware I2C channels as Linux I2C adapters by sending LJCA protocol commands for init, start, stop, read, and write.

Important APIs, types, and functions: `struct ljca_i2c_dev` stores the LJCA client, per-channel info, adapter, and fixed 60-byte input/output buffers. `struct ljca_i2c_rw_packet` is the packed LJCA command packet with channel id, little-endian length, and data payload. `ljca_i2c_xfer()` is the algorithm hook, using `ljca_i2c_read()` or `ljca_i2c_write()` per message.

Control flow: probe allocates state, obtains `ljca_i2c_info` platform data, initializes the LJCA channel at 400 kHz, registers the adapter with max transfer quirks, and clears ACPI dependencies if present. Each I2C message is handled independently: send START with address and direction, issue a pure read or write LJCA command, validate returned id and length, then send STOP. There is no repeated-start preservation across messages.

State and persistence: persistent state is only the LJCA client/channel metadata, adapter, and reusable packet buffers. No hardware register state is owned by this driver; LJCA firmware owns bus timing and transaction execution after `ljca_transfer`.

Dependencies and integration points: integrates with the auxiliary bus id `usb_ljca.ljca-i2c`, LJCA USB API and namespace, ACPI companion handling, I2C adapter quirks, HWMON class, and I2C core. It advertises I2C plus SMBus emulation except quick and disallows zero-length transfers.

Risks: fixed packet buffer size limits reads/writes to 57 bytes after packet header; adapter quirks enforce this. Each message emits its own STOP, so Linux combined transactions that rely on repeated start semantics are not faithfully represented. Return validation only checks response length/id, not deeper firmware status bytes. `ljca_i2c_init()` hardcodes 400 kHz.

Test signals: adapter creation for each LJCA I2C channel, read/write lengths at 1 and max 57, zero-length rejection through quirks, response id mismatch and short response handling, ACPI dependency clearing, firmware transfer errors, and multi-message client behavior where repeated start might be expected.
