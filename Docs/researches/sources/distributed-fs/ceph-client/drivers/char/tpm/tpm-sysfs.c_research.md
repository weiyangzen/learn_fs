<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-sysfs.c

## Purpose
Builds TPM sysfs attributes for legacy TPM1 state, TPM version reporting, optional TPM2 HMAC null-key name exposure, and PCR bank value directories.

## Important APIs, Types, And Functions
Defines show/store handlers for `pubek`, `pcrs`, `enabled`, `active`, `owned`, `temp_deactivated`, `caps`, `cancel`, `durations`, `timeouts`, `tpm_version_major`, and optional `null_name`. It builds PCR attribute groups with macros `PCR_ATTR_BUILD()` for SHA1, SHA256, SHA384, SHA512, and SM3, and exports `tpm_sysfs_add_device()`.

## Control Flow
TPM1 attributes issue TPM1 commands under `tpm_try_get_ops()` to read PUBEK, PCRs, capability flags, version, and state. PCR bank files call generic `tpm_pcr_read()` using the bank algorithm and PCR number encoded in the attribute. `tpm_sysfs_add_device()` attaches either TPM1 or TPM2 base group and then one PCR group per allocated bank.

## State And Persistence
Attribute groups persist on the class device while the chip is registered. PCR values are read live on each file read. The optional `null_name` exposes the TPM2 NULL primary name saved during HMAC session initialization.

## Dependencies And Integration Points
Called during `tpm_chip_register()` after PCR allocation. Integrates TPM1 command helpers, generic PCR APIs, TPM2 HMAC initialization state, sysfs attribute groups, and legacy sysfs symlinks created by `tpm-chip.c`.

## Risks And Edge Cases
TPM1 sysfs handlers return zero-length output on command failure, preserving older behavior but hiding errors. PCR group macros assume 24 platform PCRs and fixed supported hash algorithms. Adding a new TPM hash requires a macro group and switch case.

## Test Signals
Read each TPM1 sysfs file on enabled, disabled, and deactivated TPMs; read TPM2 PCR bank directories for every allocated bank; validate unsupported bank logging; check `cancel` store behavior; and verify `null_name` appears only with TPM2 HMAC support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-sysfs.c -->
