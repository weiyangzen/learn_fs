<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-interface.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-interface.c

## Purpose
Implements the generic TPM command transport wrapper and public in-kernel TPM APIs for command transmit, PCR operations, RNG, startup, suspend/resume, and module initialization.

## Important APIs, Types, And Functions
Exports `tpm_calc_ordinal_duration()`, `tpm_transmit()`, `tpm_transmit_cmd()`, `tpm_get_timeouts()`, `tpm_is_tpm2()`, `tpm_pcr_read()`, `tpm_pcr_extend()`, `tpm_pm_suspend()`, `tpm_pm_resume()`, and `tpm_get_random()`. Internal helpers include `tpm_try_transmit()`, `tpm_chip_cancel()`, `tpm_chip_status()`, and module init/exit for classes, char-device region, and common dev workqueue.

## Control Flow
`tpm_try_transmit()` validates the command header length, sends through chip ops, handles synchronous devices or waits for IRQ/poll completion, receives the response, and validates response length. `tpm_transmit()` wraps this with TPM2 retry/testing backoff and restores the original header/handles before retries. Public APIs acquire ops, dispatch to TPM1 or TPM2 implementations, and release ops. Suspend sends TPM2 shutdown-state or TPM1 savestate unless the chip is always powered or firmware-managed.

## State And Persistence
Module initialization registers TPM classes and char-device numbers. Runtime state changes include suspended flags, TPM2 auth-session teardown, retry buffers, PCR/RNG command buffers, and module parameter `suspend_pcr`.

## Dependencies And Integration Points
Central path for transport `struct tpm_class_ops`, TPM1/TPM2 command files, chip lifecycle locking, PM core, hwrng, userspace char devices, and in-kernel consumers of PCR/RNG APIs.

## Risks And Edge Cases
Command length validation protects against malformed buffers. Retry loops must preserve transformed handles for TPM2 spaces. Poll completion must detect cancellation and timeout. Suspend intentionally ignores errors after logging to avoid blocking system sleep.

## Test Signals
Malformed command headers, synchronous and asynchronous transport paths, IRQ and polling completion, TPM2 `RC_RETRY` and `RC_TESTING`, PCR read/extend across banks, RNG size validation, suspend/resume on TPM1 and TPM2, and module init/exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-interface.c -->
