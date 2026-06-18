# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_infineon.c

## Purpose
Implements the legacy Infineon SLB9635/SLB9645 I2C TPM protocol using TIS-like register semantics over vendor-specific I2C transfers.

## Important APIs, Types, And Functions
Global `struct tpm_inf_dev tpm_dev` stores the single supported client, locality, chip type, adapter limit, command buffer, and chip. Low-level helpers are `iic_tpm_read()`, `iic_tpm_write_generic()`, `iic_tpm_write()`, and `iic_tpm_write_long()`. TIS operations include `request_locality()`, `release_locality()`, `tpm_tis_i2c_status()`, `get_burstcount()`, `wait_for_stat()`, `recv_data()`, `tpm_tis_i2c_recv()`, and `tpm_tis_i2c_send()`.

## Control Flow
Probe enforces a single client and full I2C functionality, then initializes a TPM chip with TIS timeouts. Initialization requests locality zero, reads `TPM_DID_VID`, identifies SLB9635 or SLB9645, and registers the chip. Reads either use combined transfer for SLB9645 or split address/data messages for SLB9635, with retries, guard sleeps, and adapter-limit fallback. Send requests locality, enters command-ready state, writes FIFO data in burst chunks, verifies `DATA_EXPECT`, writes `GO`, and leaves response polling to core. Recv reads header, validates expected length, drains remaining data, checks for leftover data, resets ready, sleeps for cleanup, and releases locality.

## State And Persistence
Uses global singleton state for client, locality, adapter-limit fallback, and chip pointer. TPM persistent state remains in hardware.

## Dependencies And Integration Points
Depends on raw `__i2c_transfer()` under adapter segment lock, TPM class callbacks, I2C/OF IDs for Infineon TPMs, and TPM PM helpers.

## Risks And Edge Cases
Singleton state prevents multiple devices. Split-transfer timing and guard sleeps are chip-specific. Locality release happens on recv and error paths, so missing recv after send could hold locality. Adapter quirk fallback changes transfer chunking after `-EOPNOTSUPP`. Vendor ID byte order is easy to misinterpret.

## Test Signals
SLB9635 split protocol, SLB9645 combined protocol, I2C NAK retry, adapter block-size fallback, locality timeout, burstcount timeout, malformed response sizes, leftover data detection, and suspend/resume.
