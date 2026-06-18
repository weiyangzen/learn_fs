<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_syscalls.c -->
# sources/distributed-fs/ceph-client/security/lsm_syscalls.c

## Purpose

`lsm_syscalls.c` implements userspace syscalls for the Linux Security Module API: setting and getting current task security attributes and listing active LSM module IDs.

## Important APIs, Types, and Functions

- `lsm_name_to_attr()` maps textual attribute names to `LSM_ATTR_*` identifiers.
- `SYSCALL_DEFINE4(lsm_set_self_attr)` delegates setting an attribute to `security_setselfattr()`.
- `SYSCALL_DEFINE4(lsm_get_self_attr)` delegates querying attributes to `security_getselfattr()`.
- `SYSCALL_DEFINE3(lsm_list_modules)` copies the active LSM id list to userspace.

## Control Flow

Attribute set/get syscalls are thin wrappers; validation and module-specific behavior are owned by the security core and active LSMs. `lsm_list_modules()` rejects nonzero flags, reads the userspace buffer size, stores the required total byte size back through `size`, returns `-E2BIG` if the supplied buffer is too small, then writes each active LSM numeric id from `lsm_idlist[]` and returns the count.

## State and Persistence Behavior

The file does not mutate LSM framework state except through delegated set-self calls. It reads `lsm_active_cnt` and `lsm_idlist[]`, which are fixed after security initialization.

## Dependencies and Integration Points

It depends on syscall infrastructure, `security_setselfattr()`, `security_getselfattr()`, LSM UAPI structs and flags, and private `lsm.h` globals. It is the userspace ABI bridge for tools that need to inspect or set stacked LSM contexts.

## Risks and Edge Cases

The list syscall writes the required size before checking capacity, so userspace can use a probe-and-retry pattern. A null or invalid `size` pointer fails with `-EFAULT`. Attribute name mapping must stay synchronized with UAPI names exposed elsewhere. The syscall wrappers rely on lower layers for per-LSM authorization and context validation.

## Test Signals

Tests should cover all known name mappings, unknown names returning `LSM_ATTR_UNDEF`, list probe with zero-sized buffer returning `-E2BIG` and required size, successful list matching boot LSM order, invalid flags, bad user pointers, and set/get behavior for each active LSM that supports a given attribute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_syscalls.c -->
