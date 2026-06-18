# sources/distributed-fs/ceph-client/samples/vfs/mountinfo.c

## Purpose
`mountinfo.c` demonstrates how pidfds, namespace file descriptors, `listmount()`, and `statmount()` can reproduce `/proc/self/mountinfo`-style output, optionally for another PID and recursively across child mount namespaces.

## APIs, Types, And Functions
Important wrappers are `statmount()` and `listmount()`, which build `struct mnt_id_req` and invoke raw syscalls. Formatting helpers are `show_mnt_attrs()`, `show_propagation()`, and `show_sb_flags()`. `dump_mountinfo()` prints one mount; `dump_mounts()` paginates mount IDs; `main()` parses `-e`, `-p`, and `-r` options and opens namespace fds.

## Control Flow
The program opens a pidfd for the selected PID, gets its mount namespace fd through `PIDFD_GET_MNT_NAMESPACE`, reads namespace info with `NS_MNT_GET_INFO`, and lists all mounts using repeated `listmount(LSMT_ROOT, ..., last_mnt_id)`. Each mount ID is passed to `statmount()` with a mask requesting basic mount/superblock fields and strings, then printed in mountinfo order. Recursive mode advances through mount namespaces with `NS_MNT_GET_NEXT`.

## State And Persistence
State is process-local: selected PID, namespace fd, current namespace ID, pagination cursor, and stack-allocated `statmount` buffers. It does not mutate mounts or persist data.

## Dependencies And Integration Points
It depends on `samples-vfs.h`, raw syscall numbers for `statmount`/`listmount`/`pidfd_open`, namespace ioctls, and recent kernel support. It integrates with `/proc`-like mount diagnostics without reading `/proc/self/mountinfo`.

## Risks And Test Signals
Risks include syscall availability, fixed 4096-byte `statmount` buffer overflow responses, and assuming returned string offsets are valid when mask bits are set. Test signals include output matching `/proc/<pid>/mountinfo`, extended `-e` IDs being present, recursive namespace traversal stopping cleanly at `ENOENT`, and errors on older kernels being reported through `perror()`.
