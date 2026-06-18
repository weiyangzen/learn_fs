<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_skb_pkt_end.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_skb_pkt_end.c

Purpose: verifies skb packet-end handling when `bpf_prog_test_run_opts()` is run with checksum-complete skb test flags.

Important APIs/types/functions: generated `skb_pkt_end` skeleton, `sanity_run()`, `pkt_v4` from network helpers, `BPF_F_TEST_SKB_CHECKSUM_COMPLETE`, and expected retval `123`.

Control flow: load and attach skeleton, test-run `main_prog` with IPv4 packet bytes and checksum-complete flag, assert syscall success and retval.

State and persistence: no persistent state; skeleton link is destroyed at cleanup.

Dependencies and integration: depends on network helper packet fixture, generated skeleton, and kernel support for skb checksum-complete test-run mode. Integrated as `test_test_skb_pkt_end`.

Risks: primarily sensitive to verifier/JIT packet-boundary logic and test-run flag semantics. Attach is performed even though the substantive signal comes from direct test-run.

Test signals: skeleton load/attach and exact test-run retval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_skb_pkt_end.c -->
