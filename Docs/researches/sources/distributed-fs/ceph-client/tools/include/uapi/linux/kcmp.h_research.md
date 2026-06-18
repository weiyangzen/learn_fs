# sources/distributed-fs/ceph-client/tools/include/uapi/linux/kcmp.h

Purpose: defines comparison selector constants for the `kcmp(2)` syscall, which lets privileged userspace compare selected kernel resources between two processes.

Important APIs/types: `enum kcmp_type` values cover file table, VM, files, fs, sighand, IO context, System V semundo, individual file descriptors, epoll target-file checks, and named type maximum. `struct kcmp_epoll_slot` identifies an epoll fd, target fd, and target offset for `KCMP_EPOLL_TFD`.

Control flow, state, and persistence: userspace calls `kcmp(pid1, pid2, type, idx1, idx2)`. Kernel compares references or selected objects and returns ordering/equality information. No state is mutated or persisted by the ABI.

Dependencies and integration points: depends on `<linux/types.h>`. It integrates checkpoint/restore tooling, process inspection, and debugging utilities that need to infer resource sharing.

Risks and test signals: risks include permission failures, racing process exit or fd reuse, misinterpreting ordering as more than equality, and using wrong indices for epoll slots. Tests should compare cloned processes with shared/unshared VM/files/fs/sighand resources, compare duplicated fds, verify epoll target checks, and cover permission-denied and stale-pid cases.
