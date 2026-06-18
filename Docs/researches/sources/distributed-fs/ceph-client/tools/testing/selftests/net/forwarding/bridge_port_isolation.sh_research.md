# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_port_isolation.sh

## Purpose
`bridge_port_isolation.sh` verifies Linux bridge port isolation. Two bridge ports are configured as isolated and a third as non-isolated; the script checks unicast reachability and flooding rules.

## Important APIs, Functions, and Control Flow
`switch_create` creates `br0`, enslaves three switch ports, sets `$swp1` and `$swp2` to `type bridge_slave isolated on`, explicitly sets `$swp3` isolation off, and brings bridge and ports up. `ping_ipv4` and `ping_ipv6` expect traffic from host 1 to host 2 to fail because both ingress/egress ports are isolated, while traffic from non-isolated host 3 to host 2 must succeed. `flooding` uses `flood_test_do` to ensure unknown unicast from isolated host 1 is not flooded to isolated host 2, but unknown unicast from non-isolated host 3 is flooded.

## State, Dependencies, Integration Points, and Risks
State is per-port bridge isolation plus bridge FDB/flood behavior. The script depends on `CHECK_TC=yes`, `lib.sh`, ping helpers, and flooding helpers that use tc/mausezahn. The primary risk is false failure when the kernel or iproute2 lacks bridge slave isolation support; `check_err` on the setup commands catches this as a test failure rather than a skip.

## Test Signals
The pass criteria are explicit `check_fail` for disallowed pings, `check_err` for allowed pings, and flood helper results matching the isolated/non-isolated path expectations.
