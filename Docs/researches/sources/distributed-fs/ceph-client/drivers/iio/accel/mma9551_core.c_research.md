# sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551_core.c

Purpose: shared mailbox-command library for MMA955x intelligent sensor drivers. It implements the MMA955x application protocol over I2C and exports helpers for config/status byte/word transfers, GPIO routing, version reads, sleep/wake power state, accelerometer channels, and application reset.

Important APIs/types/functions: packed `mma9551_mbox_request`, `mma9551_mbox_response`, and `mma9551_version_info` model the wire format. `mma9551_transfer()` is the core write-then-poll-read transaction engine. Exported helpers include `mma9551_read_config_*`, `mma9551_write_config_*`, `mma9551_read_status_*`, `mma9551_update_config_bits()`, `mma9551_gpio_config()`, `mma9551_read_version()`, `mma9551_set_device_state()`, `mma9551_set_power_state()`, `mma9551_sleep()`, `mma9551_read_accel_chan()`, `mma9551_read_accel_scale()`, and `mma9551_app_reset()`.

Control flow: a transfer validates 12-bit offset, builds a mailbox request, writes it with `i2c_transfer()`, polls up to five times with 50 us delay for COCO, validates app id, error code, and response length, then copies output bytes. Word helpers convert big-endian mailbox payloads. GPIO config writes app id/bit selection and polarity. Device power uses Sleep/Wake app config bits; runtime PM wrapper delegates to kernel PM.

State and persistence: this file keeps no private state. It modifies persistent device application configuration and relies on callers to hold their per-device mutex, as documented on each exported helper.

Dependencies and integration points: Linux I2C, runtime PM, endian helpers, IIO channel definitions, and `mma9551_core.h` app ids/macros. Used by both MMA9551 and MMA9553 frontend drivers.

Risks: locking is entirely external, so any new caller that omits serialization can interleave mailbox commands. `i2c_transfer()` returning 0 is not treated as a short transfer failure. Response length validation compares two response fields, not requested output length directly.

Test signals: mailbox timeout/error-code/app-id mismatch injection, byte/word endian correctness, max mailbox length validation, GPIO polarity mapping for pins 6-9, runtime PM balance, accelerometer axis reads, and pedometer app reset.
