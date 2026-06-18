<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm1-cmd.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm1-cmd.c

## Purpose
Implements TPM 1.x command helpers used by the kernel for startup, timeout discovery, PCR operations, capabilities, RNG, self-test, suspend savestate, and PCR allocation.

## Important APIs, Types, And Functions
Exports `tpm1_calc_ordinal_duration()`, `tpm1_get_timeouts()`, `tpm1_pcr_extend()`, `tpm1_getcap()`, `tpm1_get_random()`, `tpm1_pcr_read()`, `tpm1_do_selftest()`, `tpm1_auto_startup()`, `tpm1_pm_suspend()`, and `tpm1_get_pcr_allocation()`. Internal helpers include `tpm1_startup()` and `tpm1_continue_selftest()`.

## Control Flow
Timeout discovery reads TIS timeout and duration capabilities, performs manual startup on `TPM_ERR_INVALID_POSTINIT`, applies vendor override hooks, repairs zero or millisecond-reported values, and stores jiffies in the chip. Self-test sends `ContinueSelfTest` and polls PCR0 reads until tests finish, disabled/deactivated states are accepted, or the duration expires. RNG loops `GetRandom` up to five retries. Suspend optionally extends a dummy PCR then retries `SaveState` on `TPM_WARN_RETRY`.

## State And Persistence
The file initializes `chip->timeout_*`, `chip->duration[]`, `timeout_adjusted`, `duration_adjusted`, `TPM_CHIP_FLAG_HAVE_TIMEOUTS`, `TPM_CHIP_FLAG_ALWAYS_POWERED`, `TPM_CHIP_FLAG_FIRMWARE_UPGRADE`, and the single SHA1 allocated PCR bank.

## Dependencies And Integration Points
Called by generic TPM APIs and chip bootstrap. It depends on `tpm_buf` construction, `tpm_transmit_cmd()`, TPM1 capability structures from `tpm.h`, hash digest sizes, and optional transport timeout/duration update hooks.

## Risks And Edge Cases
Firmware-reported timeouts and durations are often wrong and require heuristics. Positive TPM errors are converted to probe failures in startup paths. RNG and PCR read length checks must prevent short response use. Suspend SaveState after prior firmware use may need repeated retries.

## Test Signals
TPM1 startup on already-started and postinit-required chips, bogus timeout/duration reports, disabled/deactivated self-test behavior, failed self-test firmware-upgrade mode, PCR read/extend, random short reads and retries, and suspend SaveState retry loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm1-cmd.c -->
