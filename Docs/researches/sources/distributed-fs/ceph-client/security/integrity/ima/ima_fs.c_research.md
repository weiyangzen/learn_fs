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
