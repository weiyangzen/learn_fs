# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/common.sh

## Purpose
`common.sh` is the shared OVPN selftest library. It provides KTAP-aware command wrappers, namespace and interface setup, peer/key registration, notification capture and comparison, and cleanup for all OVPN test variants.

## Important APIs and functions
- Environment knobs include `OVPN_UDP_PEERS_FILE`, `OVPN_TCP_PEERS_FILE`, `OVPN_CLI`, `OVPN_YNL`, `OVPN_ALG`, `OVPN_PROTO`, `OVPN_FLOAT`, `OVPN_SYMMETRIC_ID`, `OVPN_VERBOSE`, and derived `OVPN_ID_OFFSET`.
- `OVPN_JQ_FILTER` normalizes YNL JSON notifications by flattening arrays, dropping IPv6 remote notifications, deleting `ifindex`, sorting by peer id, and selecting each message.
- `ovpn_cmd_run`, `ovpn_cmd_ok`, `ovpn_cmd_mayfail`, and `ovpn_cmd_fail` standardize command execution and failure reporting.
- `ovpn_run_stage` and `ovpn_stage_err` connect test stages to `ktap_test_pass`/`ktap_test_fail` under `set -eE`.
- `ovpn_create_ns`, `ovpn_setup_ns`, and `ovpn_cleanup_peer_ns` manage per-peer network namespaces, veth topology, `tunN` OVPN interfaces, overlay IPs, MTU, and optional LAN-behind-peer routing.
- `ovpn_build_capture_filter` emits tcpdump filters that match OpenVPN DATA_V2 headers for UDP and TCP.
- `ovpn_setup_listener`, `ovpn_compare_ntfs`, and `ovpn_stop_listener` capture YNL peer multicast notifications and diff them against JSON fixtures.
- `ovpn_add_peer` registers UDP or TCP peers and installs keys, switching between asymmetric and symmetric peer IDs.
- `ovpn_cleanup` kills background `ovpn-cli` processes, listener PIDs, veth links, and OVPN namespaces.

## Control flow
Tests source this file, then call its functions from staged test bodies. At source time it computes `OVPN_NUM_PEERS` from the selected peer table unless already set. Setup generally creates namespaces, starts listeners, creates OVPN interfaces, registers peers and keys, then test-specific traffic/lifecycle stages run. Cleanup is driven by each test script's EXIT trap.

## State and persistence
Runtime state includes network namespaces `ovpn_peer*`, veth links, OVPN netdevices `tun*`, background `ovpn-cli` daemons that keep sockets alive, YNL listener PIDs, temporary JSON files, nftables state in some tests, and `OVPN_TMP_JSONS`/`OVPN_LISTENER_PIDS` associative arrays. The file intentionally removes this state during cleanup.

## Dependencies and integration points
It depends on Bash associative arrays, `iproute2`, `jq`, `diff`, `tcpdump`, `timeout`, `killall`, the built `ovpn-cli`, kselftest KTAP helpers, peer fixture files, `data64.key`, and the YNL CLI. It integrates with `ovpn-cli.c` commands such as `new_iface`, `new_multi_peer`, `new_peer`, `new_key`, `set_peer`, `del_peer`, and `listen/connect`.

## Risks and edge cases
Asynchronous YNL listener startup can stall, so `test.sh` serializes listener creation. JSON comparison intentionally ignores IPv6 remote notifications and `ifindex`; changes in notification schema or ordering require fixture updates. Cleanup uses `killall` by basename, which can affect other same-named helpers in the namespace context. TCP mode uses background listeners and fixed sleeps, making it timing sensitive.

## Test signals
A healthy common setup yields reachable tunnel IPs, tcpdump matches for DATA_V2 headers, successful key operations, and JSON diffs against `json/peer*.json` with no output differences.
