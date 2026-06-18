
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_flow_label.py`

## Purpose
Tests IPv6 Flow Label participation in RSS hashing and verifies that Flow Label configuration does not leak into IPv4 flow types.

## Important APIs, Types, And Functions
- `_check_system()` ensures Python exposes `SO_INCOMING_CPU`, at least two RX queues exist, RPS/RFS is not configured, and the remote has IPv6 auto flow labels enabled.
- `_ethtool_get_cfg()` parses `rx-flow-hash` flags including `IPv6 Flow Label` as `l`.
- `_traffic()` sends either repeated datagrams on one socket or multiple sockets and records incoming CPUs.
- `test_rss_flow_label()` enables/disables UDP6 flow-label hashing and checks CPU spread.
- `test_rss_flow_label_6only()` rejects Flow Label on IPv4 types and scans IPv4 configs.

## Control Flow
The main IPv6 test reads initial UDP6 hash fields, adds `l` if needed, sends one-socket traffic expecting one CPU, sends multi-socket traffic expecting multiple CPUs, then disables `l` and expects multi-socket traffic to collapse to one CPU. The 6-only test attempts invalid `tcp4` configuration and inspects several IPv4 flow types.

## State And Persistence
Mutates UDP6 RSS hash fields through `ethtool -N`; restoration to the initial config is deferred. It reads but does not change RPS/RFS or remote auto-flowlabel sysctl.

## Dependencies And Integration Points
Depends on `NetDrvEpEnv`, `socat` on the remote, Python 3.11 `SO_INCOMING_CPU`, ethtool flow-hash support, and default remote IPv6 `auto_flowlabels=1`.

## Risks
CPU-based validation assumes IRQ/RSS CPU mapping reflects RSS queues and that RPS/RFS is off. It is sensitive to low CPU counts or external RPS configuration.

## Test Signals
Pass signals are exactly one CPU for one-socket flow-label traffic, at least two CPUs for multiple auto-labeled sockets with flow-label hashing enabled, one CPU after removing `l`, and `Invalid argument` for IPv4 flow-label configuration.
