# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_synproxy.c

## Purpose

Integration test for XDP and TC SYN proxy sample behavior using namespaces, iptables/nft-like control commands, and TCP handshake observation. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`SYS()`/`SYS_OUT()` command helpers, `popen()`, `escape_str()`, `expect_str()`, veth/netns setup, `ethtool` checksum offload control, TCP sockets, and command output parsing.

## Control Flow

`test_synproxy()` creates a `synproxy` namespace and veth pair, disables checksum offload where needed, configures addresses and BPF SYN proxy path for XDP or TC mode, opens server/client sockets, reads control output, and compares expected strings. `test_xdp_synproxy()` runs XDP and likely TC variants through subtests.

## State and Persistence Behavior

Transient namespace, veth devices, sysctl/ethtool state inside the test topology, sockets, popen streams, and output buffers. Cleanup deletes the namespace.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires network namespaces, veth, TCP stack behavior, command-line networking tools, and SYN proxy BPF sample support.

## Risks and Edge Cases

String comparisons are exact after escaping, so command output changes are brittle. Checksum offload must be disabled because the XDP program sees pre-offload checksums.

## Test Signals

Expected command output strings, successful TCP connection/accept path, and no unexpected packet drops in XDP/TC SYN proxy modes.
