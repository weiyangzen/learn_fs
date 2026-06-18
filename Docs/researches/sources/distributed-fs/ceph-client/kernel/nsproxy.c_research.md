<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nsproxy.c -->
# sources/distributed-fs/ceph-client/kernel/nsproxy.c

Purpose: Owns task namespace sets (`struct nsproxy`) and implements cloning, unsharing, switching, exiting, exec-time time namespace updates, credential namespace active-reference transitions, and the `setns(2)` syscall.

Important APIs/types/functions: `init_nsproxy`, `copy_namespaces()`, `unshare_nsproxy_namespaces()`, `switch_task_namespaces()`, `exit_nsproxy_namespaces()`, `switch_cred_namespaces()`, `get_cred_namespaces()`, `exit_cred_namespaces()`, `exec_task_namespaces()`, `setns`, and `nsproxy_cache_init()`. Internal helpers include `create_new_namespaces()`, `prepare_nsset()`, `validate_nsset()`, `commit_nsset()`, `check_setns_flags()`, and `put_nsset()`.

Control flow: clone fast-paths by taking an extra ref when no new non-user namespaces are requested and the time namespace is already committed. Otherwise it checks `CAP_SYS_ADMIN`, rejects incompatible `CLONE_NEWIPC|CLONE_SYSVSEM`, creates a new nsproxy by copying mount, UTS, IPC, PID-for-children, cgroup, net, and time namespaces, then activates it and attaches it to the task. Unshare converts `UNSHARE_EMPTY_MNTNS` to `CLONE_EMPTY_MNTNS` before creating a detached nsproxy. `setns(2)` accepts either proc namespace files or pidfds: proc namespace files validate one namespace, while pidfds snapshot the target task's namespace set under RCU/task lock and validate requested namespaces in user, mount, UTS, IPC, PID, cgroup, net, and time order before commit.

State and persistence: Namespace membership is in task `nsproxy` pointers and credential user namespace active references. `nsproxy_free()` releases each namespace reference and frees from `nsproxy_cachep`. `switch_task_namespaces()` activates the incoming set before swapping under `task_lock()` and drops the old set after unlock.

Dependencies/integration: Integrates with every namespace implementation (`copy_mnt_ns`, `copy_utsname`, `copy_ipcs`, `copy_pid_ns`, `copy_cgroup_ns`, `copy_net_ns`, `copy_time_ns`), credentials, fs root/pwd switching, IPC semaphore cleanup, perf namespace notifications, proc namespace files, pidfd lookup, ptrace access control, and the namespace active-reference helpers.

Risks: `setns()` correctness depends on validating all requested namespaces before the point of no return in `commit_nsset()`. Temporary `fs_struct` ownership differs for mount-only versus multi-namespace transitions. PID namespace installation is constrained by ancestry and active namespace semantics. Time namespaces require special exec/fork commit handling; missing it can leave `time_ns_for_children` inconsistent with `time_ns`.

Test signals: clone/unshare/setns combinations for every namespace flag, permission failures without `CAP_SYS_ADMIN`, pidfd setns with target exit races, mount namespace root/pwd updates, `CLONE_NEWIPC|CLONE_SYSVSEM` rejection, time namespace commit on fork/exec, credential active ref accounting, and nsproxy cache initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nsproxy.c -->
