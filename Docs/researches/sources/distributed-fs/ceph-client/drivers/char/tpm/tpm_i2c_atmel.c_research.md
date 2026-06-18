# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_atmel.c

## Purpose
Supports Atmel AT97SC3204T I2C TPMs whose protocol sends raw TPM command buffers over I2C and later reads raw TPM responses, without the normal TIS locality/status register model.

## Important APIs, Types, And Functions
Defines `struct priv_data` with a cached short response buffer and length. TPM class operations are `i2c_atmel_send()`, `i2c_atmel_recv()`, `i2c_atmel_read_status()`, `i2c_atmel_cancel()`, and `i2c_atmel_req_canceled()`.

## Control Flow
Probe checks `I2C_FUNC_I2C`, allocates a TPM chip and private data, sets conservative default timeouts, and registers the chip. Send writes the complete command with `i2c_master_send()` and treats partial sends as errors. Status polling attempts an I2C read; failed reads mean not ready, successful reads cache the response prefix and return `ATMEL_STS_OK`. Recv uses the cached TPM header to determine response length, copies cached data when complete, or re-reads the expected response length.

## State And Persistence
Private state caches the latest response prefix until recv consumes it. There is no explicit locality, cancellation, or persistent software state.

## Dependencies And Integration Points
Integrates with the TPM core through `TPM_OPS_AUTO_STARTUP` and standard send/status/recv callbacks. Device matching is through I2C id `tpm_i2c_atmel` or OF compatible `atmel,at97sc3204t`.

## Risks And Edge Cases
The hardware has no known probe command, so registration relies on TPM startup detecting invalid devices. Cancellation is unsupported. Cached short responses depend on the header being present in the first read. Re-reading after partial cache assumes the device leaves the completed response readable until the next command.

## Test Signals
Full and partial response reads, failed-read polling behavior, partial I2C send errors, timeout handling, small response fast path, OF/I2C matching, and suspend/resume through TPM PM helpers.
