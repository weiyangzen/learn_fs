<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.c

## Purpose
This C utility file provides shared helpers for filesystem selftests that need user namespaces, id maps, capability dropping, mount namespace isolation, robust child waiting, simple proc/sysfs writes, and unique mount IDs. It is support code rather than a standalone test.

## Important APIs, Types, And Functions
Important local types are `enum idmap_type_t`, `struct id_map`, `struct list`, and `struct userns_hierarchy`. Public functions exported through `utils.h` are `get_userns_fd()`, `switch_ids()`, `setup_userns()`, `enter_userns()`, `caps_down()`, `cap_down()`, `wait_for_pid()`, `write_file()`, and `get_unique_mnt_id()`. Internal helpers include `do_clone()`, `write_id_mapping()`, `map_ids_from_idmap()`, `get_userns_fd_from_idmap()`, `create_userns_hierarchy()`, `read_nointr()`, and `write_nointr()`.

## Control Flow
Namespace helpers clone or unshare into new user/mount namespaces, write `/proc/<pid>/{u,g}id_map`, deny `/proc/<pid>/setgroups` when required, synchronize parent/child setup over a socketpair, and then expose `/proc/<pid>/ns/user` as an fd. `setup_userns()` creates a private mount tree after writing the current uid/gid as id 0; `enter_userns()` only creates a user namespace. Capability helpers fetch process caps, clear either all effective caps or one named cap, then install the modified set.

## State And Persistence
The file owns only transient heap, stack, child process, socketpair, and fd state. Persistent effects are process credentials/capabilities, namespace membership, `/proc` id-map writes, and mount propagation changes in the calling test process. `get_unique_mnt_id()` reads `statx()` metadata and does not mutate state.

## Dependencies And Integration Points
The code depends on Linux namespace and capability APIs, `/proc` id-map semantics, libcap, `clone()`, `setns()`, `setresuid()`, `setresgid()`, `mount()`, `statx()`, kselftest logging, and syscall compatibility definitions from `wrappers.h`.

## Risks
The user namespace code is ordering-sensitive: writing gid maps without denying setgroups can fail for unprivileged callers, and the shared `CLONE_VM|CLONE_FILES` hierarchy path requires careful socket/fd cleanup. `map_ids_from_idmap()` has a per-map 4 KiB buffer and returns `-E2BIG` if exceeded. Several functions return negative errno-like values while others return bool-style success, so callers must not mix conventions.

## Test Signals
Good signals are successful id-mapped namespace creation as root and non-root, correct skip/failure messages on blocked user namespaces, successful capability dropping, no leaked child processes, `setup_userns()` leaving mounts private, and nonzero `STATX_MNT_ID_UNIQUE` on kernels that support unique mount IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.c -->
