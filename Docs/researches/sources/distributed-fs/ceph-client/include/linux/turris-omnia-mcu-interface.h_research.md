# sources/distributed-fs/ceph-client/include/linux/turris-omnia-mcu-interface.h

## Purpose
Defines the CZ.NIC Turris Omnia MCU I2C command set, status/control/feature bit fields, interrupt bits, and typed inline helpers for command read/write transactions.

## Important APIs, Types, And Functions
Enums cover MCU commands (`OMNIA_CMD_*`), flashing subcommands, status word bits, control byte bits, feature bits, extended status/control, interrupt bits, LED mode/state fields, poweroff magic, and USB over-current protection fields. APIs include `omnia_cmd_write_read()`, `omnia_cmd_write()`, typed write helpers for u8/u16/u32, `omnia_cmd_read()`, `omnia_compute_reply_length()`, `omnia_cmd_read_bits()`, `omnia_cmd_read_bit()`, and typed read helpers for u8/u16/u32.

## Control Flow
Callers serialize a command byte and optional little-endian payload, send it over I2C through `omnia_cmd_write_read()`, and optionally parse replies. `omnia_cmd_read_bits()` computes the shortest reply length needed for a bit mask, reads that many bytes, converts little-endian data to CPU order, and masks the requested bits. Feature flags gate use of newer MCU commands.

## State, Persistence, And Dependencies
No state is held. Wire protocol state is represented by fixed command IDs and bit masks. Dependencies include bitfield helpers, bitops, unaligned little-endian stores, byteorder, types, and `struct i2c_client`.

## Integration Points
Used by Turris Omnia platform drivers for LEDs, watchdog, MCU firmware/flashing, wakeup/poweroff, USB power/over-current, TRNG, crypto signing, board info, and interrupt handling.

## Risks And Test Signals
Risks include using commands without checking feature bits, invalid legacy 32-bit feature reads when bit 20 is set, endian mistakes, too-short reply lengths, and magic poweroff misuse. Test signals include mocked I2C command buffers, feature-gated command probing, bit-mask length tests, endian round-trips, interrupt mask read/write, and board hardware integration tests.
