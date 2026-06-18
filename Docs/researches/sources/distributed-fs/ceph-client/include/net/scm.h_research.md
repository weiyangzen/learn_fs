# sources/distributed-fs/ceph-client/include/net/scm.h

## Purpose
This header defines socket control-message state used for passing credentials, file descriptors, and security labels through Unix-domain and other socket ancillary data paths.

## Important APIs, Types, And Functions
`SCM_MAX_FD` caps descriptor passing at 253. `struct scm_creds` carries pid/uid/gid; `struct scm_fp_list` owns passed file pointers plus Unix inflight graph metadata under `CONFIG_UNIX`; `struct scm_cookie` bundles credentials, file list, pid reference, and optional security ID. APIs include `scm_send()`, `__scm_send()`, `scm_recv()`, `scm_recv_unix()`, `scm_detach_fds()`, `scm_detach_fds_compat()`, `scm_fp_dup()`, and `scm_recv_one_fd()`. Inline helpers manage credential references and optional peer security.

## Control Flow
Send-side callers initialize a cookie through `scm_send()`, optionally force current process credentials, collect peer security, and parse ancillary data with `__scm_send()`. Receive-side paths detach file descriptors and credentials into user msghdr control buffers. Destroy paths release pid references and any passed file list.

## State And Persistence
SCM state is per-message and must be destroyed after use. File descriptor lists hold referenced `struct file` objects and `struct user_struct`; Unix inflight state tracks garbage-collection edges for descriptor cycles.

## Dependencies And Integration Points
It depends on credentials, file tables, pid references, LSM network hooks, compat control-message handling, and Unix socket internals. `receive_fd()` bridges kernel files to user fd tables.

## Risks And Test Signals
Risks include fd leaks, credential lifetime bugs, Unix inflight GC cycles, compat layout errors, and missing LSM secid propagation. Test signals are SCM_RIGHTS/SCM_CREDENTIALS send-receive tests, forced credentials, descriptor-limit tests, compat syscall tests, and Unix garbage collection stress.
