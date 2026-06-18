# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test.sh

## Purpose
`test.sh` is the main OVPN data-channel accelerator integration test. It validates namespace topology setup, tunnel traffic, LAN-behind-peer routing, optional floating transport addresses, throughput, key rollover, peer/key queries, deletion during traffic, stale-key deletion, timeout behavior, and YNL notification output.

## Important APIs and functions
- `ovpn_prepare_network` creates all namespaces, starts notification listeners, configures OVPN interfaces and veth underlay links, registers peers, and sets keepalive values.
- `ovpn_run_basic_traffic` starts tcpdump filters for OpenVPN DATA_V2 headers and sends baseline plus large-payload pings to each peer.
- `ovpn_run_lan_traffic` validates the extra LAN address behind peer1.
- `ovpn_run_float_mode` changes peer underlay addresses and verifies tunnel reachability after peer float.
- `ovpn_run_iperf` checks throughput with iperf3.
- `ovpn_run_key_rollover` adds secondary keys and swaps them on peers.
- `ovpn_run_queries` and `ovpn_query_peer_missing` validate successful and failing peer queries.
- `ovpn_run_peer_cleanup`, `ovpn_run_traffic_delete_peer`, `ovpn_run_key_cleanup`, and `ovpn_run_timeouts` exercise lifecycle cleanup and timeout notifications.
- `ovpn_run_notifications` compares captured YNL output against `json/peer*.json` fixtures selected by mode.

## Control flow
The script sources `common.sh`, installs EXIT and ERR traps, chooses a KTAP plan of 12 or 13 depending on `OVPN_FLOAT`, cleans old state, loads `ovpn`, then runs each stage with `ovpn_run_stage`. Wrapper scripts change behavior by setting `OVPN_PROTO`, `OVPN_ALG`, `OVPN_FLOAT`, `OVPN_SYMMETRIC_ID`, or `MTU` before sourcing this file.

## State and persistence
Runtime state includes namespaces `ovpn_peer0..N`, veth underlay links, OVPN interfaces `tun0..N`, routes, addresses, background socket-owning `ovpn-cli` processes, tcpdump and iperf children, temporary YNL JSON captures, peer/key state in the kernel, and optional changed underlay addresses for float mode. The EXIT trap removes this state.

## Dependencies and integration points
It depends on `common.sh`, `ovpn-cli`, `ip`, `ping`, `tcpdump`, `timeout`, `iperf3`, `jq`, `diff`, peer tables, JSON fixtures, YNL CLI, `data64.key`, and the `ovpn` module. It is the target sourced by most thin OVPN wrapper scripts.

## Risks and edge cases
The test is timing sensitive around YNL listener startup, tcpdump readiness, TCP listener setup, timeout sleeps, and background traffic during deletion. It normalizes notifications but still requires exact peer IDs, event names, delete reasons, and float remote addresses. TCP mode treats one peer deletion as non-fatal because protocol behavior can differ.

## Test signals
Passing output is a full KTAP run with all planned stages passing. Strong signals include tcpdump seeing both expected DATA_V2 peer IDs, pings succeeding before and after key rollover/float, missing peer query failing as expected, stale key deletion succeeding, timeout-generated delete notifications, and all JSON fixture diffs passing.
