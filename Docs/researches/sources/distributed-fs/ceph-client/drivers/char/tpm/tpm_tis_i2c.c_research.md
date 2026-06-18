# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_i2c.c

## Purpose
Implements the native TCG PTP TPM 2.0 I2C transport as a PHY under the generic TIS core.

## Important APIs, Types, And Functions
`struct tpm_tis_i2c_phy` stores the I2C client, guard-time settings, and I/O buffer. Key helpers are `tpm_tis_i2c_address_to_register()`, `tpm_tis_i2c_retry_transfer_until_ack()`, `tpm_tis_i2c_sanity_check_read()`, `tpm_tis_i2c_read_bytes()`, `tpm_tis_i2c_write_bytes()`, `tpm_tis_i2c_verify_crc()`, and `tpm_tis_i2c_init_guard_time()`.

## Control Flow
Probe allocates PHY and buffer, sets default cancellation semantics, reads I2C interface capability to derive guard time, selects locality zero, enables data checksum, and calls `tpm_tis_core_init()` in polling mode. Reads write the register selector, read data in I2C block chunks, retry and sanity-check reserved-zero bits. Writes send register plus data chunks. CRC verification reads `TPM_DATA_CSUM` and compares reflected CCITT CRC with the command or response bytes.

## State And Persistence
Per-device state tracks guard-time requirements for read/write sequences, min/max guard delay, and a reusable I/O buffer. Locality is forced to zero through `TPM_LOC_SEL`.

## Dependencies And Integration Points
Depends on I2C block transfer limits, CRC-CCITT, OF matches for Infineon/Nuvoton/TCG I2C TPMs, and the TIS core PHY contract.

## Risks And Edge Cases
Register translation must map TIS core addresses into native I2C register addresses. Guard-time interpretation is vendor-specific and required after ACK and NACK sequences. Reserved-zero sanity failures trigger retries and protect against bus corruption. Enabling checksum means all command/response paths depend on CRC register correctness.

## Test Signals
Guard-time capability parsing, register translation, large FIFO chunking, NACK retries, reserved-zero sanity failures, CRC mismatch, locality selection, checksum enable, and TIS core registration.
