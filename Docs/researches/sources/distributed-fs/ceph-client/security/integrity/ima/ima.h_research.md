<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima.h -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima.h

## Purpose
Central internal header for IMA. It defines measurement templates, inode-integrity state, action flags, hook identifiers, policy APIs, appraisal APIs, crypto APIs, kexec support, key measurement support, and configuration-dependent stubs.

## Important APIs, Types, And Functions
- Core structs: `ima_event_data`, `ima_field_data`, `ima_template_field`, `ima_template_desc`, `ima_template_entry`, `ima_queue_entry`, `ima_kexec_hdr`, `ima_iint_cache`, `ima_algo_desc`.
- Action/cache flags: `IMA_MEASURE`, `IMA_APPRAISE`, `IMA_AUDIT`, `IMA_HASH`, done flags, appraise subaction flags, and nonaction policy flags such as `IMA_DIGSIG_REQUIRED`, `IMA_MODSIG_ALLOWED`, and `IMA_VERITY_REQUIRED`.
- Hook enum: `enum ima_hooks` covers file, mmap, bprm, creds, modules, firmware, kexec, policy, key, critical data, and setxattr checks.
- APIs declared for crypto, measurement storage, securityfs display, policy matching, appraisal, modsig handling, key queueing, and kexec restore.

## Control Flow
The header does not execute control flow directly, but it defines the contracts used by `ima_main.c`: policy produces action bits, action bits select measure/appraise/audit/hash work, and done bits cache completed work in `ima_iint_cache`. Configuration blocks provide no-op stubs when optional features are disabled.

## State And Persistence
`ima_iint_cache` is the key per-inode volatile state, storing mutex-protected digest/version/flags plus atomic invalidation flags and per-hook appraisal statuses. Measurement list entries persist for the boot in `ima_measurements` and may be exported for kexec. Global hash algorithm and TPM bank descriptors are initialized once.

## Dependencies And Integration Points
It includes the shared integrity header, Linux security/TPM/audit/hash interfaces, and declares integration with EVM xattrs, LSM policy matching, TPM measurement queues, keyrings, fs-verity, appended module signatures, and securityfs.

## Risks And Edge Cases
Flag overlap is security-sensitive; stale done bits can skip required appraisal, while overly broad invalidation can cause repeated hashing. Optional stubs must preserve caller expectations. The hook enum and string arrays must stay aligned with policy token parsing.

## Test Signals
Compile coverage across configurations is critical: appraisal off/on, modsig off/on, kexec off/on, LSM rules off/on, and key queueing. Runtime signals include correct per-hook cache status and policy actions matching expected hook identifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima.h -->
