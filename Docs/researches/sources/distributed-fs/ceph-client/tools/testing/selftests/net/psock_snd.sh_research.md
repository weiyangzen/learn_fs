<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_snd.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_snd.sh

## Purpose

`psock_snd.sh` is the shell driver for `psock_snd`. It runs a focused regression suite over packet socket transmit modes, MTU boundaries, truncation behavior, VLAN handling, virtio-net headers, checksum offload, qdisc bypass, and UDP GSO.

## Important APIs, Types, and Functions

The script computes constants for MTU, IPv4 header length, UDP header length, virtio-net header length, Ethernet header length, MSS, maximum MTU, and maximum MSS. It invokes `./in_netns.sh ./psock_snd` with option combinations such as `-d`, `-b`, `-q`, `-V`, `-v`, `-c`, `-C`, `-l`, `-t`, and `-g`. Expected failures are expressed with shell negation `(! command)`.

## Control Flow

With `set -e`, the script runs positive functional checks first, then negative checksum-offset, MTU, and truncation checks, then GSO boundary checks. Each case prints a short label before invocation. Because all runs are wrapped in `in_netns.sh`, namespace-local loopback modifications by `psock_snd` do not leak.

## State and Persistence Behavior

The script itself stores only readonly calculations. Each `in_netns.sh` invocation creates isolated runtime state for the C helper's loopback address, sysctl, and sockets.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include `in_netns.sh`, the compiled `psock_snd` binary, namespace privileges, AF_PACKET support, and shell support for `set -e` plus negated subshell tests. Integration is with the selftests/net Makefile that builds `psock_snd`. Risks include negative tests passing unexpectedly, GSO boundary changes, and the commented VLAN-MTU case documenting an unsupported ARPHRD_ETHER path. Signals are completion of every positive and expected-negative case and final `OK. All tests passed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_snd.sh -->
