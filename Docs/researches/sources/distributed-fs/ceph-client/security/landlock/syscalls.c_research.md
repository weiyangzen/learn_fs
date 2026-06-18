<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/syscalls.c -->
# sources/distributed-fs/ceph-client/security/landlock/syscalls.c

## Purpose

`syscalls.c` implements Landlock's userspace ABI: creating ruleset file descriptors, adding filesystem and network rules, querying ABI version/errata, and enforcing a ruleset on the calling task. It is the boundary between untrusted userspace buffers and Landlock's internal ruleset/domain machinery.

## Important APIs, Types, and Functions

- `SYSCALL_DEFINE3(landlock_create_ruleset)` validates `landlock_ruleset_attr`, handles `LANDLOCK_CREATE_RULESET_VERSION` and `LANDLOCK_CREATE_RULESET_ERRATA`, creates a one-layer `landlock_ruleset`, and exposes it through an anonymous fd.
- `SYSCALL_DEFINE4(landlock_add_rule)` dispatches `LANDLOCK_RULE_PATH_BENEATH` and `LANDLOCK_RULE_NET_PORT` to rule import helpers.
- `SYSCALL_DEFINE2(landlock_restrict_self)` merges a ruleset into current credentials and optionally synchronizes sibling threads through `landlock_restrict_sibling_threads()`.
- `copy_min_struct_from_user()` wraps `copy_struct_from_user()` with minimum-size, page-size, and null checks for forward-compatible ABI structs.
- `get_ruleset_from_fd()` verifies Landlock anonymous fd identity and read/write mode, then returns a referenced ruleset.
- `get_path_from_fd()`, `add_rule_path_beneath()`, and `add_rule_net_port()` import user-supplied rule attributes.
- `ruleset_fops` gives ruleset fds dummy read/write methods so fd modes can gate later add/enforce operations.

## Control Flow

Every syscall first rejects use when `landlock_initialized` is false, returning `-EOPNOTSUPP` and warning once. Ruleset creation either returns ABI metadata for special flags or copies and validates `landlock_ruleset_attr`, ensuring fs/net/scope masks contain no unknown bits before calling `landlock_create_ruleset()`. Successful rulesets are installed as anonymous `O_RDWR | O_CLOEXEC` fds; fd creation failure drops the ruleset reference.

Rule addition obtains the ruleset with `FMODE_CAN_WRITE`, checks flags, then copies the exact rule structure for the selected type. Path rules reject empty access masks, accesses outside the ruleset mask, Landlock ruleset fds, internal/no-user/private filesystems, and then call `landlock_append_fs_rule()`. Network rules reject empty masks, masks outside the handled network mask, and ports above `U16_MAX`, then call `landlock_append_net_rule()`.

Restricting self requires either `no_new_privs` or `CAP_SYS_ADMIN` in the current user namespace. It validates flags, prepares new credentials, adjusts audit logging options, optionally merges a ruleset with the current domain, replaces the prepared credential domain, marks the new layer as exec-active for audit, optionally runs thread synchronization, and finally commits credentials.

## State and Persistence Behavior

Ruleset fds hold referenced `struct landlock_ruleset` objects in `file->private_data`; release drops the reference. Enforced policy persists in `struct cred` through `landlock_cred_security->domain` and audit logging fields. Restriction is monotonic because merging creates a new domain layered over the old one, and `landlock_merge_ruleset()` enforces the maximum layer limit. `landlock_abi_version` is a stable userspace contract constant, currently `9`.

## Dependencies and Integration Points

The file depends on Landlock internals from `cred.h`, `domain.h`, `fs.h`, `net.h`, `ruleset.h`, `setup.h`, and `tsync.h`; kernel helpers for anonymous fds, credentials, capabilities, path refs, and user copy; and UAPI definitions from `uapi/linux/landlock.h`. It integrates with audit behavior under `CONFIG_AUDIT` and with cross-thread propagation through `tsync.c`.

## Risks and Edge Cases

User-copy size handling is ABI-critical: too-small structs are `-EINVAL`, very large sizes are `-E2BIG`, and future fields must zero-fill safely. The `ruleset_fd == -1` logging-only path is intentionally narrow and must not accept unrelated flags. Path fd filtering prevents impossible or internal objects from becoming path-beneath anchors. Thread synchronization may abort credential changes after preparation; callers must not assume local `prepare_creds()` implies final enforcement.

## Test Signals

Useful tests include ABI version/errata queries, unknown flag and unknown mask rejection, short/oversized struct copies, path rule addition against regular directories versus internal filesystems, network port validation, empty-rule `-ENOMSG`, fd mode checks, layer-limit `-E2BIG`, no-new-privs/capability gating, audit logging flag behavior, and `LANDLOCK_RESTRICT_SELF_TSYNC` with concurrent sibling threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/syscalls.c -->
