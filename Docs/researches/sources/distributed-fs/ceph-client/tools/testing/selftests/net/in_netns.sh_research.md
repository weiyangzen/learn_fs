# sources/distributed-fs/ceph-client/tools/testing/selftests/net/in_netns.sh

Purpose: Small helper wrapper that executes an arbitrary command in a temporary network namespace with loopback enabled. Other network selftests use it to isolate sysctl and socket state.

Important APIs and commands: Uses `mktemp -u` for a namespace suffix, `ip netns add`, `ip -netns ... link set lo up`, `ip netns exec`, a shell `trap`, and `ip netns del`.

Control flow: The script enables `set -e`, creates a unique namespace name, registers cleanup on exit, creates the namespace, brings loopback up, executes the command passed as arguments inside that namespace, and exits with the command's status.

State and persistence: The only state is the temporary netns. Cleanup deletes it on normal exit or failure. There is no file state.

Dependencies and integration: Depends on `iproute2` and privileges to create network namespaces. It is used by tests such as IPv6 flowlabel and per-socket local port range to avoid cross-test state contamination.

Risks: `mktemp -u` reserves no name, so namespace-name collision is theoretically possible. If cleanup is interrupted by severe process termination, a stale namespace can remain.

Test signals: A wrapped command should see isolated network sysctls and working loopback; the wrapper should propagate the wrapped command's exit code.
