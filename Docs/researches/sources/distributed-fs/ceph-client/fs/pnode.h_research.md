# sources/distributed-fs/ceph-client/fs/pnode.h

Purpose: Declares mount propagation helpers and flag macros shared by mount namespace code and `pnode.c`.

Important APIs and types: Defines predicates and mutators for propagation flags, including `IS_MNT_SHARED()`, `IS_MNT_SLAVE()`, `IS_MNT_NEW()`, `CLEAR_MNT_SHARED()`, `IS_MNT_UNBINDABLE()`, `IS_MNT_MARKED()`, `SET_MNT_MARK()`, `CLEAR_MNT_MARK()`, and `IS_MNT_LOCKED()`. It defines copy/clone flags such as `CL_EXPIRE`, `CL_SLAVE`, `CL_COPY_UNBINDABLE`, `CL_MAKE_SHARED`, `CL_PRIVATE`, and `CL_COPY_MNT_NS_FILE`. Inline helpers `set_mnt_shared()` and `peers()` encapsulate shared group setup and peer-group equality.

Control flow: The header itself has no runtime flow beyond inline flag updates. It exposes the public propagation surface used by namespace operations: propagation-mode changes, mount-copy propagation, unmount propagation, busy/unlock checks, group ID release, mountpoint updates, copy-tree helpers, reachability, mount counting, and overmount prediction.

State and persistence: The macros directly mutate or inspect `struct mount` fields such as `mnt_t_flags`, `mnt_group_id`, `mnt_master`, and `mnt.mnt_flags`. These fields are transient kernel mount namespace state, protected by namespace/mount locks in callers.

Dependencies and integration points: Includes `linux/list.h` and local `mount.h`, so it is tightly coupled to the VFS mount implementation. Callers include mount namespace setup, bind/clone paths, mount propagation code, and unmount logic.

Risks: Because these are low-level macros, callers must hold the documented locks and avoid double-evaluating expressions with side effects. `peers()` requires a nonzero group ID, which prevents unrelated private mounts with ID zero from comparing as peers. Incorrect use of `CL_*` flags can silently change propagation behavior across namespaces.

Test signals: Compile coverage from namespace/mount code, mount propagation xfstests, shared/slave/private flag transitions, recursive bind tests with unbindable mounts, and lockdep coverage around `set_mnt_shared()` callers.
