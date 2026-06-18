# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_loongson.c

## Purpose
Registers a TPM 2.0 device backed by the Loongson security engine MFD interface.

## Important APIs, Types, And Functions
Defines `struct tpm_loongson_cmd` for the engine command header and TPM callbacks `tpm_loongson_send()` and `tpm_loongson_recv()`. `tpm_loongson_probe()` initializes the engine and TPM chip.

## Control Flow
Probe obtains `SE_ENGINE_TPM` from the parent Loongson security engine, initializes command id and data offset, allocates a TPM chip, marks it TPM2 and IRQ-capable, stores the engine as chip drvdata, and registers the chip. Send bounds-checks the engine buffer, sets data length, copies the TPM command into the engine data buffer, and calls `loongson_se_send_engine_cmd()`. Recv copies the returned data buffer according to `command_ret->data_len`.

## State And Persistence
Runtime state is owned mostly by `struct loongson_se_engine`: command headers, return headers, data buffer, buffer size, and offset. TPM persistent state lives in the security engine.

## Dependencies And Integration Points
Depends on `linux/mfd/loongson-se.h`, platform device binding `tpm_loongson`, and the TPM core.

## Risks And Edge Cases
There is minimal validation of response format beyond buffer length. The driver assumes the engine command path is synchronous enough for TPM core send/recv ordering. It sets IRQ flag but does not implement status/interrupt callbacks, relying on the engine command completion semantics.

## Test Signals
Engine initialization failure, command-size boundary, response-size boundary, TPM2 startup, command timeout behavior in the MFD engine, and platform-device binding.
