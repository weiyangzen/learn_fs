<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_init.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_init.c

## Purpose
Coordinates IMA runtime initialization: TPM discovery, keyring setup, crypto/template initialization, kexec-list restore, boot aggregate measurement, policy setup, securityfs setup, key queue setup, reboot notifier registration, and initial kernel-version measurement.

## Important APIs, Types, And Functions
- Global `boot_aggregate_name` and `ima_tpm_chip`.
- `ima_add_boot_aggregate()` creates the first measurement list entry.
- Optional `ima_load_x509()` loads IMA and EVM X509 certificates while appraisal policy is temporarily masked.
- `ima_init()` is the main initialization sequence called by `ima_main.c`.

## Control Flow
Initialization gets the default TPM chip, initializes the IMA keyring, crypto transforms, templates, restores any previous kexec measurement list, initializes digest support, adds the boot aggregate, initializes policy, creates securityfs, initializes queued keys and reboot notifier, then measures kernel version critical data.

## State And Persistence
Boot-lifetime state includes the TPM chip pointer, IMA keyring contents, measurement list, policy state, securityfs files, queued key state, and reboot notifier. The boot aggregate becomes the first persistent measurement-list entry for the boot.

## Dependencies And Integration Points
Depends on TPM, integrity keyrings, crypto, templates, kexec restore, digest initialization, policy, securityfs, key queueing, reboot notifier, EVM X509 loading, and `ima_measure_critical_data()`.

## Risks And Edge Cases
No TPM triggers TPM-bypass behavior but still creates measurements. Crypto initialization can fail for a selected hash and is retried by the caller with default hash. The boot aggregate must be first; failure prevents IMA initialization. Temporarily masking appraisal during X509 load avoids appraising the certificate file before keys exist.

## Test Signals
Boot logs for TPM discovery/bypass, successful first `boot_aggregate` measurement, available IMA keyring, securityfs entries, restored kexec measurements when present, and a `kernel_version` critical-data measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_init.c -->
