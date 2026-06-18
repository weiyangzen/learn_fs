<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdping.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdping.sh

## Purpose
`test_xdping.sh` sets up a root/netns veth topology and exercises the `xdping` tool in skb and native driver modes, with and without a server, and with default and explicit count options.

## Important APIs, Types, And Functions
- Constants define target namespace, target IP, and local IP.
- `setup()` creates namespace `xdp_ns0`, veth pair, moves `veth0` into the namespace, assigns IPv4 addresses, and brings interfaces up.
- `cleanup()` deletes namespace/device and terminates any background server.
- `test()` optionally starts `xdping` server in the namespace, runs the root client, stops the server, and prints PASS text.

## Control Flow
With `set -e`, the script installs EXIT cleanup, creates topology, loops through no-server and skb server modes for client `-S` runs with and without `-c 10`, then runs native mode `-N` server/client pairs with and without `-c 10`. All `xdping` commands target `10.1.1.100`; any failure aborts before the final success line.

## State And Persistence
The script creates transient namespace, veth devices, IP addresses, XDP programs attached by `xdping`, and optional background server process. Cleanup deletes topology and kills the server pid.

## Dependencies And Integration Points
It depends on `ip`, namespace/veth support, XDP skb/native support on veth, the `xdping` binary, and network privileges.

## Risks And Edge Cases
The server startup uses fixed `sleep 10`, making the test slow and timing-dependent. Interface and namespace names are fixed and can collide. Native driver mode may be unsupported depending on device/kernel behavior.

## Test Signals
Success prints per-case PASS messages and `OK. All tests passed`. Any failed `xdping` invocation exits nonzero due to `set -e`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdping.sh -->
