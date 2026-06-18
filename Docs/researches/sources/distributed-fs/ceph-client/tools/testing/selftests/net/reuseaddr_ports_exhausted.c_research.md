<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseaddr_ports_exhausted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseaddr_ports_exhausted.c

## Purpose

`reuseaddr_ports_exhausted.c` validates TCP ephemeral-port reuse rules when the available local port range is exhausted. It checks which combinations of `SO_REUSEADDR`, `SO_REUSEPORT`, and effective UID may bind the only ephemeral port for future `connect()` use.

## Important APIs, Types, and Functions

The file uses `kselftest_harness.h`. `struct reuse_opts` holds two sockets' reuseaddr/reuseport settings. `unreusable_opts` encodes 12 combinations expected to reject the second bind; `reusable_opts` encodes four combinations where the first socket has reuseaddr and the second may be allowed depending on reuseport and euid. `bind_port` creates an AF_INET TCP socket, sets both socket options, and binds `127.0.0.1:0`. Tests are `reuseaddr_ports_exhausted_unreusable`, `reuseaddr_ports_exhausted_reusable_same_euid`, and `reuseaddr_ports_exhausted_reusable_different_euid`.

## Control Flow

Each test iterates option combinations, opens two sockets, and asserts whether the second bind should fail or succeed. The different-euid test temporarily switches to euid 10 and 20 around bind attempts, then returns to root. If both sockets bind, it verifies that listening on both is not allowed because only one UID can reserve the port for TCP_LISTEN.

## State and Persistence Behavior

State is transient socket FDs and temporary euid changes. The companion shell script constrains `ip_local_port_range` to a single port and enables `ip_autobind_reuse`, making port exhaustion deterministic. FDs are closed after each combination.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include root for `seteuid` and namespace sysctl setup, TCP autobind behavior, and the shell wrapper's single-port namespace. Integration points are inet ephemeral port selection, bind conflict checks, reuseport same-euid policy, and listen-time reservation. Risks include running without the wrapper, euid values unavailable under some security policies, and exact reuse semantics changing. Signals are kselftest assertions for every matrix row and no harness failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseaddr_ports_exhausted.c -->
