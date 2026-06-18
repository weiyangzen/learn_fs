<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/shm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/shm.h

Purpose: defines the System V shared memory userspace ABI: default limits, legacy and modern info structures, shmget/shmat flags, hugepage encoding, and shmctl commands.

Important APIs, types, and functions: constants define `SHMMIN`, `SHMMNI`, `SHMMAX`, `SHMALL`, and `SHMSEG`. Legacy `struct shmid_ds` and `struct shminfo` remain for compatibility while `asm/shmbuf.h` supplies 64-bit layouts. Flags include `SHM_R`, `SHM_W`, `SHM_HUGETLB`, `SHM_NORESERVE`, `SHM_RDONLY`, `SHM_RND`, `SHM_REMAP`, `SHM_EXEC`, hugepage-size encodings, and commands `SHM_LOCK`, `SHM_UNLOCK`, `SHM_STAT`, `SHM_INFO`, `SHM_STAT_ANY`. `struct shm_info` reports usage.

Control flow: userspace creates segments with shmget, attaches with shmat, controls/removes/locks/queries with shmctl, and detaches with shmdt. HugeTLB size bits refine `SHM_HUGETLB` allocations.

State and persistence behavior: shared-memory segments live in an IPC namespace until removed and detached. Attach counts, creator/last operator pids, timestamps, permissions, resident/swap usage, and hugepage backing are kernel state. Defaults are sysctl-adjustable.

Dependencies and integration points: depends on IPC, errno, and generic hugepage encoding headers plus architecture shmbuf layouts. It integrates with SysV IPC, hugetlbfs, namespaces, libc, and ipcs/ipcrm tools.

Risks and edge cases: `SHMMAX` and `SHMALL` are intentionally below `ULONG_MAX` to avoid userspace overflow patterns. Hugepage flags must not conflict with mode bits. Legacy structures have old time and size fields and need compat handling.

Test signals: shmget/shmat/shmctl/shmdt flows, hugepage-size selection, `SHM_NORESERVE`, lock/unlock permissions, namespace isolation, 32-bit compat structure tests, and boundary limit/sysctl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/shm.h -->
