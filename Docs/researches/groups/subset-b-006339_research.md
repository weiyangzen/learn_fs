<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_main.c -->
# sources/distributed-fs/ceph-client/security/integrity/evm/evm_main.c

## Purpose
Implements the EVM LSM integration that protects `security.evm` and the metadata covered by it. The file verifies EVM HMACs and signatures, blocks unsafe metadata/xattr changes, initializes EVM inode state, and updates `security.evm` after approved mutations.

## Important APIs, Types, And Functions
- Global state: `evm_initialized`, `evm_hmac_attrs`, `evm_config_xattrnames`, `evm_fixmode`.
- Verification: `evm_verify_hmac()`, exported `evm_verifyxattr()`, `evm_verify_current_integrity()`, `evm_read_protected_xattrs()`.
- Mutation gates: `evm_inode_setxattr()`, `evm_inode_removexattr()`, `evm_inode_setattr()`, `evm_inode_set_acl()`, `evm_inode_remove_acl()`.
- Post-change updates: `evm_inode_post_setxattr()`, `evm_inode_post_removexattr()`, `evm_inode_post_setattr()`, ACL post hooks, `evm_update_evmxattr()` callers.
- Initialization and integration: `evm_inode_init_security()`, `evm_inode_alloc_security()`, `evm_file_release()`, `evm_post_path_mknod()`, `DEFINE_LSM(evm)`.

## Control Flow
Boot initializes default protected xattr names, parses `evm=fix`, initializes the EVM keyring, and creates securityfs controls. Runtime LSM hooks first decide whether a mutation touches protected metadata, then verify current EVM integrity unless metadata writes are temporarily allowed. On success, post hooks reset cached status and recalculate the HMAC for `security.evm` when HMAC support is active. Verification reads `security.evm`, distinguishes HMAC, normal digital signature, and portable immutable signature formats, then compares a calculated HMAC or verifies a signature against the EVM keyring.

## State And Persistence
Persistent state is stored in xattrs, primarily `security.evm` and the protected xattrs listed in `evm_config_xattrnames`. Per-inode volatile state lives in `struct evm_iint_cache`, especially `evm_status`, `EVM_NEW_FILE`, and `EVM_IMMUTABLE_DIGSIG`. The code also tracks global initialization bits that determine whether HMACs, X509 verification, metadata-write allowance, setup completion, or sigv3 requirements are active.

## Dependencies And Integration Points
This file depends on VFS xattr operations, LSM hooks, integrity keyrings, crypto digest helpers, EVM digest/HMAC helpers from `evm.h`, POSIX ACL helpers, filesystem flags such as `SB_I_EVM_HMAC_UNSUPPORTED`, and IMA interactions via `security.ima` and `evm_verifyxattr()`. Overlay/copy-up handling permits only portable EVM signatures to be copied up.

## Risks And Edge Cases
Risk centers on stale iint cache state, filesystems without xattr/i_version support, unsupported HMAC filesystems, portable signatures that intentionally make metadata immutable, and fix mode accidentally masking labeling gaps. ACL changes are risky because system ACL xattrs can alter `i_mode`, which is covered by EVM. Secure boot disables `evm=fix`, and missing setup completion changes how unlabeled metadata updates are treated.

## Test Signals
Useful signals include successful/failed xattr and chmod/chown operations under EVM appraisal, audit messages for `update_metadata` and `appraise_metadata`, `security.evm` HMAC updates after metadata changes, immutable portable-signature behavior, overlay copy-up behavior, and boot logs showing initialized protected xattrs and HMAC attrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_posix_acl.c -->
# sources/distributed-fs/ceph-client/security/integrity/evm/evm_posix_acl.c

## Purpose
Provides a small helper that identifies POSIX ACL xattr names so EVM can treat ACL writes/removals as metadata-affecting operations even though they live under the `system.*` namespace.

## Important APIs, Types, And Functions
- `posix_xattr_acl(const char *xattr)` returns true for `XATTR_NAME_POSIX_ACL_ACCESS` and `XATTR_NAME_POSIX_ACL_DEFAULT`.

## Control Flow
The helper compares the requested xattr length and bytes against the two known POSIX ACL xattr names. It returns `1` on exact match and `0` otherwise.

## State And Persistence
This file has no persistent state. It only classifies names passed by EVM xattr and ACL hooks.

## Dependencies And Integration Points
It depends on Linux xattr constants and is consumed by `evm_main.c` when deciding whether an otherwise unprotected xattr operation can still require EVM revalidation because ACL updates may change mode bits protected by the EVM HMAC.

## Risks And Edge Cases
The function requires exact string length and content matches; aliases or future ACL xattr names would not be recognized. Because the return type is integer rather than bool, callers treat any nonzero value as true.

## Test Signals
Expected signals are that `system.posix_acl_access` and `system.posix_acl_default` trigger EVM ACL protections, while unrelated `system.*` xattrs do not.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_posix_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_secfs.c -->
# sources/distributed-fs/ceph-client/security/integrity/evm/evm_secfs.c

## Purpose
Implements the EVM securityfs control plane under `/sys/kernel/security/integrity/evm`. It exposes the EVM initialization/key state and, when enabled, lets privileged users extend or lock the set of protected xattrs.

## Important APIs, Types, And Functions
- `evm_read_key()` and `evm_write_key()` implement the `evm` control file.
- Optional `evm_read_xattrs()` and `evm_write_xattrs()` implement `evm_xattrs` under `CONFIG_EVM_ADD_XATTRS`.
- `evm_init_secfs()` creates the securityfs directory, control file, symlink, and optional xattr file.
- State includes `evm_dir`, `evm_symlink`, optional `evm_xattrs`, `xattr_list_mutex`, and `evm_xattrs_locked`.

## Control Flow
Initialization calls `integrity_fs_init()`, creates `integrity/evm`, creates an `evm` file backed by key operations, then creates a top-level symlink and optional xattr-control file. Writing a valid initialization bitmask to `evm` requires `CAP_SYS_ADMIN`; HMAC initialization calls `evm_init_key()` and sets `EVM_SETUP_COMPLETE`, preventing further writes. Optional xattr writes add security-prefixed names to `evm_config_xattrnames`, re-enable existing disabled names, or lock the file by writing `.`.

## State And Persistence
Securityfs files are runtime state, not on-disk configuration. The writes mutate global in-kernel state: `evm_initialized`, the protected-xattr list, and a lock bit that turns `evm_xattrs` read-only. Audit records persist externally through the audit subsystem.

## Dependencies And Integration Points
This file depends on securityfs, audit, capabilities, EVM key initialization, and the shared `integrity_dir` from `iint.c`. The protected-xattr list is consumed locklessly by HMAC/hash calculation and EVM policy checks, so new entries are appended and never deleted.

## Risks And Edge Cases
Incorrect initialization writes can permanently set setup completion for the boot. The xattr list uses a mutex only for read/write operations while hot paths traverse locklessly, making append-only behavior essential. `evm_xattrs` accepts only `security.*` names and enforces maximum xattr-name length; a lock write changes file mode to prevent later mutation.

## Test Signals
Read `/sys/kernel/security/integrity/evm/evm` for initialization bits, write valid and invalid bitmasks as privileged user, observe `EVM_SETUP_COMPLETE` after HMAC load, read/write `evm_xattrs` when configured, and check audit events for protected-xattr additions and failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_secfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/iint.c -->
# sources/distributed-fs/ceph-client/security/integrity/iint.c

## Purpose
Provides shared integrity subsystem helpers for securityfs setup, raw kernel file reads used by IMA hashing, and late loading of IMA/EVM X509 keys.

## Important APIs, Types, And Functions
- Global `struct dentry *integrity_dir`.
- `integrity_kernel_read()` wraps `__kernel_read()` without normal lock/security checks relevant to user reads.
- `integrity_load_keys()` invokes `ima_load_x509()` and conditionally `evm_load_x509()`.
- `integrity_fs_init()` and `integrity_fs_fini()` create and remove the shared `integrity` securityfs directory.

## Control Flow
IMA/EVM callers request the shared securityfs root through `integrity_fs_init()`. The function is idempotent if the directory already exists and reports non-`ENODEV` creation failures. On teardown, `integrity_fs_fini()` removes the directory only when present and empty. Key loading occurs once rootfs is ready through the integrity key-loading hook.

## State And Persistence
The only in-kernel state here is the `integrity_dir` dentry pointer. Securityfs directory presence is runtime state. Loaded X509 certificates persist in kernel keyrings for the boot.

## Dependencies And Integration Points
This file is a shared dependency for IMA and EVM securityfs code and for IMA file hashing in `ima_crypto.c`. It integrates with securityfs, key-loading helpers, and generated configuration controlling whether IMA or EVM owns X509 loading.

## Risks And Edge Cases
Securityfs may be unavailable, returning `-ENODEV`; callers must handle that as initialization failure or unsupported runtime interface. The raw read helper intentionally bypasses normal checks, so it should remain limited to integrity internals.

## Test Signals
Boot logs for integrity securityfs creation failures, presence of `/sys/kernel/security/integrity`, successful IMA/EVM key loading, and IMA hashes over files that require `integrity_kernel_read()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/iint.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/Makefile -->
# sources/distributed-fs/ceph-client/security/integrity/ima/Makefile

## Purpose
Defines how IMA object files are built and conditionally included based on kernel configuration.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_IMA) += ima.o ima_iint.o` builds the core IMA composite object and inode cache support.
- `ima-y` lists always-built core sources: securityfs, queue, init, main hooks, crypto, API, policy, template, and template library.
- Conditional additions include appraisal, module signatures, kexec, blacklist, asymmetric-key measurement, queued early boot keys, and EFI architecture policy.

## Control Flow
The kernel build system expands `ima-y` into the composite `ima.o`. Kconfig symbols determine whether optional source files become part of that object.

## State And Persistence
This file has no runtime state. It controls which code paths exist in the resulting kernel image.

## Dependencies And Integration Points
It maps Kconfig symbols to source files and therefore ties `Kconfig` decisions to link-time composition. EFI architecture policy is included only when both EFI and `IMA_SECURE_AND_OR_TRUSTED_BOOT` are enabled.

## Risks And Edge Cases
Incorrect object inclusion can produce unresolved symbols or silently remove expected enforcement features. Appraisal stubs in `ima.h` must remain consistent with optional object inclusion.

## Test Signals
Build output should include expected IMA objects for a given `.config`; link failures or missing runtime hooks indicate Kconfig/Makefile drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/Makefile -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_asymmetric_keys.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_asymmetric_keys.c

## Purpose
Measures asymmetric key payloads when keys are created or updated, allowing IMA policy to record key material linked to configured keyrings.

## Important APIs, Types, And Functions
- `ima_post_key_create_or_update()` is the LSM key hook implementation for asymmetric-key measurement.

## Control Flow
The hook ignores non-asymmetric keys and empty payloads. If early boot key queueing is active, it attempts to queue the key payload. Otherwise it calls `process_buffer_measurement()` using the keyring description as both event name and policy `func_data` for `KEY_CHECK`.

## State And Persistence
This file does not own persistent state. Measurements become IMA measurement-list entries, and early keys may be temporarily stored by the key queue subsystem until policy is ready.

## Dependencies And Integration Points
Depends on key subsystem types, `key_type_asymmetric`, optional early boot key queueing helpers, and the generic IMA buffer measurement path. Policy can select keyrings by name through the keyring description passed as function data.

## Risks And Edge Cases
Null keyrings or unexpected missing descriptions would affect event naming. Measurements are policy-dependent and can be skipped if no rule matches. Queuing is important before policy initialization; lost queueing would miss early key measurements.

## Test Signals
Create or update asymmetric keys in measured keyrings, then inspect the IMA measurement list for `KEY_CHECK` events named after the keyring. Test early boot queueing by loading keys before policy processing completes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_asymmetric_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_crypto.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_crypto.c

## Purpose
Implements IMA cryptographic hashing for file data, in-memory buffers, template field arrays, and the boot aggregate. It also initializes hash transforms for the configured IMA algorithm and TPM PCR banks.

## Important APIs, Types, And Functions
- Initialization: `ima_init_crypto()`, internal `ima_init_ima_crypto()`, `ima_alloc_tfm()`, `ima_free_tfm()`.
- Hashing: `ima_calc_file_hash()`, `ima_calc_buffer_hash()`, `ima_calc_field_array_hash()`.
- Boot aggregate: `ima_calc_boot_aggregate()`, internal TPM PCR read and aggregate helpers.
- Global state: `ima_shash_tfm`, `ima_sha1_idx`, `ima_hash_algo_idx`, `ima_extra_slots`, `ima_algo_array`.

## Control Flow
Initialization allocates the default hash transform, maps TPM allocated banks to hash algorithms, and reserves extra slots for SHA1 and the IMA default algorithm when missing from TPM banks. File hashing reopens non-readable files read-only when possible, rejects O_DIRECT consistently, reads page-sized chunks with `integrity_kernel_read()`, and finalizes the digest. Template hashing serializes fields in native or canonical format and computes digests for SHA1 plus all mapped TPM banks. Boot aggregate reads PCRs 0-7 and, for non-SHA1, PCRs 8-9.

## State And Persistence
Crypto transforms and algorithm descriptors are boot-lifetime state. Hash results are stored by callers in `ima_digest_data`, template entries, or `ima_iint_cache`. TPM PCR values are external hardware state that influences the boot aggregate.

## Dependencies And Integration Points
Depends on Linux crypto shash APIs, TPM bank metadata and PCR reads, IMA canonical format, template descriptors, `integrity_kernel_read()`, and hash algorithm tables. `ima_api.c`, `ima_init.c`, and `ima_main.c` rely on these functions.

## Risks And Edge Cases
Unsupported TPM algorithms fall back to padded SHA1 template digests. Missing SHA1 transform is fatal because SHA1 remains required for legacy template output. Very large or changing files can cause read/hash mismatch behavior. O_DIRECT returns `-EINVAL` and is later conditionally tolerated only by policy.

## Test Signals
Boot logs for allocated hash algorithms, measurement entries with expected per-bank digests, correct canonical binary output, O_DIRECT audit behavior, successful boot aggregate as first measurement, and failure logs for unavailable crypto transforms or TPM communication errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_efi.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_efi.c

## Purpose
Supplies architecture secure-boot IMA policy rules for EFI/secure-boot systems and enables kernel module and kexec signature enforcement when those rules are active.

## Important APIs, Types, And Functions
- `sb_arch_rules[]` contains secure-boot measurement/appraisal rules for kexec kernels, modules, and optionally IMA policy.
- `arch_get_ima_policy()` returns those rules when `CONFIG_IMA_ARCH_POLICY` is enabled and secure boot is active.

## Control Flow
At policy initialization time, IMA can call `arch_get_ima_policy()`. If secure boot is detected, this function enables module and kexec signature enforcement and returns the static rules; otherwise it returns `NULL`.

## State And Persistence
The rule array is static read-only policy data. Calls may change global kernel enforcement state for module and kexec signatures during the boot.

## Dependencies And Integration Points
Depends on `arch_get_secureboot()`, module signature enforcement, kexec signature enforcement, Kconfig symbols for module/kexec signature availability, machine keyring policy admission, and IMA architecture policy loading.

## Risks And Edge Cases
Rules vary by build options; if kernel module or kexec signature support is already compiled in, the corresponding appraisal rule may be omitted. Secure boot forces stricter behavior that can prevent unsigned module or kexec usage.

## Test Signals
On secure-boot systems, inspect loaded IMA policy for module/kexec measure and appraisal rules, verify unsigned modules/kexec images are denied when required, and confirm no architecture policy is returned when secure boot is off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_fs.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_fs.c

## Purpose
Implements IMA securityfs reporting and policy loading under `/sys/kernel/security/integrity/ima`. It exposes binary/ascii runtime measurements, counts, violation counts, and the policy file.

## Important APIs, Types, And Functions
- Measurement display: `ima_measurements_show()`, `ima_ascii_measurements_show()`, sequence operations, `ima_putc()`, `ima_print_digest()`.
- Counters: runtime measurement count and violation file operations.
- Policy loading: `ima_write_policy()`, `ima_read_policy()`, `ima_open_policy()`, `ima_release_policy()`.
- Setup: `create_securityfs_measurement_lists()`, `ima_fs_init()`.
- State: `ima_canonical_fmt`, `valid_policy`, `ima_fs_flags`, `ima_dir`, `ima_symlink`.

## Control Flow
Initialization creates the IMA securityfs directory, symlink, per-algorithm measurement files, legacy SHA1 symlinks, count files, and policy file. Measurement readers iterate the append-only measurement list and serialize entries either in binary template format or ascii. Policy writes are serialized with a mutex, can load rules directly or read them from an absolute path, and commit or discard rules on file release.

## State And Persistence
Securityfs files expose boot-lifetime in-memory state: measurement list, htable counters, policy rules, and violation count. `ima_canonical_fmt` affects binary serialization endianness. Policy may become read-only or removed depending on build options after a successful update.

## Dependencies And Integration Points
Depends on shared `integrity_dir`, IMA queue/list structures, template field show callbacks, policy parser/check/update APIs, kernel file loading for policy files, securityfs, seq_file, audit, and TPM bank/hash algorithm descriptors.

## Risks And Edge Cases
Binary output format must remain compatible with verifiers and kexec restore. Policy writes reject partial writes and can permanently remove write access depending on configuration. A failed policy update deletes staged rules and resets validity. Per-bank file creation must handle unknown TPM algorithms.

## Test Signals
Read `runtime_measurements_count`, `violations`, ascii and binary measurement files, and per-algorithm measurement files. Write valid and invalid policies, verify audit messages `policy_update completed/failed`, check readback when enabled, and test `ima_canonical_fmt` on big-endian or boot-parameter paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_iint.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_iint.c

## Purpose
Manages the per-inode IMA integrity cache stored through the inode LSM security blob.

## Important APIs, Types, And Functions
- `ima_iint_find()` returns an existing cache only when `S_IMA` is set.
- `ima_inode_get()` allocates and attaches a new `ima_iint_cache`.
- `ima_inode_free_rcu()` frees cache data during inode security RCU cleanup.
- `ima_iintcache_init()` creates the slab cache.

## Control Flow
Callers holding the inode lock request an iint with `ima_inode_get()`. If none exists, the code allocates from `ima_iint_cache`, initializes flags/statuses/hash/version, annotates the mutex lock class by filesystem stack depth, sets `S_IMA`, and stores the pointer in the inode security blob. Freeing occurs later through the LSM inode-free RCU hook.

## State And Persistence
The cache is volatile per-inode state. It persists while the inode exists and stores collected hash data, version/change-cookie data, measurement flags, appraisal statuses, and atomic invalidation flags.

## Dependencies And Integration Points
Depends on LSM blob sizing from `ima_blob_sizes`, slab allocation, lockdep, filesystem stack depth, and the `S_IMA` inode flag. `ima_main.c`, `ima_api.c`, and `ima_appraise.c` all rely on this cache.

## Risks And Edge Cases
Allocation failure causes IMA operations to fail or skip enforcement depending on caller context. Lockdep class assignment must account for overlay/stacked filesystems to avoid false positives. RCU cleanup assumes the security blob still contains the pointer slot.

## Test Signals
Runtime signals include successful measurement/appraisal caching, no leaks on inode eviction, stable behavior on overlayfs, and lockdep remaining quiet for nested IMA operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_iint.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_kexec.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_kexec.c

## Purpose
Carries the IMA measurement list across kexec soft reboots and validates/restores measurement buffers supplied by the previous kernel.

## Important APIs, Types, And Functions
- Under `CONFIG_IMA_KEXEC`: `ima_add_kexec_buffer()`, `ima_kexec_post_load()`, `ima_measure_kexec_event()`, internal allocation/dump/update helpers, reboot notifier.
- Always built restore path: `ima_load_kexec_buffer()`.
- Range validation: `ima_validate_range()`.
- State includes `ima_kexec_file`, `kexec_segment_size`, `ima_kexec_buffer`, and notifier registration flag.

## Control Flow
During kexec file load, IMA sizes a segment for the current binary runtime list plus extra memory, allocates a seq_file buffer, measures a `kexec_load` event, and adds an aligned buffer segment to the kexec image. After load, it maps the segment and registers a reboot notifier. At execute time, the notifier serializes the current measurement list with an `ima_kexec_hdr` into the mapped segment. On next boot, `ima_load_kexec_buffer()` fetches and restores that list, then frees the handoff buffer.

## State And Persistence
The handoff buffer is transient memory passed between kernels. The serialized list and header persist only across the kexec transition. The runtime measurement list remains append-only and is restored into the next kernel's IMA state.

## Dependencies And Integration Points
Depends on kexec image APIs, seq_file serialization from `ima_fs.c`, IMA queue state, reboot notifiers, physical memory validation helpers, architecture page/RAM checks, and `ima_restore_measurement_list()`.

## Risks And Edge Cases
Crash kernels are skipped. Oversized measurement lists are rejected if they approach address limits or consume too much RAM. The segment size cannot change between load and execute. Mapping failures or buffer overflows can prevent restoration and should not corrupt the next kernel.

## Test Signals
Kexec tests should show `ima_kexec` measurement events, populated `image->ima_buffer_*` fields, successful restore logs after soft reboot, correct measurement counts before/after kexec, and warnings for invalid previous-kernel buffer ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_kexec.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_modsig.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_modsig.c

## Purpose
Supports IMA appraisal of module-style appended PKCS#7 signatures embedded at the end of files.

## Important APIs, Types, And Functions
- `struct modsig` stores parsed PKCS#7 message, digest algorithm, digest pointer/size, and raw PKCS#7 bytes.
- `ima_read_modsig()` locates and parses an appended module signature.
- `ima_collect_modsig()` supplies detached file data to PKCS#7 and retrieves the digest.
- `ima_modsig_verify()`, `ima_get_modsig_digest()`, `ima_get_raw_modsig()`, `ima_free_modsig()`.

## Control Flow
`ima_read_modsig()` checks for `MODULE_SIGNATURE_MARKER`, validates the module signature footer with `mod_check_sig()`, allocates a flexible `modsig`, parses the PKCS#7 payload, and copies raw signature bytes. Later, collection strips the marker/footer/signature from the signed data, supplies detached data to PKCS#7, and asks PKCS#7 for the digest. Verification delegates to PKCS#7 signature verification against the selected keyring.

## State And Persistence
`struct modsig` is per-operation heap state and is freed after appraisal/measurement. Raw signature bytes may be included in IMA templates that support modsig fields, but this file itself does not persist state.

## Dependencies And Integration Points
Depends on module signature format constants, `mod_check_sig()`, PKCS#7 parser/verifier APIs, asymmetric key support, and callers in `ima_main.c`/`ima_appraise.c` that allow modsig policy.

## Risks And Edge Cases
Malformed or too-short buffers return `-ENOENT` or parser errors. Digest algorithm is unknown until collection supplies detached data. Size arithmetic must correctly exclude signature trailer bytes or verification will cover the wrong data.

## Test Signals
Use files with valid appended module signatures under IMA modsig policy, verify appraisal success, inspect measurement templates containing modsig data where configured, and test malformed marker/footer/signature cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_modsig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_mok.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_mok.c

## Purpose
Initializes the optional IMA blacklist keyring used to reject revoked binary hashes or keys during appraisal.

## Important APIs, Types, And Functions
- Global `struct key *ima_blacklist_keyring`.
- `ima_mok_init()` allocates `.ima_blacklist` during `device_initcall`.

## Control Flow
At device init time, the code allocates a `key_restriction`, sets its check function to `restrict_link_by_builtin_trusted`, then creates a persistent root-owned keyring named `.ima_blacklist` with view/read/write/search permissions and keep-in-memory allocation flags. Allocation failure panics.

## State And Persistence
The keyring persists for the boot and is kept out of quota. It stores blacklist entries consulted by IMA appraisal paths such as `ima_check_blacklist()`.

## Dependencies And Integration Points
Depends on the Linux keyring subsystem, built-in trusted key restriction, current credentials during init, and blacklist lookup helpers used from appraisal code.

## Risks And Edge Cases
Failure to allocate the restriction or keyring panics the kernel when this feature is configured. Link restrictions mean blacklist entries must be trusted according to built-in key policy.

## Test Signals
Boot should log allocation of the IMA blacklist keyring. Loading a revoked hash/key should make appraisal fail with blacklist behavior, while untrusted additions should be rejected by the keyring restriction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_mok.c -->
