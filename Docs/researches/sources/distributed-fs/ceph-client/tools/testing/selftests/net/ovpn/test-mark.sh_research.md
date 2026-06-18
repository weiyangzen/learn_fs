# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-mark.sh

## Purpose
`test-mark.sh` validates OVPN socket firewall mark propagation. It creates a multi-peer UDP topology with a server-side socket mark, installs an nftables output rule that drops packets with that mark, verifies traffic is dropped and counted, removes the rule, and verifies recovery.

## Important APIs and functions
- `MARK=1056` is passed to `ovpn-cli new_multi_peer` and matched by nftables `meta mark`.
- `ovpn_mark_prepare_network` creates namespaces/interfaces, creates the marked server multi-peer socket, installs server/client keys, registers peers, and sets keepalive values.
- `ovpn_mark_run_baseline_traffic` proves tunnel traffic works before filtering.
- `ovpn_mark_add_drop_rule` flushes nftables, creates an inet filter output chain, and installs a counter drop rule for `MARK`.
- `ovpn_mark_verify_drop_traffic` expects ping failures, parses transmitted packet counts, and verifies the nft counter equals the expected drop total.
- `ovpn_mark_remove_drop_rule` and `ovpn_mark_verify_traffic_recovery` clear filtering and ensure traffic resumes.

## Control flow
The script uses `set -eE`, sources `common.sh`, installs EXIT/ERR traps, declares a six-stage KTAP plan, cleans old state, loads `ovpn`, and runs the mark-specific stages in order.

## State and persistence
It creates OVPN namespaces/devices/peers plus an nftables ruleset inside `ovpn_peer0`. Cleanup removes OVPN state and unloads the module; `ovpn_mark_remove_drop_rule` flushes nftables before the recovery stage.

## Dependencies and integration points
It depends on `common.sh`, `ovpn-cli`, `nft`, `ping`, `ip`, the UDP peer table, `data64.key`, and `CONFIG_NF_TABLES*` support from the OVPN config. It specifically exercises the `mark` argument handled by `ovpn-cli` in `CMD_NEW_MULTI_PEER` and `SO_MARK` in `ovpn_socket`.

## Risks and edge cases
Counter parsing depends on nft output text. The expected drop counter is derived from ping's transmitted count, so unusual ping output can fail parsing. The script configures only peers 0 through 3 despite `OVPN_NUM_PEERS` potentially being larger, intentionally narrowing the mark scenario.

## Test signals
Pass signals are six KTAP stages: setup, baseline traffic, nft rule install, marked traffic drop/count, rule removal, and recovery traffic. A mismatch between expected and actual nft packet counters is the central failure signal.
