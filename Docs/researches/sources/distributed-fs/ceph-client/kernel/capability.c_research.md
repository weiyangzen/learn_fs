# sources/distributed-fs/ceph-client/kernel/capability.c

## Purpose

`capability.c` implements the kernel capability syscall surface and common capability-check helpers. It translates legacy userspace capability ABI versions into `kernel_cap_t`, delegates policy decisions to the Linux Security Module hooks, updates process credentials through the normal copy-on-write credential path, and exports capability predicates used by filesystem, ptrace, namespace, and general kernel authorization code.

The file is not Ceph-specific despite its repository path; it is generic Linux kernel privilege plumbing. It also owns the `no_file_caps` boot setup switch through the global `file_caps_enabled`.

## Important APIs, types, and functions

- `file_caps_enabled` is initialized to enabled and can be cleared by `file_caps_disable()` via `__setup("no_file_caps", ...)`.
- `cap_validate_magic()` validates `_LINUX_CAPABILITY_VERSION_1`, `_VERSION_2`, and `_VERSION_3`, returns the number of 32-bit words userspace expects, warns once for legacy/deprecated ABI use, and writes `_KERNEL_CAPABILITY_VERSION` back for unknown versions.
- `SYSCALL_DEFINE2(capget)` reads `header->pid`, calls `cap_get_target_pid()`, splits effective/permitted/inheritable `kernel_cap_t` values into legacy 32-bit user fields, and copies only the ABI-requested word count.
- `SYSCALL_DEFINE2(capset)` accepts only the current task, copies user capability data, masks it with `CAP_VALID_MASK` through `mk_kernel_cap()`, creates new credentials with `prepare_creds()`, validates and applies them through `security_capset()`, audits, and commits or aborts.
- `has_ns_capability()`, `has_ns_capability_noaudit()`, and `has_capability_noaudit()` query another task's credentials under RCU.
- `ns_capable()`, `ns_capable_noaudit()`, `ns_capable_setid()`, and `capable()` check the current task through `ns_capable_common()` and set `PF_SUPERPRIV` on success.
- `file_ns_capable()` checks the file opener's saved credentials, not current credentials.
- `privileged_wrt_inode_uidgid()` and `capable_wrt_inode_uidgid()` combine namespace capability checks with idmapped mount UID/GID mapping checks.
- `ptracer_capable()` checks `tsk->ptracer_cred` for `CAP_SYS_PTRACE` in the requested namespace without auditing.

## Control flow

`capget` first validates the capability header. If userspace probes the version with a null data pointer and an invalid version, the syscall follows the historical ABI and returns success after writing the supported version. For real requests it rejects negative PIDs, reads either current credentials or another task via `find_task_by_vpid()` under RCU, then serializes capabilities into one or two `__user_cap_data_struct` records.

`capset` performs the reverse path. It rejects attempts to alter any task other than the caller, copies the ABI-sized data, builds bounded `kernel_cap_t` masks, then uses the credential transaction helpers. The LSM hook controls the actual policy, including restrictions that raised inheritable/permitted/effective bits remain valid. Successful changes are audited before `commit_creds()`.

The capability predicates are thin but security-sensitive wrappers around `security_capable()`. Current-task checks validate `cap` with `cap_valid()` and deliberately BUG on invalid capability constants. File and ptracer checks use stored credentials so authorization is tied to open-time or ptrace-time authority rather than the caller's current mutable credentials.

## State and persistence behavior

The durable kernel state touched here is task credential state. `capset` never mutates credentials in place; it builds a new `struct cred`, lets the security layer update it, then atomically installs it. `file_caps_enabled` is process-independent global boot state. Capability checks may set the transient `PF_SUPERPRIV` task flag to record that the task used privilege. The inode helper has no persistence; it only evaluates whether VFS UID/GID mappings make namespace privilege meaningful for the inode.

## Dependencies and integration points

The file depends on `linux/capability.h`, `linux/security.h`, `linux/audit.h`, user access helpers, PID namespaces, user namespaces, and credential helpers. LSM integration is through `security_capget()`, `security_capset()`, and `security_capable()`. Audit integration is through `audit_log_capset()`. Exported helpers are consumed broadly by VFS, process control, namespace, and driver code needing capability gates.

## Risks and edge cases

- Capability ABI compatibility is subtle: older callers receive truncated upper capability bits by design, which is fail-safe but can surprise capget/modify/capset flows.
- `capset` only allows current-task changes. Any code assuming historical group or arbitrary-pid behavior will receive `-EPERM`.
- Stored-credential checks in `file_ns_capable()` and `ptracer_capable()` are intentional. Replacing them with current credentials would reopen inherited-fd or tracer-credential races.
- `ns_capable_common()` BUGs on invalid capability numbers. Callers must validate dynamic capability values before passing them here.
- `capable_wrt_inode_uidgid()` requires both capability and mapped inode owner IDs. Namespace privilege alone is insufficient over unmapped idmapped mount owners.

## Test signals

Useful tests include syscall ABI probes for all three capability versions, invalid version writeback, null `dataptr` probing, negative PID rejection, non-current `capset` rejection, and upper-bit truncation for v1 callers. Security tests should exercise LSM denial paths, audit records on successful `capset`, `PF_SUPERPRIV` setting on successful `capable()`, idmapped mount owner mapping failures, and file-descriptor checks that continue to use opener credentials after caller credential changes.
