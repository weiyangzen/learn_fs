<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdp_features.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdp_features.sh

## Purpose
This shell script exercises the `xdp_features` binary across a veth pair and network namespace for core XDP actions/features: PASS, DROP, ABORTED, TX, REDIRECT, and NDO_XMIT over IPv4-mapped and IPv6 targets.

## Important APIs, Types, And Functions
- Constants define namespace name and veth IPv4/IPv6 addresses.
- `setup()` creates a namespace, veth pair, addresses, enables links, sets GRO on, and disables TX checksumming.
- `cleanup()` deletes the veth root device, namespace, and any running `xdp_features` process.
- `wait_for_dut_server()` waits until `ss -tlp` sees `xdp_features`.
- `test_xdp_features()` starts a DUT server for each feature and runs the peer client in the namespace.

## Control Flow
The script uses `set -e`, installs cleanup traps, runs `setup`, then for each XDP feature starts `./xdp_features` on `v1` in the root namespace, waits for readiness, and invokes `ip netns exec $NS ./xdp_features -t ... v0` as the peer. Any failing client exits immediately. The final NDO_XMIT result is saved in `ret`, cleanup runs, and the script exits with that status.

## State And Persistence
External state includes a temporary netns, root `v1`, namespace `v0`, IP addresses, ethtool feature changes, and background `xdp_features` processes. Cleanup removes the namespace/device and kills matching processes by `pidof`.

## Dependencies And Integration Points
It depends on `ip`, `ethtool`, `ss`, network namespace support, veth support, the compiled `xdp_features` binary, and privileges for network setup and XDP attachment.

## Risks And Edge Cases
`pidof xdp_features` can kill unrelated instances. The readiness loop has no timeout and can hang if the server never listens. Trap signal `9` is ineffective because SIGKILL cannot be trapped. Device names `v1`/`v0` may collide. Cleanup after intermediate failures relies on traps.

## Test Signals
The script returns zero only when all feature subtests succeed. Any `xdp_features` client nonzero exit aborts. Successful cleanup and final `ret=0` indicate XDP feature support for the tested topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdp_features.sh -->
