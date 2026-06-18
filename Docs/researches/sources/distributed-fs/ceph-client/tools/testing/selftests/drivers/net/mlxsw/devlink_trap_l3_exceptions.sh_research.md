# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_l3_exceptions.sh

## Purpose

mlxsw devlink exception-trap coverage for packets that should be trapped to CPU instead of silently dropped.

## Important APIs, Types, and Functions

Defines routed H1/RP1/RP2/H2 topology with clsact on H1 and RP2, requires multicast routing daemons (`$MCD`, `$MC_CLI`), and tests `mtu_value_is_too_small`, `ttl_value_is_too_small`, multicast reverse-path forwarding, reject routes, unresolved neighbor variants, and IPv4/IPv6 LPM misses. It uses `devlink_trap_exception_test`, trap action inspection, ICMP TC filters, route manipulation, and multicast daemon control.

## Control Flow

Setup starts the multicast daemon, prepares VRFs/forwarding, and configures router addresses. Tests verify normal ping, confirm the expected default trap action, create a forwarding exception such as DF+oversized packet, low TTL, mroute RPF miss, reject route, missing neighbor, or route-table miss, then assert the devlink exception and any expected ICMP reply/counter. Cleanup stops traffic, removes routes/filters/VRFs, restores forwarding, and kills the daemon.

## State and Persistence Behavior

State includes multicast routing daemon process state, routes and reject routes, MTU changes, neighbor entries, temporary VRFs without routes, TC filters, and devlink trap counters/actions. All state is expected to be local to the test run.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It additionally requires multicast routing helper binaries exposed through `$MCD` and `$MC_CLI`.

## Risks and Edge Cases

Exception tests depend heavily on CPU trap action defaults, ICMP generation, and timing of multicast daemon programming. Missing daemon support or changed ICMP behavior can produce failures unrelated to mlxsw. Route and neighbor cleanup must be exact to avoid influencing later tests.

## Test Signals

Signals include trap action checks, `devlink_trap_exception_test`, ICMP ingress TC hits for MTU/TTL cases, and per-test `log_test` outcomes.
