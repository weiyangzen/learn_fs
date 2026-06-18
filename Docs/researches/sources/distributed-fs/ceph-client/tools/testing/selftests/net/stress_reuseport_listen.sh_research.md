# sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.sh

Purpose: this shell wrapper prepares the namespace and resource limits for the `stress_reuseport_listen` binary. Its target workload is 300 VIPs with 80 reuseport sockets each, for 24,000 listening sockets.

Important APIs and functions: it sources `lib.sh`, uses `setup_ns` and `cleanup_ns`, changes `net.ipv6.ip_nonlocal_bind`, adjusts `ulimit -n`, and runs `ip netns exec $NS ./stress_reuseport_listen 300 80`. `setup` and `cleanup` are the only local functions.

Control flow: the script saves the current file descriptor limit, registers cleanup with EXIT, creates one namespace, enables IPv6 nonlocal bind inside it, raises the file descriptor limit to 24,100, and invokes the C helper. Cleanup removes the namespace and restores the saved limit.

State and persistence: transient shell state includes `NR_FILES`, `SAVED_NR_FILES`, and the namespace variable from `setup_ns`. Kernel state includes the namespace sysctl and sockets created by the child process. No persistent output is created beyond stdout/stderr.

Dependencies and integration points: depends on the compiled `stress_reuseport_listen` binary being in the current directory, root or sufficient privileges for namespace/sysctl operations, and `lib.sh`. It participates in kselftest by returning the helper's status unless setup or cleanup fails.

Risks: the script does not explicitly check that raising `ulimit -n` succeeded before running the helper. It assumes the current working directory inside kselftest contains the compiled binary. The namespace variable is unquoted in a few commands, relying on `setup_ns` to produce safe names.

Test signals: success is the helper's timing line and zero exit. Resource limit, namespace, sysctl, or helper failures cause nonzero exit and are visible in shell diagnostics.
