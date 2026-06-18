# subset-b-006322 Research

Grouped code research for selected Linux sample BPF, cgroup, check-exec, and configfs files under `sources/distributed-fs/ceph-client/samples`. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_user.c

## Purpose
`task_fd_query_user.c` is a userspace validation harness for `bpf_task_fd_query()`. It loads the matching kernel BPF object, attaches kprobe/kretprobe and uprobe/uretprobe programs through both tracefs/debugfs and perf-event PMU paths, then verifies that the kernel reports the expected probe target name, fd type, offset, address, and program id.

## Important APIs, Types, And Functions
Important routines are `bpf_find_probe_type()`, `bpf_get_retprobe_bit()`, `test_debug_fs_kprobe()`, `test_nondebug_fs_kuprobe_common()`, `test_nondebug_fs_probe()`, `test_debug_fs_uprobe()`, and `main()`. It uses `bpf_object__open_file()`, `bpf_object__load()`, `bpf_program__attach()`, `bpf_program__attach_perf_event()`, `bpf_task_fd_query()`, `sys_perf_event_open()`, `load_kallsyms()`, and `ksym_get_addr()`.

## Control Flow
Startup loads kallsyms, opens `<argv[0]>_kern.o`, loads all BPF programs, and attaches them as libbpf links. The debugfs kprobe checks query the fd returned by an attached `bpf_link`. Non-debugfs tests discover PMU type and retprobe config bits from sysfs, create perf events by symbol, offset, or absolute address, attach a program to each fd, and call `bpf_task_fd_query()`. Debugfs uprobe testing writes a temporary event to `uprobe_events`, opens the generated tracepoint id as a perf event, attaches BPF, and validates query metadata.

## State And Persistence
Persistent process state is limited to two arrays of `struct bpf_program *` and `struct bpf_link *`. Kernel-visible temporary state includes perf-event fds, tracefs probe definitions, and libbpf links; all links are destroyed on cleanup. No long-lived BPF map data is managed here.

## Dependencies And Integration Points
The harness depends on libbpf, `bpf_util.h`, `perf-sys.h`, `trace_helpers.h`, `/proc/kallsyms`, `/sys/bus/event_source/devices/{kprobe,uprobe}`, `/sys/kernel/tracing`, and kernel support for BPF task fd querying. It integrates with the companion task-fd-query kernel sample object and the perf event subsystem.

## Risks And Edge Cases
The uprobe file-offset calculation relies on `main - __executable_start`, which the comments acknowledge is linker/compiler dependent. Tracefs permissions, disabled kallsyms, unavailable PMUs, architecture-specific offsets, stale probe aliases, and short query buffers can all cause false failures. Error exits through macros can bypass some cleanup in inner helpers.

## Test Signals
Success is all `CHECK_AND_RET()` calls returning zero and process exit status zero. Useful signals include correct fd type for kprobe/kretprobe/uprobe/uretprobe, zero buffer length behavior for address-only probes, x86 offset coverage, tracefs event cleanup, and running under kernels with and without debugfs-style probe creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect.sh

## Purpose
`tc_l2_redirect.sh` is an integration test for tc BPF L2-to-IP-tunnel redirect programs. It builds a veth and namespace topology, attaches sections from `tc_l2_redirect_kern.o`, programs the pinned tunnel-interface map with `tc_l2_redirect_user`, and verifies IPv4 and IPv6 reachability through IPIP and IP6 tunnel devices.

## Important APIs, Types, And Functions
Key shell functions are `config_common()`, `cleanup()`, `l2_to_ipip()`, and `l2_to_ip6tnl()`. It drives `ip netns`, `ip link`, `ip route`, `tc qdisc/filter`, `sysctl`, `ping`, and the user helper `./tc_l2_redirect`.

## Control Flow
The script snapshots global rp_filter and IPv6 sysctls, removes stale topology, then iterates selected test names and directions. `config_common()` creates `ns1` and `ns2`, veth pairs, tunnel endpoints, tc clsact qdiscs, and an ingress drop filter in `ns2`. Each test creates an external tunnel on the host, attaches a redirect section on ingress or egress, updates the pinned `tun_iface` map with the tunnel ifindex, pings VIP addresses, optionally tests direct egress, and calls `cleanup()`.

## State And Persistence
State is mostly system state: network namespaces, veth devices, tunnel devices, routes, qdiscs, tc filters, sysctls, and `/sys/fs/bpf/tc/globals/tun_iface`. Cleanup restores saved sysctl values and deletes topology and pinned map artifacts.

## Dependencies And Integration Points
It depends on root privileges, iproute2 with BPF support, ping, kernel IPIP/IP6 tunnel support, tc clsact, BPF map pinning, and the companion kernel and user sample files. The script integrates map values written by userspace with tc programs attached by iproute2.

## Risks And Edge Cases
The script changes global forwarding/rp_filter/IPv6 settings and assumes cleanup runs. Failures before cleanup, missing privileges, unavailable IPv6, existing namespace/device names, or missing tunnel modules can leave host networking altered. The tests use fixed addresses and ifnames that can conflict with local setup.

## Test Signals
Passing output prints `OK` for `l2_to_ipip` and `l2_to_ip6tnl` in ingress and egress modes. Additional signals are successful tc filter attach, pinned map update, namespace pings to `10.10.1.102` and `2401:face::66`, and absence of leftover namespaces/qdiscs after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_kern.c

## Purpose
`tc_l2_redirect_kern.c` contains tc classifier programs that redirect selected L2 frames into IPIP/IP6 tunnel devices and drop non-tunneled traffic to configured VIP prefixes. It demonstrates `bpf_skb_set_tunnel_key()`, `bpf_redirect()`, ingress redirection, pinned maps, and packet parsing in cls_bpf.

## Important APIs, Types, And Functions
The pinned `tun_iface` array map stores the tunnel ifindex. `is_vip_addr()` matches IPv4 `10.10.1.0/24` and IPv6 `2401:face::/` prefix fragments. Program sections are `l2_to_iptun_ingress_forward`, `l2_to_iptun_ingress_redirect`, `l2_to_ip6tun_ingress_redirect`, and `drop_non_tun_vip`.

## Control Flow
Each tc program validates Ethernet and IP header bounds before reading packet fields. The forward section recognizes tunneled IP/IP6 packets and redirects them to the configured tunnel with `BPF_F_INGRESS`. Redirect sections match VIP destinations, fill a `bpf_tunnel_key` for IPv4 or IPv6 remote tunnel endpoints, call `bpf_skb_set_tunnel_key()`, and redirect to the tunnel ifindex. The drop section drops VIP-bound packets that are not accepted through the tunnel path.

## State And Persistence
The only persistent BPF state is the pinned single-entry `tun_iface` map updated by userspace. Packet mutations are transient per skb. Trace messages are emitted with `bpf_trace_printk()` for diagnostics.

## Dependencies And Integration Points
The program depends on tc clsact, BPF helper support for tunnel keys and redirect, iproute2 ELF map pinning, and the shell/user helpers. It integrates with Linux tunnel devices whose ifindex is shared through the map.

## Risks And Edge Cases
Header parsing must remain verifier-safe and correctly account for Ethernet/IP header sizes. The code assumes simple non-fragmented IPv4/IPv6 headers and fixed VIP/tunnel addresses. Missing map values silently pass packets, and bad ifindex values can blackhole traffic. `bpf_trace_printk()` is diagnostic-only and expensive under load.

## Test Signals
Expected signals are successful verifier load for all sections, correct redirect counters in `tc -s`, successful pings through IPIP/IP6 tunnels, VIP drops for non-tunnel packets, and trace output showing selected redirect/forward decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_user.c

## Purpose
`tc_l2_redirect_user.c` is the tiny userspace companion that updates a pinned BPF array map with a tunnel interface index for the tc L2 redirect sample.

## Important APIs, Types, And Functions
`main()` parses `-U <pinned-file>` and `-i <ifindex>`, opens the map with `bpf_obj_get()`, and writes key zero with `bpf_map_update_elem()`. `usage()` prints command syntax.

## Control Flow
The program validates required arguments, opens the pinned map path, updates array key `0` with the parsed ifindex, closes the fd, and returns the libbpf update status.

## State And Persistence
It persists exactly one integer in a pinned BPF map shared with tc programs. The process owns no durable local state after exit.

## Dependencies And Integration Points
It depends on libbpf's low-level BPF syscall wrappers and on the map created and pinned by iproute2 under `/sys/fs/bpf/tc/globals/tun_iface`. It is invoked by `tc_l2_redirect.sh`.

## Risks And Edge Cases
The code uses `atoi()` without strict validation, so malformed ifindex input can become zero. It assumes the pinned object is a compatible array map. A stale or wrong map path results in update failure without modifying kernel state.

## Test Signals
Successful execution returns zero and subsequent tc traffic is redirected to the target tunnel. Failure signals are `bpf_obj_get()` or `bpf_map_update_elem()` diagnostics and unchanged redirect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcbpf1_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcbpf1_kern.c

## Purpose
`tcbpf1_kern.c` is a tc classifier sample that rewrites selected IPv4/TCP packet fields and demonstrates redirect and clone-redirect helpers.

## Important APIs, Types, And Functions
Helpers include `set_dst_mac()`, `set_ip_tos()`, `set_tcp_ip_src()`, and `set_tcp_dest_port()`. Program sections are `classifier`, `redirect_xmit`, `redirect_recv`, `clone_redirect_xmit`, and `clone_redirect_recv`. It uses legacy load helpers, `bpf_skb_store_bytes()`, `bpf_l3_csum_replace()`, `bpf_l4_csum_replace()`, `bpf_redirect()`, and `bpf_clone_redirect()`.

## Control Flow
The classifier reads the IP protocol byte from the skb. For TCP packets it updates TOS, source IP, and destination TCP port while adjusting IP and TCP checksums. Redirect programs send to `skb->ifindex + 1` in transmit or receive direction. Clone redirect programs clone to the neighboring ifindex and then drop the original.

## State And Persistence
There is no map or persistent state. All behavior is per-packet skb mutation or redirection.

## Dependencies And Integration Points
The sample depends on tc cls_bpf, legacy BPF packet load helpers from `bpf_legacy.h`, and Ethernet/IPv4/TCP header layout. It is exercised by tc classifier tests and iproute2 object loading.

## Risks And Edge Cases
The classifier assumes standard Ethernet plus IPv4 header locations and does not explicitly bounds-check headers in C, relying on helper semantics and verifier constraints. The `ifindex + 1` redirect convention is topology-specific. Checksum replacement must match byte order and field sizes.

## Test Signals
Signals include successful tc load, packets rewritten with TOS `8`, source IP `10.1.1.1`, destination port `5001`, and redirect/clone behavior visible in tc counters or peer veth traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcbpf1_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_basertt_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_basertt_kern.c

## Purpose
`tcp_basertt_kern.c` is a sock_ops sample that supplies a custom base RTT value for TCP-NV when local and remote IPv6 addresses appear to be in the same datacenter.

## Important APIs, Types, And Functions
The sole BPF entry point is `bpf_basertt()` in section `sockops`. It uses `struct bpf_sock_ops`, `BPF_SOCK_OPS_BASE_RTT`, `bpf_getsockopt()` for `TCP_CONGESTION`, `bpf_ntohl()`, `bpf_printk()`, and `skops->reply`.

## Control Flow
The program checks the sock_ops operation and IPv6 prefix relationship. On `BPF_SOCK_OPS_BASE_RTT`, it reads the TCP congestion control name and returns `80` microseconds only when it matches `nv`; otherwise it returns the helper error or `-1`. Unsupported operations and non-matching address families/prefixes return `-1`.

## State And Persistence
No maps are used. The only state change is the per-callback `skops->reply` value consumed by TCP sock_ops.

## Dependencies And Integration Points
It depends on cgroup sock_ops attachment via bpftool, TCP-NV availability, and kernel support for `TCP_CONGESTION` getsockopt from sock_ops. It integrates with TCP connection setup and base RTT callbacks.

## Risks And Edge Cases
The datacenter heuristic is hard-coded to the first 5.5 bytes of IPv6 addresses and ignores IPv4. String comparison uses the fixed `nv` array size. Debug printing can be noisy.

## Test Signals
Attach to a cgroup and establish IPv6 TCP-NV connections with matching and non-matching prefixes. Confirm `skops->reply` becomes `80` only for the matching TCP-NV case and `-1` otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_basertt_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_bufs_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_bufs_kern.c

## Purpose
`tcp_bufs_kern.c` demonstrates sock_ops control of initial receive window and socket buffer sizes for selected TCP connections.

## Important APIs, Types, And Functions
`bpf_bufs()` handles `BPF_SOCK_OPS_RWND_INIT`, `BPF_SOCK_OPS_TCP_CONNECT_CB`, `BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB`, and `BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB`. It uses `bpf_setsockopt()` for `SO_SNDBUF` and `SO_RCVBUF`, `bpf_ntohl()`, and `skops->reply`.

## Control Flow
The program gates behavior to connections where either local or remote port is `55601`. It returns an initial receive window of `40` packets on `RWND_INIT`, sets send and receive buffers to 1.5 MB on active connect and passive established callbacks, does nothing for active established, and returns `-1` for unsupported operations.

## State And Persistence
No BPF maps are used. Persistent effects are socket option changes applied to each matched TCP socket.

## Dependencies And Integration Points
It attaches as a cgroup sock_ops program and integrates with TCP socket option handling. The sample assumes caller traffic uses port `55601` for test selection.

## Risks And Edge Cases
The port guard comment says "neither" but the logic actually runs when either side is port `55601`. Summing two setsockopt return codes can obscure which option failed. Applying large buffers without real RTT checks can waste memory.

## Test Signals
Use TCP traffic involving port `55601` and verify initial receive window and socket buffers. Non-matching ports should receive `reply = -1` and unchanged buffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_bufs_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_clamp_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_clamp_kern.c

## Purpose
`tcp_clamp_kern.c` is a sock_ops sample that sets short SYN RTOs, 150 KB buffers, and a send congestion-window clamp for same-datacenter IPv6 TCP connections.

## Important APIs, Types, And Functions
`bpf_clamp()` handles `BPF_SOCK_OPS_TIMEOUT_INIT`, connect, active established, and passive established callbacks. It uses `bpf_setsockopt()` for `SO_SNDBUF`, `SO_RCVBUF`, and `TCP_BPF_SNDCWND_CLAMP`, plus `skops->reply`.

## Control Flow
The program filters to port `55601`, checks IPv6 prefix similarity, then returns timeout init `10`, sets buffers on active connect, sets the cwnd clamp on active established, and sets clamp plus buffers on passive established. Non-matching cases return `-1`.

## State And Persistence
There is no map state. Per-socket state changes persist as TCP options for the lifetime of the connection.

## Dependencies And Integration Points
It depends on cgroup sock_ops, TCP BPF setsockopt support, and the TCP `TCP_BPF_SNDCWND_CLAMP` option. It integrates with TCP handshake and established callbacks.

## Risks And Edge Cases
The sample hard-codes datacenter and port heuristics and can impose unsuitable RTO/clamp values outside the intended environment. One early unmatched-port branch returns `0` while setting reply `-1`, unlike most other samples. Return-code accumulation can hide partial setsockopt failures.

## Test Signals
Verify SYN/SYN-ACK timeout reply `10`, buffer sizes, and cwnd clamp for matching IPv6/port traffic. Non-matching prefixes or ports should leave TCP defaults unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_clamp_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_cong_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_cong_kern.c

## Purpose
`tcp_cong_kern.c` demonstrates selecting DCTCP congestion control and requesting ECN for same-datacenter IPv6 TCP connections through cgroup sock_ops.

## Important APIs, Types, And Functions
`bpf_cong()` handles `BPF_SOCK_OPS_NEEDS_ECN`, `BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB`, and `BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB`. It uses `bpf_setsockopt()` with `TCP_CONGESTION`, `bpf_ntohl()`, and `skops->reply`.

## Control Flow
After a port `55601` gate and IPv6 prefix check, the program returns `1` for `NEEDS_ECN` and sets `TCP_CONGESTION` to `"dctcp"` for both active and passive established callbacks. Unsupported operations return `-1`.

## State And Persistence
No maps are present. The persistent effect is per-socket congestion-control state and ECN negotiation behavior.

## Dependencies And Integration Points
It requires cgroup sock_ops attachment and a kernel with DCTCP congestion control available. It integrates with TCP ECN decision callbacks and established socket option updates.

## Risks And Edge Cases
If DCTCP is unavailable, `bpf_setsockopt()` will fail and its error is propagated through `reply`. The address heuristic is IPv6-only and hard-coded. Incorrect deployment can force unsuitable congestion control.

## Test Signals
Connections matching port and prefix should request ECN and show `dctcp` congestion control after establishment. Non-matching traffic should receive `reply = -1` and retain default congestion control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_cong_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_dumpstats_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_dumpstats_kern.c

## Purpose
`tcp_dumpstats_kern.c` is a sock_ops sample that periodically prints selected TCP internal statistics for each socket during RTT callbacks.

## Important APIs, Types, And Functions
The `bpf_next_dump` `BPF_MAP_TYPE_SK_STORAGE` map stores the next dump timestamp per socket. `_sockops()` uses `bpf_sock_ops_cb_flags_set()`, `bpf_sk_storage_get()`, `bpf_ktime_get_ns()`, `bpf_tcp_sock()`, and `bpf_printk()`.

## Control Flow
On `TCP_CONNECT_CB`, it enables RTT callbacks and exits. On `RTT_CB`, it obtains `ctx->sk`, creates or finds per-socket storage, checks whether one second has elapsed, casts to `struct bpf_tcp_sock`, stores the next timestamp, and prints DSACK, delivered, ECN-delivered, and retransmit counters.

## State And Persistence
Per-socket BPF local storage persists while the socket exists and contains the next allowed dump time. Printed statistics are transient trace output.

## Dependencies And Integration Points
It depends on cgroup sock_ops, BPF socket local storage, RTT callback support, and `bpf_tcp_sock()` typed access. It references `samples/bpf/tcp_bpf.readme` for run instructions.

## Risks And Edge Cases
If socket local storage allocation or `bpf_tcp_sock()` fails, the callback silently returns. Trace printing at one-second cadence can still be noisy at scale. It only activates for sockets that receive `TCP_CONNECT_CB`.

## Test Signals
Attach to a cgroup, start TCP connections, and observe one-second `bpf_printk()` lines with `dsack_dups`, `delivered`, `delivered_ce`, and `icsk_retransmits`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_dumpstats_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_iw_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_iw_kern.c

## Purpose
`tcp_iw_kern.c` demonstrates sock_ops control of initial congestion window, initial receive window, and socket buffers for selected TCP traffic.

## Important APIs, Types, And Functions
`bpf_iw()` handles `BPF_SOCK_OPS_RWND_INIT`, `BPF_SOCK_OPS_TCP_CONNECT_CB`, `BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB`, and `BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB`. It sets `SO_SNDBUF`, `SO_RCVBUF`, and `TCP_BPF_IW`.

## Control Flow
For connections involving port `55601`, the program returns receive window `40`, sets 1.5 MB buffers during active connect and passive established callbacks, and sets initial congestion window `40` on active established. Other callbacks return `-1`.

## State And Persistence
No BPF maps are used. Socket options persist on the affected TCP socket.

## Dependencies And Integration Points
It integrates with TCP cgroup sock_ops and depends on kernel support for `TCP_BPF_IW` setsockopt.

## Risks And Edge Cases
The sample lacks the real distance/RTT policy its comments describe. Port gating is test-specific. Over-large initial windows and buffers can hurt congestion behavior if deployed blindly.

## Test Signals
For port `55601`, inspect TCP socket buffers and initial congestion/receive window behavior. Non-matching ports should not be modified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_iw_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_rwnd_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_rwnd_kern.c

## Purpose
`tcp_rwnd_kern.c` is a sock_ops sample that increases the initial TCP receive window for IPv6 connections whose prefixes suggest they are not in the same datacenter.

## Important APIs, Types, And Functions
The entry point is `bpf_rwnd()`. It reads `struct bpf_sock_ops` fields, checks `BPF_SOCK_OPS_RWND_INIT`, uses `bpf_ntohl()`, and writes `skops->reply`.

## Control Flow
The program gates on port `55601`, then only handles `RWND_INIT` for IPv6 sockets. If the first prefix components differ, it returns `40`; otherwise the default `-1` reply is kept.

## State And Persistence
No maps or persistent state exist. The reply value influences TCP's initial advertised receive window for the connection.

## Dependencies And Integration Points
It depends on cgroup sock_ops and TCP receive-window callback support. It is intended to be loaded with `bpftool cgroup attach`.

## Risks And Edge Cases
The IPv6 prefix comparison mask differs slightly from other samples and is hard-coded. IPv4 traffic and unsupported operations are ignored. The comment typo does not affect behavior but reflects sample-only polish.

## Test Signals
Matching IPv6 remote/local prefixes that differ should produce `reply = 40`; same-prefix or non-IPv6 traffic should preserve default behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_rwnd_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_synrto_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_synrto_kern.c

## Purpose
`tcp_synrto_kern.c` demonstrates using sock_ops to set SYN and SYN-ACK initial RTO to 10 ms for same-datacenter IPv6 TCP connections.

## Important APIs, Types, And Functions
The single entry point `bpf_synrto()` handles `BPF_SOCK_OPS_TIMEOUT_INIT`, IPv6 address fields, `bpf_ntohl()`, and `skops->reply`.

## Control Flow
After filtering to port `55601`, it checks for `TIMEOUT_INIT` and IPv6. If the first 5.5 bytes of local and remote IPv6 addresses match, it returns `10`; otherwise it leaves `rv = -1`.

## State And Persistence
There is no persistent BPF state. The callback reply influences TCP handshake timeout initialization.

## Dependencies And Integration Points
It depends on cgroup sock_ops and TCP timeout initialization callbacks.

## Risks And Edge Cases
The 10 ms timeout is environment-specific and can trigger unnecessary retransmits outside low-latency domains. The sample ignores IPv4 and uses a fixed prefix heuristic.

## Test Signals
Same-prefix IPv6 port `55601` connections should report timeout init `10`; other connections should use default timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_synrto_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_tos_reflect_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_tos_reflect_kern.c

## Purpose
`tcp_tos_reflect_kern.c` is a sock_ops sample that saves the incoming SYN and reflects its IPv4 TOS or IPv6 traffic class onto the accepted socket.

## Important APIs, Types, And Functions
`bpf_basertt()` handles `BPF_SOCK_OPS_TCP_LISTEN_CB` and `BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB`. It uses `bpf_setsockopt()` for `TCP_SAVE_SYN`, `IP_TOS`, and `IPV6_TCLASS`, and `bpf_getsockopt()` for `TCP_SAVED_SYN`.

## Control Flow
On listen callback, it enables SYN saving. On passive established callback, it chooses IPv4 or IPv6 header size, reads the saved SYN header, extracts TOS/traffic class, and sets the corresponding IP option when nonzero. Unsupported operations return `-1`.

## State And Persistence
No maps are used. The kernel stores saved SYN data due to `TCP_SAVE_SYN`; the accepted socket persists the reflected TOS or traffic-class option.

## Dependencies And Integration Points
It depends on cgroup sock_ops callbacks and TCP saved SYN support. It integrates with passive TCP accept paths and IP/IPv6 socket option handling.

## Risks And Edge Cases
It assumes the saved SYN header layout matches the address family and does not inspect option lengths beyond fixed IP headers. Nonzero traffic class is reflected without policy validation. Failure from the final setsockopt is not always assigned back to `rv`.

## Test Signals
Create a listening socket under the cgroup, connect with IPv4 TOS or IPv6 traffic class set, and verify the accepted socket inherits the value. Zero TOS should leave defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_tos_reflect_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_cls_bpf.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/test_cls_bpf.sh

## Purpose
`test_cls_bpf.sh` is a simple tc classifier smoke test for sample packet parsers. It attaches three BPF parser objects to a veth ingress hook and uses pktgen to confirm packets are filtered/dropped.

## Important APIs, Types, And Functions
Shell functions are `pktgen()` and `test()`. It uses `ip link`, `tc qdisc`, `tc filter`, `tc -s`, `awk`, and `../pktgen/pktgen_bench_xmit_mode_netif_receive.sh`.

## Control Flow
The script creates a veth pair, brings both ends up, attaches each object/section pair (`parse_simple.o:simple`, `parse_varlen.o:varlen`, `parse_ldabs.o:ldabs`) to ingress clsact, runs pktgen, inspects qdisc drop counters, deletes clsact, and finally deletes the veth.

## State And Persistence
State is temporary network device and qdisc state. No BPF map data is persisted.

## Dependencies And Integration Points
It depends on root privileges, pktgen sample scripts, tc clsact, parser object files built beforehand, and a kernel with cls_bpf support.

## Risks And Edge Cases
No trap is installed, so failures can leave the veth or qdisc behind. The drop counter parsing relies on `tc -s` output layout. It assumes generated traffic reaches the ingress path of the test veth.

## Test Signals
For each parser, attach should print `ok`, pktgen should run, and qdisc drop counters should be nonzero. A zero drop count prints `FAIL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_cls_bpf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lru_dist.c -->
# sources/distributed-fs/ceph-client/samples/bpf/test_lru_dist.c

## Purpose
`test_lru_dist.c` is a userspace stress and distribution test for BPF LRU hash maps. It compares kernel LRU map behavior against a perfect userspace LRU model, tests loss patterns, and exercises common and per-CPU LRU modes under parallel access.

## Important APIs, Types, And Functions
Core helpers are `pfect_lru_init()`, `pfect_lru_lookup_or_insert()`, `read_keys()`, `create_map()`, `sched_next_online()`, `run_parallel()`, `do_test_lru_dist()`, `test_parallel_lru_dist()`, `test_lru_loss0()`, `test_lru_loss1()`, `do_test_parallel_lru_loss()`, and `test_parallel_lru_loss()`. It uses `bpf_map_create()`, `bpf_map_lookup_elem()`, `bpf_map_update_elem()`, and BPF map flags including `BPF_F_NO_COMMON_LRU`.

## Control Flow
`main()` parses a key distribution file, LRU size, and task count, determines possible CPUs, and runs tests for common and per-CPU LRU maps. The perfect LRU uses a userspace hash map plus linked list to track ideal hits/misses. Parallel tests fork workers pinned across CPUs, execute the distribution, count map misses/unique entries, and print comparisons. Loss tests insert, touch, and evict key ranges to observe whether active entries survive.

## State And Persistence
Runtime state includes BPF map fds, per-process perfect-LRU nodes, loaded distribution keys, forked child processes, CPU affinity, and transient loss counters. No state persists after map fds close and memory is freed.

## Dependencies And Integration Points
It depends on libbpf syscall wrappers, CPU affinity APIs, fork/wait, input distribution files, and kernel BPF LRU hash map implementation. It integrates with BPF map semantics rather than loading any BPF program.

## Risks And Edge Cases
The test uses `assert()` heavily, so any syscall failure aborts. Parent and child share map fds across fork, which is intended but sensitive to process scheduling. Per-CPU LRU sizing differs from common LRU sizing. Input parsing reads the whole file into memory and assumes numeric lines.

## Test Signals
Useful output includes `nr_cpus`, loss counts for old/active/new ranges, per-task loss lines, and perfect-versus-kernel miss statistics. Stable active entries should show fewer losses than unused ranges, and both map flag modes should complete without assertion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lru_dist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.c

## Purpose
`test_lwt_bpf.c` provides multiple lightweight tunnel route BPF programs used by the accompanying shell integration test. It validates lwt context access, skb control-buffer clearing, packet data reads, checksum-safe IP rewriting, L2 header push and redirect, intentional corruption, and drops.

## Important APIs, Types, And Functions
Program sections include `nop`, `test_ctx`, `test_cb`, `test_data`, `test_rewrite`, `push_ll_and_redirect_silent`, `push_ll_and_redirect`, `fill_garbage`, `fill_garbage_and_redirect`, and `drop_all`. Helpers include `rewrite()`, `__do_push_ll_and_redirect()`, and `__fill_garbage()`. It uses `bpf_skb_load_bytes()`, `bpf_skb_store_bytes()`, `bpf_l3_csum_replace()`, `bpf_l4_csum_replace()`, `bpf_skb_change_head()`, `bpf_redirect()`, and `bpf_trace_printk()`.

## Control Flow
Each route-attached section returns `BPF_OK`, `BPF_DROP`, or a redirect result. Context tests print skb fields and write `skb->cb[0]`. Data tests parse IPv4 headers. Rewrite tests replace a configured destination IP and update L3/L4 checksums based on protocol. Redirect tests prepend an Ethernet header using compile-time MAC/ifindex constants and redirect to the destination interface.

## State And Persistence
The BPF programs use no maps. State is per-packet skb context and trace output. MAC addresses and destination ifindex are compiled in by the test script.

## Dependencies And Integration Points
It depends on lwt BPF route encap support, kernel networking headers from `vmlinux.h` and `net_shared.h`, and test-provided `SRC_MAC`, `DST_MAC`, and `DST_IFINDEX` defines. It integrates with `ip route encap bpf` in `test_lwt_bpf.sh`.

## Risks And Edge Cases
The programs intentionally corrupt or drop packets in several sections. IPv4 checksum offsets assume no IP options. Compile-time constants must match the generated veth topology. Trace output is part of the test contract and can be affected by tracing configuration.

## Test Signals
The shell harness verifies exact trace strings for context, data, cb, rewrite, redirect, garbage, and drop cases, plus ping/netperf success or failure depending on the installed section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.sh

## Purpose
`test_lwt_bpf.sh` is the integration harness for lwt BPF route programs. It creates namespaces and veth devices, compiles `test_lwt_bpf.c` with topology-specific constants, installs programs on `xmit`, `out`, and `in` route hooks, and validates packet behavior and trace output.

## Important APIs, Types, And Functions
Important functions are `lookup_mac()`, `cleanup()`, `setup_one_veth()`, `install_test()`, `remove_prog()`, `get_trace()`, `match_trace()`, and test cases such as `test_ctx_xmit()`, `test_data_in()`, `test_drop_all()`, `test_rewrite()`, `test_netperf_nop()`, and `test_netperf_redirect()`.

## Control Flow
The script cleans stale state, creates two namespaces/veth pairs, starts `netserver`, enables tracing, discovers MACs and ifindex, compiles the BPF object with clang, then sequentially installs route encap BPF programs and runs pings or netperf. Each test clears trace, installs a section, validates connectivity and exact trace text, then removes the route program. Cleanup restores tracing options and deletes topology.

## State And Persistence
State includes namespaces, veth devices, routes, generated `test_lwt_bpf.o`, trace buffer contents, trace options, and a `netserver` process in `NS1`. Cleanup removes most state and restores the saved trace context option.

## Dependencies And Integration Points
It depends on root privileges, `clang --target=bpf`, iproute2 lwt BPF support, `/sys/kernel/tracing`, ping, netperf/netserver, and the companion C source.

## Risks And Edge Cases
The script uses `set -ex` after setup but no global trap, so early failures can leave topology or tracing changed. Exact trace matching is brittle across kernel formatting changes. `killall netserver` in a namespace assumes process name availability. Netperf is optional on many systems.

## Test Signals
All named tests must complete, trace output must match expected lines, ping failures must occur only in drop/corrupt cases, netperf must succeed for nop and redirect, and final exit status must be zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map.bpf.c

## Purpose
`test_map_in_map.bpf.c` is the kernel-side half of a map-in-map self-test. It verifies that BPF programs can look up inner maps from array-of-maps and hash-of-maps outer maps, then perform both regular and inline inner-map lookups.

## Important APIs, Types, And Functions
Maps include `port_a`, `port_h`, `reg_result_h`, `inline_result_h`, `a_of_port_a`, `h_of_port_a`, and `h_of_port_h`. Helpers are `do_reg_lookup()`, `do_inline_array_lookup()`, `do_inline_hash_lookup()`, and syscall program `trace_sys_connect` attached to `ksyscall/connect`.

## Control Flow
The syscall program reads a user `sockaddr_in6` from `connect()`, filters for destination prefix `dead:beef`, uses the last IPv6 word as a test-case id, reads the port as the key, selects the matching outer map, looks up the inner map, performs a generic lookup, performs the expected inline array/hash lookup, and writes both results to result maps.

## State And Persistence
Persistent state is the set of BPF maps and their contents populated by userspace. Result maps store the latest regular and inline lookup return values at key zero.

## Dependencies And Integration Points
It depends on BTF/vmlinux, libbpf CO-RE macros, syscall tracing attachment, user memory reads, map-in-map verifier support, and the companion userspace file that populates maps and triggers `connect()`.

## Risks And Edge Cases
The program intentionally uses invalid `connect(-1, ...)` calls as triggers, so it must filter carefully. Inline helpers validate inner map identity and return `-EINVAL` if the verifier or map population did not preserve expected inner-map type. User pointer reads can fail and are reported through result maps.

## Test Signals
For test cases array-of-array, hash-of-array, and hash-of-hash, both `reg_result_h` and `inline_result_h` should equal the userspace magic value after the trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map_user.c

## Purpose
`test_map_in_map_user.c` loads the map-in-map BPF object, populates inner and outer maps, triggers the syscall probe, and validates map lookup results for array-of-array, hash-of-array, and hash-of-hash cases.

## Important APIs, Types, And Functions
Important functions are `check_map_id()`, `populate_map()`, `test_map_in_map()`, and `main()`. It uses `bpf_object__open_file()`, `bpf_object__load()`, `bpf_object__find_program_by_name()`, `bpf_program__attach()`, `bpf_object__find_map_fd_by_name()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_map_get_info_by_fd()`, and `connect()`.

## Control Flow
`main()` opens `<argv[0]>.bpf.o`, loads it, resolves seven map fds, attaches `trace_sys_connect`, then calls `test_map_in_map()`. The test picks a random port key, populates inner maps and outer maps with map fds, checks outer maps expose the expected inner map ids, constructs `dead:beef::*:<testid>` IPv6 addresses, calls `connect(-1, ...)` to trigger BPF, and compares both result maps to the magic value.

## State And Persistence
State is all inside the loaded BPF object maps and the libbpf link. Results are deleted after each case. No pinned state survives process exit.

## Dependencies And Integration Points
It depends on libbpf, map-in-map kernel support, syscall tracing, and the companion BPF object. The invalid `connect()` is an intentional trigger path and should fail with `EBADF`.

## Risks And Edge Cases
The test uses `assert()` for most failures and returns zero on some setup failures for sample compatibility. Random key selection is masked to low 8 bits, avoiding broad coverage. Endianness of `sin6_port` is treated consistently with the BPF side for this test rather than as a real network port.

## Test Signals
The program should print `Array of Array: Pass`, `Hash of Array: Pass`, and `Hash of Hash: Pass`; result map mismatches print both values and exit with failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_event_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/trace_event_kern.c

## Purpose
`trace_event_kern.c` is a perf-event BPF program that collects kernel and user stack traces keyed by current command and stack ids, while also demonstrating perf-event value and address reads.

## Important APIs, Types, And Functions
The maps are `counts` (`BPF_MAP_TYPE_HASH`) and `stackmap` (`BPF_MAP_TYPE_STACK_TRACE`). The entry point `bpf_prog1()` uses `bpf_get_current_comm()`, `bpf_get_stackid()`, `bpf_perf_prog_read_value()`, `bpf_get_smp_processor_id()`, `PT_REGS_IP()`, `bpf_map_lookup_elem()`, and `bpf_map_update_elem()`.

## Control Flow
The program ignores warmup samples with small `sample_period`, records current command, gets kernel and user stack ids, prints fallback diagnostics when both stack ids fail, reads perf-event enabled/running time, optionally prints recorded address, then increments or creates the count for the `(comm,kernstack,userstack)` key.

## State And Persistence
Stack trace samples persist in `stackmap`; aggregate counts persist in `counts` until userspace drains and deletes them. Other values are per-event.

## Dependencies And Integration Points
It depends on perf-event program attachment, stack trace helper support, perf event data context, and the companion userspace program that attaches across event types and prints stacks.

## Risks And Edge Cases
Stack id collection can fail due to collisions, missing user stacks, or unsupported contexts. `bpf_perf_prog_read_value()` can fail for inherited task events. Trace printing can be noisy and changes timing.

## Test Signals
Expected signals are nonzero count entries, stack ids resolvable from `stackmap`, perf enabled/running trace lines for all-CPU events, optional address lines for precise events, and userspace validation that kernel stacks include read/write syscall paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_event_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_event_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/trace_event_user.c

## Purpose
`trace_event_user.c` is the userspace driver for the perf-event stack trace sample. It attaches the BPF program to several hardware, software, cache, raw, and precise perf events in all-CPU and inherited task modes, generates load, prints stack aggregates, and validates expected syscall stack content.

## Important APIs, Types, And Functions
Important routines are `print_ksym()`, `print_stack()`, `print_stacks()`, `generate_load()`, `test_perf_event_all_cpu()`, `test_perf_event_task()`, `test_bpf_perf_event()`, and `main()`. It uses `sys_perf_event_open()`, `bpf_program__attach_perf_event()`, `bpf_map_get_next_key()`, `bpf_map_lookup_elem()`, `bpf_map_delete_elem()`, `load_kallsyms()`, and `read_trace_pipe()`.

## Control Flow
Startup loads kallsyms and the BPF object, resolves `counts` and `stackmap`, forks a trace-pipe reader, then runs a suite of perf events. Each all-CPU test opens a perf event per CPU and attaches the program; each task test opens an inherited event for the process. After running `dd`, it prints and clears count and stack maps, checking that read/write kernel stack symbols were observed.

## State And Persistence
State includes perf event fds, BPF links, two map fds, a child trace-pipe reader process, and transient stack/count data. Maps are cleared between test iterations.

## Dependencies And Integration Points
It depends on libbpf, perf_event_open permissions, kallsyms access, `dd`, signal handling, and the kernel sample object. Some raw event configs are CPU-model specific.

## Risks And Edge Cases
Raw events such as Intel instruction retired and lock load may not exist on all CPUs or virtual machines. The symbol checks appear inverted in `print_ksym()` due to `!strstr()` logic and may make the sample fragile. `err_exit()` kills the child and exits, so cleanup is abrupt.

## Test Signals
The suite prints each tested perf event name and ends with `*** PASS ***` if stack maps are populated and expected syscall stack evidence is found. Failures include perf open errors, missing maps, empty stack results, or missing syscall symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_event_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_output.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/trace_output.bpf.c

## Purpose
`trace_output.bpf.c` is a minimal syscall tracing program that emits records to a perf event array on every `write()` syscall.

## Important APIs, Types, And Functions
The `my_map` `BPF_MAP_TYPE_PERF_EVENT_ARRAY` map is consumed by userspace. `bpf_prog1()` is attached to `ksyscall/write` and uses `bpf_get_current_pid_tgid()` and `bpf_perf_event_output()`.

## Control Flow
On each traced write syscall, the program fills a small struct with pid/tgid and constant cookie `0x12345678`, then outputs it to the perf event array for the current CPU.

## State And Persistence
The perf event array map persists while the BPF object is loaded. Event records are transient and delivered to perf buffers.

## Dependencies And Integration Points
It depends on syscall tracing attachment, perf event array maps, and the companion `trace_output_user.c` perf buffer reader.

## Risks And Edge Cases
High write rates can overflow perf buffers or increase overhead. The map has max entries `2`, so systems or readers expecting broader CPU coverage must size it appropriately or rely on sample constraints.

## Test Signals
The userspace reader should receive records with cookie `0x12345678` and print an event rate after `MAX_CNT` events without reporting cookie mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_output.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_output_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/trace_output_user.c

## Purpose
`trace_output_user.c` loads the perf-output syscall tracing sample, attaches it, consumes perf-buffer records, validates their cookie, and measures event throughput.

## Important APIs, Types, And Functions
Key functions are `time_get_ns()`, `print_bpf_output()`, and `main()`. It uses `bpf_object__open_file()`, `bpf_object__load()`, `bpf_object__find_map_fd_by_name()`, `bpf_object__find_program_by_name()`, `bpf_program__attach()`, `perf_buffer__new()`, and `perf_buffer__poll()`.

## Control Flow
The program opens `<argv[0]>.bpf.o`, loads it, finds `my_map` and `bpf_prog1`, attaches the syscall program, creates a perf buffer, starts a `dd` workload through `popen()`, and polls until it receives `MAX_CNT` valid records. The callback counts records and prints events per second at the limit.

## State And Persistence
State is process-local: a libbpf object/link, perf buffer, start time, and event count. Kernel map state exists only while the object is loaded.

## Dependencies And Integration Points
It depends on libbpf perf buffer support, a companion BPF object, syscall tracing, `taskset`, `dd`, and signal delivery. It integrates with perf-event-array output generated by the BPF program.

## Risks And Edge Cases
The perf buffer is not freed explicitly on cleanup, and `popen()` is not closed. `kill(0, SIGINT)` signals the process group, which can affect the parent shell if not isolated. Map max entries may be too small for high CPU ids.

## Test Signals
Successful runs receive `MAX_CNT` records with the expected cookie and print `recv ... events per sec`; any cookie mismatch prints `BUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_output_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex1.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex1.bpf.c

## Purpose
`tracex1.bpf.c` is a kprobe sample that observes loopback packets entering `__netif_receive_skb_core*` and prints skb pointer and length.

## Important APIs, Types, And Functions
The single program `bpf_prog1()` attaches to `kprobe.multi/__netif_receive_skb_core*`. It uses `PT_REGS_PARM1()`, `BPF_CORE_READ()`, `BPF_CORE_READ_STR_INTO()`, `IFNAMSIZ`, and `bpf_trace_printk()`.

## Control Flow
On each kprobe hit, the program reads the `sk_buff *`, follows `skb->dev`, reads `skb->len` and device name, and prints only when the device name starts with `lo`.

## State And Persistence
There are no maps. The only output is transient trace pipe text.

## Dependencies And Integration Points
It depends on kprobe/multi attach support, BTF CO-RE field reads, and the networking receive path symbol naming. The userspace companion triggers loopback pings and reads trace output.

## Risks And Edge Cases
Kprobes are not stable ABI, and the wildcard is used to tolerate symbol suffix changes. CO-RE field reads depend on BTF availability. Trace printing is for debugging only.

## Test Signals
Running the companion should show trace lines like `skb <ptr> len <n>` during localhost ping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex1.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex1_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex1_user.c

## Purpose
`tracex1_user.c` loads and attaches the loopback skb kprobe sample, generates localhost ICMP traffic, and streams BPF trace output.

## Important APIs, Types, And Functions
`main()` uses `bpf_object__open_file()`, `bpf_object__find_program_by_name()`, `bpf_object__load()`, `bpf_program__attach()`, `popen()`, and `read_trace_pipe()`.

## Control Flow
The program opens `<argv[0]>.bpf.o`, finds `bpf_prog1`, loads and attaches it, launches `taskset 1 ping -c5 localhost`, and then reads trace pipe until interrupted or EOF.

## State And Persistence
State is a libbpf object and link plus the child command started with `popen()`. No map state is used.

## Dependencies And Integration Points
It depends on libbpf, the companion BPF object, ping, taskset, and tracefs availability through `trace_helpers.h`.

## Risks And Edge Cases
The `popen()` handle is not closed, and the infinite trace read means the sample is interactive. Attachment can fail if the probed symbol changes or kprobe permissions are missing.

## Test Signals
Expected trace output contains loopback skb lines during the ping workload; setup failures print libbpf error messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex1_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex3.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex3.bpf.c

## Purpose
`tracex3.bpf.c` measures block I/O latency by recording timestamps at block I/O start tracepoints and adding completions to a logarithmic per-CPU latency histogram.

## Important APIs, Types, And Functions
Maps are `my_map` for start timestamps keyed by device/sector and `lat_map` as a 100-slot per-CPU array. Programs are `bpf_prog1()` for `tracepoint/block/block_io_start` and `bpf_prog2()` for `tracepoint/block/block_io_done`. Helper `log2l()` approximates log scaling.

## Control Flow
The start tracepoint stores `bpf_ktime_get_ns()` under a `start_key`. The done tracepoint looks up the start time, computes delta, deletes the start entry, converts latency to a log-scaled index, clamps it to the histogram range, and increments the per-CPU slot.

## State And Persistence
Outstanding I/O timestamps persist in `my_map` until completion. Histogram counts persist in `lat_map` until userspace reads and clears them.

## Dependencies And Integration Points
It depends on block tracepoint format, BPF per-CPU array maps, and the companion userspace histogram printer.

## Risks And Edge Cases
Device/sector alone may collide for overlapping requests. Missing start events produce no histogram increment. Long-lived entries can accumulate if completion events are missed. The log math is approximate by design.

## Test Signals
Under disk activity, the userspace program should print nonzero latency heatmap counts and clear slots between intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex3.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex3_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex3_user.c

## Purpose
`tracex3_user.c` loads the block I/O latency BPF programs and renders the per-CPU latency histogram as a colored or text heatmap.

## Important APIs, Types, And Functions
Important functions are `clear_stats()`, `print_banner()`, `print_hist()`, and `main()`. It uses `bpf_object__open_file()`, `bpf_object__load()`, `bpf_object__for_each_program()`, `bpf_program__attach()`, `bpf_map_lookup_elem()`, and `bpf_map_update_elem()`.

## Control Flow
It parses `-a` for full range and `-t` for text output, loads `<argv[0]>.bpf.o`, finds `lat_map`, attaches all programs, prints a legend, and loops every two seconds printing a heatmap and clearing the histogram.

## State And Persistence
Userspace maintains display flags and link handles. Kernel histogram state is cleared by writing zeroed per-CPU values for all slots after every print.

## Dependencies And Integration Points
It depends on libbpf, block tracepoints from the companion BPF object, terminal ANSI color support unless `-t` is used, and `bpf_num_possible_cpus()`.

## Risks And Edge Cases
The program runs forever until interrupted. ANSI color output may not be suitable for logs. It assumes exactly two programs when destroying `links[2]`.

## Test Signals
The heatmap should show nonzero event totals under block I/O, with banners every 20 intervals and successful attachment of both tracepoint programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex3_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex4.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex4.bpf.c

## Purpose
`tracex4.bpf.c` tracks kernel slab allocations that have not yet been freed, storing allocation time and caller IP for later userspace inspection.

## Important APIs, Types, And Functions
`my_map` is a large hash keyed by object pointer with `struct pair { val, ip }`. `bpf_prog1()` attaches to `kprobe/kmem_cache_free`; `bpf_prog2()` attaches to `kretprobe/kmem_cache_alloc_node_noprof`. It uses `PT_REGS_PARM2()`, `PT_REGS_RC()`, `BPF_KRETPROBE_READ_RET_IP()`, `bpf_ktime_get_ns()`, `bpf_map_update_elem()`, and `bpf_map_delete_elem()`.

## Control Flow
On allocation return, the program records the returned object pointer, current timestamp, and caller IP. On free, it deletes the pointer key from the map. Userspace later reports objects older than one second.

## State And Persistence
Outstanding allocation records persist in `my_map` while the BPF object is loaded or until a matching free occurs.

## Dependencies And Integration Points
It depends on kprobe/kretprobe attachment to kernel slab allocation symbols and the userspace map walker.

## Risks And Edge Cases
Kernel allocator symbol names change across versions; this sample probes `kmem_cache_alloc_node_noprof`. Pointer reuse and missed events can produce misleading records. The map can grow large under high allocation rates.

## Test Signals
The userspace companion should show old object pointers and allocation IPs during normal kernel allocation activity, and records should disappear after frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex4.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex4_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex4_user.c

## Purpose
`tracex4_user.c` loads the slab allocation tracking BPF sample and periodically prints objects that have remained allocated for more than one second.

## Important APIs, Types, And Functions
Key routines are `time_get_ns()`, `print_old_objects()`, and `main()`. It uses libbpf object/program attach APIs and BPF map iteration with `bpf_map_get_next_key()` and `bpf_map_lookup_elem()`.

## Control Flow
The program loads `<argv[0]>.bpf.o`, finds `my_map`, attaches all programs, then loops once per second clearing the terminal and iterating map entries. Entries older than one second are printed with age and allocation IP.

## State And Persistence
Userspace state is minimal. Kernel state is the outstanding allocation map maintained by the BPF programs.

## Dependencies And Integration Points
It depends on libbpf, terminal escape handling, the companion kprobe object, and a kernel with the probed slab symbols.

## Risks And Edge Cases
It loops forever and clears the screen with ANSI escapes. It assumes two programs when destroying links. Without symbolization, IPs are raw addresses.

## Test Signals
Expected output is periodic lines of old object pointers under allocation activity; no setup errors should occur during object load, map lookup, or program attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex4_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex5.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex5.bpf.c

## Purpose
`tracex5.bpf.c` demonstrates BPF tail calls by dispatching from a seccomp kprobe to syscall-specific BPF programs based on syscall number.

## Important APIs, Types, And Functions
The `progs` `BPF_MAP_TYPE_PROG_ARRAY` stores syscall-number-to-program entries. Entry program `bpf_prog1()` attaches to `kprobe/__seccomp_filter`. Tail-call targets are generated with `PROG(SYS__NR_write)`, `PROG(SYS__NR_read)`, and optional mmap/mmap2 sections. It uses `bpf_tail_call()`, `bpf_core_read()`, and `bpf_trace_printk()`.

## Control Flow
The seccomp kprobe reads the syscall number from the first argument and tail-calls into `progs[sc_nr]`. If no target exists, it optionally prints a message for get/set uid/pid/gid syscalls. The read/write targets read `struct seccomp_data` from the second argument and print selected calls based on buffer size.

## State And Persistence
Persistent state is the prog-array map populated by userspace after object load. There are no data maps.

## Dependencies And Integration Points
It depends on seccomp being active, kprobe access to `__seccomp_filter`, syscall number definitions from `syscall_nrs.h`, CO-RE reads, and the userspace companion that installs a permissive seccomp filter and populates the prog array.

## Risks And Edge Cases
Kernel internal seccomp symbols and arguments are unstable. Tail-call map sizing is architecture-specific, with a larger value for MIPS. If the prog array is not populated, only fallback prints occur.

## Test Signals
After userspace populates the map and runs `dd`, trace output should include selected read/write or mmap messages from tail-called programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex5.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex5_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex5_user.c

## Purpose
`tracex5_user.c` loads the tail-call seccomp tracing sample, populates the program array with syscall-specific programs, enables a permissive seccomp filter, generates I/O, and reads trace output.

## Important APIs, Types, And Functions
Key functions are `install_accept_all_seccomp()` and `main()`. It uses classic BPF seccomp filter structures, `prctl(PR_SET_SECCOMP)`, libbpf object/program APIs, `bpf_map_update_elem()`, `bpf_program__section_name()`, `bpf_program__fd()`, `popen()`, and `read_trace_pipe()`.

## Control Flow
The program loads `<argv[0]>.bpf.o`, attaches `bpf_prog1`, finds the `progs` prog-array map, iterates all programs, parses syscall numbers from sections named `kprobe/<number>`, inserts program fds into the map, installs an allow-all seccomp filter, runs `dd`, and streams trace output.

## State And Persistence
The prog array persists while the object is loaded and maps syscall numbers to tail-call targets. The process also enters seccomp mode for the remainder of execution.

## Dependencies And Integration Points
It depends on libbpf, seccomp, the companion BPF object, `dd`, and tracefs. It integrates classic seccomp activation with eBPF kprobe observation of the seccomp path.

## Risks And Edge Cases
Once seccomp is installed it cannot be undone. Section parsing assumes numeric section names for tail-call targets. The trace read is long-running and `popen()` is not closed explicitly.

## Test Signals
Expected behavior is trace output from read/write tail-call programs after the `dd` workload, with no failures populating the prog array.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex5_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex6.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex6.bpf.c

## Purpose
`tracex6.bpf.c` demonstrates reading perf event counters from BPF through both `bpf_perf_event_read()` and `bpf_perf_event_read_value()`.

## Important APIs, Types, And Functions
Maps are `counters` (`BPF_MAP_TYPE_PERF_EVENT_ARRAY`), `values` (hash of counter values), and `values2` (hash of `struct bpf_perf_event_value`). Programs are `bpf_prog1()` on `kprobe/htab_map_get_next_key` and `bpf_prog2()` on `kprobe/bpf_map_copy_value`.

## Control Flow
`bpf_prog1()` reads the current CPU's perf event counter from `counters` and stores it in `values`, ignoring common error ranges. `bpf_prog2()` filters to hash maps by CO-RE-reading `map_type`, reads the full counter/enabled/running value, and stores it in `values2`.

## State And Persistence
Perf event fds are supplied by userspace through `counters`. Read values persist in `values` and `values2` until userspace deletes them.

## Dependencies And Integration Points
It depends on kprobe attachment to BPF map functions, perf event arrays, CO-RE map type reads, and the userspace test that binds events per CPU and triggers map operations.

## Risks And Edge Cases
Probing BPF map internals is sensitive to instrumentation recursion; the sample comments avoid `*_map_lookup_elem` and probe `bpf_map_copy_value` instead. Counter availability depends on CPU/VM support. Error values from `bpf_perf_event_read()` need filtering.

## Test Signals
The companion should populate `values` and `values2` for each CPU with non-missing counter data and print counter/enabled/running values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex6.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex6_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex6_user.c

## Purpose
`tracex6_user.c` tests BPF perf-event-array reads by opening perf counters on each CPU, inserting them into a BPF map, triggering the companion kprobes, and checking stored counter values.

## Important APIs, Types, And Functions
Important functions are `check_on_cpu()`, `test_perf_event_array()`, `test_bpf_perf_event()`, and `main()`. It uses `sys_perf_event_open()`, `sched_setaffinity()`, `bpf_map_update_elem()`, `ioctl(PERF_EVENT_IOC_ENABLE/DISABLE)`, `bpf_map_get_next_key()`, `bpf_map_lookup_elem()`, fork/wait, and libbpf attach APIs.

## Control Flow
`main()` loads and attaches all BPF programs, resolves three maps, and calls `test_bpf_perf_event()`. Each test forks one child per configured CPU. The child pins itself to the CPU, opens a perf event for that CPU, writes the fd to the perf event array, triggers kprobes through map operations, verifies both result maps, cleans up map entries and fd, and exits with status.

## State And Persistence
State includes per-child perf event fds, perf event array entries, result map entries, CPU affinity, and libbpf links. Entries are removed after each child check.

## Dependencies And Integration Points
It depends on perf event permissions and hardware support for cycles, software clock, raw instruction-retired, L1D load, LLC miss, and MSR TSC events. Some tests may fail in QEMU as noted.

## Risks And Edge Cases
The program forks based on `_SC_NPROCESSORS_CONF`, including offline CPUs where perf open or affinity can fail. It uses many `assert()` calls, causing abrupt abort on errors. Raw and dynamic PMU type constants are platform-specific.

## Test Signals
For each event type and CPU, output should show `CPU N: <counter>` and `CPU N: counter: ..., enabled: ..., running: ...`; a nonzero child status reports test failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex6_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta.sh

## Purpose
`xdp2skb_meta.sh` is a wrapper that attaches a pair of cooperating XDP and tc BPF programs used to transfer metadata from XDP `data_meta` to `skb->mark`.

## Important APIs, Types, And Functions
Shell helpers include `usage()`, `err()`, `info()`, `_call_cmd()`, `call_tc()`, `call_tc_allow_fail()`, `call_ip()`, `list_tc()`, `list_xdp()`, `flush_tc()`, `flush_xdp()`, `attach_tc_mark()`, and `attach_xdp_mark()`. It uses `getopt`, `tc`, and `ip`.

## Control Flow
The script parses `--dev`, `--flush`, `--list`, `--dry-run`, and verbosity flags, checks for `xdp2skb_meta_kern.o`, and requires a device. Flush mode removes tc and XDP programs. List mode displays current tc/XDP state. Default mode attaches `tc_mark` to ingress clsact and `xdp_mark` to the device.

## State And Persistence
State is kernel attachment state on the selected network device: tc clsact/filter and XDP link. No maps are managed by the script.

## Dependencies And Integration Points
It depends on iproute2, root privileges, the companion BPF object, XDP-capable device support, and tc clsact. It integrates two hook points that share metadata through packet metadata rather than maps.

## Risks And Edge Cases
The script deletes existing clsact qdisc and XDP programs on the device when attaching. Dry-run avoids changes but still requires argument parsing. Drivers without XDP metadata support cause the XDP program to abort packets.

## Test Signals
`--list` should show attached tc and XDP programs; packet tests with iptables marks should distinguish mark `42` when XDP metadata is present and `41` when absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta_kern.c

## Purpose
`xdp2skb_meta_kern.c` demonstrates passing metadata from an XDP program to a tc ingress program using `xdp_md->data_meta`, then copying that value to `skb->mark`.

## Important APIs, Types, And Functions
`struct meta_info` contains a 32-bit mark. Programs are `_xdp_mark()` in section `xdp_mark` and `_tc_mark()` in section `tc_mark`. It uses `bpf_xdp_adjust_meta()` and writable `ctx->mark` on `struct __sk_buff`.

## Control Flow
The XDP program reserves metadata space before packet data, reloads invalidated packet pointers, bounds-checks the metadata area, writes mark `42`, and passes the packet. The tc program checks whether metadata exists; if not, it sets mark `41`, otherwise it copies `meta->mark` to `skb->mark`.

## State And Persistence
There are no maps. Metadata exists only while the packet moves from XDP to skb/tc processing; mark persists on the skb after tc.

## Dependencies And Integration Points
It depends on driver support for XDP metadata, XDP_PASS handoff to skb, tc ingress attachment, and the shell wrapper that loads both sections.

## Risks And Edge Cases
Helpers that change packet data invalidate pointers, so the program reloads `ctx->data` after adjustment. Drivers lacking metadata support return an error and the sample returns `XDP_ABORTED`. Metadata layout is private to these two programs.

## Test Signals
Packets traversing both hooks should have skb mark `42`; packets without metadata should receive mark `41`. XDP exception tracepoints can reveal `XDP_ABORTED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_kern.c

## Purpose
`xdp_adjust_tail_kern.c` demonstrates `bpf_xdp_adjust_tail()` and `bpf_xdp_adjust_head()` by turning oversized IPv4 packets into ICMP "fragmentation needed" responses sent with `XDP_TX`.

## Important APIs, Types, And Functions
The `icmpcnt` array map counts generated ICMP packets. Helpers include `count_icmp()`, `swap_mac()`, `csum_fold_helper()`, `ipv4_csum()`, `send_icmp4_too_big()`, and `handle_ipv4()`. Entry point `_xdp_icmp()` is in section `xdp_icmp`.

## Control Flow
The XDP program parses Ethernet, handles IPv4 packets, and if packet size exceeds the configured maximum and ICMP response size, trims the tail to preserve the quoted payload, grows the head for a new IP+ICMP header, swaps MAC/IP addresses, fills ICMP frag-needed fields and checksums, increments `icmpcnt`, and transmits back out the ingress device.

## State And Persistence
`icmpcnt` persists generated response count. `max_pcktsz` is a global data variable that userspace can update through the `.data` map before attach.

## Dependencies And Integration Points
It depends on XDP helper support for head/tail adjustment, IPv4/ICMP header layout, and the userspace loader that sets max packet size and polls `icmpcnt`.

## Risks And Edge Cases
Only simple IPv4 Ethernet packets are handled; VLAN, IPv6, fragments, and IP options are not covered. Incorrect size constants can corrupt response construction. `XDP_DROP` is used for malformed or failed adjustment paths.

## Test Signals
Oversized IPv4 ingress packets should cause ICMP packet-too-big responses and increment `icmpcnt`; smaller packets should pass unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_user.c

## Purpose
`xdp_adjust_tail_user.c` loads and attaches the XDP ICMP packet-too-big sample, optionally updates its maximum packet size, and polls the ICMP response counter.

## Important APIs, Types, And Functions
Important functions are `int_exit()`, `poll_stats()`, `usage()`, and `main()`. It uses `bpf_object__open_file()`, `bpf_program__set_type()`, `bpf_object__load()`, `bpf_object__find_map_fd_by_name()`, `bpf_map_update_elem()`, `bpf_xdp_attach()`, `bpf_xdp_query_id()`, `bpf_xdp_detach()`, and `bpf_prog_get_info_by_fd()`.

## Control Flow
The program parses interface, timeout, packet size, skb/native/force flags, loads `<argv[0]>_kern.o`, sets the program type to XDP, optionally updates the `.data` map variable `max_pcktsz`, resolves `icmpcnt`, installs signal handlers, attaches XDP, records the program id, and polls `icmpcnt` every two seconds until timeout or signal.

## State And Persistence
State includes the attached XDP program, its program id, the `icmpcnt` map, and optional `.data` global value. Signal cleanup detaches only if the current program id still matches the one it attached.

## Dependencies And Integration Points
It depends on libbpf, XDP attach support on the selected interface, optional driver/native mode, and the companion kernel object.

## Risks And Edge Cases
The `.data` map name `xdp_adju.data` is object-name dependent and can change with build naming. If another program replaces the XDP program, cleanup intentionally does not detach it. Missing interface or mode support fails attach.

## Test Signals
Successful attach prints periodic `icmp "packet too big" sent` counts. Signal exit should remove the program if it is still the attached id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_kern.c

## Purpose
`xdp_fwd_kern.c` implements an XDP forwarding sample using `bpf_fib_lookup()` and a devmap of allowed egress ports.

## Important APIs, Types, And Functions
The `xdp_tx_ports` `BPF_MAP_TYPE_DEVMAP` map stores egress ifindexes. Helpers are `ip_decrease_ttl()` and `xdp_fwd_flags()`. Entry programs are `xdp_fwd_prog()` and `xdp_fwd_direct_prog()`.

## Control Flow
The program parses Ethernet, IPv4, and IPv6 headers, skips packets with TTL/hop-limit <= 1, fills `struct bpf_fib_lookup`, and calls `bpf_fib_lookup()` with normal or direct flags. On success, it verifies the returned egress ifindex is present in the devmap, decrements TTL/hop-limit, rewrites Ethernet source/destination MACs from FIB results, and redirects through the devmap. Other cases pass or drop malformed packets.

## State And Persistence
Persistent state is the devmap populated by userspace with interfaces eligible for XDP transmit. Packet header updates are transient.

## Dependencies And Integration Points
It depends on XDP, devmap lookup and redirect, kernel FIB/neighbour tables, forwarding sysctls, and the userspace loader.

## Risks And Edge Cases
Packets are passed to the stack when neighbor resolution is missing, forwarding disabled, or egress is not configured. VLAN parsing is not included. Direct lookup skips fib rules. Not all egress devices support XDP xmit, causing drops after redirect.

## Test Signals
Valid routed IPv4/IPv6 packets should be redirected with updated MACs and decremented TTL/hop-limit when the egress ifindex is in `xdp_tx_ports`; missing neighbours should show `XDP_PASS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_user.c

## Purpose
`xdp_fwd_user.c` loads, attaches, detaches, and configures the XDP forwarding sample across one or more interfaces.

## Important APIs, Types, And Functions
Key functions are `do_attach()`, `do_detach()`, `usage()`, and `main()`. It uses `bpf_xdp_attach()`, `bpf_xdp_query_id()`, `bpf_prog_get_fd_by_id()`, `bpf_prog_get_info_by_fd()`, `bpf_xdp_detach()`, `bpf_map_update_elem()`, and libbpf object/program/map APIs.

## Control Flow
The program parses detach, skb, force, and direct flags. In attach mode, it loads `<argv[0]>_kern.o`, selects `xdp_fwd` or `xdp_fwd_direct`, finds `xdp_tx_ports`, attaches the program to each interface, and writes each ifindex into the devmap. In detach mode, it checks the currently attached program name matches the expected app program before detaching with `old_prog_fd`.

## State And Persistence
Attach mode leaves XDP programs attached and devmap entries populated until detached or process exit tears down non-pinned maps. Detach mode only removes matching attached programs; map cleanup is noted as TODO.

## Dependencies And Integration Points
It depends on libbpf, XDP driver or skb mode, devmap lookup support in the kernel verifier, and interface names/ifindexes. It integrates with kernel FIB and the companion XDP program.

## Risks And Edge Cases
Program name checks derive from the selected section name plus `_prog`, so naming drift breaks detach. The object is not kept open after process exit unless map/program lifetimes are held by attachment, so map persistence depends on kernel link ownership. Generic mode lacks some devmap xmit stats.

## Test Signals
Attach should succeed for each interface and populate `xdp_tx_ports`; forwarding traffic should traverse XDP. Detach should refuse to remove unrelated XDP programs and remove matching ones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4.bpf.c

## Purpose
`xdp_router_ipv4.bpf.c` is an XDP IPv4 router sample. It combines exact-route, LPM route, ARP, devmap, and shared sample statistics maps to redirect IPv4 packets at XDP.

## Important APIs, Types, And Functions
Maps include `lpm_map`, `arp_table`, `exact_match`, and `tx_port`, plus shared `rx_cnt` from `xdp_sample.bpf.h`. `xdp_router_ipv4_prog()` handles packet parsing and redirect. Structures include `trie_value`, `union key_4`, `arp_entry`, and `direct_map`.

## Control Flow
The program increments receive stats, parses Ethernet and optional VLAN headers, passes ARP, and handles IPv4. It first checks `exact_match` for destination IP and cached MAC data. If absent, it builds a 32-bit LPM key, looks up the route prefix, finds the destination MAC by destination or gateway in `arp_table`, and passes to the stack if gateway ARP discovery is needed. With source and destination MACs resolved, it rewrites Ethernet addresses and redirects through `tx_port`.

## State And Persistence
Routing state persists in BPF maps populated by userspace from netlink route and neighbour tables. Statistics persist in shared sample maps until userspace collects them.

## Dependencies And Integration Points
It depends on XDP, BPF LPM trie maps, hash maps, devmap redirect, shared XDP sample stats infrastructure, and `xdp_router_ipv4_user.c`.

## Risks And Edge Cases
Only ARP and IPv4 are explicitly handled; other traffic drops by default after parsing. The LPM key builds bytes from network-order destination fields and must match userspace population. Missing ARP for a gateway passes packets to the kernel, while missing route drops them.

## Test Signals
Route/ARP maps populated from userspace should produce `XDP_REDIRECT` and increment redirect stats. Missing ARP should increment pass stats; malformed or unroutable packets should increment drop stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4_user.c

## Purpose
`xdp_router_ipv4_user.c` is the control plane and stats UI for the XDP IPv4 router sample. It loads the BPF skeleton, attaches XDP programs, mirrors kernel route and ARP state into BPF maps via netlink, and runs the shared XDP sample statistics loop.

## Important APIs, Types, And Functions
Important routines are `recv_msg()`, `read_route()`, `get_route_table()`, `read_arp()`, `get_arp_table()`, `monitor_routes_thread()`, `usage()`, and `main()`. It uses netlink route/neighbour messages, `bpf_map_update_elem()`, `bpf_map_delete_elem()`, `sample_init_pre_load()`, `sample_init()`, `sample_install_xdp()`, `sample_run()`, and skeleton APIs from `xdp_router_ipv4.skel.h`.

## Control Flow
Startup opens and loads the skeleton, initializes shared stats maps and tracepoint attachments, parses options, resolves router maps, attaches XDP to each interface, starts a route-monitor thread, and runs the stats loop. The monitor thread dumps initial ARP and route tables, subscribes to route and neighbour multicast groups, and updates `lpm_map`, `exact_match`, `arp_table`, and `tx_port` as messages arrive.

## State And Persistence
Userspace maintains map fds, route-monitor thread state, interval, and sample stats state. BPF maps hold mirrored route, exact host, ARP, and devmap state. XDP programs remain attached until `sample_exit()` cleanup.

## Dependencies And Integration Points
It depends on libbpf skeleton generation, pthreads, netlink route/neighbour APIs, shared XDP sample helpers, interface MAC lookup, and kernel XDP support. It integrates host routing state with fast-path BPF forwarding.

## Risks And Edge Cases
Route parsing uses string buffers and `atoi()` on binary addresses, making formatting fragile. Option parsing adjusts `ifname_list` manually and can be error-prone. Route deletion triggers a full route-table reread for same-prefix replacement. Netlink polling intervals can delay updates.

## Test Signals
Successful runs attach to all named interfaces, populate maps from existing routes/ARP, print XDP sample stats, and update forwarding behavior after route or neighbour changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.c

## Purpose
`xdp_sample.bpf.c` provides reusable tracing-side statistics programs for XDP samples. It collects redirect errors, cpumap enqueue/kthread stats, exceptions, and devmap transmit stats into shared maps consumed by userspace.

## Important APIs, Types, And Functions
Maps include `rx_cnt`, `redir_err_cnt`, `cpumap_enqueue_cnt`, `cpumap_kthread_cnt`, `exception_cnt`, `devmap_xmit_cnt`, and `devmap_xmit_cnt_multi`. Programs attach to tp_btf tracepoints such as `xdp_redirect_err`, `xdp_redirect_map_err`, `xdp_redirect`, `xdp_redirect_map`, `xdp_cpumap_enqueue`, `xdp_cpumap_kthread`, `xdp_exception`, and `xdp_devmap_xmit`.

## Control Flow
Tracepoint programs filter by configured `from_match`, `to_match`, or `cpumap_map_id`, compute a per-CPU or pair key, look up the appropriate stats record, and update processed/drop/issue/info counters with no-tear macros. Redirect errors are normalized into errno buckets.

## State And Persistence
Persistent state is all in BPF maps and read-only globals (`nr_cpus`, match arrays) configured before load. Counters accumulate until userspace reads, diffs, or clears them.

## Dependencies And Integration Points
It depends on BTF tracepoint attachment, shared `struct datarec`, and userspace helper setup in `xdp_sample_user.c`/`.h`. It is linked into higher-level samples such as the IPv4 router.

## Risks And Edge Cases
Map sizing is tied to CPU count and expected action/error dimensions; userspace must size maps before load. Duplicate `tp_btf/xdp_devmap_xmit` sections collect aggregate and pairwise stats from the same tracepoint. Filtering arrays treat empty sets as match-all.

## Test Signals
Under XDP redirect/cpumap/devmap activity, corresponding maps should show increasing processed, dropped, issue, and info counters. Userspace summary output should reflect these deltas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.h -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.h

## Purpose
`xdp_sample.bpf.h` is the BPF-side shared header for XDP samples. It declares common map types, global externs, MAC-swap helper, no-tear counter macros, and small errno/action constants used by tracepoint stats programs.

## Important APIs, Types, And Functions
It defines `array_map`, extern `rx_cnt` and `nr_cpus`, `XDP_REDIRECT_SUCCESS`, `XDP_REDIRECT_ERROR`, `swap_src_dst_mac()`, alias-safe `READ_ONCE()`/`WRITE_ONCE()`, `NO_TEAR_ADD()`, `NO_TEAR_INC()`, and `ARRAY_SIZE()`.

## Control Flow
The header has no standalone control flow. Including BPF programs use the macros and inline helpers to update shared counters and manipulate Ethernet addresses.

## State And Persistence
It declares map/global contracts but owns no runtime state. Included map declarations are backed by concrete BPF objects.

## Dependencies And Integration Points
It depends on `vmlinux.h`, BPF helper/tracing headers, `net_shared.h`, and `xdp_sample_shared.h`. It is included by XDP sample BPF programs and must match userspace map setup.

## Risks And Edge Cases
The no-tear macros are relaxed read/write increments and are suitable only where write concurrency is controlled or acceptable. Header-defined errno constants must stay aligned with kernel values. Broad includes can conflict with other BPF compilation environments.

## Test Signals
Compile coverage of all XDP samples and correct userspace interpretation of `struct datarec` counters are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_shared.h -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_shared.h

## Purpose
`xdp_sample_shared.h` defines the shared counter record layout used by both BPF-side XDP sample programs and userspace statistics readers.

## Important APIs, Types, And Functions
It defines `struct datarec` with `processed`, `dropped`, `issue`, a union of `xdp_pass`/`info`, `xdp_drop`, and `xdp_redirect`, aligned to 64 bytes.

## Control Flow
There is no executable control flow.

## State And Persistence
Instances of `struct datarec` persist in BPF maps and in userspace snapshots. The 64-byte alignment reduces false sharing for per-CPU or mmaped counters.

## Dependencies And Integration Points
The header is included by BPF programs and userspace utilities, forming the ABI for sample statistic maps.

## Risks And Edge Cases
Changing field order, sizes, or alignment would break map value compatibility between BPF and userspace. `size_t` width must be consistent for the target userspace/BPF ABI.

## Test Signals
Correct stats output from `xdp_sample_user.c` consumers verifies that map values are read with the expected layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.c

## Purpose
`xdp_sample_user.c` is the shared userspace statistics and lifecycle library for XDP samples. It sets up counter maps, collects per-CPU and pairwise records, computes rates, prints summaries, installs/removes XDP programs, handles signals, and provides utility helpers for driver and MAC lookup.

## Important APIs, Types, And Functions
Public APIs include `sample_setup_maps()`, `__sample_init()`, `sample_install_xdp()`, `sample_exit()`, `sample_run()`, `sample_switch_mode()`, `sample_usage()`, `get_driver_name()`, and `get_mac_addr()`. Internal flows include map collection helpers, stats calculations, `sample_timer_cb()`, and `sample_signal_cb()`.

## Control Flow
Initialization records requested stat masks, possible CPU count, signal fd, and map metadata. `sample_setup_maps()` sizes mmapable maps according to stat dimensions. `sample_run()` creates a timerfd, allocates current/previous snapshots, collects initial stats, then polls signal and timer fds. On each timer, it swaps snapshots, collects maps, computes rates, updates summaries, and prints terse or verbose output. `sample_exit()` removes installed XDP programs and prints a final summary.

## State And Persistence
Global state tracks sample maps, mmap pointers, map entry counts, installed XDP program descriptors, log level, interval, signal fd, output totals, CPU count, and requested mask. Kernel state includes attached XDP programs and BPF stats maps.

## Dependencies And Integration Points
It depends on libbpf, BPF mmapable maps, timerfd/signalfd, poll, ethtool/ioctl, locale formatting, Linux hlist/hash utilities, and `xdp_sample_user.h`. It is used by sample skeleton-based tools such as `xdp_router_ipv4_user.c`.

## Risks And Edge Cases
The code is a shared support layer with many global variables, so consumers must call setup in the expected order. Map dimensions must match BPF-side `nr_cpus` and stat masks. Signal handling toggles output mode at runtime. Driver and MAC lookup rely on ioctl support and interface stability.

## Test Signals
Sample consumers should show correct per-second rates, expanded error details on failures, mode switching with SIGQUIT, cleanup of attached XDP programs on exit, and final summary totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.h -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.h

## Purpose
`xdp_sample_user.h` declares the userspace API, stat masks, exit codes, skeleton integration macros, and utility helpers for XDP sample applications.

## Important APIs, Types, And Functions
It defines `enum stats_mask`, `EXIT_*` codes, prototypes for sample setup/run/exit/install helpers, `get_driver_name()`, `get_mac_addr()`, `safe_strncpy()`, `__attach_tp()`, `sample_init_pre_load()`, and `DEFINE_SAMPLE_INIT()`.

## Control Flow
Macros drive skeleton consumers: `sample_init_pre_load()` sets `nr_cpus` and configures map sizes before load; `DEFINE_SAMPLE_INIT()` attaches selected tracepoint programs after load based on the stat mask.

## State And Persistence
The header owns no state but defines the contract for shared globals and skeleton maps/links used by `xdp_sample_user.c` and generated skeletons.

## Dependencies And Integration Points
It depends on libbpf skeleton conventions and `xdp_sample_shared.h`. Consumers must have maps and programs with the expected names.

## Risks And Edge Cases
Macro-based skeleton integration fails at compile time or runtime if generated skeleton names differ. `__attach_tp()` returns `-EINVAL` when the program type is not tracing, so consumers must configure sections correctly.

## Test Signals
Successful skeleton samples call `sample_init_pre_load()`, load, then `sample_init()` without error and show attached tracepoint links for requested stat masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_common.h -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_common.h

## Purpose
`xdp_tx_iptunnel_common.h` defines shared key/value structures for the XDP IP-in-IP tunnel transmit sample.

## Important APIs, Types, And Functions
It defines `MAX_IPTNL_ENTRIES`, `struct vip` for matching service destination address/port/family/protocol, and `struct iptnl_info` for tunnel source/destination addresses, family, and destination MAC.

## Control Flow
There is no executable control flow.

## State And Persistence
Instances of `struct vip` and `struct iptnl_info` persist as keys and values in the `vip2tnl` BPF map populated by userspace and read by the XDP program.

## Dependencies And Integration Points
The header is included by both kernel and userspace halves, making it the ABI for tunnel map population and lookup.

## Risks And Edge Cases
Any layout or byte-order mismatch between userspace population and BPF lookup breaks encapsulation selection. The maximum entries constant limits accepted port-range size.

## Test Signals
Successful map lookups in the XDP program for user-configured VIP/port/protocol entries validate the shared layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_kern.c

## Purpose
`xdp_tx_iptunnel_kern.c` demonstrates using `bpf_xdp_adjust_head()` to encapsulate selected IPv4 or IPv6 packets in a new outer IP header and transmit them back with `XDP_TX`.

## Important APIs, Types, And Functions
Maps are `rxcnt` per-protocol counters and `vip2tnl` hash from `struct vip` to `struct iptnl_info`. Helpers include `count_tx()`, `get_dport()`, `set_ethhdr()`, `handle_ipv4()`, and `handle_ipv6()`. Entry point `_xdp_tx_iptunnel()` is in section `xdp.frags`.

## Control Flow
The entry parses Ethernet and dispatches IPv4 or IPv6. Each handler reads the transport destination port for TCP/UDP, builds a VIP key from destination/protocol/family/port, looks up tunnel info, and passes unmatched traffic. On match, it grows packet head by an IPv4 or IPv6 header, rewrites Ethernet addresses, fills outer tunnel header fields, increments protocol counters, and returns `XDP_TX`.

## State And Persistence
`vip2tnl` holds configured encapsulation policies; `rxcnt` accumulates per-protocol transmitted packet counts. Packet modifications are transient.

## Dependencies And Integration Points
It depends on XDP head adjustment, XDP fragments section support, IP header definitions, and the userspace loader that populates `vip2tnl`.

## Risks And Edge Cases
It only performs v4-in-v4 and v6-in-v6, not cross-family tunneling. Header construction assumes enough headroom after adjustment and simple TCP/UDP/other transport parsing. Outer IPv4 checksum is manually computed and must remain correct.

## Test Signals
Packets matching configured VIP entries should be encapsulated and counted under their protocol in `rxcnt`; unmatched traffic should pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_user.c

## Purpose
`xdp_tx_iptunnel_user.c` loads the XDP tunnel transmit sample, populates VIP-to-tunnel mappings from command-line arguments, attaches the XDP program, and prints per-protocol encapsulation rates.

## Important APIs, Types, And Functions
Key routines are `int_exit()`, `poll_stats()`, `usage()`, `parse_ipstr()`, `parse_ports()`, and `main()`. It uses `inet_pton()`, `ether_aton_r()`, `bpf_object__open_file()`, `bpf_program__set_type()`, `bpf_object__load()`, `bpf_map_update_elem()`, `bpf_xdp_attach()`, `bpf_xdp_query_id()`, and `bpf_xdp_detach()`.

## Control Flow
The program requires interface, VIP address, port/range, tunnel source/destination, and destination MAC. It validates IP families, opens `<argv[0]>_kern.o`, loads the XDP program, resolves `rxcnt` and `vip2tnl`, inserts one map entry for each port in the range, attaches XDP, records program id, and polls per-protocol counters until timeout or signal.

## State And Persistence
State includes attached XDP program id, `vip2tnl` entries, `rxcnt` counters, and local previous-counter snapshots. Signal cleanup detaches only if the attached program id matches.

## Dependencies And Integration Points
It depends on libbpf, XDP attach support, valid interface/MAC/IP arguments, and the shared common header layout.

## Risks And Edge Cases
`parse_ports()` references `optarg` instead of its parameter internally, which is safe for current call sites but fragile. The map capacity limits port ranges to 256 entries. Family mismatch between tunnel source and destination is rejected, but VIP and tunnel family compatibility is enforced by the BPF side.

## Test Signals
After attach, matching traffic should produce periodic `proto <n>` packet/rate lines. Cleanup should remove the program unless another XDP program replaced it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/Makefile -->
# sources/distributed-fs/ceph-client/samples/cgroup/Makefile

## Purpose
The cgroup samples `Makefile` declares two userspace sample programs for cgroup event listening.

## Important APIs, Types, And Functions
It adds `cgroup_event_listener` and `memcg_event_listener` to `userprogs-always-y` and appends `-I usr/include` to `userccflags`.

## Control Flow
Kbuild consumes these variables to compile the listed userspace binaries whenever samples are built.

## State And Persistence
There is no runtime state. The persistent effect is build inclusion of the two sample tools.

## Dependencies And Integration Points
It integrates with the kernel samples Kbuild infrastructure and the userspace include staging path.

## Risks And Edge Cases
Missing the include flag can break builds against generated UAPI headers. Adding binaries here makes them always built with the cgroup samples.

## Test Signals
`make samples/cgroup/` should build both listener binaries without missing-header errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/cgroup_event_listener.c -->
# sources/distributed-fs/ceph-client/samples/cgroup/cgroup_event_listener.c

## Purpose
`cgroup_event_listener.c` is a cgroup v1 event listener sample. It registers an eventfd against a cgroup control file and event arguments through `cgroup.event_control`, then prints when the threshold/event is crossed.

## Important APIs, Types, And Functions
`main()` uses `open()`, `dirname()`, `eventfd()`, `snprintf()`, `write()` to `cgroup.event_control`, `read()` from the eventfd, and `access()` to detect cgroup removal.

## Control Flow
The program expects a control-file path and event args. It opens the control file, constructs the sibling `cgroup.event_control` path, opens it for writing, creates an eventfd, writes `<efd> <cfd> <args>` to register, then loops reading eventfd counters and printing `<control> <args>: crossed`. If the event-control file disappears, it reports cgroup removal and exits.

## State And Persistence
Kernel event registration persists while fds remain open. Process state consists of the eventfd, control fd, event_control fd, paths, and line buffer.

## Dependencies And Integration Points
It depends on cgroup v1 event-control files, eventfd support, and the specific controller event syntax passed by the user.

## Risks And Edge Cases
`dirname(argv[1])` may modify the argument buffer. The loop is infinite until cgroup removal or error. It uses `assert()` for exact eventfd read size. It does not close fds explicitly on exit.

## Test Signals
Triggering the configured cgroup threshold should wake the eventfd and print `crossed`; removing the cgroup should print `The cgroup seems to have removed.`
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/cgroup_event_listener.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/memcg_event_listener.c -->
# sources/distributed-fs/ceph-client/samples/cgroup/memcg_event_listener.c

## Purpose
`memcg_event_listener.c` is a cgroup v2 memory event listener. It reads `/sys/fs/cgroup/<cgroup>/memory.events`, stores baseline counters, watches the file with inotify, and prints counter deltas when memory events occur.

## Important APIs, Types, And Functions
Important types are `struct memcg_counters` and `struct memcg_events`. Functions include `print_memcg_counters()`, `get_memcg_counter()`, `read_memcg_events()`, `process_memcg_events()`, `monitor_events()`, `initialize_memcg_events()`, `cleanup_memcg_events()`, and `main()`.

## Control Flow
Initialization builds the memory.events path, reads baseline counters, creates an inotify fd, and watches for `IN_MODIFY`. `monitor_events()` polls forever, reads inotify events, validates watch descriptor and mask, then calls `read_memcg_events(show_diff=true)`. The reader parses expected lines in order, compares new values to old values, prints deltas, and updates stored counters.

## State And Persistence
Persistent process state is the path, inotify fd/watch descriptor, and last-seen counters. Kernel cgroup counters persist independently in cgroupfs.

## Dependencies And Integration Points
It depends on cgroup v2 `memory.events`, inotify, poll, and the exact counter names `low`, `high`, `max`, `oom`, `oom_kill`, and `oom_group_kill`.

## Risks And Edge Cases
The parser expects counters in fixed order; cgroup files are generally stable but extensions could require changes. Cleanup after `monitor_events()` is unreachable because the monitor loops forever. Counter decreases are ignored, which is appropriate for monotonic event counters.

## Test Signals
On startup it prints initialized counters. Memory pressure or OOM events should produce `Received event` followed by delta lines for increased counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/memcg_event_listener.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/Makefile -->
# sources/distributed-fs/ceph-client/samples/check-exec/Makefile

## Purpose
The check-exec `Makefile` builds the userspace `inc` interpreter and `set-exec` securebits wrapper samples.

## Important APIs, Types, And Functions
It declares `userprogs-always-y := inc set-exec`, adds `-I usr/include`, and defines `all` and `clean` phony targets that recurse into the kernel sample build.

## Control Flow
Kbuild builds the listed userspace programs. The local `all` target invokes `$(MAKE) -C ../.. samples/check-exec/`; `clean` invokes kernel clean for `M=samples/check-exec/`.

## State And Persistence
There is no runtime state. Build outputs are the `inc` and `set-exec` sample binaries.

## Dependencies And Integration Points
It integrates with kernel samples Kbuild and generated UAPI include headers.

## Risks And Edge Cases
The BSD-3-Clause sample differs from most GPL samples but only affects source licensing. Incorrect relative invocation can fail if not run from the expected samples directory.

## Test Signals
`make samples/check-exec/` should build both binaries and `make -C ../.. M=samples/check-exec/ clean` should remove generated objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/inc.c -->
# sources/distributed-fs/ceph-client/samples/check-exec/inc.c

## Purpose
`inc.c` is a tiny script interpreter used to demonstrate and test exec-check securebits. It interprets line-oriented `?` and `+` commands from a file, stdin, or `-c` command string while consulting kernel `AT_EXECVE_CHECK` policy.

## Important APIs, Types, And Functions
Important routines are `sys_execveat()`, `interpret_buffer()`, `interpret_stream()`, `print_usage()`, and `main()`. It uses `prctl(PR_GET_SECUREBITS)`, `SECBIT_EXEC_DENY_INTERACTIVE`, `SECBIT_EXEC_RESTRICT_FILE`, `execveat(AT_EMPTY_PATH | AT_EXECVE_CHECK)`, `fread()`, `strtok_r()`, and `scanf()`.

## Control Flow
`main()` reads current securebits, parses `-c`, `-i`, or script path mode, and enforces that exactly one interpretation source is used. Command-string mode is denied when interactive interpretation is denied. Stdin mode treats `/proc/self/fd/0` as the script name and restricts based on interactive policy. File mode opens the script and restricts based on file policy. `interpret_stream()` asks the kernel to check execution permission on the script fd, then reads and interprets up to 127 bytes. The interpreter increments/prints a counter for `+` and reads a new number for `?`.

## State And Persistence
Process state includes current counter value, securebit-derived booleans, script stream, and input buffer. Securebits are inherited from the launcher and are not changed here.

## Dependencies And Integration Points
It depends on new securebits and `AT_EXECVE_CHECK` kernel support, UAPI headers, and the `set-exec` wrapper. It is referenced by the scripts and selftest documentation.

## Risks And Edge Cases
Only a small fixed buffer is read from scripts, so longer scripts are truncated. Command validation only accepts single-character commands or comments. Kernels lacking the feature cause check errors only when restrictive mode requires them.

## Test Signals
Executable scripts should run under allowed policy. `-c` or stdin should be rejected when `SECBIT_EXEC_DENY_INTERACTIVE` is locked. Non-executable/restricted files should fail when `SECBIT_EXEC_RESTRICT_FILE` applies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/inc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/run-script-ask.sh -->
# sources/distributed-fs/ceph-client/samples/check-exec/run-script-ask.sh

## Purpose
`run-script-ask.sh` is a small wrapper that ensures the sample directory is on `PATH` and executes `script-ask.inc`.

## Important APIs, Types, And Functions
It uses POSIX shell, `dirname`, `PATH` modification, `set -x`, and direct execution of `${DIR}/script-ask.inc`.

## Control Flow
The script computes its directory, appends it to `PATH` so `/usr/bin/env inc` can resolve the sample interpreter, enables command tracing, and executes the ask script.

## State And Persistence
It only modifies its process environment and then replaces/executes the script command. No files are changed.

## Dependencies And Integration Points
It depends on `inc` being built and present in the same directory, `script-ask.inc` being executable, and `/usr/bin/env` resolving the interpreter through `PATH`.

## Risks And Edge Cases
Appending the directory to `PATH` can shadow later commands in this process. The script uses `dirname --`, which is supported by common coreutils but may vary on minimal shells.

## Test Signals
Running the wrapper should invoke `script-ask.inc`, prompt for a number, and print the incremented result through `inc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/run-script-ask.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-ask.inc -->
# sources/distributed-fs/ceph-client/samples/check-exec/script-ask.inc

## Purpose
`script-ask.inc` is an executable sample script for the `inc` interpreter that reads a number interactively and increments it.

## Important APIs, Types, And Functions
The shebang is `#!/usr/bin/env inc`. Interpreter commands are `?` to read a number from stdin and `+` to increment and print it.

## Control Flow
When executed, the kernel invokes `env inc`, and `inc` reads the script. The `?` command prompts for a new counter value, then `+` increments and prints it.

## State And Persistence
The only state is the interpreter's in-memory counter during script execution.

## Dependencies And Integration Points
It depends on `inc` being in `PATH` and integrates with check-exec policy around executable scripts and interactive input.

## Risks And Edge Cases
Under `SECBIT_EXEC_DENY_INTERACTIVE`, the prompt/read behavior may be denied depending on how the script is invoked. If stdin is not numeric, the interpreter warns and keeps the existing counter value.

## Test Signals
Supplying `41` should result in output `42` after the prompt when policy permits interactive reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-ask.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-exec.inc -->
# sources/distributed-fs/ceph-client/samples/check-exec/script-exec.inc

## Purpose
`script-exec.inc` is a minimal executable script for the `inc` interpreter that increments the default counter once.

## Important APIs, Types, And Functions
It uses the shebang `#!/usr/bin/env inc` and a single `+` command.

## Control Flow
Execution invokes `inc`, which starts its counter at zero, processes `+`, increments to one, and prints `1`.

## State And Persistence
State is limited to the transient interpreter counter.

## Dependencies And Integration Points
It depends on `inc` in `PATH` and is used to exercise allowed executable-file interpretation under check-exec policy.

## Risks And Edge Cases
If the file lacks execute permission or file execution is restricted, the interpreter's `AT_EXECVE_CHECK` path can reject it.

## Test Signals
Executing the script under allowed policy should print `1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-exec.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-noexec.inc -->
# sources/distributed-fs/ceph-client/samples/check-exec/script-noexec.inc

## Purpose
`script-noexec.inc` is a minimal inc script intended to represent a non-executable or restricted script case in check-exec testing.

## Important APIs, Types, And Functions
It has the same `/usr/bin/env inc` shebang and single `+` command as the executable variant.

## Control Flow
If interpreted by `inc`, it increments the default counter and prints `1`; under restrictive file-exec policy it is expected to be denied when file permissions or policy mark it as not executable.

## State And Persistence
Only the interpreter's transient counter is used.

## Dependencies And Integration Points
It depends on external file mode or test harness setup to distinguish it from `script-exec.inc`. It integrates with the kernel check-exec examples.

## Risks And Edge Cases
The source contents alone do not enforce non-executable behavior; tests must set file permissions or invoke the right policy. If made executable, it behaves like `script-exec.inc`.

## Test Signals
Allowed interpretation prints `1`; restrictive file-exec tests should reject it when permissions/policy indicate non-executable input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-noexec.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/set-exec.c -->
# sources/distributed-fs/ceph-client/samples/check-exec/set-exec.c

## Purpose
`set-exec.c` is a wrapper that sets check-exec-related securebits before executing another command. It is used to demonstrate file-execution restrictions and denial of interactive interpretation.

## Important APIs, Types, And Functions
`main()` uses `prctl(PR_GET_SECUREBITS)`, `prctl(PR_SET_SECUREBITS)`, `SECBIT_EXEC_RESTRICT_FILE`, `SECBIT_EXEC_RESTRICT_FILE_LOCKED`, `SECBIT_EXEC_DENY_INTERACTIVE`, `SECBIT_EXEC_DENY_INTERACTIVE_LOCKED`, and `execvpe()`.

## Control Flow
The program parses `-f` and/or `-i`, ORs the requested securebits and lock bits into the current mask, requires a following command, sets securebits if changed, and then executes the command with the original environment.

## State And Persistence
Securebits become persistent process credentials state and are inherited by the executed command. The wrapper process is replaced by `execvpe()` on success.

## Dependencies And Integration Points
It depends on kernel support for the check-exec securebits and generated UAPI headers. It integrates with `inc` and the sample scripts by launching them under policy.

## Risks And Edge Cases
Locked securebits cannot be undone by the child. Kernels without support return an error and the wrapper prints a hint. The wrapper requires at least one policy flag and a command.

## Test Signals
Running `set-exec -fi -- ./inc ...` should execute the command with both policies set; unsupported kernels should fail at `PR_SET_SECUREBITS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/set-exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/configfs/Makefile -->
# sources/distributed-fs/ceph-client/samples/configfs/Makefile

## Purpose
The configfs sample `Makefile` wires the configfs sample kernel module into Kbuild.

## Important APIs, Types, And Functions
It contains one object selection rule: `obj-$(CONFIG_SAMPLE_CONFIGFS) += configfs_sample.o`.

## Control Flow
When `CONFIG_SAMPLE_CONFIGFS` is enabled as built-in or module, Kbuild compiles and links `configfs_sample.o` accordingly.

## State And Persistence
There is no runtime state. Build configuration determines whether the sample module exists.

## Dependencies And Integration Points
It integrates with the kernel samples build system and the `CONFIG_SAMPLE_CONFIGFS` Kconfig symbol.

## Risks And Edge Cases
If the Kconfig symbol is unset, the sample is not built. The Makefile assumes `configfs_sample.c` exists in the same directory.

## Test Signals
Builds with `CONFIG_SAMPLE_CONFIGFS=m` should produce a `configfs_sample` module; built-in configs should include the object in the kernel image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/configfs/Makefile -->
