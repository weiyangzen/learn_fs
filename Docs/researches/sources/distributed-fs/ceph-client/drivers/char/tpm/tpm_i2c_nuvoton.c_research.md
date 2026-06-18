# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_i2c_nuvoton.c

## Purpose
Supports Nuvoton/Winbond WPCT301, NPCT501, and NPCT6xx TPMs over their I2C FIFO register protocol, including optional data-available interrupt acceleration.

## Important APIs, Types, And Functions
Private data contains IRQ number, interrupt counter, and read waitqueue. Important helpers are `i2c_nuvoton_read_buf()`, `i2c_nuvoton_write_buf()`, `i2c_nuvoton_read_status()`, `i2c_nuvoton_write_status()`, `i2c_nuvoton_wait_for_stat()`, `i2c_nuvoton_recv_data()`, `i2c_nuvoton_recv()`, `i2c_nuvoton_send()`, `i2c_nuvoton_int_handler()`, and `get_vid()`.

## Control Flow
Probe validates VID/DID/RID, allocates chip/private state, marks TPM2 when matched by data, sets default timeouts, optionally requests a level-low IRQ, and registers the chip. Send retries command setup, writes `COMMAND_READY`, waits for readiness, writes FIFO chunks constrained by burst count and 32-byte I2C block size, verifies `EXPECT`, writes `GO`, computes ordinal duration, and waits for data availability. Recv retries up to five times, optionally uses response-retry status, reads an initial burst containing the TPM header, validates expected length, drains remaining bytes, checks for leftover data, and returns ready state.

## State And Persistence
State is per-chip IRQ/read queue metadata and transient FIFO buffer contents. Persistent TPM state is hardware-owned.

## Dependencies And Integration Points
Uses SMBus block I/O helpers, optional OF match data for TPM2, TPM core timeouts/duration calculation, TPM PM helpers, and I2C device-tree interrupt registration.

## Risks And Edge Cases
The IRQ only signals data availability and is disabled in the handler, so missed re-enable or spurious interrupts can force timeouts. `get_vid()` has a firmware-revision fallback that reads FIFO offset as an alternate ID. Send keeps `count` outside the retry loop, so retry logic must be evaluated carefully if a partial write path fails late. Level-low IRQs cannot be shared.

## Test Signals
Polling and IRQ modes, VID fallback path, response retry, malformed response length, burstcount zero timeout, command duration timeout, TPM2 match data, interrupt disable/re-enable behavior, and PM suspend/resume.
