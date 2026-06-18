<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseaddr_conflict.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseaddr_conflict.c

## Purpose

`reuseaddr_conflict.c` is a regression test for IPv4/IPv6 bind-bucket interaction with `SO_REUSEADDR`. It checks that creating an IPv6 wildcard socket does not reset or hide the conflict state for an already listening IPv4 socket on the same port.

## Important APIs, Types, and Functions

`open_port(int ipv6, int any)` creates either an AF_INET or AF_INET6 TCP socket, sets `IPV6_V6ONLY` for IPv6, sets `SO_REUSEADDR`, binds to either a specific IPv4 loopback address or wildcard, and listens when binding a specific address. `main` uses fixed `PORT=9999` and ordered open attempts to validate failures and successes.

## Control Flow

The test first opens and listens on `127.0.0.1:9999`. It then verifies that binding IPv4 `INADDR_ANY:9999` with reuseaddr fails. It opens IPv6 `in6addr_any:9999` with v6-only and expects success. While that IPv6 socket exists, it again expects IPv4 wildcard binding to fail. After closing the IPv6 socket, it expects IPv4 wildcard binding to still fail because the original IPv4 listener remains.

## State and Persistence Behavior

State is limited to TCP sockets on port 9999 in the current namespace. FDs are closed on normal process exit; there is no namespace setup inside the program.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include IPv4/IPv6 TCP, `SO_REUSEADDR`, `IPV6_V6ONLY`, and a free port 9999 in the test namespace. Integration is with inet bind bucket conflict logic. Risks are port conflicts when not run isolated, exact historical regression assumptions, and IPv6 disabled environments. Signals are expected failures for IPv4 wildcard bind attempts, successful IPv6 v6-only wildcard bind, and final `Success`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseaddr_conflict.c -->
