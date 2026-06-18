
# sources/distributed-fs/ceph-client/include/linux/nsproxy.h

Purpose: defines `struct nsproxy`, the per-task bundle of namespace pointers shared by tasks that share all namespaces, plus APIs for copying, switching, unsharing, and exiting namespace sets.

Important APIs/types/functions: `struct nsproxy` holds refs to UTS, IPC, mount, PID-for-children, net, time, time-for-children, and cgroup namespaces. `struct nsset` carries a partial or complete install set plus flags, fs, and credentials. APIs include `copy_namespaces()`, `switch_cred_namespaces()`, `exit_nsproxy_namespaces()`, `get_cred_namespaces()`, `exit_cred_namespaces()`, `switch_task_namespaces()`, `exec_task_namespaces()`, `deactivate_nsproxy()`, `unshare_nsproxy_namespaces()`, and `nsproxy_cache_init()`. `get_nsproxy()` and `put_nsproxy()` manage the nsproxy refcount.

Control flow: fork/clone uses `copy_namespaces()` to share or duplicate namespace sets based on clone flags. unshare/setns paths build an `nsset` and install it into the current task. Exit paths drop task and credential namespace references. `put_nsproxy()` calls `deactivate_nsproxy()` when the last task reference disappears.

State and persistence: nsproxy state is task-lifetime in-memory state. The nsproxy refcount counts tasks sharing the bundle, while individual namespace lifetimes are tracked separately through namespace refs and active refs.

Dependencies and integration points: depends on refcounts, spinlocks, task locking rules, scheduler types, credentials, fs structs, and each namespace subsystem. It is the core bridge between process lifecycle, clone/unshare/setns/exec, and namespace reference management.

Risks and test signals: risks include changing another task's nsproxy without `task_lock`, confusing `pid_ns_for_children` with active PID namespace, credential namespace ref mismatches, and leaks during partial namespace install failures. Test signals include clone/unshare/setns regression tests, concurrent `/proc/<pid>/ns` access during exit, credential switch tests, and refcount debug coverage for shared nsproxy groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nsproxy.h -->
