# subset-b-006867 research

Grouped research report for the requested Linux networking selftest files. Each section title preserves the source path and each section is bounded for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/msg_zerocopy.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/msg_zerocopy.c

Purpose: standalone traffic generator/receiver for validating Linux `MSG_ZEROCOPY` behavior across IPv4, IPv6, packet sockets, raw sockets, TCP, UDP, UDP corking, and RDS seqpacket mode. It can run as either sender or receiver and, when zerocopy is requested, verifies that completion notifications arrive and optionally match the expected copied/not-copied outcome.

Important APIs and types: uses `socket`, `connect`, `bind`, `listen`, `accept`, `sendmsg`, `recvmsg`, `poll`, `setsockopt`, `sched_setaffinity`, `if_nametoindex`, `MSG_ERRQUEUE`, `SO_ZEROCOPY`, `MSG_ZEROCOPY`, `SO_EE_ORIGIN_ZEROCOPY`, `SO_EE_CODE_ZEROCOPY_COPIED`, packet `sockaddr_ll`, IPv4/IPv6/raw headers, UDP `UDP_CORK`, and RDS zerocopy control messages `RDS_CMSG_ZCOPY_COOKIE` and `RDS_CMSG_ZCOPY_COMPLETION`.

Control flow: `parse_opts()` selects address family, source/destination, interface, runtime, payload, corking, receiver mode, and test mode. `main()` dispatches to `do_test()`, which fills deterministic payload data and calls either `do_tx()` or `do_rx()`. `do_tx()` constructs the needed L2/L3/iovec layout, sends until the runtime expires, polls for writable state, and periodically drains zerocopy completions. `do_rx()` binds/listens as needed and drains stream or datagram payloads while validating datagram payload length/content. Completion handling is split between error queue parsing for IP/PACKET sockets and RDS control-message parsing.

State and persistence: state is entirely process-local global configuration and counters (`packets`, `bytes`, `completions`, `expected_completions`, completion sequence state). It does not persist data outside process output. Risks include timing sensitivity, reliance on root/network capabilities for raw and packet modes, large socket buffers/optmem, and completion gaps due to drops/reordering. Test signals are stderr summaries (`tx=...`, `rx=...`) and nonzero exit when expectations fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/msg_zerocopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/msg_zerocopy.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/msg_zerocopy.sh

Purpose: namespace harness for `msg_zerocopy`, exercising IPv4/IPv6 TCP and UDP by default and supporting manual runs for TCP, UDP, raw, raw header-included, packet, and packet datagram modes. It compares local tx-rx behavior, where zerocopy may be copied, with a tx-only path through a dummy device, where outgoing packets should remain zerocopy.

Important APIs and tools: uses `ip netns`, veth and dummy devices, namespace-local `sysctl net.core.optmem_max`, fixed MAC and IP addresses, route setup, and the compiled `./msg_zerocopy` binary. It relies on kernel namespace, veth, dummy, IPv4/IPv6 forwarding, and sufficient privileges.

Control flow: no arguments trigger four automated tests: IPv4/IPv6 TCP and UDP. With arguments, it validates IP version and mode, maps transmit mode to receive mode for packet/raw-hdrincl cases, creates two namespaces, configures a high-MTU veth and a dummy interface, assigns deterministic addresses and routes, enables forwarding in the receiver namespace, then calls `do_test()` twice: once without `-z`, once with `-z`. `do_test()` first starts a receiver in namespace 2 and a sender in namespace 1 against the veth destination, then for non-TCP modes performs a tx-only send to the dummy-routed destination.

State and persistence: namespace and link state are temporary and cleaned by `trap cleanup EXIT`; no files are persisted. Integration points are the C helper, network namespace support, route behavior, and zerocopy completion semantics. Risks include background receiver timing (`sleep 0.2`), optmem limits, missing binary, and root requirement. Test signal is final `OK` plus exit status accumulated in `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/msg_zerocopy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nat6to4.bpf.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/nat6to4.bpf.c

Purpose: eBPF TC classifier program pair that translates selected Ethernet IPv6 ingress packets into IPv4 and selected Ethernet IPv4 egress packets into IPv6. It is a compact CLAT/NAT64-style selftest object used to exercise `bpf_skb_change_proto()`, checksum adjustment, and verifier-safe packet header mutation.

Important APIs and types: uses BPF section annotations `SEC("schedcls/...")`, `struct __sk_buff`, Ethernet/IP/IPv6/UDP headers, TC actions `TC_ACT_OK` and `TC_ACT_SHOT`, `bpf_htons`, `bpf_ntohs`, `bpf_htonl`, `bpf_skb_change_proto`, `bpf_csum_update`, and `bpf_redirect`.

Control flow: `sched_cls_ingress6_nat_6_prog()` accepts only host-bound Ethernet IPv6 frames with supported L4 protocols (TCP, UDP, GRE, ESP), checks bounds and length, constructs a fixed IPv4 header using hard-coded 192.168.1.2 to 192.168.1.1 addresses, computes header checksum, calls `bpf_skb_change_proto()` to shrink to IPv4, updates checksum state using the negative IPv6 header sum, reloads pointers, writes Ethernet and IPv4 headers, then redirects back to ingress. `sched_cls_egress4_snat4_prog()` validates IPv4, rejects IP options, fragments, bad checksums, and zero UDP checksums, constructs fixed 2001:db8::1 to ::2 IPv6 headers, grows the packet to IPv6, adjusts checksum state, rewrites headers, and lets the packet continue.

State and persistence: there are no maps or persistent state; all behavior is packet-local. Dependencies are libbpf headers, TC direct-action loading, and verifier-friendly bounded parsing. Risks include hard-coded addresses, no extension-header support, no recalculation for zero UDP checksum, and fallback-to-OK behavior that depends on userspace/stack handling. Test signal is successful load/execution without verifier or packet mutation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nat6to4.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nat6to4.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/nat6to4.sh

Purpose: minimal smoke test that loads `nat6to4.bpf.o` into a namespace loopback ingress hook and sends a UDP multicast datagram to exercise the IPv4-to-IPv6 egress section path.

Important APIs and tools: uses `ip netns`, loopback route setup, `tc qdisc add dev lo ingress`, `tc filter add ... bpf object-file ... section schedcls/egress4/snat4 direct-action`, and `socat` for UDP4 datagram generation.

Control flow: creates a temporary namespace, brings loopback up, adds a default route via loopback, attaches the BPF object to loopback ingress with protocol `ip`, then executes a `socat` UDP4 datagram send inside the namespace. There is no explicit cleanup trap in the file, so namespace cleanup is left to the caller or broader selftest environment.

State and persistence: creates a net namespace and attaches a TC qdisc/filter; those are persistent until namespace deletion. Dependencies are compiled `nat6to4.bpf.o`, `tc`, `ip`, `socat`, BPF syscall support, and privileges. Risks include namespace leak on failure, no assertion beyond command exit, and dependence on multicast loopback behavior. Test signal is command success or failure from `tc`/`socat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nat6to4.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ndisc_unsolicited_na_test.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/ndisc_unsolicited_na_test.sh

Purpose: validates IPv6 neighbor discovery behavior for RFC9131-style `accept_untracked_na`, specifically whether unsolicited Neighbor Advertisements create STALE neighbor cache entries only when `drop_unsolicited_na=0`, `accept_untracked_na=1`, and forwarding is enabled.

Important APIs and tools: sources `lib.sh` for namespace helpers and kselftest counters, uses `ip -6`, `ip netns exec`, interface sysctls under `net.ipv6.conf.<if>`, `tcpdump`, and neighbor table queries via `ip neigh show ... nud stale`.

Control flow: option parsing supports pause modes. For each matrix entry, `setup()` creates host/router namespaces connected by a veth, configures router sysctls and IPv6 address, and enables host `ndisc_notify`. `link_up()` brings both ends up so the host emits unsolicited NA. `start_tcpdump()` captures one NA packet, and `verify_ndisc()` checks whether the router neighbor table contains the expected STALE entry. `test_unsolicited_na_combinations()` runs the single expected-accept case and seven expected-drop/no-update cases, logging pass/fail counts via `log_test()`.

State and persistence: creates temporary namespaces, veths, sysctl mutations, and temporary tcpdump files; cleanup removes tcpdump files and namespaces. Dependencies include root, `ip`, `tcpdump`, and IPv6 sysctls. Risks include asynchronous NA timing, `tcpdump` timeout behavior, missing kernel support for the sysctls, and possible stale namespace variables if setup fails before assignment. Test signals are per-case `[ OK ]`/`[FAIL]`, total pass/fail counts, and final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ndisc_unsolicited_na_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netdev-l2addr.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netdev-l2addr.sh

Purpose: tests link-layer address reporting and setting for `netdevsim`, including current address, broadcast address, and permanent address (`permaddr`) semantics.

Important APIs and tools: sources `lib.sh`, uses `setup_ns`, `create_netdevsim`, `create_netdevsim_port`, `cleanup_netdevsim`, `ip -j link show`, `jq`, and `ip link set ... address/brd`.

Control flow: creates a namespace and netdevsim instance, verifies `address` and `broadcast` JSON fields exist, verifies `permaddr` is absent before a permanent address is configured, changes address and broadcast to a test MAC, and re-reads JSON to assert the changes. It then verifies that creating a netdevsim port with the broadcast MAC as permanent address fails, creates a port with a valid permanent address, and confirms the `permaddr` JSON field equals the requested value.

State and persistence: creates netdevsim devices under a fixed test id (`2025`) and one namespace; trap cleanup removes both. Dependencies include netdevsim support, JSON output from iproute2, and `jq`. Risks include fixed simulator id collisions, missing netdevsim debugfs support, and `fail()` using shell `$_` for return display rather than the exact failed command status. Test signal is exit code `RET_CODE` plus stderr failure messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netdev-l2addr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netdevice.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netdevice.sh

Purpose: broad legacy selftest for basic Ethernet-like network device operations: bring device up, set MAC address, exercise mutable ethtool offload features, query ethtool dump/stats, and bring device back down.

Important APIs and tools: uses `ip link`, `ip address`, `ethtool --version`, `ethtool -k`, `ethtool --offload`, `ethtool -d`, `ethtool -S`, root checks, temp files, and optional veth creation when no matching physical device exists.

Control flow: validates root and `ip`, builds a temp list of devices matching `eth*` or `enp*s*`, creates a veth pair if no valid device is found, then runs `kci_test_netdev()` per device. That wrapper detects VLAN-style names, calls `kci_net_start()` if the master/down device can be brought up, `kci_net_setup()` to set a fixed MAC and skip IP assignment, `kci_netdev_ethtool()` to iterate non-fixed feature toggles off/on/restore, and `kci_netdev_stop()` if the script brought the device up.

State and persistence: may alter live network interfaces by changing state, MAC address, and offload settings; it attempts to restore offload values but does not restore original MAC. Temporary device list and fallback veth are cleaned. Dependencies include root, iproute2, ethtool, and devices tolerant of offload toggles. Risks are high on real hosts because it can disrupt active NICs and does not aggregate failures into final nonzero status. Test signals are PASS/FAIL/SKIP/XFAIL lines, but final exit is always 0 unless setup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netdevice.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/Makefile -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/Makefile

Purpose: kselftest build and install manifest for netfilter selftests. It lists runnable shell tests, generated helper binaries, extended/manual tests, support files, and libmnl linkage.

Important variables and integration points: `top_srcdir`, `HOSTPKG_CONFIG`, `MNL_CFLAGS`, `MNL_LDLIBS`, `TEST_PROGS`, `TEST_PROGS_EXTENDED`, `TEST_GEN_FILES`, `TEST_FILES`, and `TEST_INCLUDES`. It includes `../../lib.mk`, which provides kselftest build rules for generated binaries and script installation.

Control flow: Make does not define explicit test execution logic here; it declares files for the kselftest framework. Helpers `nf_queue` and `conntrack_dump_flush` receive libmnl compile/link flags, and `udpclash` receives `-lpthread`. `TEST_PROGS` includes many netfilter scripts beyond this subset, while `TEST_GEN_FILES` ensures compiled helpers are available for shell harnesses.

State and persistence: build artifacts are created under `$(OUTPUT)` through kselftest conventions. Dependencies are `pkg-config`, `libmnl`, shell tools, and kernel selftest make infrastructure. Risks include missing libmnl pkg-config data, scripts referencing helpers not built or not in cwd, and `TEST_PROGS_EXTENDED` excluding performance tests from default runs. Test signal is build/install success and subsequent kselftest discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/audit_logread.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/audit_logread.c

Purpose: small NETLINK_AUDIT reader used by `nft_audit.sh` to enable audit logging, register itself as the audit listener, normalize netfilter audit messages, and print stable fields for comparison.

Important APIs and types: uses `socket(PF_NETLINK, SOCK_RAW, NETLINK_AUDIT)`, `sendto`, `recvfrom`, `sigaction`, `AUDIT_SET`, `AUDIT_STATUS_ENABLED`, `AUDIT_STATUS_PID`, `AUDIT_NETFILTER_CFG`, `struct audit_status`, and `struct nlmsghdr`.

Control flow: `audit_send()` sends audit control requests with increasing sequence ids. `audit_set()` sends and waits for an ACK. `main()` opens the audit netlink socket, installs SIGTERM/SIGINT cleanup, enables auditing, sets the audit PID to this process, then loops through `readlog()`. `readlog()` ignores non-netfilter audit records, tokenizes message fields, drops variable/uninteresting keys (`pid`, `comm`, `subj`), strips table sequence suffixes, and prints normalized `key=value` fields.

State and persistence: global `fd` identifies the audit socket. Cleanup disables audit and closes the socket; if killed ungracefully, audit state may remain altered until reset elsewhere. Dependencies are audit kernel support and privilege to set audit status. Risks include destructive `strtok()` parsing on kernel-provided text, assuming one audit daemon is not concurrently managing the audit socket, and broad audit disabling on exit. Test signals are normalized stdout lines consumed by shell diffing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/audit_logread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/br_netfilter.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/br_netfilter.sh

Purpose: regression stress for legacy `br_netfilter` plus connection tracking when broadcast/multicast packets are cloned through bridge and IP netfilter paths. It also checks that the kernel taint flag remains unchanged.

Important APIs and tools: sources netfilter `lib.sh`, requires `nft`, uses `/proc/sys/kernel/tainted`, `modprobe br_netfilter`, `ip` bridge/veth/macvlan setup, bridge sysctl `net.bridge.bridge-nf-call-iptables`, nftables bridge and IP rules, and broadcast pings.

Control flow: skips if the kernel is already tainted. It creates five namespaces with one bridge namespace, four veth peers, a bridge, a macvlan on the bridge, and a macvlan on a non-bridge veth enslaved to the bridge. It enables bridge netfilter and conntrack, loads rules that accept new conntrack state in IP input and drop broadcast ICMP in bridge forward, then verifies unicast connectivity and repeated broadcast pings from multiple ingress paths. It ends by re-reading taint state and dumping dmesg on taint.

State and persistence: all namespace/link/ruleset state is temporary and cleaned by `cleanup_all_ns`. Dependencies include bridge, macvlan, br_netfilter, nftables bridge family, and root. Risks include flood-ping timing, slow-machine packet count reduction still being load-sensitive, and false skips on pre-tainted kernels. Test signals are PASS/ERROR lines and final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/br_netfilter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/br_netfilter_queue.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/br_netfilter_queue.sh

Purpose: tests bridge netfilter interaction with nft queue verdicting and conntrack flushing under broadcast ICMP load, again using kernel taint as a crash/BUG signal.

Important APIs and tools: uses `unshare -n`, namespace helpers, bridge and veth setup, `modprobe br_netfilter`, bridge netfilter sysctl, nft queue rule with `queue num 0 bypass`, compiled `./nf_queue`, `conntrack -F`, `ping -f -b`, and `/proc/self/net/netfilter/nfnetlink_queue`.

Control flow: top-level re-execs itself in a fresh network namespace. It creates a root bridge plus four port namespaces, verifies unicast pings, installs an nft forward-chain rule that queues ICMP and counts new conntrack states, starts `nf_queue -t 5`, waits until queue 0 appears, then concurrently flushes conntrack while sending flood broadcast pings. Finally it checks that the global kernel taint value remains zero.

State and persistence: namespace and queue state are temporary; cleanup deletes all named netns. Dependencies include nfnetlink_queue support, nft, conntrack, bridge netfilter, and the helper binary. Risks include races around queue readiness, flood sensitivity, and reliance on host taint being clean before start. Test signal is PASS/ERROR plus exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/br_netfilter_queue.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/bridge_brouter.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/bridge_brouter.sh

Purpose: validates bridge "brouting" behavior, where ebtables BROUTING redirects selected bridged IPv4/ICMP frames into L3 routing rather than normal bridge forwarding.

Important APIs and tools: requires `ebtables`, uses namespace helpers, bridge/veth setup, IPv4 forwarding sysctls on bridge ports, `ebtables -t broute`, `ebtables -t filter`, and `ping`.

Control flow: creates a bridge namespace connected to two host namespaces by veths, bridges both veths, assigns bridge and endpoint IPv4 addresses, and verifies baseline bridged connectivity. `test_ebtables_broute()` installs a BROUTING redirect/drop rule for ICMP, first verifies ping fails while interface forwarding is off, then enables forwarding and verifies routed connectivity. It flushes broute to verify normal bridging, installs a bridge FORWARD drop, verifies bridge forwarding is blocked, then reinstalls broute and verifies routing still succeeds around the bridge filter drop.

State and persistence: namespace, bridge, routes, and ebtables rules are temporary and cleaned by `cleanup_all_ns`. Dependencies include legacy ebtables broute support, bridge module support, and root. Risks include legacy ebtables backend differences and short ping timeout sensitivity. Test signals are PASS/ERROR lines and the function exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/bridge_brouter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/config -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/config

Purpose: kernel configuration fragment documenting/enabling the modules and built-ins required for the netfilter selftest suite.

Important entries: covers audit, BPF syscall, namespaces, bridge/netfilter/ebtables legacy modules, IPv4/IPv6 iptables and raw/filter/nat modules, conntrack zones/events/protocol support, nfnetlink queue, nftables families and expressions (`NFT_CT`, `NFT_FIB`, `NFT_FLOW_OFFLOAD`, `NFT_QUEUE`, NAT/masq/redir/synproxy/tproxy), IPVS, VRF, veth, dummy, macvlan, VLAN, VXLAN, TUN, IPIP, XFRM, SCTP, and traffic control qdiscs/classes used by the tests.

Control flow: no executable logic; it integrates with kselftest/kernel build config tooling. The fragment intentionally mixes built-in and module settings to allow tests to modprobe functionality while keeping core dependencies available.

State and persistence: affects kernel build configuration, not runtime state. Dependencies are Kconfig symbols existing for the target kernel. Risks are configuration drift when tests add features without updating this fragment, and false skips/failures when optional modules are absent. Test signal is indirect: tests should avoid feature-missing skips when run on a kernel built with this config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/connect_close.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/connect_close.c

Purpose: TCP connection churn helper for netfilter tests. It repeatedly creates nonblocking loopback TCP connections while another process repeatedly accepts, useful for racing connection setup/teardown behavior.

Important APIs and types: uses `socket(AF_INET, SOCK_STREAM)`, `fcntl(... O_NONBLOCK)`, `connect`, `bind`, `listen`, `accept`, `setsockopt(SO_REUSEADDR/SO_REUSEPORT)`, `fork`, `alarm`, and `sigaction`.

Control flow: `parse_opts()` accepts timeout and port. `main()` forks; the parent runs `accept_loop()` and the child runs `connect_loop()`. Both configure a SIGALRM timeout. The accept side repeatedly creates a listening socket on 127.0.0.1:port, accepts one connection if present, and closes. The connect side repeatedly creates a nonblocking socket, initiates connect to the same address, and closes immediately.

State and persistence: only process-local options and loopback sockets; no files or netns are created. Dependencies are local TCP stack and signal delivery. Risks include ignoring many syscall errors by design, potentially hiding environment problems, and high churn causing resource pressure. Test signal is exit status: SIGALRM maps to success via `_exit(0)`, other signals map to failure, fork failure returns 111.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/connect_close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_clash.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_clash.sh

Purpose: tests conntrack clash-resolution accounting for concurrent UDP flows, both through nft DNAT load balancing and without NAT on loopback.

Important APIs and tools: requires `nft`, `conntrack`, `socat`, helper `./udpclash`, namespace helpers, nft `numgen random mod` maps, and `conntrack -S` counters including `clash_resolve`.

Control flow: sets up two client namespaces and one router namespace. The router receives a NAT ruleset that DNATs a fixed UDP destination port to one of three backend ports. Helper functions create simple forward rules, spawn UDP echo servers, configure addresses/routes/forwarding, and verify ping connectivity. `run_clash_test()` invokes `udpclash` up to ten times and inspects `conntrack -S`; if any namespace reports a nonzero clash resolution delta, the test passes. If timing never triggers the race, it returns kselftest xfail rather than hard failure.

State and persistence: temporary namespaces, nft rules, socat servers, and conntrack state are cleaned with namespace removal. Dependencies include helper binary and timing-sensitive concurrent inserts. Risks include legitimate xfail when the race does not happen, hidden failure if `udpclash` times out but stats still show clash resolution, and reliance on exact conntrack stat names. Test signals are PASS/XFAIL/INFO lines and final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_clash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_dump_flush.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_dump_flush.c

Purpose: kselftest harness validating ctnetlink dump and flush operations filtered by conntrack zone, including the default zone, for IPv4 and IPv6 entries.

Important APIs and types: uses libmnl (`mnl_socket_open/bind/sendto/recvfrom`, `mnl_nlmsg_put_header`, `mnl_attr_put`, `mnl_attr_nest_start/end`, `mnl_cb_run`), NETLINK_NETFILTER, `NFNL_SUBSYS_CTNETLINK`, `IPCTNL_MSG_CT_NEW/GET/DELETE`, `CTA_TUPLE_*`, `CTA_PROTOINFO_TCP`, `CTA_ZONE`, and `kselftest_harness.h` fixtures.

Control flow: helper builders construct IPv4/IPv6 original and reply tuples and TCP established protoinfo. `conntrack_data_insert()` sends create requests with ACK handling, treating `EEXIST` as acceptable. `conntracK_count_zone()` sends a dump with `CTA_ZONE` and counts reply messages; `conntrack_flush_zone()` sends a delete request with `CTA_ZONE`. Fixture setup opens and binds netlink, skips on permission or unsupported zone filtering, inserts two entries in zone 123, two in 124, two in 125, and two in default zone, then verifies the selected zone has exactly two entries. Tests assert zone-specific dump count, flushing non-default zone does not remove adjacent/default zones, and flushing default zone does not remove non-default zones.

State and persistence: creates conntrack entries in the current network namespace with long timeouts; the shell wrapper runs under `unshare -n` to isolate them. Dependencies are root or CAP_NET_ADMIN, ctnetlink, conntrack zones, libmnl. Risks include old kernels that ignore zone filter, time-based netlink sequence reuse, and no explicit teardown flush. Test signals are kselftest EXPECT/SKIP output and process exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_dump_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_dump_flush.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_dump_flush.sh

Purpose: tiny wrapper that executes the compiled `conntrack_dump_flush` kselftest helper inside a new network namespace.

Important APIs and tools: `unshare -n` and local `./conntrack_dump_flush`.

Control flow: single `exec unshare -n ./conntrack_dump_flush`, replacing the shell so exit status is exactly the helper status.

State and persistence: the unshared netns confines conntrack entries created by the helper to the subprocess lifetime. Dependencies are unshare support, privileges to create a network namespace, and compiled helper availability. Risks are minimal; missing privileges or helper binary cause immediate failure. Test signal is helper output/exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_dump_flush.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_icmp_related.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_icmp_related.sh

Purpose: verifies that ICMP/ICMPv6 PMTU errors and redirect messages are classified as `ct state related`, including across NAT masquerade for ICMP echo traffic.

Important APIs and tools: uses namespace helpers, nftables inet/ip/ip6 tables, counters, IPv4/IPv6 forwarding sysctls, `ping`/`ping6`, route manipulation, and NAT masquerade rules.

Control flow: creates client1 -> router1 -> router2 -> client2 topology with the router2-client2 link at MTU 1280. It installs forward/input nft rules with counters for `unknown`, `related`, `new`, and redirects; router1 also masquerades ICMP/ICMPv6 toward router2. Baseline pings assert routing and no unknown drops. Oversized IPv4 and IPv6 pings with DF/PMTU behavior are expected to fail while causing related counters on router1 and client1, not router2 forward. Later, it adds bad routes on client1 to provoke IPv4/IPv6 redirects and checks redirect counters.

State and persistence: all netns/rules/routes are temporary. Dependencies include nft, ICMP conntrack, NAT core, IPv6, and deterministic packet sizes/counter bytes. Risks include byte-count dependence on kernel packet formatting, route/redirect suppression differences, and PMTU timing. Test signals are PASS/ERROR lines and counter comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_icmp_related.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_ipip_mtu.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_ipip_mtu.sh

Purpose: regression test for packet loss caused by conntrack reassembly on fragmented packets traversing an IPIP tunnel with PMTU constraints.

Important APIs and tools: requires `iptables` and `socat`, uses five namespaces, veth topology, `ip link add ipip0 type ipip`, IPv4 forwarding sysctls, MTU changes, UDP socat listener/sender, and a single conntrack match rule via iptables.

Control flow: builds Client A - Router A - WAN - Router B - Client B with IPIP tunnels between routers and WAN MTU 1400. `test_path()` starts a UDP listener on Client B, sends three 1400-byte UDP payloads from Client A, then expects exactly 1400 bytes received, demonstrating that PMTU behavior allows one successful delivery. The test first runs without conntrack, then adds `iptables -A FORWARD -m conntrack --ctstate NEW` on Router A and repeats to ensure conntrack reassembly does not drop the packet.

State and persistence: temporary namespaces, routes, ipip devices, MTUs, and iptables rule are cleaned via namespace removal. Dependencies include IPIP support, socat, iptables conntrack match, root, and PMTU propagation. Risks include timing around listener exit, strict byte expectation, and old kernels lacking the IPIP device type. Test signal is `OK`/`FAIL` from byte count and exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_ipip_mtu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_resize.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_resize.sh

Purpose: stress/regression suite for conntrack table resizing, dumping, flushing, namespace limits, timeout changes, and disabling conntrack pickup under concurrent load.

Important APIs and tools: requires `conntrack`, `nft`, optional `socat` and `udpclash`, uses `modprobe nf_conntrack`, sysctls `nf_conntrack_max`, `nf_conntrack_buckets`, `nf_conntrack_expect_max`, timeout sysctls, `/proc/self/net/nf_conntrack`, `conntrack -I/-L/-C/-F`, ping floods, nft ct rules, and kernel taint checks.

Control flow: saves initial sysctl values and restores them on cleanup. It validates the legacy `net.nf_conntrack_max` alias, creates two namespaces, checks which sysctls are immutable from non-init namespaces, enables conntrack via nft rules, and runs four major tests. `test_conntrack_max_limit()` lowers init-net max and inserts entries to confirm clamping. `test_dump_all()` creates ICMP and UDP entries and compares `conntrack -C`, sorted `conntrack -L`, protocol-filtered dump, uniqueness, and optional `/proc` view. `test_floodresize_all()` launches per-namespace insert/flush/dump/timeout/packet floods while repeatedly changing bucket count, then checks taint. `test_conntrack_disable()` flushes the nft table in one namespace and verifies no new entries are picked up there.

State and persistence: mutates init namespace conntrack sysctls and creates conntrack entries; cleanup restores saved values and deletes namespaces/temp files. Risks include global sysctl side effects if interrupted, load-sensitive timing, table exhaustion, and reliance on taint as a crash proxy. Test signals are PASS/FAIL lines and exit `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_resize.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_reverse_clash.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_reverse_clash.c

Purpose: UDP loopback stress helper for verifying that NAT null bindings do not unexpectedly rewrite source ports during reverse-direction conntrack clashes.

Important APIs and types: uses UDP sockets, `SO_RCVTIMEO`, `bind`, `sendto`, `recvfrom`, `fork`, `wait`, `inet_pton`, and IPv4 sockaddr checks.

Control flow: creates two UDP sockets bound to 127.0.0.11:56789 and 127.0.0.12:56790, forks, and for five seconds both parent and child send fixed-size datagrams to each other. Each side receives on the opposite socket and validates the peer source port is exactly the expected original port. `die_port()` prints the unexpected address/port and exits failure if NAT changed it.

State and persistence: process-local sockets only; no external files. It expects the shell wrapper to install NAT null-binding rules and conntrack flushing. Dependencies are loopback routing for 127/8, socket timeouts, and concurrent execution. Risks include `fork() == 0` without explicit fork failure handling, random receive timeouts treated as fatal, and uninitialized payload content being irrelevant but sent. Test signal is exit 0 if no port changes occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_reverse_clash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_reverse_clash.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_reverse_clash.sh

Purpose: harness for `conntrack_reverse_clash`, verifying that NAT null bindings created by a nonmatching masquerade rule do not produce source NAT on loopback UDP traffic while conntrack entries are concurrently flushed.

Important APIs and tools: requires `nft`, `conntrack`, namespace helpers, `conntrack -F`, nft NAT postrouting masquerade rule on an impossible `oifname "nomatch"`, and compiled helper `./conntrack_reverse_clash`.

Control flow: creates one namespace and loads an nft NAT table whose postrouting chain creates NAT null bindings for loopback connections without matching actual output. `do_flush()` loops for five seconds flushing conntrack state in the namespace. The flush loop runs in background while the helper runs; success prints PASS, failure dumps conntrack table and stats.

State and persistence: namespace, nft rules, and conntrack state are temporary. Dependencies include null-binding behavior, nft NAT support, helper binary, and timing between flushes and UDP exchange. Risks include background flusher continuing briefly after helper exit, false negatives on slow systems, and reliance on loopback conntrack NAT behavior. Test signal is helper exit status plus PASS/ERROR output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_reverse_clash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_sctp_collision.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_sctp_collision.sh

Purpose: reproduces an SCTP collision scenario where simultaneous INIT exchanges and delayed INIT ACKs can interact badly with nf_conntrack state handling.

Important APIs and tools: sources `lib.sh`, uses three namespaces, veth topology, IPv4 forwarding, `tc htb` and `netem delay`, iptables state match, SCTP module/sysctls, and compiled `./sctp_collision`.

Control flow: `setup()` creates SERVER, ROUTER, and CLIENT namespaces with routed veth links. It adds a `tc` filter on the server side matching SCTP INIT ACK-like traffic and delays it by 1200 ms, installs router iptables rules to drop INVALID/UNTRACKED forwarded packets and input SCTP, loads SCTP, and lowers client `net.sctp.association_max_retrans`. `do_test()` starts the helper server in the server namespace and runs the client helper from the client namespace. Cleanup kills helper processes and removes namespaces.

State and persistence: temporary namespaces, qdiscs, iptables rules, and SCTP sysctl changes inside namespaces. Dependencies include SCTP, `tc` netem, iptables state match, and helper binary. Risks include fragile byte-offset filter matching, timing dependence, and missing netem causing skip. Test signal is helper success followed by `PASS!` and exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_sctp_collision.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_tcp_unreplied.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_tcp_unreplied.sh

Purpose: checks that an UNREPLIED TCP conntrack entry eventually times out and that a later NAT redirect can create a fresh redirected connection.

Important APIs and tools: requires `nft`, `conntrack`, `socat`, namespace helpers, veth pair, nft counters, `nf_conntrack_tcp_timeout_syn_sent`, `conntrack -L`, and route/DNAT setup.

Control flow: builds two namespaces connected by veth. ns1 routes a virtual IP through ns2; ns2 has forwarding and a TCP listener. ns2 nft rules count initial SYNs to 10.99.99.99:80 and redirected DNAT traffic. A loop from ns1 attempts repeated connections to the virtual IP before NAT exists, creating an UNREPLIED conntrack entry. The script waits until conntrack sees it, then adds a redirect/DNAT rule and waits for counters/connection state to show the stale entry expired and a redirected connection succeeded.

State and persistence: temporary namespaces, nft rules, conntrack entries, background socat/connect loops; cleanup kills namespace pids. Dependencies include conntrack timeout behavior, busywait helpers, and socat. Risks include timing windows around 10-second timeout, background process cleanup, and counter expectations that depend on retries. Test signals are INFO/ERROR/PASS lines and final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_tcp_unreplied.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_vrf.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_vrf.sh

Purpose: verifies conntrack and NAT behavior on VRF devices, including conntrack zone assignment by incoming interface and masquerade behavior when traffic is transmitted through a VRF or its lower veth device.

Important APIs and tools: requires `nft`, `conntrack`, `socat`, namespace helpers, VRF device type, veth pair, `ip vrf exec`, nft `ct zone set`, `ct original zone`, `masquerade random`, and conntrack flushing.

Control flow: creates two namespaces, connects them with a veth, creates a VRF in ns0, enslaves ns0 veth to it, assigns addresses, and starts a TCP listener in ns1. `test_ct_zone_in()` loads nft rules that set ct zone for packets from the VRF/veth and checks a VRF-sourced TCP connection is tracked in the expected zone. `test_masquerade_vrf()` tests masquerade with the VRF as output, both default and pfifo qdisc variants. `test_masquerade_veth()` verifies NAT table evaluation during the lower-device iteration, expecting the veth-output masquerade counter to increment.

State and persistence: temporary netns, VRF, nft rules, conntrack entries, and socat listener. Dependencies include VRF support, nft ct zone/NAT support, and `ip vrf exec`. Risks include device-name/qdisc assumptions, NAT hook double-iteration behavior changes, and counter exactness. Test signals are PASS/FAIL lines and final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_vrf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/ipvs.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/ipvs.sh

Purpose: end-to-end IPVS validation for direct routing, NAT, and IPIP tunneling forwarding modes using a three-namespace topology and real TCP payload transfer.

Important APIs and tools: sources `lib.sh`, requires `ipvsadm`, `socat`, optional `modprobe ip_vs` and `ipip`, uses bridge/veth setup, `ipvsadm -A/-a`, loopback VIP assignment, ARP suppression sysctls, and file comparison.

Control flow: `setup()` creates ns0 client/bridge, ns1 director, and ns2 real server with veth links and random input payload. `server_listen()`, `client_connect()`, and `verify_data()` perform a TCP transfer to the VIP and compare bytes. `test_dr()` configures IPVS direct routing with VIP on director and real server loopback. `test_nat()` configures IPVS masquerading and changes real server default route. `test_tun()` configures IPVS IPIP tunnel mode with `tunl0` and VIP loopbacks. `run_tests()` resets topology between modes and sums errors.

State and persistence: temporary namespaces, bridge, IPVS services, temp input/output files; cleanup removes all. Dependencies include IPVS kernel modules/protocol, ipvsadm, socat, and IPIP for tunnel mode. Risks include hard-coded addresses, ARP behavior sensitivity, fixed TCP port 8080, and short timeout. Test signals are payload `cmp`, colored PASS/FAIL, and exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/ipvs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/lib.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/lib.sh

Purpose: small netfilter-local shell library that imports the parent networking selftest library and adds a command availability helper.

Important APIs: sets `net_netfilter_dir` from the resolved script path, sources `../lib.sh`, and defines `checktool()`.

Control flow: `checktool <command> <message>` executes the command with stdout/stderr suppressed; if it fails, it prints a kselftest skip message and exits with `$ksft_skip`. This centralizes common dependency checks used by many netfilter scripts.

State and persistence: no persistent state beyond shell variables/functions. Dependencies are Bash, `readlink -e`, and the parent `../lib.sh` defining `ksft_skip` and namespace helpers. Risks include unsafe command-string evaluation (`$1` is executed by shell word splitting), but all callers pass fixed command strings. Test signal is immediate skip when required tools are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_conntrack_packetdrill.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_conntrack_packetdrill.sh

Purpose: runs a curated set of packetdrill scripts against nf_conntrack for IPv4 and IPv6 TCP edge cases such as ACK loss, inexact RST, challenge ACK, old/reused SYNACK, and invalid RST.

Important APIs and tools: requires `conntrack`, `iptables`, `ip6tables`, `packetdrill`, `timeout`, `unshare -n`, `modprobe tun`, `modprobe nf_conntrack`, and environment variables `NFCT_IP_VERSION` and `xtables` consumed by packetdrill scripts.

Control flow: verifies packetdrill is installed via dry run, then iterates over the listed `.pkt` files. `run_packetdrill()` exports IP version and xtables command, chooses MTU 1500 for IPv4 and 1520 for IPv6, then runs packetdrill in an isolated network namespace with tolerance and non-fatal packet mode. Each file is run for both IPv4 and IPv6, printing OK/FAIL and accumulating `ret`.

State and persistence: no long-lived state; each packetdrill run uses `unshare -n`. Dependencies include packetdrill scripts under `packetdrill/`, tun, netfilter modules, and iptables tooling. Risks include a likely variable mismatch where `run_one_test_file()` ignores its parameter and uses global `$f`, making correctness depend on loop variable scope. Test signals are per-case OK/FAIL and final exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_conntrack_packetdrill.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_nat_edemux.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_nat_edemux.sh

Purpose: tests NAT source-port clash resolution and early demux behavior when local port range is constrained and multiple redirected connections target the same backend service.

Important APIs and tools: requires `socat`, `iptables`, `conntrack`, namespace helpers, `ip_local_port_range`, DNAT in OUTPUT, REDIRECT in PREROUTING, `ss`, and `conntrack --get`.

Control flow: creates two namespaces on one subnet, starts a TCP server in ns1, restricts ns2 ephemeral ports to exactly 10000, adds ns2 OUTPUT DNAT from virtual 10.96.0.1:443 to ns1:5201, and opens a persistent direct connection consuming source port 10000. It then connects to the DNAT address, expecting NAT to reallocate source port rather than fail. Next it adds ns1 PREROUTING redirects from ports 5202 and 5203 to 5201, opens two simultaneous connections, waits for them established, and validates conntrack entries for both original destination ports.

State and persistence: temporary namespaces, iptables NAT rules, conntrack entries, socat processes; cleanup kills server and deletes namespaces. Dependencies include NAT clash handling and conntrack CLI. Risks include fixed port range affecting namespace only, timing around established detection, and process cleanup if connection setup fails. Test signals are PASS/FAIL lines and final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_nat_edemux.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_queue.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_queue.c

Purpose: user-space nfnetlink_queue consumer for nft queue tests. It binds a queue, receives packets, optionally prints/counts per-hook packet stats, and sends accept or queue-forwarding verdicts, including stress modes for out-of-order and bogus verdicts.

Important APIs and types: uses libmnl with NETLINK_NETFILTER, `NFNL_SUBSYS_QUEUE`, `NFQNL_MSG_CONFIG`, `NFQNL_MSG_VERDICT`, `NFQA_CFG_CMD`, `NFQA_CFG_PARAMS`, `NFQA_CFG_FLAGS`, `NFQA_VERDICT_HDR`, `NFQA_PACKET_HDR`, `NFQA_SKB_INFO`, and verdict constants `NF_ACCEPT`/`NF_QUEUE`.

Control flow: `parse_opts()` sets count, verbosity, queue number, timeout, fail-open, GSO flag, verdict destination queue, delay, out-of-order mode, and bogus verdict mode. `open_queue()` binds netlink, binds the nfqueue, configures copy-packet mode, flags, and receive timeout. `mainloop()` receives netlink batches, parses attributes in `queue_cb()`, computes packet id from callback return, optionally delays, sends bogus verdicts for nonexistent ids, batches 16 ids for reverse-order verdicts, or immediately sends a verdict for the packet id. On timeout it exits cleanly; with `-c` it prints hook counters.

State and persistence: process-local options and `queue_stats`; queue binding exists while process runs. Dependencies include nfnetlink_queue kernel support and libmnl. Risks include callback return encoding `MNL_CB_OK + id`, fixed hook count array of 5, and leaving queued packets to bypass/fail-open depending on nft rule if process exits. Test signals are exit status, optional stats, and kernel queue behavior observed by scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_audit.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_audit.sh

Purpose: validates audit records emitted by nftables operations, checking operation names and aggregated entry counts for table, chain, rule, set, element, counter, quota, reset, flush, and delete paths.

Important APIs and tools: uses `nft`, `unshare -n`, compiled `./audit_logread`, temp files, shell process substitution, `diff`, `sed`, and audit daemon detection through `/var/run/auditd.pid`.

Control flow: skips if auditd is active or nft lacks reset support. It re-execs in a new net namespace, starts `audit_logread` to normalize audit output, then `do_test()` drains prior logs, executes a command, waits briefly, summarizes adjacent audit lines with the same prefix/suffix by adding `entries=`, and diffs against the expected string. The script builds nft state progressively across add/set/reset/delete scenarios, including bulk 500-rule/object cases, handle-based rule deletes, set element resets/deletes, and table flushes.

State and persistence: temp rule/log files and audit PID registration; trap kills audit reader and removes files. It globally manipulates audit enabled/PID via helper, so it skips when auditd owns audit. Dependencies are audit kernel support, privileges, recent nft, and exact audit message schema. Risks include races with other nft/audit activity, fixed sleep for log delivery, and `RC--` producing negative failure count. Test signal is per-command OK/FAIL diff and final `RC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_audit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_concat_range.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_concat_range.sh

Purpose: comprehensive nftables pipapo/interval set regression suite for concatenated ranged keys. It covers correctness, large-set representation changes, concurrency, timeouts, performance baselines, and many reported bug scenarios.

Important APIs and tools: sources `lib.sh`, uses `unshare -n`, nft tables/sets/elements/counters across inet and netdev families, veth namespace B, `sendip`/`socat`/bash UDP, `ping`, `iperf3`/`iperf`/`netperf`, optional pktgen script, dynamic shell `eval` of `TYPE_*` descriptors, and kselftest skip codes.

Control flow: descriptors define key shapes such as IPv4/IPv6 address plus port, protocol, MAC, and multi-field concatenations, with protocol/tool/performance/race parameters. Setup builds veth topology and a templated nft set/rule. Formatting helpers convert integers to addresses, ports, protocols, and ranged nft element expressions. Correctness tests add ranges, send matching and nonmatching packets, and delete selected ranges. Large correctness inserts tens of thousands of filler elements to exercise compact lookup representations. Concurrency floods traffic while per-CPU workers repeatedly add, flush, recreate, and delete sets. Timeout tests add expiring elements and verify post-timeout misses. Performance compares raw drop, hash-like non-ranged, first-field rbtree, and full ranged concatenation rates. Reported-issue tests cover flush/remove/add ordering, reload without add/delete, overlap insertion, double create, AVX2 false match, and load/flush/reload cases.

State and persistence: creates a temporary namespace, veth pair, nft rulesets, background traffic processes, and temp command file; cleanup flushes rulesets and kills traffic tools. Dependencies are root, nft interval concatenation support, optional traffic generators, and enough CPU/time. Risks include heavy runtime, many `eval` paths, random sampling in some bug checks, and tool-dependent skips. Test signal is per subtest `[ OK ]`, `[FAIL]`, `[SKIP]`, buffered diagnostics, and nonzero exit on hard failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_concat_range.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_concat_range_perf.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_concat_range_perf.sh

Purpose: extended/performance-only wrapper for `nft_concat_range.sh`.

Important APIs and tools: sources `lib.sh`, checks `KSFT_MACHINE_SLOW`, sets environment variable `NFT_CONCAT_RANGE_TESTS=performance`, and `exec`s `./nft_concat_range.sh`.

Control flow: if running on a slow-machine kselftest environment, exits skip immediately. Otherwise it replaces itself with the main concat-range suite limited to the `performance` group.

State and persistence: no independent state; all setup/cleanup is delegated to `nft_concat_range.sh`. Dependencies are the main script, performance tools/pktgen availability, and root. Risks are that performance tests are environment-sensitive and may skip internally if pktgen is unavailable. Test signal is inherited exit/output from the main script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_concat_range_perf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_conntrack_helper.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_conntrack_helper.sh

Purpose: tests nftables assignment of conntrack FTP helpers and verifies auto-assignment behavior controlled by `nf_conntrack_helper`.

Important APIs and tools: requires `socat`, `conntrack`, `nft`, namespace helpers, nft `ct helper` objects, `ct helper set`, sysctl `net.netfilter.nf_conntrack_helper`, and IPv4/IPv6 TCP connections.

Control flow: creates two namespaces connected by veth with IPv4 and IPv6 addresses. `load_ruleset_family()` installs raw-family helper rules setting the FTP helper for TCP dport 2121 in prerouting and output. It tries ip/ip6 in ns1 and inet fallback in ns2. `test_helper()` starts a TCP listener in ns2, connects from ns1, and calls `check_for_helper()` in both namespaces to assert helper presence for ruleset assignment on port 2121. It then enables auto assignment in both namespaces and tests port 21, expecting helper absence/presence semantics according to the `autoassign` flag in the check logic. IPv6 is skipped if ip6 ruleset load fails.

State and persistence: temporary netns, nft rules, conntrack entries, socat listeners; cleanup kills ns1 pids and deletes namespaces. Dependencies include FTP conntrack helper support and nft helper syntax. Risks include confusing local/global `autoassign` use in `check_for_helper()`, IPv6 conditional coverage, and stale conntrack entries if flush fails. Test signals are PASS/FAIL messages and final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_conntrack_helper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_fib.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_fib.sh

Purpose: validates nftables `fib` expression behavior for reverse-path filtering, address type lookups, policy-based routing, loopback handling, and VRF interactions across IPv4 and IPv6.

Important APIs and tools: uses nft inet/ip/ip6 tables, `fib saddr . iif oif missing`, `fib daddr type`, `fib daddr . iif type`, dynamic nft sets, `ip rule`/routing tables, VRF/dummy devices, dmesg log prefixes, forwarding sysctls, and ping.

Control flow: creates ns1 - nsrouter - ns2 topology, loads rpfilter-like prerouting rules in all namespaces, enables logging for netns, and verifies normal routing does not produce fib drops. It tests input-chain loopback/local behavior, then readdresses ns1 to create expected missing reverse routes and checks fib counters. Policy-routing tests remove main IPv4 table lookup, install table 128/129 rules, and assert forwarded ping works with `fib saddr . iif oif`. Type tests reload ip/ip6 rules and compare counters for local-on-incoming-interface, local-on-other-interface, and remote unicast addresses. VRF tests add dummy0 and tvrf, use dynamic sets to record fib outputs/types, first with incoming interface outside VRF, then with veth0 enslaved to VRF, deleting expected elements and ensuring no unexpected set entries remain.

State and persistence: temporary namespaces, nft rules, dmesg reads, sysctl change for `nf_log_all_netns`, routes/rules/VRF devices; cleanup restores log sysctl and namespaces. Dependencies include nft fib expression, VRF, IPv6, and clean dmesg signal. Risks include duplicate address add in setup, dmesg noise from prior tests, exact packet counter expectations, and complex VRF route semantics. Test signal is PASS/FAIL lines, fib counters, and final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_fib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_flowtable.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_flowtable.sh

Purpose: extensive flowtable offload functional test for forwarding, NAT, PMTU, DSCP mangling, IPIP/IP6 tunnels, VLAN, bridge, and IPsec tunnel mode.

Important APIs and tools: requires `nft`, `socat`, namespace helpers, flowtables with `flow add`, nft counters/marks/NAT, veth/bridge/VLAN/IPIP/IP6TNL/XFRM devices, PMTU sysctls, `cmp`, random file generation, and `nf_log_all_netns`.

Control flow: builds originator ns1, responder ns2, and routers nsr1/nsr2 with deliberately mismatched MTUs. Router1 nft forward chain marks/offloads original TCP flows and counts routed original/reply packets; ns2 counts DSCP classes. Helpers generate input files, run bidirectional socat TCP transfers, compare outputs, inspect counters, and validate DSCP handling. Initial tests cover IPv4/IPv6 forwarding without PMTU, then IPv4 NAT with DNAT/masquerade, DSCP changes at netdev ingress/egress and forward hook, and PMTU-enabled offload where routed counters must stay below file size. `test_ipip()` reroutes through IPIP and IP6 tunnels, then VLAN-tagged tunnels. `test_bridge()` moves ingress under a bridge, then bridge plus VLAN, and retests NAT/offload. Final XFRM setup installs ESP tunnel state/policies and checks IPv4 and IPv6 transfers. With no arguments, the script recursively reruns itself once with random MTUs and file size.

State and persistence: heavy temporary namespace topology, temp files, nft rules, routes, tunnels, XFRM state, and sysctl changes; cleanup kills namespace pids, removes temp files, and restores logging. Dependencies are broad kernel feature support and enough runtime. Risks include long runtime, recursive random rerun variability, exact counter threshold assumptions, and many skip/fail points. Test signals are transfer byte equality, nft counter checks, PASS/FAIL lines, and final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_flowtable.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_interface_stress.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_interface_stress.sh

Purpose: stress test for nftables netdevice notifier callbacks and flowtable device tracking while interfaces are rapidly renamed, listed, monitored, created, and deleted under traffic.

Important APIs and tools: requires `nft`, `iperf3`, namespace helpers, veth routing topology, netdev-family ingress chains, IP flowtables, `nft list ruleset`, `nft monitor`, dummy devices, kernel taint, and optional kmemleak.

Control flow: records initial taint, sets runtime to 80 percent of kselftest timeout capped at 48 seconds, creates client/router/server namespaces and routed IPv4 topology. It loads a ruleset with ten pairs of netdev ingress chains bound to `rc0..rc9`/`rs0..rs9` and ten flowtables using matching device names, then starts a loop renaming `rcN`/`rsN` modulo 10. In parallel it continuously lists the ruleset and runs `nft monitor`, while iperf3 transfers traffic through the router. After killing stress processes, it attempts wildcard flowtable devices (`wild*`) and concurrently creates/deletes 100 dummy devices in several patterns. It then checks that a previously clean kernel did not become tainted, throughput was nonzero, and kmemleak is empty if available.

State and persistence: temporary namespaces, nft rules, rename/list/monitor background processes, dummy devices, and iperf server; cleanup removes namespaces. Dependencies include nft support for netdev hooks, flowtables, wildcard devices, iperf3, debugfs kmemleak if checked. Risks include `#!/bin/bash -e` making unexpected command failures fatal, background wait behavior after killed infinite loops, and environment-sensitive throughput. Test signals are taint/kmemleak/throughput checks and kselftest pass/fail/skip exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_interface_stress.sh -->
