<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_main.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_main.c

## Purpose
Implements the primary IMA LSM hooks and central measurement/appraisal state machine. It covers file opens, mmap/mprotect, exec, credential calculation, kernel file reads, kernel load data, kexec command lines, critical data, key hooks, exported hash APIs, and initialization.

## Important APIs, Types, And Functions
- Central engine: `process_measurement()`.
- Hook helpers: `ima_file_mmap()`, `ima_file_mprotect()`, `ima_bprm_check()`, `ima_creds_check()`, `ima_file_check()`, `ima_read_file()`, `ima_post_read_file()`, `ima_load_data()`, `ima_post_load_data()`.
- Exported APIs: `ima_file_hash()`, `ima_inode_hash()`, `ima_measure_critical_data()`.
- Buffer measurement: `process_buffer_measurement()`, `ima_kexec_cmdline()`.
- Init and LSM registration: `init_ima()`, `init_ima_lsm()`, `DEFINE_LSM(ima)`.
- Boot params: `ima=`, `ima_hash=`.

## Control Flow
Each LSM hook maps its context to an `enum ima_hooks` value and calls `process_measurement()` or the buffer-measurement path. `process_measurement()` looks up policy action bits, allocates/locks the inode iint, performs read/write violation checks, invalidates stale cache state, reads `security.ima` and optional appended signatures, collects a digest, stores measurements, appraises signatures or hashes, audits, applies O_DIRECT policy, enforces hash allowlists, and returns access denial only when appraisal enforcement requires it.

## State And Persistence
Per-inode state is cached in `ima_iint_cache` with done/action flags, measured PCR bitmask, hash, real-inode version, and atomic invalidation flags. The runtime measurement list and TPM PCR extensions persist for the boot. Global state includes `ima_appraise`, `ima_hash_algo`, `ima_disabled`, and LSM policy notifier registration.

## Dependencies And Integration Points
Integrates with VFS, mmap, exec, kernel module/firmware/kexec loading, LSM properties, EVM metadata status, IMA policy, crypto, appraisal, module signatures, key hooks, crash/kdump mode, securityfs, TPM, and module-request filtering for asymmetric crypto verification loops.

## Risks And Edge Cases
The central risks are stale cache flags, files changed while measured, open-writer and ToMToU violations, inability to verify signatures on untrusted filesystems, mprotect transitions to executable mappings, appraisal of buffers without file descriptors, compressed module deferral, and kdump-only IMA disabling. Enforcement mode converts appraisal failures to `-EACCES`.

## Test Signals
Exercise file open/read/exec/mmap policies, mprotect execute transitions, kernel module/firmware/kexec loading, O_DIRECT rules, ToMToU/open-writers violations, `ima_file_hash()` and `ima_inode_hash()` exports, critical-data measurements, policy hash allowlists, and boot logs for LSM registration and hash fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_main.c -->
