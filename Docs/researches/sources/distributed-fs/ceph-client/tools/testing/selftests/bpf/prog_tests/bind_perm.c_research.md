# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bind_perm.c

Purpose: tests cgroup bind hooks enforcing privileged-port bind permissions for IPv4 and IPv6.

Important APIs/types/functions: `create_netns` calls `unshare(CLONE_NEWNET)`. `try_bind` creates a TCP socket for AF_INET or AF_INET6 and checks bind errno for a requested port. `test_bind_perm` loads `bind_perm.skel.h`, attaches cgroup bind programs, disables `CAP_NET_BIND_SERVICE`, and validates expected bind outcomes.

Control flow: create new network namespace, join cgroup `/bind_perm`, load skeleton, attach v4 and v6 bind programs to the cgroup, drop effective net-bind-service capability, then try port 110 expecting `EACCES` and port 111 expecting success for both families. Restore capability if it was previously present.

State and persistence behavior: the process enters a new netns via `unshare`; cgroup FD remains open until cleanup. Capability state is saved and restored. Skeleton links attach to the cgroup and are destroyed at cleanup.

Dependencies and integration points: cgroup test helper, capability helper, generated skeleton, socket bind hooks, and namespace privileges.

Risks: failing to restore capability could affect later tests in the same process. `unshare(CLONE_NEWNET)` changes process namespace state. Port policy is encoded in the paired BPF program; userspace checks only expected errno.

Test signals: cgroup join and attach success, capability disable/restore success, and exact bind errno for blocked/allowed ports.
