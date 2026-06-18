# sources/distributed-fs/ceph-client/security/commoncap.c

Purpose: implements the common Linux capability LSM: namespace-aware capability checks, ptrace checks, capability set mutation, file capability xattr conversion, exec-time credential derivation, setuid/fsgid capability fixups, scheduler/nice/ioprio checks, prctl capability operations, low-mmap checks, and LSM registration.

Important APIs, types, and functions: major exports include `cap_capable()`, `cap_settime()`, `cap_ptrace_access_check()`, `cap_ptrace_traceme()`, `cap_capget()`, `cap_capset()`, `cap_inode_need_killpriv()`, `cap_inode_killpriv()`, `cap_inode_getsecurity()`, `cap_convert_nscap()`, `get_vfs_caps_from_disk()`, `cap_bprm_creds_from_file()`, `cap_inode_setxattr()`, `cap_inode_removexattr()`, `cap_task_fix_setuid()`, `cap_task_setscheduler()`, `cap_task_setioprio()`, `cap_task_setnice()`, `cap_task_prctl()`, `cap_vm_enough_memory()`, and `cap_mmap_addr()`. It registers `capability_hooks` with `DEFINE_LSM(capability)` at `LSM_ORDER_FIRST`.

Control flow: capability checks climb target user namespaces, accepting same-namespace effective caps or namespace owner privileges. File capability reads validate v1/v2/v3 xattr formats, map idmapped mounts and rootids, and convert v2/v3 data for callers. Exec handling clears/derives file capabilities, applies privileged-root compatibility, handles unsafe/no-new-privs downgrade, clears ambient caps on setid/fcap, computes permitted/effective sets, audits non-root effective gains, and sets secureexec. Prctl handling gates bounding set, securebits, keepcaps, and ambient operations.

State and persistence: mutates proposed or current credentials, file capability xattr values passed to VFS, task flags (`PF_SUPERPRIV`), and `bprm` secureexec/personality-clear fields. It can remove `security.capability` xattrs via killpriv.

Dependencies and integration: central LSM hooks, user namespaces, idmapped mounts, xattr/VFS, exec binprm, securebits, ptrace, audit, tracepoints, and memory management policy.

Risks and test signals: high-risk areas are user-namespace root mapping, idmapped mount conversion, ambient/permitted invariant preservation, setuid-root plus fcaps behavior, no-new-privs downgrade, and security xattr permission checks. KUnit coverage targets namespace-root helpers; broader tests should cover filecap xattr v2/v3 conversion, exec transitions, prctl securebits/ambient paths, ptrace, and low mmap.
