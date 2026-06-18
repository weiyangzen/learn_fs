# sources/distributed-fs/ceph-client/include/linux/sched/user.h

Purpose: declares per-UID resource accounting and lifetime management for `struct user_struct`.

Important APIs and types: `struct user_struct`, `uids_sysfs_init()`, `find_user()`, `root_user`, `INIT_USER`, `alloc_uid()`, `get_uid()`, and `free_uid()` are central. The structure tracks refcount, UID hash linkage, optional epoll watches, UNIX inflight files, pipe buffers, locked VM, watch count, and rate limiting.

Control flow: credential/user lookup code allocates or finds UID records, increments references when attached to credentials or resources, and frees when no longer used. Resource subsystems charge per-user counters through fields gated by config.

State and persistence: per-UID runtime accounting persists while references exist. It is not persistent across boot.

Dependencies and integration points: integrates credentials, sysfs UID exposure, epoll, UNIX sockets, pipes, perf/BPF/network/io_uring/VFIO/IOMMUFD locked memory, watch queues, and rate limiting.

Risks and test signals: risks include refcount leaks, per-user counter underflow, UID hash races, and config-dependent field users. Test UID creation/destruction, credential churn, epoll/pipe/UNIX socket limits, locked-memory accounting, and namespace/user stress.
