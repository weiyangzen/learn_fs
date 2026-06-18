<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/Kconfig -->
# sources/distributed-fs/ceph-client/security/integrity/ima/Kconfig

## Purpose
Defines build-time configuration for IMA measurement, appraisal, templates, hash algorithms, kexec carry-over, architecture policy, keyrings, X509 loading, asymmetric-key measurement, and blacklist support.

## Important APIs, Types, And Functions
- Core `CONFIG_IMA` selects securityfs, crypto, HMAC/SHA1/hash info, path security hooks, TPM support, and integrity audit when audit is enabled.
- Measurement options include `IMA_KEXEC`, `IMA_MEASURE_PCR_IDX`, `IMA_DISABLE_HTABLE`, and `IMA_KEXEC_EXTRA_MEMORY_KB`.
- Template/hash choices set `IMA_DEFAULT_TEMPLATE` and `IMA_DEFAULT_HASH`.
- Appraisal options include `IMA_APPRAISE`, boot parameter support, build-time policy requirements, appended module signatures, and signed init.
- Key options include trusted-keyring admission, blacklist keyring, X509 path loading, and asymmetric-key measurement/queueing.

## Control Flow
Kconfig dependencies control which source files are compiled and which policy modes are available. Choices select one default template and one default hash, while runtime boot parameters can override some compiled defaults if secure-boot and appraisal restrictions allow it.

## State And Persistence
The file produces compile-time symbols used throughout IMA. These choices persist in the kernel image and shape runtime defaults, available securityfs files, accepted signature mechanisms, and keyring behavior.

## Dependencies And Integration Points
It integrates with TPM, crypto algorithms, system and secondary trusted keyrings, module/kexec signature options, EFI/architecture secure boot policy, fs-verity-related appraisal behavior, audit, and security modules that supply LSM policy fields.

## Risks And Edge Cases
Enabling strict build-time appraisal rules can prevent boot or runtime loading of modules, firmware, kexec images, or policy files if signatures and keys are missing. Hash algorithm choices require matching built-in crypto. Kexec list memory can be too small for large measurement lists unless extra memory is configured.

## Test Signals
Configuration tests should verify expected object inclusion, boot logs for selected hash/template/appraisal behavior, securityfs policy permissions, required-signature enforcement for modules/firmware/kexec/policy, and X509/keyring availability when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/Kconfig -->
