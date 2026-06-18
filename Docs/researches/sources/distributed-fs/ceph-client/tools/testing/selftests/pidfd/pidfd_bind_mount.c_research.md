# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_bind_mount.c

Purpose: validates pidfds as mountable pidfs objects: cloning a detached mount from a pidfd, attaching it to the filesystem, and reopening/verifying identity.

Important APIs/types/functions: fixture stores a temp path, temp fd, self pidfd, stat data, generation numbers from `FS_IOC_GETVERSION`, and unmount state. Tests use `sys_open_tree()`, `move_mount()`, procfs fd reopening, `fstat()`, and `ioctl(FS_IOC_GETVERSION)`.

Control flow: setup unshares mount namespace, creates a temp file path, opens a self pidfd, records stat and generation. `bind_mount` clones an open tree from the pidfd with `AT_EMPTY_PATH` and attaches it over the temp file. `reopen` opens `/proc/self/fd/<pidfd>` and compares identity. `bind_mount_reopen` mounts then opens the attached path and compares identity/generation. Teardown closes, unmounts if needed, and unlinks.

State and persistence: creates and removes a temp file, unshares mount namespace, may mount pidfs over that temp file, and opens pidfds. Mount effects are namespace-scoped.

Dependencies/integration: requires mount namespace permission, pidfs mount support, `open_tree`/`move_mount` wrappers from `../filesystems/wrappers.h`, procfs, and FS generation ioctl support.

Risks: restricted environments may block unshare or mount syscalls. Teardown asserts unmount/unlink success, so partial setup failures can cascade if state tracking is wrong.

Test signals: kselftest harness assertions; identity mismatch or mount/reopen failure fails the test.
