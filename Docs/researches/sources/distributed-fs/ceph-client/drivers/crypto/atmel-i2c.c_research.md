# sources/distributed-fs/ceph-client/drivers/crypto/atmel-i2c.c

## Purpose

`atmel-i2c.c` is the shared transport and command-construction layer for Atmel/Microchip I2C crypto devices used by the ECC and SHA204A drivers. It builds device commands with CRC16, performs wake-command-delay-read-sleep transactions, verifies lock state during probe, and provides a per-CPU workqueue for asynchronous requests.

## Important APIs, Types, And Functions

Exported command builders include `atmel_i2c_init_read_config_cmd()`, `atmel_i2c_init_read_otp_cmd()`, `atmel_i2c_init_random_cmd()`, `atmel_i2c_init_genkey_cmd()`, and `atmel_i2c_init_ecdh_cmd()`. `atmel_i2c_send_receive()` is the synchronous transaction primitive. `atmel_i2c_enqueue()` and `atmel_i2c_flush_queue()` manage async work. `atmel_i2c_probe()` validates adapter support, bus speed, wake-token length, client-private data, and locked configuration/data zones.

## Control Flow

Command builders fill word address, opcode, parameters, count, CRC, expected execution time, and response size. `send_receive()` locks the client mutex, sends a wake token while ignoring NAK, waits the wake interval, reads wake status, sends the command, sleeps for the command-specific execution time, reads the response, sends sleep, unlocks, and decodes status/error bytes. Async work simply calls the synchronous primitive and invokes the caller callback.

## State And Persistence Behavior

Per-client state contains the I2C client pointer, list node, transaction mutex, precomputed all-zero wake token sized from bus clock, active transform count, and optional hwrng object. The module owns a global workqueue. Secure-element configuration, OTP, and data zones are persistent hardware state; probe rejects devices whose configuration or data/OTP zones are unlocked because secrets could be modified.

## Dependencies And Integration Points

The file depends on I2C core, ACPI/firmware bus-speed discovery, CRC16/bit reversal, delay/sleep APIs, workqueues, scatterlist copying for ECDH public keys, and exported symbols consumed by `atmel-ecc.c` and `atmel-sha204a.c`.

## Risks And Test Signals

Risks include imprecise fixed sleeps for command completion, status responses with unknown error IDs being ignored, failure to sleep the device on some error paths, wake-token sizing for unusual bus rates, async work executing after device removal, and security-sensitive lock-state assumptions. Test probe at valid/invalid I2C clock rates, locked/unlocked device configs, command CRC vectors, random/genkey/ecdh/read commands, concurrent async enqueue, and I2C NAK/timeout/status-error injection.
