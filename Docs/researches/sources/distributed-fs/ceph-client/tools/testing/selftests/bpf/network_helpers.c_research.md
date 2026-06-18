# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/network_helpers.c

Purpose: shared network helper implementation for BPF selftests. It provides socket server/client setup, namespace switching, TUN/TAP and ethtool helpers, data transfer helpers, TC attach helper, canned packet vectors, and optional libpcap-based traffic monitoring.

Important APIs/types/functions: socket helpers include `settimeo`, `start_server_addr`, `start_server_str`, `start_server`, `start_reuseport_server`, `client_socket`, `connect_to_addr`, `connect_to_addr_str`, `connect_to_fd_opts`, `connect_to_fd`, `connect_fd_to_fd`, and `fastopen_connect`. Namespace/helpers include `make_sockaddr`, `ping_command`, `append_tid`, `make_netns`, `remove_netns`, `open_netns`, `close_netns`, `open_tuntap`, `get_socket_local_port`, `get_hw_ring_size`, `set_hw_ring_size`, `send_recv_data`, and `tc_prog_attach`. Under `TRAFFIC_MONITOR`, `traffic_monitor_start`, `traffic_monitor_stop`, and packet pretty-printers capture and dump traffic.

Control flow: server creation makes a socket, applies timeouts and optional post-socket callbacks, binds, and listens for streams. Client helpers infer address/type/protocol and connect. Namespace helpers shell out for netns creation/deletion and use `setns` with an `nstoken` to restore the original namespace. `send_recv_data` starts a server thread that accepts and sends fixed byte counts while the client receives. `tc_prog_attach` creates a libbpf TC hook and attaches ingress and/or egress programs. Traffic monitor switches namespace if requested, configures a nonblocking immediate-mode pcap on `any`, starts a select loop on pcap and eventfd, dumps captured packets, and decodes IPv4/IPv6/TCP/UDP/ICMP summaries.

State and persistence behavior: global packet templates `pkt_v4` and `pkt_v6` are exported. Most helpers own only FDs returned to callers. `open_netns` allocates a token holding the original namespace FD until `close_netns`. Traffic monitor writes pcap files under `/tmp/tmon_pcap`, owns pcap/dumper/eventfd/thread state, and frees it on stop.

Dependencies and integration points: depends on sockets, netns mount paths, ioctl, fcntl, libbpf TC APIs, `test_progs.h` assertions, `bpf_util.h`, and optionally libpcap. Many prog tests in this subset use these helpers for loopback servers, netns setup, packet contexts, and TC attachment.

Risks: helpers mix assertion-based test failures and negative errno returns. Netns creation/removal shells out to `ip`, so tests depend on userspace tooling and privileges. `get_socket_local_port` returns network byte order port values. Traffic monitoring only parses Ethernet-compatible SLL2 captures and writes to `/tmp`, so permissions and cleanup matter. `start_server_addr` has a typo in one log string but not behavior.

Test signals: callers observe valid FDs, zero returns, `ASSERT_*` failures, or negative errnos. Traffic monitor provides diagnostic pcap/log output rather than primary pass/fail criteria.
