## sources/distributed-fs/ceph-client/security/selinux/include/objsec.h

### Purpose
`objsec.h` defines SELinux security-blob structures for kernel objects and inline accessors that locate SELinux data inside LSM-managed blobs. It is the shared data model used by `hooks.c` and related SELinux subsystems.

### Important APIs, types, and functions
Key structures include `cred_security_struct`, `task_security_struct`, `inode_security_struct`, `file_security_struct`, `backing_file_security_struct`, `superblock_security_struct`, `msg_security_struct`, `ipc_security_struct`, `netif_security_struct`, `netnode_security_struct`, `netport_security_struct`, `sk_security_struct`, `tun_security_struct`, `key_security_struct`, `ib_security_struct`, `pkey_security_struct`, `bpf_security_struct`, and `perf_event_security_struct`. Accessors include `selinux_cred`, `selinux_task`, `selinux_file`, `selinux_inode`, `selinux_superblock`, `selinux_sock`, `selinux_ib`, and BPF/perf/key helpers. `current_sid()` returns the current task's subjective SID.

### Control flow
Hook implementations obtain the relevant blob through these inline accessors, then read or write SIDs, classes, policy sequence numbers, and initialization flags. `task_avdcache_permnoaudit()` is a small inline optimization for permissive/neversaudited directory checks.

### State and persistence
The structures hold in-memory SELinux labels and metadata. They mirror, cache, or derive from persistent policy/xattr state but are not persistent themselves. Some fields are protected by object locks (`inode_security_struct.lock`, superblock mutex/spinlock) or RCU/LSM object lifetime rules.

### Dependencies and integration points
It depends on many kernel object definitions, `flask.h`, `avc.h`, and the externally defined `selinux_blob_sizes` from `hooks.c`. Every major SELinux subsystem relies on these structures for object labeling.

### Risks
Accessor offsets must match `selinux_blob_sizes`. Missing blob size updates for new structures can corrupt memory. Label initialization states (`INVALID`, `PENDING`, `INITIALIZED`) must be respected to avoid using stale or uninitialized SIDs.

### Test signals
Full LSM blob build tests, KASAN/lockdep runs, inode labeling tests, socket clone/free tests, BPF/perf/key object tests, and policy reload/revalidation tests are useful.
