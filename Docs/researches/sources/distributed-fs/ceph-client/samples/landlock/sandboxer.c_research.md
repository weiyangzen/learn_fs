# sources/distributed-fs/ceph-client/samples/landlock/sandboxer.c

Purpose: user-space Landlock sandbox launcher that restricts filesystem, TCP bind/connect, abstract Unix socket, and signal access before executing a command.

Important APIs/functions: syscall wrappers for `landlock_create_ruleset`, `landlock_add_rule`, and `landlock_restrict_self`; `populate_ruleset_fs`, `populate_ruleset_net`, `check_ruleset_scope`, `prctl(PR_SET_NO_NEW_PRIVS)`, and `execvpe`.

Control flow: main checks ABI version, masks unsupported access rights for older Landlock ABIs up to version 9, reads environment variables (`LL_FS_RO`, `LL_FS_RW`, `LL_TCP_BIND`, `LL_TCP_CONNECT`, `LL_SCOPED`, `LL_FORCE_LOG`), creates a ruleset, adds path and port rules, sets no-new-privs, restricts self, closes the ruleset, and executes the target command.

State and persistence: environment variables are consumed/unset before exec; ruleset applies to the process and descendants. No files are persisted.

Dependencies and integration: Landlock LSM enabled in the kernel, UAPI headers, normal Unix path and port semantics.

Risks: missing mandatory filesystem env vars aborts. If execute/interpreter/library paths are not allowed, `execvpe` fails. ABI downgrade behavior intentionally removes unsupported rights, which can be more restrictive for older kernels.

Test signals: run with read/write path env vars and a shell command, verify allowed paths work and denied paths fail; test optional TCP and scoped restrictions on kernels supporting those ABIs.
