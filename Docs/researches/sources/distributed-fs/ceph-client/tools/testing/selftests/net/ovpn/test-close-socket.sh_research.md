# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-close-socket.sh

## Purpose
`test-close-socket.sh` validates that OVPN peer state and data forwarding survive normal setup and then behave correctly when userspace socket-owning helper processes are closed during cleanup. It is shared by UDP mode and `test-close-socket-tcp.sh`.

## Important APIs and functions
- Sources `common.sh`, enabling namespace setup, peer registration, command wrappers, and cleanup.
- `ovpn_prepare_network` creates peer namespaces, creates OVPN interfaces, registers every peer, and sets keepalive intervals/timeouts on both server and peers.
- `ovpn_run_ping_traffic` sends high-count ping traffic from peer0 to every peer tunnel IP.
- `ovpn_run_iperf` starts an iperf3 server in peer0 and runs a zerocopy client from peer1.
- `ovpn_test_exit` cleans namespaces and removes the `ovpn` module, printing partial KTAP totals if the test exits early.

## Control flow
With `set -eE`, the script installs EXIT and ERR traps, prints a KTAP header with plan 3, performs cleanup, loads the `ovpn` module, and runs three stages: topology setup, ping traffic, and iperf throughput. On completion it marks `ovpn_test_finished=1` and calls `ktap_finished`.

## State and persistence
Runtime state is the common OVPN namespace topology plus background `ovpn-cli` helpers that own sockets. All state is intended to be removed in the EXIT trap by `ovpn_cleanup` and `modprobe -r ovpn`.

## Dependencies and integration points
It depends on `common.sh`, `ovpn-cli`, `ip`, `ping`, `iperf3`, the selected peer table, `data64.key`, and the `ovpn` kernel module. TCP mode is selected externally by `test-close-socket-tcp.sh` via `OVPN_PROTO=TCP`.

## Risks and edge cases
If iperf3 is absent or slow, the third stage fails. Background socket helpers must be killed reliably or the module removal can fail. The test uses high packet counts, so slow machines may expose timing sensitivity even though this script has no explicit slow-machine tuning.

## Test signals
Expected KTAP stages are `setup network topology`, `run ping traffic`, and `run iperf throughput`. Any command wrapper failure prints the command and return code before the ERR trap records the active stage as failed.
