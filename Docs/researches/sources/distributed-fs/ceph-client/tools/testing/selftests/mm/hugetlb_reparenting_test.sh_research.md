# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_reparenting_test.sh

## Purpose
`hugetlb_reparenting_test.sh` validates hugetlb cgroup accounting and reparenting behavior for cgroup v1 and optionally cgroup v2. It checks that charges remain visible on parent cgroups after child removal and disappear after deleting hugetlbfs files.

## Important APIs, types, and functions
The script defines `cleanup()`, `assert_with_retry()`, `assert_state()`, `setup()`, `get_machine_hugepage_size()`, and `write_hugetlbfs()`. It writes `/proc/sys/vm/nr_hugepages`, mounts cgroup and hugetlbfs filesystems when necessary, moves the current shell into test cgroups, and invokes `./write_to_hugetlbfs`.

## Control flow
After root check and environment detection, it saves the original hugepage count, identifies or mounts the cgroup root, and computes the machine hugepage size. It first tests charge/rmdir/uncharge on a temporary cgroup. For cgroup v1 it also tests parent plus child hugetlb usage, child removal reparenting, and uncharge on file deletion. Finally it tests child-only usage and reparenting in both cgroup modes.

## State and persistence behavior
The script mutates global hugepage pool size, cgroup hierarchy, cgroup membership, and `/mnt/huge` mount state. `cleanup()` removes files, unmounts hugetlbfs, removes cgroups, and restores the original `nr_hugepages`; a final block unmounts temporary cgroup roots.

## Dependencies and integration points
Requires root, cgroup hugetlb and memory controllers, mount permissions, hugetlbfs, `/proc/meminfo`, and the companion `write_to_hugetlbfs` binary. It reads either `usage_in_bytes` for v1 or `current` for v2.

## Risks and edge cases
The test is invasive and can disturb existing cgroup or hugepage configuration. Accounting updates are asynchronous enough to need retry/tolerance. Error cleanup is broad but relies on predictable paths such as `/mnt/huge`.

## Test signals
The script prints `ALL PASS` after every `assert_state` succeeds within tolerance and the original hugepage count is restored.
