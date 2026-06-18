<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-cmd.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-cmd.c

## Purpose
Implements TPM 2.0 command helpers used by the kernel for timeouts, PCR read/extend, RNG, context flush, property/capability reads, shutdown, self-test, protocol probe, PCR bank discovery, command-attribute discovery, startup, and session initialization.

## Important APIs, Types, And Functions
Exports `tpm2_find_hash_alg()`, `tpm2_get_timeouts()`, `tpm2_calc_ordinal_duration()`, `tpm2_pcr_read()`, `tpm2_pcr_extend()`, `tpm2_get_random()`, `tpm2_flush_context()`, `tpm2_get_tpm_pt()`, `tpm2_probe()`, `tpm2_get_pcr_allocation()`, `tpm2_get_cc_attrs_tbl()`, `tpm2_auto_startup()`, and `tpm2_find_cc()`. It includes module parameter `disable_pcr_integrity`.

## Control Flow
PCR read builds a bank-selecting `PCR_Read` command and validates digest size. PCR extend starts an HMAC session unless disabled, appends protected handle/name and auth, fills HMAC, transmits, and validates the response HMAC. RNG starts a session, optionally requests response encryption, loops until enough random bytes are returned or retries are exhausted, and ends the session on errors. Auto-startup sets timeouts, handles initialize/startup, self-tests, reads command attributes, handles field-upgrade/failure modes, and initializes TPM2 sessions.

## State And Persistence
The file populates `chip->allocated_banks`, `nr_allocated_banks`, `cc_attrs_tbl`, `nr_commands`, timeout flags, firmware-upgrade flag, and optionally TPM2 HMAC session/null-key state through `tpm2_sessions_init()`.

## Dependencies And Integration Points
Used by generic TPM core, sysfs PCR access, resource-manager command validation, TPM2 sessions, and chip bootstrap. It depends on `tpm_buf`, crypto hash metadata, TPM2 command attributes, and session/HMAC helpers.

## Risks And Edge Cases
PCR integrity can be disabled by module parameter. Capability responses must be length-checked and bounded by `TPM2_MAX_PCR_BANKS` and command-count sanity limits. Field-upgrade TPMs can return success with empty property lists. HMAC sessions must be ended on allocation or transmit failures.

## Test Signals
TPM2 probe across TPM1/TPM2 hardware, PCR bank discovery for supported and unknown hashes, PCR extend with and without HMAC integrity, RNG with encrypted responses, command-attribute table parsing, startup from `RC_INITIALIZE`, field-upgrade modes, and shutdown on suspend/reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-cmd.c -->
