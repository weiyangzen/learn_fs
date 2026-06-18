<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mnt_namespace.h -->
# sources/distributed-fs/ceph-client/include/linux/mnt_namespace.h

## Purpose
`mnt_namespace.h` declares the kernel-facing mount namespace lifecycle and `/proc` mount-view operations.

## Important APIs, Types, and Functions
It forward-declares `struct mnt_namespace`, `struct fs_struct`, `struct user_namespace`, and `struct ns_common`; exposes `init_mnt_ns`; declares `copy_mnt_ns()`, `put_mnt_ns()`, `from_mnt_ns()`, and the `proc_mounts_operations`, `proc_mountinfo_operations`, and `proc_mountstats_operations` file operations. `DEFINE_FREE(put_mnt_ns, ...)` provides cleanup-scope release for namespace pointers.

## Control Flow and State
Namespace creation/copy code calls `copy_mnt_ns()` with clone flags, a source namespace, target user namespace, and filesystem struct. Namespace users release references with `put_mnt_ns()` or the cleanup helper. `/proc` operations render namespace mount lists and statistics.

## State and Persistence Behavior
Mount namespace state is process namespace state, retained by reference counts and visible through procfs. It is not on-disk persistence, but it controls the mounted tree visible to processes.

## Dependencies and Integration Points
It integrates with namespace core (`ns_common`), VFS mount management, process `fs_struct`, user namespaces, cleanup helpers, and procfs.

## Risks
The main risk is lifetime: failing to drop namespace references leaks mount namespaces, while dropping error pointers or null pointers incorrectly is guarded by the cleanup macro. Copy semantics must respect user namespace and clone flag constraints.

## Test Signals
Signals include mount namespace clone/unshare tests, proc mountinfo/mountstats visibility, namespace teardown leak checks, and cleanup-helper compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mnt_namespace.h -->
