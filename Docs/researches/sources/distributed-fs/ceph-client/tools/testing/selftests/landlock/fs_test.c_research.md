<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/fs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/fs_test.c

## Purpose

`fs_test.c` is the main filesystem regression suite for the Linux Landlock selftests. It builds temporary filesystem layouts, creates Landlock path-beneath rulesets, enforces them on forked test processes, and verifies the observable syscall results for file opens, creation, deletion, renames, links, exec, truncation, device ioctls, UNIX socket path resolution, mount topology changes, overlayfs, disconnected bind-mount paths, several filesystem types, and audit records.

The file is not production filesystem code; it is a behavior specification for Landlock's userspace ABI and kernel path-walk enforcement. Its strongest value is the breadth of edge cases: layered policies, denied-by-default `REFER`, path rules across mount boundaries, disconnected dentries, O_PATH/procfd behavior, coredump socket exceptions, and audit logging content.

## Important APIs, Types, and Functions

- Landlock syscalls and UAPI structs are exercised through `landlock_create_ruleset()`, `landlock_add_rule()`, `landlock_restrict_self()`, `struct landlock_ruleset_attr`, and `struct landlock_path_beneath_attr`.
- Filesystem access masks are normalized by local macros: `ACCESS_FILE`, `ACCESS_ALL`, `ACCESS_RO`, and `ACCESS_RW`. These combine `LANDLOCK_ACCESS_FS_*` bits including execute, read/write file, read dir, create/remove file types, `REFER`, `TRUNCATE`, `IOCTL_DEV`, and `RESOLVE_UNIX`.
- `struct mnt_opt` plus `mount_opt()`, `prepare_layout_opt()`, `prepare_layout()`, and `cleanup_layout()` create isolated tmpfs or variant mounts in a private mount namespace.
- Layout helpers `create_layout1()` and `remove_layout1()` construct the baseline tree with `s1`, `s2`, and `s3` branches, including a nested tmpfs mount at `dir_s3d2`.
- Rule helpers `add_path_beneath()`, `create_ruleset()`, and `enforce_fs()` hide the repetitive open-O_PATH, add-rule, no-new-privs, enforce, and close flow.
- Syscall wrappers and probes include `test_open_rel()`, `test_open()`, `test_rename()`, `test_exchange()`, `test_renameat()`, `test_exchangeat()`, `test_truncate()`, `test_creat()`, `test_ftruncate()`, `test_fs_ioc_getflags_ioctl()`, `test_fionread_ioctl()`, `ioctl_error()`, and compatibility wrappers for `renameat2()`, `open_tree()`, and `execveat()`.
- Execution helpers `copy_file()`, `test_execute()`, and `test_check_exec()` copy `./true`, execute it, and use `AT_EXECVE_CHECK` to verify Landlock's execute permission path without replacing the caller.
- UNIX socket helpers `set_up_named_unix_server()`, `test_connect_named_unix()`, and `test_sendto_named_unix()` validate `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` on pathname sockets.
- Audit helpers `matches_log_fs_extra()` and `matches_log_fs()` build regexes for `AUDIT_LANDLOCK_ACCESS` records and verify blockers, paths, inode/device fields, and ioctl command annotations.

## Control Flow

Most tests run inside kselftest fixtures. `layout0` creates only an isolated `TMP_DIR`; `layout1` adds a multi-branch hierarchy and a mounted subtree; specialized fixtures add bind mounts, disconnected paths, overlayfs, per-filesystem mounts, ioctl variants, ftruncate variants, scoped-domain variants, coredump setup, and audit setup. Setup typically disables capabilities, creates a private mount namespace, mounts tmpfs, creates files, then grants only temporary capabilities such as `CAP_SYS_ADMIN`, `CAP_MKNOD`, `CAP_SYS_CHROOT`, `CAP_AUDIT_CONTROL`, or `CAP_SETUID` around privileged setup operations.

Policy tests follow a consistent sequence: create one or more path rules, enforce a ruleset, execute a syscall, and assert the exact result. For read/write/open tests, expected signals are `0` or `EACCES`; for reparenting and cross-parent link/rename behavior, `EXDEV` is the key Landlock denial for `REFER` or access-widening failures; for topology mutations under filesystem restrictions, mount operations fail with `EPERM`; for invalid ABI use, tests expect `EINVAL`, `EBADF`, `EBADFD`, `ENOMSG`, `EPERM`, or `E2BIG` depending on the misuse.

The early tests validate ABI boundaries: bad ruleset fds, non-O_PATH anchors, ruleset fds used as path fds, unhandled or unknown access bits, empty masks, unknown ruleset access masks, unprivileged `restrict_self()` before `no_new_privs`, and layer limit exhaustion. The main `layout1` flow then verifies effective access, unhandled access semantics, same-layer rule OR behavior, multi-layer AND behavior, inheritance from parent directories, root and mount-point rules, pivot/chroot-relative paths, and mount topology restrictions.

The rename/link section is the densest control-flow area. It separates same-directory operations from cross-directory reparenting, checks precedence between `EACCES` and `EXDEV`, validates `REFER` denied-by-default semantics across ABI layers, and verifies that moving a file or directory cannot grant it a wider Landlock access set. It also covers `RENAME_EXCHANGE`, directory-vs-file replacement, mount-root walks via `open_tree()`, cross-mount behavior, and "sinkhole" moves where moving into a more restrictive place is allowed but moving back would widen access and is denied.

Later flows cover newer access rights and special objects: `TRUNCATE` with `truncate()`, `O_TRUNC`, `creat()`, and `ftruncate()`; `IOCTL_DEV` on character/block devices versus regular files, directories, FIFOs, and UNIX sockets; `RESOLVE_UNIX` across parent/child domain combinations; coredump delivery to an `@/path` UNIX socket; overlayfs lower/upper/merged object identity; multiple filesystem variants; and audit records for each blocked filesystem access.

## State and Persistence Behavior

The test state is deliberately ephemeral. Each fixture creates `TMP_DIR`, mounts a temporary filesystem, and tears it down from the parent process. `TEST_F_FORK` isolates most policy enforcement because Landlock restrictions are monotonic and cannot be removed once applied to a process. Nested calls to `enforce_fs()` intentionally persist as additional Landlock layers, so later expectations depend on cumulative AND semantics across layers while rules within one layer are ORed.

Landlock state persists in process credentials after `landlock_restrict_self()`. Several tests deliberately reopen or reuse file descriptors across enforcement boundaries to verify time-of-open semantics: `ftruncate()` permissions attach to opened file descriptions, procfd access to unlinked files remains governed by the original file, O_PATH descriptors continue to return `EBADF` for unsupported operations, and file descriptors sent over UNIX sockets preserve their Landlock-derived truncation behavior even when received by an unrestricted parent.

Mount and dentry state is also part of the test surface. The bind and disconnected-path fixtures keep O_PATH directory fds open, rename the original directories away, then verify that Landlock evaluates the relevant mount/source/destination ancestry rather than simply the current pathname. Overlayfs tests distinguish access to lower, upper, and merged views of apparently same-content files. Filesystem variant tests unmount a filesystem while a ruleset still references it, then mount a replacement to confirm rules do not accidentally authorize newly covered objects.

## Dependencies and Integration Points

The file depends on the kselftest harness macros from `common.h`, Landlock audit helpers from `audit.h`, and generated scoped-domain variants from `scoped_base_variants.h`. It uses Linux UAPI headers for Landlock, mount APIs, `renameat2`, `open_tree`, `execveat`, fs ioctls, fiemap, filesystem magic numbers, capabilities, sockets, procfs, sysfs, cgroup2, overlayfs, and memfd.

Kernel integration points under test include Landlock syscall validation in `security/landlock/syscalls.c`, filesystem access checks in the Landlock fs hooks, domain/layer merge behavior, mount topology mediation, audit emission, named UNIX socket resolution, and special-object bypasses for pipes, memfd, namespace files, coredump sockets, and unsupported/internal filesystems. Test execution also depends on external helper binaries such as `./true`, `bin_sandbox_and_launch`, and `bin_wait_pipe` defined by the selftest support code.

Runtime dependencies are significant: many tests need a private mount namespace, tmpfs, optional overlayfs, optional ramfs/cgroup2/proc/sysfs/hostfs support, `/dev/null` and `/dev/zero`, `/proc/self/fd`, writable `/proc/sys/kernel/core_pattern` for the coredump fixture, audit support, and capabilities made available to the test harness. The file includes skip logic for unsupported filesystems and current-working-directory filesystem magic checks.

## Risks and Edge Cases

The largest behavioral risk is error-code drift. Many assertions encode exact distinctions between Landlock denials and VFS errors: `EACCES` versus `EXDEV` for reparenting, `EBUSY` for renaming a mount root, `ENOENT` for disconnected `..`, `EBADF` for O_PATH `ioctl()`/`ftruncate()`, `EPERM` for topology changes, and `ENOMSG` for empty rules. Small kernel changes in path-walk order or error precedence can break tests even when the high-level operation remains denied.

Layering is another sensitive area. Tests assume same-layer path rules are unioned, enforced rulesets are ANDed with prior domains, unhandled rights remain unrestricted, and `LANDLOCK_ACCESS_FS_REFER` is denied by default when any layer omits handling it. The reparenting tests depend on precise domain access collection for source, destination, children, covered mounts, disconnected branches, and file-vs-directory-specific rights.

Mount state creates race and cleanup risks. The suite uses private namespaces and parent teardown, but tests that unmount or move mounts can leave paths absent or covered. The code therefore often relies on namespace lifetime and tolerant `remove_path()` cleanup. `umount_sandboxer` uses pipes to avoid a race between an executing binary and unmount. The coredump test can block if the kernel fails to connect to the socket, relying on the harness timeout.

Audit tests are fragile by design because they validate formatted records with regexes. They assume stable blocker names such as `fs.execute`, escaped absolute paths from `realpath()`, `dev` and `ino` fields, domain allocation records in selected cases, and ioctl command formatting. Filesystem paths with unexpected control characters, missing audit support, or altered audit wording would invalidate these signals.

## Test Signals

Key positive signals are successful compilation under the Landlock selftest harness and successful execution of the `fs_test` binary across all fixture variants. The most important coverage signals are: invalid UAPI calls return the documented errno; read/write/open and O_PATH behavior match handled and unhandled access masks; policy layers remain monotonic; mount and pivot operations are denied only when filesystem restrictions are present; relative paths, chroot, and pivoted roots do not bypass policy; exec and `AT_EXECVE_CHECK` share the same authorization result; and same-content paths through bind or overlay mounts are mediated according to object and mount ancestry.

For regression triage, failures in `rename_*`, `reparent_*`, `path_disconnected_*`, `layout4_disconnected_leafs`, and `layout5_disconnected_branch` point at path-walk, `REFER`, or access-widening logic. Failures in `truncate`, `ftruncate`, and `open_and_ftruncate_in_different_processes` point at opened-file permission caching. Failures in `blanket_permitted_ioctls` or ioctl fixture variants point at `IOCTL_DEV` command classification. Failures in scoped-domain or coredump tests point at `RESOLVE_UNIX` scope handling. Failures in `audit_layout1` point at audit blocker selection or record formatting rather than only access enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/fs_test.c -->
