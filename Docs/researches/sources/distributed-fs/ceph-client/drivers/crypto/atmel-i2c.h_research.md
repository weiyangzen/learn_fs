# sources/distributed-fs/ceph-client/drivers/crypto/atmel-i2c.h

## Purpose

`atmel-i2c.h` is the shared protocol header for Atmel/Microchip I2C crypto secure elements. It defines packet sizes, opcodes, response formats, timing constants, secure-element zones, shared per-client/private work structures, and exported helper prototypes used by ECC and SHA204A drivers.

## Important APIs, Types, And Functions

Important types are `struct atmel_i2c_cmd`, `struct atmel_ecc_driver_data`, `struct atmel_i2c_client_priv`, and `struct atmel_i2c_work_data`. Constants describe command overhead, P-256 key sizes, response sizes, status bytes, lock-byte indexes, wake timing, max command execution times, and opcodes for ECDH, GenKey, Read, and Random. Prototypes expose probe, enqueue/flush, send/receive, and command initialization helpers.

## Control Flow

The header defines the structure that all command builders fill: word address, count, opcode, param1, param2, data/CRC, execution delay, and response size. Async users allocate `atmel_i2c_work_data`, set a client and command, then call `atmel_i2c_enqueue()` to run the transaction and invoke a callback.

## State And Persistence Behavior

Per-client state tracks serialized transport access through a mutex, the all-zero wake token, an active transform count used by ECC and SHA204A, and an embedded hwrng descriptor for SHA204A. Device persistence is modeled by constants for configuration, OTP, lock bytes, ECDH private key slot 2, and OTP zone sizing.

## Dependencies And Integration Points

The header depends on Linux hwrng/types and is shared by `atmel-i2c.c`, `atmel-ecc.c`, and `atmel-sha204a.c`. Its constants encode the secure-element protocol ABI and the crypto driver priority used by the ECC KPP algorithm.

## Risks And Test Signals

Risks include response-size constants getting out of sync with command payloads, packed-structure layout assumptions, hard-coded P-256/slot-2 behavior limiting flexibility, and wake/execute timing constants that may not cover all parts. Test by compiling all consumers, checking command byte layouts against datasheets, and exercising read/random/genkey/ecdh paths on supported devices.
