<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_appraise.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_appraise.c

## Purpose
Implements IMA appraisal: validating `security.ima` hashes/signatures, consulting EVM for xattr integrity, enforcing appraisal policy, supporting fix/log/enforce modes, handling appended module signatures, blacklist checks, and registering LSM hooks that invalidate appraisal state on metadata/xattr changes.

## Important APIs, Types, And Functions
- Mode and policy: `ima_appraise_parse_cmdline()`, `is_ima_appraise_enabled()`, `ima_must_appraise()`.
- Xattr handling: `ima_get_hash_algo()`, `ima_read_xattr()`, `ima_fix_xattr()`, `validate_hash_algo()`.
- Verification: `xattr_verify()`, `modsig_verify()`, `ima_appraise_measurement()`, `ima_check_blacklist()`.
- Cache/update: `ima_get_cache_status()`, internal status setters, `ima_update_xattr()`.
- LSM hooks: `ima_inode_post_setattr()`, `ima_inode_setxattr()`, ACL hooks, remove-xattr hooks, `init_ima_appraise_lsm()`.

## Control Flow
Boot parsing sets appraisal mode unless secure boot keeps enforcement. Runtime appraisal reads `security.ima`, asks EVM to verify that xattr's metadata protection, verifies hashes/signatures against collected file digests, optionally tries a module-style appended signature, checks blacklists, and sets per-hook cache status. In fix mode, missing or stale hash xattrs can be repaired unless a digital signature prevents replacement. LSM xattr/ACL/setattr hooks mark cached state dirty so the next measurement reappraises.

## State And Persistence
Persistent appraisal data lives in `security.ima` and, indirectly, `security.evm`. Volatile state lives in `ima_iint_cache` status fields, flags, and atomic flags such as `IMA_DIGSIG`, `IMA_CHANGE_XATTR`, `IMA_CHANGE_ATTR`, and `IMA_UPDATE_XATTR`. Blacklist state lives in integrity keyrings.

## Dependencies And Integration Points
Integrates with EVM via `evm_verifyxattr()` and `evm_fix_hmac()`, keyrings via `integrity_digsig_verify()` and platform fallback for kexec kernels, fs-verity signatures, module-signature helpers, VFS xattr operations, capability checks, and LSM hook registration.

## Risks And Edge Cases
New zero-length files, missing xattrs, unknown key errors, signature version requirements, unsupported hash algorithms, untrusted mounters, and filesystems with unverifiable signatures all have distinct outcomes. Fix mode must not overwrite file signatures. Policy-restricted hash allowlists can reject otherwise valid xattrs.

## Test Signals
Signals include appraisal pass/fail audit causes such as `missing-hash`, `invalid-HMAC`, `invalid-signature`, `IMA-signature-required`, `unverifiable-signature`, successful fix-mode xattr writes, denied unsupported hash algorithms, and correct `-EACCES` behavior only when enforcement is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_appraise.c -->
