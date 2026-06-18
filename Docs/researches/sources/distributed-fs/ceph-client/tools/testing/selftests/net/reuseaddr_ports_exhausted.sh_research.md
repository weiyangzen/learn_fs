<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseaddr_ports_exhausted.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseaddr_ports_exhausted.sh

## Purpose

This shell wrapper creates the deterministic namespace environment required by `reuseaddr_ports_exhausted`. It restricts the IPv4 ephemeral port range to one port and enables autobind reuse so the C harness exercises exhaustion paths.

## Important APIs, Types, and Functions

The script defines `NETNS`, `setup`, `cleanup`, and `do_test`. `setup` creates the namespace, brings loopback up, writes `net.ipv4.ip_local_port_range="32768 32768"`, and writes `net.ipv4.ip_autobind_reuse=1`. `do_test` runs `./reuseaddr_ports_exhausted` inside the namespace.

## Control Flow

With `set -e`, the script installs cleanup trap, runs setup, invokes the C test, and prints `tests done` only if it succeeds. Namespace deletion runs at exit.

## State and Persistence Behavior

The only persistent-while-running state is a temporary named netns and namespace-local sysctls. Cleanup deletes the namespace.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include root/CAP_NET_ADMIN, `ip netns`, sysctl write access, and the compiled C binary. Integration is with TCP ephemeral-port sysctls and the C matrix. Risks include `mktemp -u` name collision, missing `ip_autobind_reuse` on older kernels, and cleanup failure if namespace deletion races. Signals are successful C harness completion and `tests done`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseaddr_ports_exhausted.sh -->
