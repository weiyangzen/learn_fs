<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mptcp.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mptcp.c

Purpose: broad MPTCP/BPF integration test covering sockops storage, TCP-to-MPTCP conversion, subflow cgroup hooks, and sockmap behavior with fallback and native MPTCP sockets.

Important APIs and functions: `start_mptcp_server()` uses `IPPROTO_MPTCP`. `verify_tsk()` and `verify_msk()` read socket local storage and validate MPTCP token/first sock/congestion-control data. `test_base()` compares normal TCP and MPTCP sockops. `run_mptcpify()` verifies a BPF program converts a normal TCP connection to MPTCP. `endpoint_init()` creates veths and `ip mptcp endpoint` entries. `test_subflow()` attaches cgroup MPTCP subflow and getsockopt hooks. `test_mptcp_sockmap()` attaches sockmap injection and stream-verdict programs, then tests fallback redirect and rejection of true MPTCP sockets.

Control flow: top-level runs `base`, `mptcpify`, `subflow`, and `sockmap`. Each creates a cgroup and a fresh netns, loads the relevant skeleton, attaches cgroup/sockmap programs, runs socket traffic, validates storage or socket options, and frees netns/cgroup/skeleton resources.

State and persistence: external state includes netns `mptcp_ns`, cgroups, veth endpoints, MPTCP endpoint config, sockets, sockmap entries, and BSS status fields. All are cleaned via helper teardown and fd close.

Dependencies and integration: depends on MPTCP kernel support, `ip mptcp`, cgroup helpers, network helpers, and four skeletons: `mptcp_sock`, `mptcpify`, `mptcp_subflow`, and `mptcp_sockmap`.

Risks and test signals: valid MPTCP token/storage, no fallback flag, remote key received, subflow socket options, successful fallback sockmap redirect, and `-EOPNOTSUPP` for true MPTCP sockmap updates are signals. Risks are MPTCP feature availability, endpoint setup support, and timing while waiting for subflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mptcp.c -->
