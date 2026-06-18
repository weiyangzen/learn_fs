<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_incoming_cpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_incoming_cpu.c

## Purpose

`so_incoming_cpu.c` verifies that `SO_INCOMING_CPU` can steer `SO_REUSEPORT` TCP listeners according to the CPU that processes incoming SYN packets.

## Important APIs, Types, and Functions

The file uses `kselftest_harness.h` fixtures and variants. Key helpers are `write_sysctl`, `setup_netns`, `set_so_incoming_cpu`, `create_server`, `create_servers`, `create_clients`, and `verify_incoming_cpu`. It uses `unshare(CLONE_NEWNET)`, `sched_setaffinity`, `get_nprocs`, `setsockopt(SO_REUSEPORT/SO_INCOMING_CPU)`, `getsockopt(SO_INCOMING_CPU)`, `bind`, `listen`, `connect`, and `accept`.

## Control Flow

Fixture setup creates a new net namespace, brings loopback up, narrows local port range, disables `tcp_tw_reuse`, determines CPU/server counts, and initializes a loopback sockaddr. Four variants set `SO_INCOMING_CPU` before reuseport, before listen, after listen, or after all listeners are listening. Tests create one listener per CPU, pin the client process to each CPU in turn, open many connections, and verify each listener accepts only connections with matching incoming CPU.

## State and Persistence Behavior

State is mostly namespace-local sockets and sysctls. Global process CPU affinity is changed during client creation and not explicitly restored, but the test process exits afterward. Server fds are closed in teardown.

## Dependencies and Integration Points

It depends on at least two CPUs, loopback TCP, `ip` command availability for namespace setup, and kernel support for `SO_INCOMING_CPU` with reuseport selection. It integrates with the kernel's TCP accept queue, incoming CPU tagging, and reuseport listener selection.

## Risks and Edge Cases

CPU affinity calls can fail under restricted cpusets. The test scales listener count to online processors and client count to available ephemeral ports, so very large systems can be heavy. The extra no-CPU listener cases ensure unspecified CPU sockets do not steal traffic, but they also rely on nonblocking accept returning `-1`.

## Test Signals

Harness success across all variants and three tests indicates CPU-based listener selection works before and after listen setup. Failures usually show as failed accepts, wrong `SO_INCOMING_CPU` values, or client connection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_incoming_cpu.c -->
