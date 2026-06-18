<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/unprivileged-remount-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/unprivileged-remount-test.c

## Purpose
Validates which mount flags unprivileged users can preserve or reject across nested user and mount namespaces. It ensures security-sensitive flags and atime policy changes behave correctly when remounting bind mounts without initial privileges.

## Important APIs, Types, and Functions
- Namespace/mapping helpers `create_and_enter_userns()`, `write_file()`, and `maybe_write_file()`.
- `read_mnt_flags()` converts `statvfs()` flags into mount flag bits and rejects unknown flags.
- `test_unpriv_remount()` is the core child-process scenario for mounting, entering a second user/mount namespace, remounting with valid flags, then verifying invalid flags fail.
- `test_unpriv_remount_simple()` and `test_unpriv_remount_atime()` specialize common cases.
- `test_priv_mount_unpriv_remount()` bind-mounts `/dev` and verifies remount preserves original flags.

## Control Flow
`main()` runs a sequence of cases for `MS_RDONLY`, `MS_NODEV`, `MS_NOSUID`, `MS_NOEXEC`, and multiple atime combinations. Each case forks so namespace and mount mutations are isolated. The child creates a privileged-in-namespace mount, enters another user/mount namespace, remounts `/tmp` as a bind mount with allowed flags, verifies an invalid remount is rejected, and exits. The final case ensures a privileged source mount's flags do not unexpectedly change after unprivileged bind remount.

## State and Persistence Behavior
State is isolated in child user/mount namespaces and on `/tmp` mounts. Parent process only observes child exit codes. No persistent repository or host filesystem files are intentionally changed.

## Dependencies and Integration Points
Requires user namespaces, mount namespaces, ramfs, devpts for one case, bind mounts, `statvfs`, and mount flag ABI definitions. Invoked by `run_unprivileged_remount.sh`.

## Risks and Edge Cases
Mount namespace/user namespace restrictions can cause hard failures. The test intentionally dies on unknown `statvfs` flags, so newer flags may require updates. It relies on `/tmp` being usable as a mount target in isolated namespaces.

## Test Signals
Success exits 0. Each failed scenario calls `die()` with a descriptive message; wrapper may skip if uid maps are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/unprivileged-remount-test.c -->
