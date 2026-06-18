# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_core.c

## Purpose
Implements the transport-independent TPM TIS/PTP FIFO state machine used by MMIO, SPI, I2C, and platform-specific PHY front-ends.

## Important APIs, Types, And Functions
Exports `tpm_tis_core_init()`, `tpm_tis_remove()`, and `tpm_tis_resume()`. Main callbacks are `tpm_tis_status()`, `tpm_tis_recv()`, `tpm_tis_send()`, `tpm_tis_ready()`, `tpm_tis_request_locality()`, and `tpm_tis_relinquish_locality()`. Important helpers include `wait_for_tpm_stat()`, `wait_startup()`, `check_locality()`, `get_burstcount()`, `recv_data()`, `tpm_tis_send_data()`, IRQ probing/handler helpers, timeout/duration override helpers, `probe_itpm()`, and `tpm_tis_clkrun_enable()`.

## Control Flow
Core init allocates a TPM chip, installs default maximum timeouts, stores PHY ops, reads vendor ID, applies vendor quirks, maps Intel Bay Trail CLKRUN control when needed, waits for access-valid, reads and disables interrupt capabilities, requests locality zero, probes TPM version, reads revision, detects iTPM behavior, bootstraps the chip, optionally validates/probes IRQ operation, and registers the TPM chip. Send acquires FIFO readiness, writes all but the last byte in burst chunks while checking `DATA_EXPECT`, writes the last byte, verifies CRC when available, writes `GO`, and waits for data availability in IRQ mode. Recv reads header and body by burst count, validates expected length, checks for leftover data, verifies CRC, and retries recoverable reads with `RESPONSE_RETRY`.

## State And Persistence
`struct tpm_tis_data` stores locality, locality reference count, IRQ, interrupt mask, waitqueues, quirk flags, unhandled IRQ counters, manufacturer id, CLKRUN mapping, PHY ops, RNG quality, and polling delays. Hardware state includes locality ownership, interrupt enable/status, FIFO contents, and TPM status bits.

## Dependencies And Integration Points
Depends on PHY callbacks from `tpm_tis_core.h`, TPM core startup/bootstrap/registration, TPM1/TPM2 capability helpers, DMI for interrupt-storm diagnostics, ACPI handles from front-ends, and platform PM.

## Risks And Edge Cases
Locality reference counting must balance across nested TPM core operations. IRQs are probed by causing a TPM command and disabled if unconfirmed; interrupt storms force polling and schedule IRQ freeing outside interrupt context. Vendor quirks alter cancellation, timeouts, durations, and status-valid retry behavior. Invalid `TPM_STS` values dump stack for misuse forensics. CLKRUN manipulation is x86/Bay Trail specific and reference-counted.

## Test Signals
FIFO send/recv with burst boundaries, TPM1 and TPM2 startup, locality nesting, IRQ probe success/failure, interrupt storms, response retry, CRC-enabled PHYs, vendor timeout overrides, iTPM detection, ST/Winbond cancellation quirks, Bay Trail CLKRUN, and resume interrupt re-enable/self-test.
