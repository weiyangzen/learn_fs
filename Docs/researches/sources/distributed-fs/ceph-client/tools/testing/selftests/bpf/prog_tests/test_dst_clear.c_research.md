<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_dst_clear.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_dst_clear.c

Purpose: validates that a TCX-attached BPF program can observe and clear skb destination cache state on loopback UDP traffic.

Important APIs/types/functions: `test_dst_clear__open_and_load()`, `bpf_program__attach_tcx()`, `make_sockaddr()`, `sendto()`, and BSS flags `had_dst` and `dst_cleared`. Constants define loopback IPv4 address `1.0.0.1` and UDP port `7777`.

Control flow: load the skeleton, add the IPv4 address to `lo`, attach `dst_clear` to TCX on loopback, build a sockaddr, send one UDP datagram, then assert that BPF saw an existing dst and cleared it.

State and persistence: mutates the loopback address in the current network namespace and leaves cleanup to the wider namespace harness if any. Skeleton link ownership is stored in `skel->links.dst_clear` and destroyed with the skeleton.

Dependencies and integration: depends on TCX support, `if_nametoindex("lo")`, iproute2 via `SYS`, UDP sockets, and generated `test_dst_clear.skel.h`. The function name `test_ns_dst_clear` implies it is intended to run in an isolated netns selftest variant.

Risks: failure before namespace cleanup can leave the loopback alias. TCX availability and route-cache behavior are kernel-version sensitive. Requires sufficient privilege to modify addresses and attach TCX.

Test signals: asserts skeleton load, address setup, TCX link creation, sockaddr construction, exact send length, and final BSS booleans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_dst_clear.c -->
