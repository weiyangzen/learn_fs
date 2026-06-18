<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_reroute.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_reroute.c

Purpose: tests LWT xmit BPF rerouting by setting skb marks and policy-routing packets to a tun device, including qdisc drop regression coverage.

Important APIs and functions: `setup()` creates a tun device, dummy `link_err`, loopback source address, LWT BPF route from `test_lwt_reroute.bpf.o`, fwmark rule, and table 100 default route. `test_lwt_reroute_normal_xmit()` pings an IP whose final octet matches the tun ifindex and expects an ICMP packet on the tun fd. `overflow_fq()` sends UDP packets with `SO_TXTIME`/`SCM_TXTIME` to overflow an `fq` qdisc. `test_lwt_reroute_qdisc_dropped()` installs the fq qdisc and asserts no crash while overflowing.

Control flow: subtests run in an isolated thread and namespace using `RUN_TEST`. The normal path verifies actual packet delivery; the qdisc path is a crash-regression test.

State and persistence: state includes one netns, tun fd, dummy device, policy rule, route table, qdisc, UDP socket, and timestamp control messages. It is deleted with namespace teardown.

Dependencies and integration: depends on `lwt_helpers.h`, `network_helpers.h`, `ip`, `tc`, ping, tun support, and `SO_TXTIME`.

Risks and test signals: successful tun capture and no kernel crash are signals. Risks are qdisc/txtime support differences, timing, and route loops if the BPF fixture mark logic regresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_reroute.c -->
