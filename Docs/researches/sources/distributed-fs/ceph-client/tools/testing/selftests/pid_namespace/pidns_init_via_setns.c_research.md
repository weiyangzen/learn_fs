# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/pidns_init_via_setns.c

Purpose: tests creating a PID namespace via `unshare(CLONE_NEWPID)`, joining it through `setns()` on `pid_for_children`, and becoming init/PID 1 in the joined namespace. A second test validates `clone3()` `set_tid` across nested PID namespaces.

Important APIs/functions: uses pipe synchronization, `/proc/<pid>/ns/pid_for_children`, `setns()`, `fork()`, `sys_clone3()`, and `set_tid[] = {1, 1001}`. Helpers `pidns_init_via_setns_set_tid_*` parse `/proc/self/status` `NSpid:` to confirm assigned PIDs.

Control flow: first test optionally unshares a user namespace if unprivileged, parent creates new PID namespace, child joins it and forks grandchild, grandchild checks `getpid() == 1`. The set_tid test requires root, creates an outer PID namespace, wrapper creates a child, wrapper unshares user and PID namespaces, child joins wrapper's `pid_for_children`, clone3 creates grandchild with desired set_tid values, and grandchild verifies NSpid suffix.

State and persistence: creates nested namespaces and short-lived children only. Reads procfs status and namespace fds.

Dependencies/integration: requires PID/user namespace support, procfs, `clone3` set_tid support, and root for the set_tid case.

Risks: namespace policy restrictions can fail even when kernel config is enabled. The set_tid path relies on exact `NSpid:` formatting and available PID 1001 in the outer namespace.

Test signals: kselftest assertions; set_tid test skips when not root.
