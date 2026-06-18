# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/set_layers_via_fds.c

## Purpose

`set_layers_via_fds.c` validates overlayfs new mount API support for configuring workdir, upperdir, lowerdir, datadir, and credential override behavior using file descriptors instead of path strings.

## Important APIs, Types, and Functions

The fixture tracks a pidfd for child cleanup and creates mount directories. Tests use `sys_fsopen`, `sys_fsconfig` with `FSCONFIG_SET_FD`, `FSCONFIG_SET_STRING`, and `FSCONFIG_SET_FLAG`, `fsmount`, `move_mount`, `open_tree`, `openat`, user namespace helpers, pidfd helpers, libcap helpers, and `/proc/self/mountinfo` parsing.

## Control Flow, State, and Persistence

The basic test creates tmpfs directories for work, upper, four lowers, and three data dirs, opens fds for each, moves tmpfs to `/tmp`, configures overlay with `lowerdir+` and `datadir+`, enables metacopy, mounts it, and scans mountinfo for path rendering. The 500-layer tests add 500 lower fds and verify a 501st fails, both with normal and `O_PATH` fds. Credential tests toggle `override_creds` and `nooverride_creds` from child processes, validate an invalid user namespace cannot set override on a shared context, and verify dropping `CAP_MKNOD` before `override_creds` causes `mknodat` in the overlay to fail with `EPERM`. The detached mount fd test configures layers from cloned open_tree fds and checks mountinfo output.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are overlayfs fd-based fsconfig support, tmpfs, new mount API wrappers, user namespace and capability helpers, pidfds, and mountinfo formatting. It integrates with overlayfs layer parser, metacopy/datadir support, and credential stashing semantics. Risks include mountinfo string matching, hard-coded `/tmp`, high fd counts, child synchronization, and cleanup after namespace changes. Passing signals are expected failure for plain `lowerdir`, success for `lowerdir+`/`datadir+`, 500-layer limit enforcement, correct mountinfo entries, valid credential toggles, invalid namespace rejection, and `EPERM` for mknod under dropped creds.
