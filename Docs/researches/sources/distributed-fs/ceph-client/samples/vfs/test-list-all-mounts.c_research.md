# sources/distributed-fs/ceph-client/samples/vfs/test-list-all-mounts.c

## Purpose
`test-list-all-mounts.c` is a diagnostic sample that lists every mount in the current mount namespace and then walks subsequent mount namespaces using namespace ioctls.

## APIs, Types, And Functions
It wraps `statmount()` in `__statmount()` and `sys_statmount()`, with buffer growth on `EOVERFLOW`. `sys_listmount()` wraps `listmount()`. `main()` uses `sys_pidfd_open()`, `PIDFD_GET_MNT_NAMESPACE`, `NS_MNT_GET_INFO`, and `NS_MNT_GET_NEXT`.

## Control Flow
The program obtains a pidfd for itself, converts it to a mount namespace fd, fetches namespace metadata, then repeatedly calls `listmount()` in batches of ten IDs. For each ID it calls `sys_statmount()` with masks for superblock, mount basics, roots, points, options, filesystem type, namespace ID, and idmaps. When a namespace is exhausted it advances to the next namespace until `ENOENT`.

## State And Persistence
State is local to the process: list buffer, `last_mnt_id`, namespace fd, and dynamically allocated `statmount` buffers. It does not modify mounts or namespaces.

## Dependencies And Integration Points
It depends on `samples-vfs.h`, pidfd selftest helper headers, recent mount syscalls/ioctls, and idmap fields in `statmount`. It integrates with namespace enumeration from nsfs.

## Risks And Test Signals
Risks include older kernels returning `ENOSYS`/`EINVAL`, large outputs, and `statmount()` failures for individual mounts. Test signals include matching mount counts, clean namespace completion messages, idmap lines when masks are present, and graceful skip of mounts that fail `statmount()`.
