# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_port_share.c

## Purpose
`tcp_port_share.c` tests TCP bind-bucket port-sharing behavior for IPv4 and IPv6. It verifies that a source port blocked by an explicit bind becomes reusable after close, and that an auto-bound connected socket can block reuse after `connect(AF_UNSPEC)` followed by explicit binding.

## Important APIs, Types, And Functions
The file uses the kselftest harness fixture API: `FIXTURE`, `FIXTURE_VARIANT`, `FIXTURE_SETUP`, `TEST_F`, and `TEST_HARNESS_MAIN`. Helpers include `disconnect()`, `getsockname_port()`, and `make_inet_addr()`. It uses `IP_BIND_ADDRESS_NO_PORT`, `SO_REUSEADDR`, `connect(AF_UNSPEC)`, loopback namespace setup, and `/proc/sys/net/ipv4/ip_local_port_range`.

## Control Flow
Fixture setup unshares a new network namespace, brings loopback up, adds IPv6 addresses, and constrains the ephemeral port range to one port. The first test connects from one source address, binds another socket to a different address on that same source port to block reuse, verifies a second connect fails with `EADDRNOTAVAIL`, closes the blocker, and verifies the second connect succeeds. The second test disconnects the first connected socket, rebinds it to a blocking address, triggers bind-bucket state update with another bind/close, and verifies a second source cannot reuse the port.

## State, Persistence, And Dependencies
State is contained in an unshared network namespace and includes loopback addresses, proc port-range settings, and sockets. The setup writes a namespace-local proc sysctl. It depends on kselftest harness support, `ip` command availability through `system()`, and IPv4/IPv6 loopback semantics.

## Integration Points
The test targets the kernel bind bucket and port-address sharing logic used by TCP ephemeral source port selection. It specifically covers `IP_BIND_ADDRESS_NO_PORT` and disconnect/rebind transitions.

## Risks
The fixture writes only the IPv4 local port range but tests IPv6 too, relying on shared port-range behavior. Failed assertions may leave sockets open until process exit. The use of `system("ip ...")` requires the `ip` tool and sufficient privileges.

## Test Signals
Passing signals are both fixture variants passing both tests, expected `EADDRNOTAVAIL` while blocked, successful reconnect after closing the blocker in the first case, and continued failure after disconnect/rebind in the second case.
