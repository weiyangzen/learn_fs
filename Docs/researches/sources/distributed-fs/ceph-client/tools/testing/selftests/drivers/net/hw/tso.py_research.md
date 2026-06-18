
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/tso.py`

## Purpose
Runs a TSO/LSO validation suite for direct TCP and tunneled TCP traffic. It verifies that disabling segmentation features suppresses hardware GSO counts, enabling features increases hardware GSO counts, and enabling segmentation does not cause excessive retransmits.

## Important APIs, Types, And Functions
- `sock_wait_drain()` waits for the TCP send queue to drain via `TIOCOUTQ`.
- `tcp_sock_get_retrans()` extracts retransmission count from `TCP_INFO`.
- `run_one_stream()` sends 4 MiB over a TCP socket and compares queue GSO stats before/after.
- `build_tunnel()` creates matching VXLAN/GRE/IP6GRE devices locally and remotely.
- `query_nic_features()` caches hardware/wanted features, partial GSO capability, and qstat support.
- `test_builder()` creates concrete ksft cases for feature/IP/tunnel combinations.

## Control Flow
`main()` creates `NetDrvEpEnv`, queries NIC features and qstats, constructs cases for IPv4/IPv6 TCP, VXLAN, VXLAN checksum, GRE, and IP6GRE combinations, then runs generated tests. Each generated test disables the target feature and verifies low LSO counters, configures GSO partial/mangleid when relevant, enables the target feature, and verifies high LSO counters.

## State And Persistence
Mutates ethtool feature toggles, GSO partial toggles, tunnel links, and local/remote addresses. `defer(restore_wanted_features)` returns NIC features to the original wanted set, and tunnel links are deleted through deferred `ip link del`.

## Dependencies And Integration Points
Depends on `EthtoolFamily.features_get()`, `NetdevFamily.qstats_get()`, ethtool feature toggles, `socat` on remote, tunnel device support, and queue stats `tx-hw-gso-packets` or `tx-hw-gso-wire-packets`.

## Risks
Counters are best effort and system noise can create false negatives. The code tries to enable all hardware features to detect GSO partial behavior, which can fail or affect concurrent traffic. Debug kernels may require receive window clamping to keep traffic stable.

## Test Signals
Pass signals are low retransmits, low GSO stats with feature off, and sufficient super-packet or wire-packet GSO stats with feature on.
