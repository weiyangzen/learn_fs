<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.sh

## Purpose

`skf_net_off.sh` creates the isolated TAP environment for `skf_net_off` and runs the executable in three modes: no filter, filtered linear skb, and filtered NAPI-frags skb.

## Important APIs, Types, and Functions

It uses `mktemp -u` to name a namespace, `ip netns`, `ip tuntap`, `ip link`, IPv6 address assignment, `ethtool -K gro off`, `sysctl net.ipv4.ip_early_demux=0`, and `ip netns exec`.

## Control Flow

The script creates a namespace, registers cleanup on exit, brings loopback and `tap1` up, sets a fixed MAC address and IPv6 peer address, disables GRO and early demux, then runs `./skf_net_off -i tap1`, `./skf_net_off -i tap1 -f`, and `./skf_net_off -i tap1 -f -F`.

## State and Persistence Behavior

All devices and sysctl mutations are namespace-scoped. `cleanup` deletes the namespace at exit. No output artifacts are persisted.

## Dependencies and Integration Points

It depends on TUN/TAP, ethtool, IPv6, raw socket permissions, and the compiled `skf_net_off` binary. It integrates the C test with kselftest's isolated namespace pattern.

## Risks and Edge Cases

There is no explicit root check; failures surface from `ip`/`tuntap` commands. Cleanup assumes namespace creation succeeded. If `ethtool` is missing or the kernel lacks NAPI frags support, later program modes fail.

## Test Signals

Each mode should reach `OK` from the C helper. The most important signal is that the filtered fragmented mode succeeds, proving `SKF_NET_OFF` remains correct with non-linear skb layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.sh -->
