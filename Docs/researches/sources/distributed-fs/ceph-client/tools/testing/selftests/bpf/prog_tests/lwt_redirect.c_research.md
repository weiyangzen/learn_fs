<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_redirect.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_redirect.c

Purpose: tests LWT xmit BPF redirection to tun/tap/vlan devices, including normal ingress/egress delivery and regression cases where devices are down.

Important APIs and functions: `ping_dev()` encodes the target ifindex into destination IP. `new_packet_sock()` binds an AF_PACKET socket with `PACKET_IGNORE_OUTGOING`. `expect_icmp()` and `expect_icmp_nomac()` filter captured packets. `setup_redirect_target()` creates a tun/tap target, dummy route device, loopback source address, and two LWT BPF routes using `test_lwt_redirect.bpf.o`. `send_and_capture_test_packets()` checks egress via tun/tap fd and ingress via packet socket.

Control flow: a worker thread deletes/recreates `NETNS` for each subtest through `RUN_TEST()`. Normal MAC and no-MAC cases expect captured ICMP packets. Down-device and carrier-down VLAN cases only assert no kernel crash/panic while pings execute.

State and persistence: per-subtest netns, tun/tap fds, packet sockets, dummy/vlan devices, and routes are transient. Threading isolates namespace side effects from the main process.

Dependencies and integration: depends on `lwt_helpers.h`, `network_helpers.h`, tun/tap support, `ip`, ping, AF_PACKET, and BPF object sections for redirect variants.

Risks and test signals: packet capture on the target device is the positive signal; absence of kernel crash is the negative-regression signal. Risks include timing timeouts, busybox ping limitations, tun/tap permissions, and kernel instability in the tested paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_redirect.c -->
