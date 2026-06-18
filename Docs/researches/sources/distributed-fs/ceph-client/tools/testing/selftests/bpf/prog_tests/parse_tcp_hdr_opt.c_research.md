<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/parse_tcp_hdr_opt.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/parse_tcp_hdr_opt.c

Purpose: tests BPF parsing of TCP header options through the companion fixture, usually covering option iteration and malformed/edge option layouts.

Important APIs and functions: the harness loads `parse_tcp_hdr_opt`, prepares packet or socket traffic fixtures, runs BPF programs, and checks BSS/map results for parsed option values and errors.

Control flow: subtests trigger parsing on constructed or real TCP packets, compare expected option kinds/lengths/status, and destroy the skeleton.

State and persistence: packet buffers, sockets, and BPF result fields are transient.

Dependencies and integration: depends on TCP packet fixtures, network helpers, generated skeleton, and BPF TCP option parsing helpers.

Risks and test signals: exact parsed values and expected rejection of malformed options are signals. Risks include TCP option layout changes in fixtures and verifier/helper behavior changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/parse_tcp_hdr_opt.c -->
