# Research: subset-b-006864

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp_rfc4884.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp_rfc4884.c

Purpose: Kernel selftest for ICMP RFC 4884 extension reporting through the socket error queue. It synthesizes IPv4 and IPv6 ICMP destination-unreachable packets that quote UDP datagrams with and without RFC 4884 extension blocks, then checks `ee_rfc4884.len` and `SO_EE_RFC4884_FLAG_INVALID` returned by `recvmsg(MSG_ERRQUEUE)`.

Important APIs and types: Uses `kselftest_harness` fixtures and variants, raw ICMP sockets, datagram sockets with `IP_RECVERR_RFC4884` or `IPV6_RECVERR_RFC4884`, `struct sock_extended_err`, `struct icmp_ext_hdr`, `struct icmp_extobj_hdr`, IPv4/IPv6/UDP headers, `poll`, `recvmsg`, `sendto`, `unshare(CLONE_NEWNET)`, and loopback `ioctl` setup.

Control flow: Fixture setup creates a fresh network namespace and brings `lo` up. Packet builders construct original UDP datagrams, optional RFC 4884 objects, and complete ICMPv4/v6 errors. Variants enumerate small, minimum, large, absent-extension, bad-checksum, and bad-length cases for both address families. The test opens a bound UDP socket, enables error queue options, sends a crafted raw ICMP packet to loopback, waits for `POLLERR`, and validates the single relevant control message.

State and persistence: State is local to one test namespace and one fixture variant. No persistent files are written. Constants for source/destination ports, payload bytes, and minimum quoted datagram length define expected offsets.

Dependencies and integration: Integrates Linux ICMP, IPv6, and error-queue UAPI behavior with kselftest. It requires root or capabilities for raw sockets and net namespace setup.

Risks: Hand-built packet layout, checksum math, and RFC 4884 length units are delicate. The test assumes the kernel surfaces malformed extension metadata rather than silently dropping all malformed packets. It only inspects the first matching error cmsg.

Test signals: Passing variants prove valid extensions report payload offsets only when enough original datagram bytes are present, no-extension cases report zero, and malformed extension checksum or object length sets the invalid flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp_rfc4884.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/in_netns.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/in_netns.sh

Purpose: Small helper wrapper that executes an arbitrary command in a temporary network namespace with loopback enabled. Other network selftests use it to isolate sysctl and socket state.

Important APIs and commands: Uses `mktemp -u` for a namespace suffix, `ip netns add`, `ip -netns ... link set lo up`, `ip netns exec`, a shell `trap`, and `ip netns del`.

Control flow: The script enables `set -e`, creates a unique namespace name, registers cleanup on exit, creates the namespace, brings loopback up, executes the command passed as arguments inside that namespace, and exits with the command's status.

State and persistence: The only state is the temporary netns. Cleanup deletes it on normal exit or failure. There is no file state.

Dependencies and integration: Depends on `iproute2` and privileges to create network namespaces. It is used by tests such as IPv6 flowlabel and per-socket local port range to avoid cross-test state contamination.

Risks: `mktemp -u` reserves no name, so namespace-name collision is theoretically possible. If cleanup is interrupted by severe process termination, a stale namespace can remain.

Test signals: A wrapped command should see isolated network sysctls and working loopback; the wrapper should propagate the wrapped command's exit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/in_netns.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/io_uring_zerocopy_tx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/io_uring_zerocopy_tx.c

Purpose: Transmit-side exerciser for io_uring send and send zerocopy paths over TCP or UDP. It is paired with `msg_zerocopy` by the shell harness to verify normal, zerocopy, fixed-buffer zerocopy, and mixed send modes.

Important APIs and types: Uses `mini_liburing`, `io_uring_queue_init`, `io_uring_register_buffers`, `io_uring_prep_send`, `io_uring_prep_sendzc`, `IORING_RECVSEND_FIXED_BUF`, `IORING_CQE_F_MORE`, `IORING_CQE_F_NOTIF`, sockets, `connect`, `SO_SNDBUF`, optional `UDP_CORK`, and IPv4/IPv6 sockaddr parsing.

Control flow: Option parsing selects family, destination, port, payload length, runtime, batch size, corking, and mode. `do_test` fills a page-aligned payload buffer. `do_tx` connects a socket, registers the payload as an io_uring fixed buffer, repeatedly queues `cfg_nr_reqs` sends until the runtime expires, submits, drains completions, and tracks zerocopy notification CQEs separately from send completion CQEs.

State and persistence: Global `cfg_*` variables and the static payload buffer define runtime state. No persistent state exists. CQE accounting via `compl_cqes` enforces notification balance.

Dependencies and integration: Depends on io_uring send zerocopy kernel support and the local `mini_liburing` header. The harness runs it inside veth-connected namespaces against `msg_zerocopy`.

Risks: Notification ordering and `F_MORE` semantics are subtle; mismatches cause hard failure. The test assumes fixed buffer registration succeeds and that transient send failures other than `EAGAIN` are regressions.

Test signals: Successful runs print transmit counts and complete with balanced notifications across UDP/TCP, IPv4/IPv6, and modes 1 to 3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/io_uring_zerocopy_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/io_uring_zerocopy_tx.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/io_uring_zerocopy_tx.sh

Purpose: Namespace harness for `io_uring_zerocopy_tx`, sending data between two veth-connected namespaces and a `msg_zerocopy` receiver.

Important commands and variables: Creates `NS1` and `NS2`, veth `veth0`, fixed IPv4 and IPv6 addresses, high MTU, fixed MACs, `net.core.optmem_max`, and toggles `kernel.io_uring_disabled` when needed. Runs `msg_zerocopy` as receiver and `io_uring_zerocopy_tx` as sender.

Control flow: With no arguments it recursively runs IPv4 and IPv6 UDP/TCP tests for modes 1, 2, and 3. With arguments it parses IP version and transmit mode, maps raw or packet modes to receiver modes when needed, creates namespaces and veth, configures addresses, enables io_uring if disabled, starts receiver in `NS2`, runs transmitter in `NS1`, waits, and reports `ok`.

State and persistence: Runtime state is temporary namespaces plus a saved sysctl value for `kernel.io_uring_disabled`, restored in cleanup. No durable files are written.

Dependencies and integration: Requires root, `ip`, sysctl access, built `io_uring_zerocopy_tx`, and built `msg_zerocopy`.

Risks: Cleanup assumes both namespaces exist. The global io_uring sysctl is host-wide, so restoration is important. Receiver startup uses a fixed short sleep rather than a readiness probe.

Test signals: Automated mode ending with `OK. All tests passed` confirms transmit and receive behavior across the mode matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/io_uring_zerocopy_tx.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ioam6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ioam6.sh

Purpose: End-to-end IPv6 IOAM selftest covering local IOAM configuration validation, encapsulating-node output behavior, and transit-node input behavior for preallocated trace options in inline and encap modes.

Important APIs and commands: Sources `lib.sh`; uses `setup_ns`, `cleanup_ns`, `ip ioam namespace`, `ip ioam schema`, `ip -6 route encap ioam6`, IOAM sysctls under `net.ipv6`, `ping6`, `modprobe ip6_tunnel`, and `ioam6_parser`. The `ALPHA` and `BETA` arrays are the authoritative data model shared with the parser.

Control flow: `check_kernel_compatibility` verifies route-level IOAM support and optional tunnel support. `setup` builds Alpha, Beta, and Gamma namespaces with two veth links, routing, IOAM namespaces, schemas, node IDs, interface IDs, and forwarding. `run` executes LOCAL tests with no mode, inline mode, and encap mode; then OUTPUT tests with Beta IOAM disabled; then INPUT tests after removing Alpha namespace state so Beta is the node under inspection. Each packet test changes the Alpha route, starts `ioam6_parser` in Gamma, sends one ping, and records pass/fail/skip.

State and persistence: All state is temporary netns routing, sysctls, IOAM namespace/schema tables, and optional `ip6_tunnel` module load state. Cleanup removes namespaces and unloads the module only if the test loaded it.

Dependencies and integration: Depends on root, recent kernel `CONFIG_IPV6_IOAM6_LWTUNNEL`, iproute2 IOAM support, optional `ip6_tunnel`, and the parser binary.

Risks: Shell arrays must stay synchronized with `ioam6_parser.c`. The test matrix is large and route mutations must be reset after each case. Encap cases are skipped if tunnel support cannot be loaded.

Test signals: Nonzero `nfailed` fails the test. Passing signals include accepted/rejected route encap syntax, correct trace sizes and bit support, proper overflow handling, and parser-verified packet bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ioam6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ioam6_parser.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ioam6_parser.c

Purpose: Packet-level validator for `ioam6.sh`. It listens on a packet socket, filters for the expected IPv6 Hop-by-Hop packet, and validates IOAM preallocated trace header and trace data for one named test case.

Important APIs and types: Uses `AF_PACKET`/`SOCK_DGRAM`, `SO_BINDTODEVICE`, `SO_RCVTIMEO`, Linux `struct ioam6_hdr`, `struct ioam6_trace_hdr`, `struct ipv6hdr`, `struct ipv6_hopopt_hdr`, endian helpers, and a private `struct ioam_config` mirroring Alpha and Beta shell configuration.

Control flow: `main` parses interface, test name, source, destination, trace type, trace size, namespace ID, and mode. It computes expected Hop-by-Hop length, receives packets until one matches the IPv6 source/destination and Hop-by-Hop header, validates next-header, padding, IOAM option type and size, optional trailing padding, then dispatches `check_ioam_trace`. `str2id` maps shell test names to enums. `check_header` encodes expected overflow, node length, and remaining length for every case. `check_data` walks the trace fields in bit order and validates IDs, timestamps/non-default fields, namespace data, wide data, and schema data padding.

State and persistence: No persistent state. Static node configs are the expected values; all packet data is stack-local.

Dependencies and integration: Tightly coupled to `ioam6.sh`, Linux IOAM UAPI definitions, and exact IOAM option wire format.

Risks: The explicit name-to-enum table and expected-header switch are large and must be updated with any shell test change. Padding checks and trace pointer arithmetic are sensitive to UAPI layout changes.

Test signals: Exit status zero means the observed packet matches the selected IOAM case exactly; nonzero means missing packet, malformed headers, or wrong trace data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ioam6_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip6_gre_headroom.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip6_gre_headroom.sh

Purpose: Regression smoke test that verifies the first packet mirrored through IPv6 GRE-like devices has enough headroom and does not trigger a kernel panic.

Important commands: Creates veth pairs, a VRF, IPv4 and IPv6 addresses, `tc clsact` ingress mirroring, `ip6erspan` and `ip6gretap` devices, and uses `ping` to generate traffic.

Control flow: `setup_prepare` builds local devices, addresses, VRF attachment, traffic-control ingress hook, and two tunnel devices. `test_headroom` attaches a `matchall` ingress filter on `swp1` that mirrors packets to the selected tunnel, sends one ping through `h1`, removes the filter, and prints pass if the system survives. Cleanup deletes tunnel, veth, and VRF devices.

State and persistence: Temporary devices in the current network namespace. Cleanup removes them. No files are written.

Dependencies and integration: Requires root, `ip`, `tc`, `ip6erspan` and `ip6gretap` support, and packet mirroring action support.

Risks: The pass criterion is absence of panic, not packet delivery validation. Device names are fixed and can conflict with existing interfaces if run outside an isolated environment.

Test signals: Printed PASS lines for `ip6gretap headroom` and `ip6erspan headroom`; a kernel crash or command failure indicates regression or missing support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip6_gre_headroom.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip6_tunnel.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip6_tunnel.sh

Purpose: Simple IPv4-over-IPv6 and IPv6-over-IPv6 tunnel connectivity test using `ip6tnl` devices across two namespaces.

Important commands: Sources `lib.sh`, uses `setup_ns`, `cleanup_all_ns`, veth links, IPv6 transport addresses, `ip link add ... type ip6tnl mode ipip6`, `mode ip6ip6`, point-to-point IPv4 tunnel addresses, IPv6 tunnel addresses, and `ping`.

Control flow: `setup_prepare` creates a veth transport, moves endpoints into `ns1` and `ns2`, assigns two IPv6 transport address pairs, creates an IPv4 tunnel and IPv6 tunnel on each side with opposite local/remote addresses, assigns inner addresses, and brings tunnels up. The script then pings the peer IPv4 tunnel endpoint and the peer IPv6 tunnel endpoint from `ns1`.

State and persistence: Temporary namespaces and an initial transport link are removed by cleanup. No persistent state.

Dependencies and integration: Requires root, `lib.sh`, iproute2, `ip6tnl` kernel support, and ping.

Risks: Uses fixed namespace variable names from `lib.sh` and fixed addresses; failures do not distinguish tunnel creation from forwarding problems because `set -e` exits early.

Test signals: Both pings must complete within one second; any command failure fails the script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip6_tunnel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_defrag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_defrag.c

Purpose: Raw-packet generator and receiver for IPv4 and IPv6 fragment reassembly testing, including reordered fragments, duplicate fragments, run patterns, and overlap rejection behavior.

Important APIs and types: Uses raw `IPPROTO_RAW` sockets, UDP sockets, IPv4/IPv6/fragment/UDP headers, custom IPv4 and IPv6 UDP checksum generation, `SO_RCVTIMEO`, `sendto`, `recv`, randomized payload sizes, and options `-4`, `-6`, `-o`, `-p`, `-v`.

Control flow: `main` seeds randomness and runs IPv4 and/or IPv6. `run_test` opens raw transmit and UDP receive sockets, fills a known payload, iterates payload sizes, and either tests many fragment lengths for normal reassembly or one randomized overlap case per payload. `send_udp_frags` initializes headers, chooses in-order, IPv4 run, or odd-then-even ordering, optionally injects a hard-coded or random overlapping fragment, and sends fragments through `send_fragment`. `recv_validate_udp` expects correct payload for normal cases and timeout or optional permissive success for overlap cases.

State and persistence: Global buffers hold the UDP payload and current IP frame. Counters and random seed are process-local and printed for reproducibility. No durable state.

Dependencies and integration: The shell harness configures fragment thresholds/timeouts and netfilter paths. Root is required for raw sockets.

Risks: Randomized paths can expose rare failures but also need the printed seed for reproduction. Overlap behavior differs when netfilter drops invalid packets, hence permissive mode.

Test signals: `PASS` on stderr after each address-family run; failures indicate wrong reassembly, unexpected overlap acceptance, checksum issues, or socket errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_defrag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_defrag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_defrag.sh

Purpose: Harness for `ip_defrag`, configuring a dedicated namespace to exercise IPv4, IPv6, overlap, and IPv6 netfilter conntrack fragment reassembly paths.

Important commands: Uses `modprobe nf_defrag_ipv6`, temporary network namespace, loopback setup, IPv4 and IPv6 fragment sysctls, netfilter conntrack fragment sysctls, IPv6 route cache sizing, `ip6tables`, and `./ip_defrag`.

Control flow: Setup creates a namespace, enables loopback, raises fragment high/low thresholds, reduces fragment timeouts to one second, raises IPv6 route cache size, and then runs `ip_defrag -4`, `-4o`, `-6`, and `-6o`. It adds an IPv6 conntrack rule to force `nf_conntrack_reasm.c` coverage, then reruns IPv6 normal and overlap tests, using permissive overlap mode for conntrack.

State and persistence: Temporary netns and in-namespace sysctls/rules. Cleanup deletes the namespace on exit.

Dependencies and integration: Requires root, `ip`, `ip6tables`, `nf_defrag_ipv6`, and compiled `ip_defrag`.

Risks: If conntrack tools or modules are unavailable the script fails rather than gracefully skipping. Cleanup assumes namespace creation succeeded.

Test signals: Each phase prints its name; final `all tests done` means all `ip_defrag` invocations passed under `set -e`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_defrag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_local_port_range.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_local_port_range.c

Purpose: kselftest coverage for the per-socket `IP_LOCAL_PORT_RANGE` option across IPv4, IPv6, TCP, UDP, SCTP, and MPTCP variants.

Important APIs and types: Uses `kselftest_harness`, `setsockopt`/`getsockopt` with `SOL_IP` and `IP_LOCAL_PORT_RANGE`, `IP_BIND_ADDRESS_NO_PORT`, `SO_DOMAIN`, loopback binds, `getsockname`, packed 32-bit low/high port format, and fixture variants for protocol families.

Control flow: Helpers pack/unpack ranges, discover socket domain, bind to loopback port zero, and read assigned port. Variant tests validate invalid option sizes and low greater than high, ranges outside the namespace ephemeral range, clamped single-port ranges, exhaustion of an eight-port range, late bind behavior with `IP_BIND_ADDRESS_NO_PORT`, and `getsockopt` before/after set/unset. SCTP late-bind variants are marked expected failure.

State and persistence: Per-test sockets hold the configured socket option. The test assumes namespace ephemeral port sysctl is `[40000, 49999]`, set by the shell wrapper. No persistent state.

Dependencies and integration: Requires kernel support for the socket option, optional SCTP/MPTCP protocol availability, and isolated netns sysctl state.

Risks: Protocol availability can affect socket creation. Tests assume the ephemeral range is exactly configured by the wrapper and that no unrelated sockets occupy tested ports.

Test signals: Harness pass means invalid values are rejected, bind allocation respects intersection/clamping/exhaustion semantics, late bind chooses from the socket range, and getsockopt round-trips correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_local_port_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_local_port_range.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_local_port_range.sh

Purpose: Wrapper that runs `ip_local_port_range` in an isolated namespace with required sysctl setup.

Important commands: Invokes `./in_netns.sh` and inside it enables `net.mptcp.enabled=1`, sets `net.ipv4.ip_local_port_range` to `40000 49999`, then executes `./ip_local_port_range`.

Control flow: A single shell command chain is passed to the namespace wrapper. With `set -e` inherited by `in_netns.sh`, any sysctl or test failure fails the wrapper.

State and persistence: Only temporary netns sysctls are changed. No file state.

Dependencies and integration: Depends on `in_netns.sh`, `sysctl`, MPTCP sysctl availability, and the compiled test binary.

Risks: Kernels without MPTCP sysctl support may fail before reaching protocol-specific skip or xfail behavior. The wrapper hardcodes the ephemeral range assumed by the C tests.

Test signals: Exit zero from the C harness after sysctls are applied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_local_port_range.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipsec.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipsec.c

Purpose: Large XFRM/IPsec selftest that creates paired network namespaces connected by veth, drives UDP traffic through plain and XFRM tunnel paths, and validates XFRM state, policy, SPI, acquire, expire, and SPD info netlink behavior.

Important APIs and types: Uses raw netlink `NETLINK_ROUTE` and `NETLINK_XFRM`, `RTM_NEWLINK`, `RTM_NEWADDR`, `RTM_NEWROUTE`, `XFRM_MSG_NEWSA`, `NEWPOLICY`, `DELSA`, `DELPOLICY`, `ALLOCSPI`, `ACQUIRE`, `EXPIRE`, `POLEXPIRE`, `NEWSPDINFO`, `GETSPDINFO`, `struct xfrm_desc`, `struct test_desc`, pipes with `O_DIRECT`, socketpairs, netns file descriptors, `setns`, `unshare`, and kselftest reporting.

Control flow: `main` parses process count, creates three net namespaces, veth pairs, child workers, a test-plan pipe, and a result pipe. `write_test_plan` emits compatibility tests plus AH, COMP, and ESP algorithm combinations. Each child switches to one namespace, reads descriptors, coordinates with a grandchild in the peer namespace over a socketpair, and executes the selected action. Tunnel tests first verify UDP reachability, install policies and states on both ends, verify XFRM state dumps, retest through tunnel source addresses, then delete state and policy. Compatibility actions test SPI allocation, acquire multicast monitoring, state/policy expire messages, and SPD threshold attributes.

State and persistence: Runtime state includes namespace file descriptors, veth devices, XFRM states and policies, randomized keys/payload buffers, and IPC pipes. It relies on process exit and netns lifetime for cleanup rather than named namespace deletion.

Dependencies and integration: Requires root or capabilities, XFRM algorithms, veth, netlink UAPI compatibility, and enough process capacity for requested workers.

Risks: The harness is concurrency-heavy and sensitive to partial pipe messages, netlink sequence handling, missing crypto algorithms, and ABI struct-size differences. Some algorithm lists are intentionally disabled with `#if 0`.

Test signals: kselftest plan equals `proto_plan + compat_plan`; each result line reports pass/fail for descriptor type, protocol, and algorithms. Failures identify tunnel setup, data-path loss, netlink ABI regression, or unsupported algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel.c

Purpose: Datapath test for IPv6 flowlabel send and receive control messages, including explicit labels, auto flowlabels, ping sockets, and `IPV6_FLOWINFO_SEND`.

Important APIs and types: Uses IPv6 UDP or ICMPv6 datagram sockets, `IPV6_FLOWLABEL_MGR`, `IPV6_FLOWINFO`, `IPV6_FLOWINFO_SEND`, `struct in6_flowlabel_req`, `sendmsg`/`recvmsg` cmsgs, `/proc/sys/net/ipv6/auto_flowlabels`, and optional ping socket sysctls configured by the wrapper.

Control flow: Options select label, ping socket mode, and flowinfo-send mode. The test opens transmit and receive sockets, connects/binds loopback, creates an exclusive flowlabel for a non-any destination, enables flowinfo reception, sends once without an explicit label and validates either no label or wildcard auto label based on sysctl, then sends with the configured label either via cmsg or `sin6_flowinfo` plus `IPV6_FLOWINFO_SEND`, and validates the received cmsg.

State and persistence: Per-socket flowlabel manager state and the global auto-flowlabel sysctl read-only observation. No persistent file writes.

Dependencies and integration: Run inside `in_netns.sh` by `ipv6_flowlabel.sh` with sysctls adjusted for each scenario.

Risks: Ping socket mode uses the same socket for send/receive and skips payload validation. Auto flowlabels are wildcard-checked because the kernel chooses the value.

Test signals: Successful runs prove flowinfo cmsgs are delivered or absent as expected and explicit labels round-trip through send/receive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel.sh

Purpose: Orchestrates IPv6 flowlabel management and datapath tests in separate network namespaces to avoid flowlabel database conflicts.

Important commands: Runs `./in_netns.sh ./ipv6_flowlabel_mgr`, then several `./in_netns.sh sh -c ... ./ipv6_flowlabel` invocations with sysctls for `auto_flowlabels`, `flowlabel_reflect`, and `ping_group_range`.

Control flow: The script first tests management behavior. It then runs datapath tests with auto flowlabels disabled, auto flowlabels enabled, ping sockets with reflection, `IPV6_FLOWINFO_SEND`, and ping sockets plus flowinfo-send. `set -e` stops on the first failure.

State and persistence: Each test gets a fresh temporary namespace. Sysctl changes are namespace-local. No persistent output is written.

Dependencies and integration: Depends on `in_netns.sh`, compiled `ipv6_flowlabel` and `ipv6_flowlabel_mgr`, and kernel support for ping sockets and flowlabel sysctls.

Risks: Sysctl availability varies by kernel. The script isolates cases but also repeats namespace creation many times, so failures can be environmental.

Test signals: Final `OK. All tests passed` means management and all datapath variants completed successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel_mgr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel_mgr.c

Purpose: Management-plane test for `IPV6_FLOWLABEL_MGR`, validating create/get/put, exclusivity, sharing scopes, linger reuse, and process/user ownership behavior.

Important APIs and types: Uses `setsockopt(IPV6_FLOWLABEL_MGR)` with `struct in6_flowlabel_req`, actions `IPV6_FL_A_GET` and `IPV6_FL_A_PUT`, shares `IPV6_FL_S_ANY`, `IPV6_FL_S_EXCL`, `IPV6_FL_S_USER`, `IPV6_FL_S_PROCESS`, flags `IPV6_FL_F_CREATE` and `IPV6_FL_F_EXCL`, `fork`, `wait`, and optional `setuid`.

Control flow: `run_tests` checks that nonexistent labels cannot be fetched or put, over-20-bit labels fail, normal labels can be acquired multiple times and released exactly the expected number of references, exclusive labels cannot be shared, optional long-running mode checks linger delay before reuse, user-private labels are visible to same-user child but not after setuid, and process-private labels are not visible to a child process.

State and persistence: Flowlabel references live on the test socket and kernel flowlabel manager. Optional linger state persists briefly in-kernel but not in files.

Dependencies and integration: Run by `ipv6_flowlabel.sh` inside its own namespace. Requires IPv6 flowlabel manager support and permission for optional `setuid` branch.

Risks: The `__expect` macro inverts the raw expression so test readability depends on `expect_pass`/`expect_fail`. Long-running linger is off by default to avoid time cost.

Test signals: Process exit zero confirms reference accounting, exclusivity, and ownership rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_force_forwarding.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_force_forwarding.sh

Purpose: Tests the IPv6 per-interface `force_forwarding` sysctl, proving it forwards packets even when global IPv6 forwarding is disabled.

Important commands: Sources `lib.sh`, creates three namespaces, two veth pairs, IPv6 addresses and routes, manipulates `net.ipv6.conf.all.forwarding` and `net.ipv6.conf.<if>.force_forwarding`, and uses `ping -6`.

Control flow: Setup builds sender, router, and receiver namespaces with routes through the router and disables global forwarding in the router namespace. The test first confirms ping fails when `force_forwarding` is zero on both router interfaces, then sets it to one on both interfaces and confirms ping succeeds. It skips if the per-interface sysctl file is absent.

State and persistence: Temporary namespaces and sysctl values only. Cleanup removes namespaces.

Dependencies and integration: Requires root, `lib.sh`, kernel support for `force_forwarding`, IPv6, veth, and ping.

Risks: Uses only one ping per phase, so transient neighbor discovery timing could matter. It requires enabling both ingress and egress router interfaces.

Test signals: Returns pass when disabled forwarding blocks traffic and forced forwarding permits it; returns kselftest skip when unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_force_forwarding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_fragmentation.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_fragmentation.c

Purpose: Regression test for IPv6 UDP fragmentation on loopback after stable backport issues around cork `dontfrag` state.

Important APIs and types: Uses `unshare(CLONE_NEWNET)`, `ioctl(SIOCSIFMTU)`, `SIOCGIFFLAGS`, `SIOCSIFFLAGS`, IPv6 UDP socket, `sendmsg`, loopback MTU set to 1500, and an 8192-byte payload.

Control flow: `setup` enters a new network namespace, sets loopback MTU below the send size, and brings loopback up. `main` constructs a UDP destination at `::1` port 9, prepares a large iovec, opens an IPv6 datagram socket, retries briefly on `EADDRNOTAVAIL` while loopback settles, and requires `sendmsg` to return the full payload length rather than `EMSGSIZE` or a short write.

State and persistence: Only the private namespace's loopback MTU and link state change. No persistent state.

Dependencies and integration: Requires namespace privileges and standard IPv6 UDP support. It uses `kselftest.h` exit codes.

Risks: It tests successful send, not fragment reception. A very slow namespace address setup can require the retry path.

Test signals: `[PASS] sendmsg() returned 8192` confirms the kernel fragmented instead of failing with `EMSGSIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_fragmentation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_route_update_soft_lockup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_route_update_soft_lockup.sh

Purpose: Stress test for soft lockups during rapid IPv6 route replacement under heavy outgoing TCP traffic.

Important commands and state: Sources `lib.sh`; uses `iperf3`, veth namespaces, many IPv6 nexthop addresses, route add/delete loops with weighted multipath nexthops, `wait_local_port_listen`, `bc`, `nproc`, and host sysctl `kernel.softlockup_panic`.

Control flow: The script checks for `iperf3` and multicore availability, saves and sets `kernel.softlockup_panic=1`, schedules a SIGALRM after `TEST_DURATION`, creates source and sink namespaces, assigns a source address and 128 sink nexthop addresses, builds a long nexthop list, starts restart loops for iperf3 servers and clients on half the CPU count, and in parallel loops adding and deleting a route to the sink loopback address every 0.01 seconds. Cleanup kills namespace processes, detects unkillable iperf3 as soft-lockup evidence, removes namespaces, restores the sysctl, and reports pass on timeout.

State and persistence: Temporary namespaces plus a host-wide softlockup sysctl that is restored. Background loops are killed during cleanup.

Dependencies and integration: Requires root, `iperf3`, `bc`, multipath IPv6 routing, and enough CPU capacity.

Risks: It intentionally destabilizes buggy kernels by converting soft lockup into panic. Virtualized or slow machines may produce false negatives unless duration is increased.

Test signals: SIGALRM cleanup reports pass after the full duration without soft lockup; inability to terminate iperf3 or host panic indicates regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_route_update_soft_lockup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipvtap_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipvtap_test.sh

Purpose: Concurrent ipvtap/ipvlan address assignment stress test, checking that many namespaces do not retain duplicate IPv4 or IPv6 addresses after random add/delete churn.

Important commands: Sources `lib.sh`, uses `setup_ns`, `cleanup_all_ns`, veth, `ip link add ... type ipvtap mode l2 bridge`, `timeout`, background jobs, associative bash arrays, and `ip address` inspection.

Control flow: `test_ip_setup_env` creates a host namespace, physical namespace, veth pair, and 32 ipvtap namespaces each with `ipvlan0` linked to the host veth. `test_ip_set` starts one timed worker per namespace; workers bring `ipvlan0` up and repeatedly add random IPv4/IPv6 addresses from a small range then delete random addresses. After all workers finish, it scans every namespace's `ipvlan0` addresses and fails if any address appears in more than one namespace.

State and persistence: Temporary namespaces and ipvtap devices only. Cleanup deletes the host veth and all namespaces.

Dependencies and integration: Requires bash, root, `ip`, timeout, and ipvtap support.

Risks: Randomized stress can be timing-dependent. The address range is intentionally small to create conflicts, so the correctness check must handle expected add failures.

Test signals: `log_test "test multithreaded ip set"` passes if no duplicate final addresses are found after concurrent churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipvtap_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/l2_tos_ttl_inherit.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/l2_tos_ttl_inherit.sh

Purpose: Matrix test for L2 tunnel TOS and TTL inheritance or fixed-value behavior across GRE tap, VXLAN, and Geneve with IPv4 or IPv6 outer headers, IPv4/IPv6/ARP-like inner traffic, and optional VLAN.

Important commands: Uses root checks, `tcpdump`, `modprobe`, `ip netns`, veth, `gretap`, `ip6gretap`, `vxlan`, `geneve`, VLAN devices, `ping`, random TOS/TTL generation, and tcpdump BPF byte offsets.

Control flow: For each tunnel type, outer family, inner payload family, inherit/random mode, and VLAN flag, `setup` creates two namespaces, a veth underlay, tunnel endpoints with fixed or inherited TOS/TTL parameters, optional VLAN subinterfaces, and inner addresses. `verify` starts ping or ARP-generating traffic, captures exactly one matching underlay packet with tcpdump filters adjusted for tunnel type and VLAN offsets, extracts `tos`/`ttl` or IPv6 `class`/`hlim`, compares against expected values, prints a table row, and records failure. Cleanup removes namespaces after each case.

State and persistence: Temporary namespaces/devices per matrix row. Global expected values and `failed` track results.

Dependencies and integration: Requires root, tcpdump, tunnel modules, iproute2 support, and ping.

Risks: Tcpdump parsing and byte offsets are brittle across header changes. Random chosen values avoid defaults but can complicate reproduction. Non-IP inner traffic expects inheritance to fall back to default outer values.

Test signals: Final exit 0 if every table row reports `OK`; exit 1 if any captured TOS/TTL differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/l2_tos_ttl_inherit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/l2tp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/l2tp.sh

Purpose: L2TPv3 tunnel connectivity test across two host namespaces and a router namespace, with and without IPsec transport protection and after IPsec teardown.

Important commands: Sources `lib.sh`; uses namespace creation, veth pairs, IPv4/IPv6 forwarding sysctls, `ip l2tp add tunnel/session`, route setup, `ping`/`ping6`, `ip xfrm policy`, and `ip xfrm state` with ESP AEAD `rfc4106(gcm(aes))`.

Control flow: `setup` creates host_1, host_2, and router namespaces, assigns loopback service addresses, connects hosts to the router, enables forwarding, configures routes, and creates IPv4 and IPv6 L2TP sessions. `run_ping` validates basic tunnel endpoint and routed loopback connectivity for both families. `setup_ipsec` installs bidirectional XFRM policies and states for the underlay addresses. `run_tests` validates plain L2TP, L2TP with IPsec, repeats selected protected pings, tears IPsec down, and validates L2TP still works afterward.

State and persistence: Temporary namespaces, l2tp devices, routes, and XFRM state/policy. Cleanup removes namespaces.

Dependencies and integration: Requires root, `ip l2tp`, L2TPv3 kernel support, XFRM ESP with AES-GCM support, and ping utilities.

Risks: `run_cmd` uses `eval`, so command construction must remain controlled. Duplicate ping checks in the IPsec phase make reporting slightly redundant. Missing crypto support will fail setup.

Test signals: Counts of passed and failed tests are printed; any failed ping or XFRM command sets final failure state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/l2tp.sh -->
