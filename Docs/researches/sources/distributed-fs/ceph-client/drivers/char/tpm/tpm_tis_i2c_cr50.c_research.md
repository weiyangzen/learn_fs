# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_i2c_cr50.c

## Purpose
Implements the Google Cr50/Ti50 I2C TPM protocol, which is TIS-like but requires special transaction timing, four-byte status accesses, interrupt-based readiness, and custom burst handling.

## Important APIs, Types, And Functions
Private state is `struct tpm_i2c_cr50_priv_data` with IRQ, completion, and write buffer. Key functions are `tpm_cr50_i2c_read()`, `tpm_cr50_i2c_write()`, `tpm_cr50_request_locality()`, `tpm_cr50_release_locality()`, `tpm_cr50_i2c_tis_status()`, `tpm_cr50_i2c_get_burst_and_status()`, `tpm_cr50_i2c_tis_send()`, `tpm_cr50_i2c_tis_recv()`, and `tpm_cr50_i2c_probe()`.

## Control Flow
Probe checks I2C support, allocates a TPM2 chip and private state, optionally marks firmware-power-managed, requests a falling-edge IRQ with `IRQF_NO_AUTOEN`, requests locality zero, reads DID/VID, validates Cr50/Ti50 IDs, releases locality, and registers. I2C reads send the register address, wait for IRQ or fallback delay, then read data. Writes prepend register address, send, then wait for readiness. Send waits for command-ready, writes FIFO chunks based on burst count minus address byte, verifies `DATA_EXPECT` clears, and writes four-byte `GO`. Recv reads the first full burst, derives expected length, drains remaining bursts, and checks `DATA_AVAIL` clears.

## State And Persistence
State is per-chip IRQ/completion and temporary write buffer. Locality handling locks the I2C adapter segment between request and release, effectively serializing TPM access.

## Dependencies And Integration Points
Matches ACPI `GOOG0005` and OF `google,cr50`, integrates directly with TPM class ops rather than `tpm_tis_core`, and uses firmware-power-managed device property.

## Risks And Edge Cases
All four status bytes must be accessed together. No IRQ mode falls back to fixed 20 ms delays. Locality request returns while holding the I2C bus lock until release, so error paths must unlock. Burst count must stay within 63-byte max minus address overhead. The error path condition around aborting pending transactions should be checked against status semantics.

## Test Signals
IRQ and no-IRQ modes, Cr50 and Ti50 IDs, locality lock/unlock on failures, four-byte status accesses, burst chunk boundaries, TPM2 startup, firmware-power-managed property, and suspend/resume.
