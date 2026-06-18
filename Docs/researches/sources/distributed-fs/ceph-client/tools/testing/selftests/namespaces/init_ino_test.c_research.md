## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/init_ino_test.c

**Purpose:** Checks that init namespace procfs links expose the canonical inode constants from `linux/nsfs.h`.

**Important APIs and flow:** `struct ns_info` maps namespace names to `/proc/1/ns/*` paths and expected constants: IPC, UTS, USER, PID, CGROUP, TIME, NET, and MNT. `TEST(init_namespace_inodes)` iterates the table, `stat()`s each procfs namespace symlink target, skips `ENOENT`, and asserts `st_ino` equals the expected constant.

**State, dependencies, integration:** There is no owned state beyond the static table. It depends on procfs, PID 1 namespace links, and exported nsfs inode constants. It integrates as a compatibility check between kernel headers and runtime namespace inode assignment.

**Risks and test signals:** Containers can make `/proc/1/ns/*` refer to the container’s PID 1 rather than host init, so execution context matters. Missing namespace files are skipped. Passing signals that init namespace inode ABI constants are reflected in procfs.
