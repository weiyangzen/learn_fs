<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_api.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_api.c

## Purpose
Provides core IMA helper APIs for allocating measurement templates, collecting file/buffer/fs-verity hashes, storing measurements, adding violations, auditing hashes, and deriving paths.

## Important APIs, Types, And Functions
- Template lifecycle: `ima_alloc_init_template()`, `ima_free_template_entry()`, `ima_store_template()`.
- Measurement and violation: `ima_collect_measurement()`, `ima_store_measurement()`, `ima_add_violation()`.
- Policy bridge: `ima_get_action()` filters global policy flags and calls `ima_match_policy()`.
- Utility: `ima_audit_measurement()`, `ima_d_path()`, internal `ima_get_verity_digest()`.

## Control Flow
Callers obtain policy actions, collect a digest into the inode's `ima_iint_cache`, then optionally allocate and store a template entry. Template allocation calls each template field initializer and accumulates serialized field lengths. Storing calculates template digests, appends the entry to the IMA queue, and extends the configured PCR. Violations bypass normal digest calculation and add invalidating entries.

## State And Persistence
Collected hashes and inode version/change-cookie data are cached in `iint->ima_hash` and `iint->real_inode`. Stored measurements append to the in-memory measurement list and TPM PCR state. Audit records include hash algorithm and digest when requested.

## Dependencies And Integration Points
Depends on VFS attributes, `integrity_kernel_read()` through crypto helpers, fs-verity digests, IMA template field implementations, IMA queue insertion, TPM digest arrays, and audit. `ima_d_path()` feeds stable path strings into measurement and audit records.

## Risks And Edge Cases
Filesystems without change cookies or i_version force conservative change assumptions elsewhere. O_DIRECT and unreadable files can produce temporary collection errors. fs-verity mode records the verity digest rather than a traditional file hash. Template allocation must free partially initialized fields on failure.

## Test Signals
Look for measurement list additions, PCR extension success/failure audits, violation count increments, correct handling of duplicate PCR measurements, fs-verity digest measurement, O_DIRECT audit causes, and readable audit hash records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_api.c -->
