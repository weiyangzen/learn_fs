# subset-b-006875 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/traceroute.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/traceroute.sh

Purpose: Bash kselftest for IPv4 and IPv6 traceroute behavior across namespace topologies, VRF devices, and ICMP RFC 5837 extension reporting. It validates that ICMP error source address selection uses the correct ingress or forwarding interface address rather than a bridge, wrong subnet, or VRF master address.

Important APIs/functions: sources `lib.sh` for `setup_ns`, `cleanup_ns`, `cleanup_all_ns`, `check_err`, `check_fail`, `log_test`, `log_test_skip`, and `require_command`. `run_cmd()` wraps `ip netns exec` and optional verbose logging. `create_ns()` applies loopback addresses, unreachable default routes, forwarding, ICMP ratelimit, and IPv6 DAD/forwarding sysctls. `connect_ns()` creates veth pairs and assigns IPv4/IPv6 addresses. Version helpers require traceroute/traceroute6 2.1.5 for extension tests.

Control flow: the main path parses `-p`/`-v`, requires `traceroute6`, `traceroute`, and `jq`, then calls `run_tests()`. The test suite builds six independent topologies: IPv6 traceroute, IPv6 traceroute with router interfaces enslaved to VRF, IPv6 ICMP extension reporting, IPv4 traceroute source address selection with `icmp_errors_use_inbound_ifaddr`, IPv4 VRF traceroute, and IPv4 ICMP extension reporting. Each setup starts from cleanup, creates namespaces/veth/bridge/VRF state, primes neighbor state with ping, runs traceroute plus grep expectations, logs, and cleans up.

State and persistence: all state is ephemeral kernel networking state in netns, veths, bridge `br0`/`br100`, VRF `vrf100`, routes, and sysctls such as `net.ipv[46].icmp*_errors_extension_mask`. No files are persisted. The global `RET`/`EXIT_STATUS` behavior comes from `lib.sh`; cleanup is explicit after each scenario.

Dependencies and integration: depends on iproute2 VRF/bridge/netns support, traceroute utilities, `jq` for JSON link ifindex extraction, ping/ping6, root privileges, and `lib.sh`. It integrates with kselftest by returning `EXIT_STATUS`.

Risks: version parsing assumes a three-component traceroute version; extension string greps are coupled to traceroute output formatting. Namespace sysctl changes require sufficient privilege and kernel support. ICMP extension tests depend on interface names/MTUs and on `jq`; neighbor priming can hide timing issues but reduces flakiness. Some commands use `eval` inside `run_cmd`, so caller-provided command strings must remain controlled.

Test signals: PASS means expected hop/source/extension strings appeared and unsupported sysctl values were rejected. SKIP is used for too-old traceroute extension support. Failures isolate source address selection regressions, VRF source leaks, RFC 5837 extension toggling, and malformed incoming-interface metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/traceroute.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tun.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tun.c

Purpose: C kselftest harness for TUN/TAP multi-queue lifetime behavior and virtio-net UDP tunnel GSO/GRO metadata through TAP plus Geneve. It verifies both writing prebuilt tunnel packets into a TAP device and receiving tunnel-originated UDP GSO packets from TAP with correct virtio-net header fields.

Important APIs/types/functions: uses `kselftest_harness.h`, Linux `/dev/net/tun` ioctls (`TUNSETIFF`, `TUNSETQUEUE`, `TUNSETVNETHDRSZ`, `TUNSETOFFLOAD`), `SIOCGIFFLAGS`, `SIOCSIFFLAGS`, `SIOCSIFHWADDR`, UDP `sendmsg()` with `UDP_SEGMENT`, and helper APIs from `tuntap_helpers.h`. `struct geneve_setup_config` feeds YNL-generated rtnetlink requests for Geneve creation. `tun_attach`, `tun_detach`, `tun_alloc`, `tun_delete`, and `tun_open` manage the device. `parse_udp_tunnel_vnet_packet()` validates virtio, Ethernet, outer IP, UDP/Geneve, inner Ethernet/IP/UDP headers.

Control flow: fixture `tun` creates two multiqueue TAP fds on the same device and runs delete/detach/close ordering tests, including expected `EINVAL` after deleting before detach. Fixture `tun_vnet_udptnl` is variant-expanded across Geneve 4in4, 6in4, 4in6, and 6in6 and many size/GSO cases. Setup opens a TAP/TUN with `IFF_VNET_HDR`, `IFF_MULTI_QUEUE`, `IFF_NO_PI`, offload features `TUN_F_CSUM`, UDP tunnel GSO, and USO, then configures local/neighbor/routes on the TAP and Geneve device. `send_gso_packet` builds a complete virtio-net tunnel frame and writes it into TAP, expecting segmented UDP receives on the inner socket. `recv_gso_packet` sends a UDP GSO message into the Geneve path and reads/parses frames from TAP, checking `gso_size`/`gso_type` unless the variant is expected to fall back to non-GSO.

State and persistence: state is process-local fixture data plus kernel TAP/Geneve links, routes, neighbor entries, and UDP sockets. Teardown closes sockets, deletes Geneve, and deletes TAP. No persistent files are written.

Dependencies and integration: requires generated YNL rtnetlink headers/libraries, CAP_NET_ADMIN, `/dev/net/tun`, Geneve support, virtio-net header definitions including `virtio_net_hdr_v1_hash_tunnel`, and UDP tunnel offload support. `ynl.mk` helps build the generated dependencies. Integrated with kselftest harness and `XFAIL_ADD` for oversized or no-GSO receive cases.

Risks: many checks depend on precise kernel offload semantics and support for newer virtio-net tunnel header fields. Header construction is manual, so checksum, offset, or length bugs could cause false negatives. Route readiness is polled with `MAX_RETRIES`; slow setups may fail. The code uses `strcpy` into `ifr_name` from controlled fixed buffers, so misuse outside the test could be risky.

Test signals: normal fixture assertions validate ioctl/link behavior, exact received payload byte counts, MSS segment counts, tunnel header parse success, and virtio GSO fields. XFAIL entries document currently expected failures for oversized and no-GSO-too-large receive/send combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tuntap_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tuntap_helpers.h

Purpose: Inline helper library for TUN/TAP selftests. It hides YNL-generated rtnetlink request construction and provides packet construction primitives for Ethernet, IPv4, IPv6, UDP, Geneve, checksums, and virtio-net tunnel headers.

Important APIs/types/functions: includes generated `rt-route-user.h`, `rt-addr-user.h`, `rt-neigh-user.h`, `rt-link-user.h` and `ynl.h`. Netlink helpers include `ip_addr_add`, `ip_neigh_add`, `ip_route_get`, `ip_link_add`, and `ip_link_del`. Packet helpers include `build_eth`, `add_csum`, `finish_ip_csum`, `build_ip_csum`, `build_ipv4_header`, `build_ipv6_header`, `build_geneve_header`, `build_udp_header`, `build_udp_packet_csum`, `build_udp_packet`, and `build_virtio_net_hdr_v1_hash_tunnel`.

Control flow: YNL helpers allocate a family socket, allocate a generated request, fill headers and attributes, submit the request, free request/response objects, and destroy the socket on all paths. Packet helpers write headers in-place into caller-provided buffers, returning byte lengths so callers can advance a cursor. The virtio helper calculates outer transport and inner network offsets from TAP/TUN mode and IP families, then sets checksum and GSO metadata.

State and persistence: all functions are `static inline` and hold no persistent state. They mutate kernel link/address/neighbor/route state through netlink or mutate caller-provided buffers.

Dependencies and integration: designed for `tun.c` and other local TUN/TAP tests that use generated YNL rtnetlink bindings. Requires libc networking headers, Linux virtio/packet headers, and `if_nametoindex`. Build integration depends on `ynl.mk` generating/including the rtnetlink family bindings.

Risks: checksum helpers assume packet layouts where IP addresses immediately precede the UDP header; that is true for these generated packets without extension headers but not general-purpose. The packet builders do not bounds-check caller buffers. Netlink helpers return only coarse `-1` errors, so diagnostics come from callers or YNL internals.

Test signals: no standalone tests; coverage comes from `tun.c`, where successful route checks, Geneve device setup, and packet parse/segmentation validate the helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tuntap_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/txring_overwrite.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/txring_overwrite.c

Purpose: Regression test for AF_PACKET `PACKET_TX_RING` to ensure consecutive sends from the same TX ring slot are mirrored with original content intact and not overwritten before loopback receive.

Important APIs/functions: uses raw packet sockets, `PACKET_TX_RING`, `mmap`, `struct tpacket_req`, `struct tpacket_hdr`, `TP_STATUS_AVAILABLE`, `TP_STATUS_SEND_REQUEST`, `if_nametoindex("lo")`, and `sendto()` as the TX kick. `build_packet()` creates a loopback IPv4/UDP Ethernet frame with a caller-selected payload byte. `read_verify_pkt()` reads 100 bytes from RX and checks byte 60 for the pattern.

Control flow: `main()` opens a raw RX packet socket for `ETH_P_IP`, configures one TX ring frame on a raw packet socket bound to loopback, sends two packets with payload patterns `a` and `b` through the same ring slot, then reads and verifies the two mirrored packets in order.

State and persistence: state is one mmap'd packet ring slot and two sockets. The test does not unmap explicitly but exits after closing sockets. No persistent files are touched.

Dependencies and integration: requires CAP_NET_RAW/CAP_NET_ADMIN enough to create AF_PACKET raw sockets, loopback interface, and packet mmap support. It is a standalone compiled selftest with process exit status as the signal.

Risks: assumes loopback delivery ordering and fixed offset `buf[60]` into the constructed frame. It builds deliberately minimal IP/UDP headers with zero checksums, acceptable for the loopback/raw packet path tested but not a generic packet generator.

Test signals: success prints `read: a` and `read: b` and exits 0. A wrong byte reports the mismatched pattern and exits nonzero; socket/ring setup failures abort through `error(1, ...)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/txring_overwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/txtimestamp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/txtimestamp.c

Purpose: Exhaustive software TX timestamping exerciser for TCP, UDP, raw IPv4/IPv6, and PF_PACKET sockets. It validates SCHED, SND, and TCP ACK timestamps, timestamp keys, optional cmsg configuration, pktinfo, epoll/poll/busy polling, payload/no-payload error queue modes, and timing tolerances.

Important APIs/types/functions: uses `SO_TIMESTAMPING`, `SOF_TIMESTAMPING_TX_*`, `SOF_TIMESTAMPING_OPT_CMSG`, `SOF_TIMESTAMPING_OPT_ID`, `SOF_TIMESTAMPING_OPT_TSONLY`, `SCM_TS_OPT_ID`, `SCM_TIMESTAMPING`, `MSG_ERRQUEUE`, `sock_extended_err`, IP/IPV6/PACKET timestamp error queue cmsgs, `TCP_NODELAY`, raw/PF_PACKET headers, `poll`, and `epoll`. `struct timing_event` accumulates min/max/avg deltas. `validate_key()` checks sequential timestamp IDs; `validate_timestamp()` compares kernel timestamps against recorded user time plus configured delays.

Control flow: `main()` parses options, resolves the target hostname, optionally opens local listener sockets, and runs `do_main()` per selected address family. `do_main()` calls `do_test()` for SND, ENQ, ENQ+SND, and for TCP also ACK combinations. `do_test()` creates a socket, optionally connects, configures pktinfo and timestamping, builds payload/raw headers as needed, sends `cfg_num_pkts` messages, waits via poll/epoll unless busy-polling, drains the error queue with `recv_errmsg()`, validates cmsg pairs, and prints timing aggregates.

State and persistence: global configuration variables are set by command line. `saved_tskey` tracks expected key progression per socket. `ts_usr` and timing accumulators hold process-local measurements. No persistent files are written; listener fds are left open until process exit to keep connects working.

Dependencies and integration: compiled helper driven by `txtimestamp.sh`. Requires loopback or provided host, timestamping kernel support, raw socket privileges for raw/PF_PACKET modes, and optionally slow-machine tolerance via `KSFT_MACHINE_SLOW`.

Risks: timing validation is sensitive to scheduler and virtualized environments; slow machines are exempt from hard failure for timestamp delay mismatches. Raw/PF_PACKET construction uses manual checksum/header code and assumes MTU constraints. The `-E` option intentionally falls through to `-F`, making edge-triggered epoll wait indefinitely; this is subtle but encoded in parsing.

Test signals: nonzero exit if timestamp cmsgs are missing, keys jump unexpectedly, send/read setup fails, or timing is outside tolerance on normal machines. Output includes per-family/protocol timing and payload/pktinfo diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/txtimestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/txtimestamp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/txtimestamp.sh

Purpose: Namespace wrapper for `txtimestamp` that installs deterministic loopback/ifb netem delays and runs timestamp validation across TCP, UDP, raw, IP_HDRINCL raw, PF_PACKET, setsockopt, cmsg, and timestamp-without-payload modes.

Important APIs/functions: `setup()` adds 10 ms netem delay to `lo`, creates `ifb_netem0`, adds 20 ms netem there, and redirects loopback ingress to IFB with a `mirred` action. `run_test_v4v6()` supplies expected SND and ACK delays to `txtimestamp`. `run_test_tcpudpraw()` enumerates protocol modes, including fixed timestamp key tests with `-o 42`.

Control flow: if not already in a namespace, it re-execs itself through `in_netns.sh`. With no args it calls `run_test_all()`: setup, all protocol/config combinations, and final success message. With `-r|--run`, it sets up netem and passes remaining args to `./txtimestamp`; otherwise it prints usage.

State and persistence: creates temporary qdisc, IFB device, ingress filter, and netns state inside `in_netns.sh` context. No persistent files.

Dependencies and integration: requires `tc`, `ifb` module, iproute2, mirred action, root privileges, and compiled `txtimestamp`. Integrates into kselftest by exiting on first failure due to `set -e`.

Risks: depends on ifb module availability and qdisc/action support. Timing tolerances are broad but still susceptible to severe scheduling delay. It does not define its own cleanup because the namespace wrapper removes the namespace state.

Test signals: all `txtimestamp` invocations must exit 0; the wrapper prints `OK. All tests passed` only after the full matrix succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/txtimestamp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro.sh

Purpose: Functional UDP GRO test matrix over veth, validating unaggregated receive, GRO aggregation, UDP_GRO cmsg reporting, custom segment sizes, NAT-induced socket lookup behavior, and multiple GRO sockets for IPv4 and IPv6.

Important APIs/functions: uses `udpgso_bench_tx` as traffic generator and `udpgso_bench_rx` as receiver/verifier. `cfg_veth()` creates host plus peer namespace veth with IPv4/IPv6 addresses and enables GRO on peer. `run_one()`, `run_one_nat()`, and `run_one_2sock()` launch receiver(s), wait for UDP port readiness via `wait_local_port_listen`, run TX, and aggregate exit status using `check_err()`.

Control flow: no-arg `run_all()` executes IPv4 and IPv6 cases. Each case re-execs in a fresh namespace through `in_netns.sh` and a private peer namespace. It tests no GRO with ten 1400-byte packets, absence of UDP_GRO cmsg with `-S -1`, one aggregated GSO datagram, correct cmsg segment size, custom segment size 500, NAT lookup bypass using iptables/ip6tables DNAT, and two-socket delivery on different ports.

State and persistence: ephemeral namespaces, veths, iptables NAT rules, background receiver PIDs, and process-local `ret`. `trap cleanup EXIT` kills jobs and deletes the peer namespace.

Dependencies and integration: requires root, iproute2, ethtool, iptables/ip6tables NAT, compiled benchmark helpers, and `lib.sh`. Uses kselftest-style exit code via script status.

Risks: relies on veth NAPI timing for aggregation and on iptables availability. The string split around literal `rx` is simple but controlled by callers. Background receiver synchronization depends on local port readiness.

Test signals: expected packet count, length, UDP_GRO cmsg size, and exit status from RX/TX determine pass/fail. NAT and two-socket cases catch socket lookup and GRO destination matching regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_bench.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_bench.sh

Purpose: UDP/TCP GRO benchmark harness over veth with an XDP dummy program attached to the receiver side so data is touched while measuring GSO/GRO throughput paths.

Important APIs/functions: `run_one()` creates a peer namespace and veth, assigns IPv4/IPv6 addresses, attaches `lib/xdp_dummy.bpf.o` to `veth1`, starts UDP and TCP receivers (`udpgso_bench_rx`, one with `-t`), waits for UDP port 8000, and runs `udpgso_bench_tx`. `run_udp()` runs GSO-only and GSO+GRO (`-G` receiver) modes; `run_tcp()` runs TCP.

Control flow: checks that the BPF object exists, then with no args runs IPv4 and IPv6 benchmark sets. With `__subprocess` it performs setup and execution; otherwise it wraps arguments through `in_netns.sh`.

State and persistence: temporary namespace/veth/XDP state and background receiver processes are cleaned on exit. No result file is persisted; throughput is printed by helpers.

Dependencies and integration: requires built BPF object, compiled bench helpers, XDP attach support, root privileges, and `lib.sh`. It is a performance-oriented selftest/benchmark rather than a strict functional validator.

Risks: script appears to call `run_tcp "${ipv4_args}"` under the IPv6 heading, likely preserving existing upstream behavior but worth noting because it means IPv6 TCP benchmark may not use IPv6 args. Benchmark output depends on CPU/load and is not checked against thresholds.

Test signals: primarily successful command completion and printed throughput. Missing BPF object exits nonzero with a build hint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_bench.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_frglist.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_frglist.sh

Purpose: UDP GRO fraglist benchmark/test variant that enables `rx-gro-list` and uses BPF NAT helpers to exercise IPv6-to-IPv4 transformed traffic through GRO fraglist paths.

Important APIs/functions: resembles `udpgro_bench.sh` but additionally enables `ethtool -K veth1 rx-gro-list on`, attaches `lib/xdp_dummy.bpf.o`, installs clsact qdisc and `nat6to4.bpf.o` ingress/egress tc BPF filters, and runs receivers/transmitters with verbose IPv4 receive arguments after IPv6 transmission.

Control flow: validates both BPF objects exist, then no-arg `run_all()` builds IPv6 sender arguments and executes TCP and UDP benchmark cases through `in_netns.sh`. `run_one()` creates namespace/veth topology, attaches XDP and tc filters, starts receiver, waits for port readiness, and runs TX.

State and persistence: temporary namespace, veth, XDP, tc qdisc/filter state, and background jobs. Cleaned by trap. No files are persisted.

Dependencies and integration: requires built `lib/xdp_dummy.bpf.o` and `nat6to4.bpf.o`, tc BPF direct-action support, ethtool rx-gro-list support, compiled benchmark helpers, and root.

Risks: contains debug `echo ${rx_args}`/`echo ${args}` output and spacing quirks, so output is less polished than pure kselftest TAP. Functional result depends on BPF helper behavior and kernel fraglist offload support.

Test signals: command exit status and benchmark/helper output. Missing BPF artifacts produce immediate failure with "Run make first".
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_frglist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_fwd.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_fwd.sh

Purpose: Functional and performance tests for UDP GRO forwarding, GRO fraglist, and GRO forwarding over VXLAN/UDP tunnels for IPv4 and IPv6, including checksum validation after forced segmentation and reaggregation.

Important APIs/functions: `create_ns()` creates source/destination namespaces and veth, optionally attaching XDP dummy on destination. `create_vxlan_endpoint()` and `create_vxlan_pair()` build VXLAN overlay pairs for IPv4 and IPv6. `run_test()` sends one GSO packet of ten UDP frames, counts iptables/ip6tables INPUT hits on UDP 8000 and VXLAN 4789, and validates expected aggregation. `run_test_csum()` uses iperf3 and nstat checksum counters. `run_bench()` pins sender/receiver to CPUs and toggles RPS.

Control flow: loops over families 4 and 6. For each family it tests no GRO, GRO fraglist, GRO fwd with NAT to bypass socket lookup guard, performance before/after `rx-udp-gro-forwarding`, GRO fraglist over VXLAN, GRO fwd over VXLAN with NAT and neighbor priming, then a bridge/veth segmentation topology that disables TX offloads and checks no UDP checksum errors during iperf3.

State and persistence: namespaces, veths, VXLAN devices, bridges, iptables rules, ethtool feature flags, RPS sysfs changes, nstat counters, and background jobs are temporary. `cleanup` runs between scenarios and on exit.

Dependencies and integration: requires root, iproute2 VXLAN/bridge/netns, ethtool features (`generic-receive-offload`, `rx-gro-list`, `rx-udp-gro-forwarding`), iptables/ip6tables, jq, iperf3, compiled benchmark helpers, and BPF object. Uses `lib.sh`.

Risks: packet counter expectations allow VXLAN noise tolerance but still depend on background control traffic. Performance tests skip with one CPU but are not thresholded. NAT dependency and feature availability can cause environment-specific failures.

Test signals: explicit pass/fail lines per scenario based on RX/TX exit status, iptables packet counters, VXLAN counter tolerance, and zero UDP checksum errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_fwd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso.c

Purpose: Core UDP segmentation offload regression test. It sends UDP payloads at and beyond MTU/MSS boundaries over IPv4 and IPv6 and verifies send success/failure and receiver datagram segmentation lengths.

Important APIs/types/functions: defines `UDP_SEGMENT`, `UDP_MAX_SEGMENTS`, MTU/MSS constants, `struct testcase`, and IPv4/IPv6 testcase arrays. Uses `IP_MTU_DISCOVER`/`IPV6_MTU_DISCOVER` to prevent fragmentation, `IP_MTU`/`IPV6_MTU` reads for connected sockets, `sendmsg()` with UDP_SEGMENT cmsg or `setsockopt(SOL_UDP, UDP_SEGMENT)`, optional `MSG_MORE`, optional IPv6 hop options, and `recv()` checks.

Control flow: command-line flags select IPv4/IPv6, connected/connectionless, MSG_MORE, receive suppression, setsockopt-vs-cmsg, and a specific test ID. `run_test()` binds RX, sets timeout, creates TX, enables PMTU discovery, then runs all testcase rows for connectionless and/or connected paths. `run_one()` applies optional IPv6 extension headers, sets UDP_SEGMENT if requested, sends, checks whether failure was expected, clears hopopts, then receives exactly the expected full MSS datagrams and trailing datagram and checks no extras remain.

State and persistence: static global buffer and process-global config. Kernel state is only local UDP sockets and route MTU/loopback setup done externally by `udpgso.sh`. No persistent files.

Dependencies and integration: driven by `udpgso.sh`; requires kernel UDP GSO support and root or namespace privileges depending on setup. Uses standard sockets only.

Risks: error mapping treats `EMSGSIZE`, `ENOMEM`, and `EINVAL` as expected send failure classes. Receive validation depends on loopback/local MTU being configured to `CONST_MTU_TEST`. Extension header case tests a narrow IPv6 hopopts path.

Test signals: any mismatch in send expectation, path MTU, receive segment length/count, or unexpected extra datagram aborts with `error(1, ...)`; success prints `OK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso.sh

Purpose: Shell regression matrix for `udpgso`, setting up loopback and dummy-device MTU/offload conditions to exercise software and hardware UDP GSO and checksum combinations.

Important APIs/functions: setup helpers configure loopback addresses/MTU, local routes with MTU 1500, and dummy `sink` with IPv4/IPv6 addresses. Offload helpers toggle `tx-checksum-ip-generic` and `tx-udp-segmentation` on the dummy device.

Control flow: when invoked with a helper name, it runs that setup, shifts past `--`, and execs the requested command. Normal no-arg flow runs `udpgso` through `in_netns.sh` for IPv4/IPv6 cmsg, setsockopt, connected route MTU, MSG_MORE, hardware GSO/hardware checksum no-receive, software GSO/hardware checksum no-receive, and software GSO/software checksum no-receive.

State and persistence: all state is inside the namespace provided by `in_netns.sh`: loopback addresses, local routes, dummy link, and ethtool offload flags. No persistent files.

Dependencies and integration: requires `ip`, `ethtool`, dummy netdev, namespace wrapper, and compiled `udpgso`.

Risks: uses `set -o errexit` and `nounset`, so setup failures stop the matrix. It assumes ethtool can manipulate dummy offloads as expected. `shift 2` assumes the helper-call ABI includes `test_* --`.

Test signals: all nested `udpgso` commands must exit 0. Echo labels identify which configuration failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench.sh

Purpose: kselftest-style launcher for UDP/TCP GSO benchmark helper pair. It runs functional audit modes for plain UDP, sendmmsg, UDP GSO, zerocopy, TX timestamping, and TCP over IPv4/IPv6 loopback namespaces.

Important APIs/functions: maintains kselftest counters `num_pass`, `num_skip`, and `num_err` and emits PASS/SKIP/FAIL. `run_one()` starts UDP and TCP receivers on the same port, waits via `ss` until both listen, and runs `udpgso_bench_tx`. `run_udp()` enumerates UDP, sendmmsg, GSO, zerocopy, timestamp, and audit combinations. `run_tcp()` runs TCP and TCP zerocopy, with intermittent TCP zerocopy audit intentionally disabled.

Control flow: no-arg path runs full IPv4 and IPv6 matrices inside `in_netns.sh` and then calls `kselftest_exit()`. `__subprocess` runs the actual receiver/TX pair. Other args are wrapped into `run_in_netns()`.

State and persistence: process-local pass/skip/fail counters and background receiver PIDs. The namespace wrapper owns network state. No files are persisted.

Dependencies and integration: requires compiled `udpgso_bench_rx`/`tx`, `ss`, namespace wrapper, and kernel support for optional zerocopy/timestamping. TX helper returns `KSFT_SKIP` for unsupported zerocopy.

Risks: readiness check expects two `ss` listening entries for the port. Background jobs are killed with SIGHUP on exit. Throughput is not thresholded; audit modes validate completion counts.

Test signals: each subtest exit code is classified into PASS/SKIP/FAIL and final script status follows kselftest semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench_rx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench_rx.c

Purpose: Receiver and verifier for UDP/TCP GSO/GRO benchmark tests. It binds IPv4 or IPv6 sockets, optionally enables UDP_GRO, accepts TCP, drains receive queues, validates datagram lengths/counts/GRO cmsgs and optional payload patterns, and prints throughput.

Important APIs/functions: uses `SO_RCVBUF`, `SO_REUSEPORT`, `UDP_GRO`, `recvmsg()` with `MSG_TRUNC|MSG_DONTWAIT`, cmsg parsing for `SOL_UDP/UDP_GRO`, `poll`, TCP `accept`, and `SIGINT` interruption. Config flags cover family, bind address, port, TCP, verify, read-all, GRO segment, expected packet count/length/GSO size, connect timeout, and receive timeout.

Control flow: `main()` parses options, installs SIGINT handler, and calls `do_recv()`. `do_socket()` creates/binds sockets and accepts TCP if needed. `do_recv()` optionally sets UDP_GRO, polls with initial connect timeout then receive timeout, flushes TCP or UDP, reports throughput once per second when no fixed expected count is set, and at exit checks expected packet count.

State and persistence: global config plus `packets` and `bytes` counters. No persistent files. State resets per process invocation.

Dependencies and integration: paired with `udpgso_bench_tx.c` and shell wrappers. Requires UDP_GRO kernel support for `-G` and usual socket privileges.

Risks: UDP flush has a budget of 256 datagrams per poll iteration, so extremely bursty traffic is processed over multiple loops. Verify mode only supports UDP, not TCP. Expected GSO cmsg `-S -1` is used by callers to assert no cmsg.

Test signals: exits nonzero on bad length, packet count, GRO cmsg size, payload pattern, socket errors, or poll anomalies. Throughput lines are informational when not in fixed-count mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench_tx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench_tx.c

Purpose: Transmitter for UDP/TCP GSO benchmarks and audit tests. It can send plain UDP chunks, UDP_SEGMENT GSO messages, sendmmsg batches, TCP streams, zerocopy sends, and TX timestamped sends while tracking completion/error-queue acknowledgements.

Important APIs/functions: supports `SO_ZEROCOPY`, `MSG_ZEROCOPY`, `SO_TIMESTAMPING`, `SOF_TIMESTAMPING_TX_SOFTWARE/HARDWARE`, `UDP_SEGMENT`, `sendmmsg`, `sendmsg`, `sendto`, TCP `send`, PMTU discovery, error queue `recvmsg(MSG_ERRQUEUE)`, and optional CPU affinity. `flush_cmsg()` accounts timestamp and zerocopy completions; `print_audit_report()` enforces expected completion counts in audit mode.

Control flow: parses options requiring `-4` or `-6` and a destination, validates incompatible combinations, computes MSS and maximum payload, fills rotating payload buffers, creates and optionally connects a socket, enables zerocopy/timestamp/PMTU, then loops sending until message count, runtime, or SIGINT. Periodically flushes error queue for zerocopy/timestamps and prints per-second throughput; final audit flush waits for completions and validates counts.

State and persistence: global config, total counters, timestamp/zerocopy completion counters, start/end time, and static packet buffers. No persistent files.

Dependencies and integration: driven by `udpgso_bench.sh`, `udpgro*.sh`, `veth.sh`, and `udpgro_fwd.sh`. Requires receiver availability, optional kernel zerocopy/timestamp support, and returns `KSFT_SKIP` when zerocopy is unsupported.

Risks: audit mode depends on timely error queue completions within `cfg_poll_loop_timeout_ms`. Hardware TX timestamping may not be available on virtual devices. Payload length is capped by `ETH_MAX_MTU - hdrlen`.

Test signals: normal mode prints throughput and exits on socket errors. Audit mode fails if TX timestamp count or zerocopy completion count does not match sends, making it useful as a correctness check in shell wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/unicast_extensions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/unicast_extensions.sh

Purpose: IPv4 unicast extension selftest that validates Linux behavior for historically reserved address ranges: allowed 0/8, 240/4, and high 255.255 subnets; forbidden 0.0.0.0, 255.255.255.255, 127/8, and 224/4 class D.

Important APIs/functions: uses `nettest`, `ping`, namespaces, veth, and routes. `_do_segmenttest()` checks assignment, ping both directions, and TCP connectivity on a shared segment. `_do_route_test()` checks gateway routing through a router namespace with IP forwarding. `segmenttest()` and `route_test()` wrap setup/cleanup, invert result when `expect_failure=true`, and report via `show_result()`.

Control flow: after `check_gen_prog nettest`, the script runs a fixed sequence of positive tests for 240/4, 0/8, 255.255/16, 255.255.255/24, route tests across extended ranges, and lowest-subnet-address cases. It then sets `expect_failure=true` and runs forbidden address/routing cases.

State and persistence: temporary namespaces and veths are killed/cleaned per test. `result` accumulates failures. Output is hidden during operations and restored for result lines. No persistent files.

Dependencies and integration: requires root, iproute2 netns/veth, ping, and generated `nettest`. Uses `lib.sh` for namespace setup/cleanup.

Risks: expected behavior is intentionally policy-sensitive; kernel changes to reserved address handling require flipping expectations. Use of global `expect_failure` inverts all following tests until unset.

Test signals: each scenario prints `[ OK ]` or `[FAIL]`; final exit status is `result`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/unicast_extensions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/veth.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/veth.sh

Purpose: Broad veth selftest for GRO/TSO feature propagation, XDP interactions, UDP GRO forwarding aggregation, channel count constraints, and optional channel-change stress under traffic.

Important APIs/functions: creates paired namespaces and veths, uses ethtool feature/channel APIs, attaches `lib/xdp_dummy.bpf.o`, uses `udpgso_bench_tx/rx` for aggregation checks, and `nstat` with a temp history file to count `IpInReceives`. Helpers validate feature flags (`chk_gro_flag`, `chk_tso_flag`), channel counts (`chk_channels`), and GRO aggregation packet counts (`chk_gro`).

Control flow: checks BPF object, warns about CPU-dependent skips, then runs multiple fresh topologies: default feature state and aggregation, GRO on destination, XDP attach while down with GRO off/on, channel configuration validity, XDP constraints on RX/TX channels, GRO/XDP/TSO flag changes while devices down/up, and final aggregation after disabling GRO/TSO. Optional `-s seconds` runs concurrent channel churn and UDP traffic.

State and persistence: uses temp stats file under `/tmp`, two namespaces, veth features/channels/XDP state, and background jobs. Cleanup removes stats file and namespaces. `ret` tracks failures.

Dependencies and integration: requires root, ethtool channel support for veth, XDP BPF object, `nproc`, `nstat`, and compiled UDP bench helpers.

Risks: CPU count changes test coverage. Some checks rely on ethtool output text. Stress mode can be noisy and is skipped unless enough CPUs are present.

Test signals: feature/channel checks print expected vs actual; aggregation expects one packet when GRO works and ten when it does not. Invalid channel operations are expected to fail and are flagged if they succeed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/veth.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vlan_bridge_binding.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vlan_bridge_binding.sh

Purpose: Tests VLAN upper-device `bridge_binding` operstate behavior on a VLAN-filtering bridge with multiple ports and VLAN memberships.

Important APIs/functions: uses `lib.sh` ADF/defer helpers (`adf_ip_link_add`, `adf_bridge_vlan_add`, `defer_scope_push/pop`, `tests_run`) plus `jq`. `setup_prepare()` creates bridge `br`, veth ports `d1..d3`, enslaves ports, and configures VLAN IDs 11-14 with different membership sets. `add_vlans()` creates `br.<vid>` VLAN upper devices with `bridge_binding` on/off. `check_operstate()` busywaits and maps JSON `operstate` to boolean.

Control flow: declared `ALL_TESTS` covers binding on, binding off, toggles on/off, and toggles while lower or upper devices are down. `do_test_binding()` repeatedly downs combinations of d1/d2/d3, optionally injects a bridge_binding toggle, checks expected operstates for VLAN uppers, then restores via defer scopes.

State and persistence: bridge, veths, VLAN devices, bridge VLAN database, and interface states are temporary in current namespace/test context. Defer scopes restore state within tests; exit trap cleans remaining scopes. No files.

Dependencies and integration: requires root, bridge VLAN filtering, VLAN devices, `jq`, iproute2, and `lib.sh` defer/ADF helpers.

Risks: operstate transitions are asynchronous, so checks depend on `busywait 1000`. Expected state vectors are tightly coupled to configured VLAN memberships.

Test signals: `log_test` reports each high-level scenario. Failures show actual/expected operstate from `check_err`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vlan_bridge_binding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vlan_hw_filter.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vlan_hw_filter.sh

Purpose: Regression tests for VLAN ID 0 and RX VLAN hardware filter toggling on bond devices, targeting previous crash/unregister/memleak paths.

Important APIs/functions: creates a unique namespace per test, uses `ip link` for bond/veth/VLAN creation and deletion, and `ethtool -K rx-vlan-filter` toggles. `tests_run()` executes `TESTS` or all tests; `fail()` records errors.

Control flow: tests cover deleting a veth peer after VLAN 0 devices on bond/slave, deleting VLAN 0 after enabling rx-vlan-filter while bond is up/down, adding VLAN 0 after enabling filter, deleting VLAN while bond down, and deleting a bond after toggling rx-vlan-filter off. Each test calls setup and cleanup explicitly.

State and persistence: temporary namespace and devices only. Trap attempts cleanup on exit. `ret` accumulates failures.

Dependencies and integration: requires bond driver support, VLAN support, ethtool, root privileges, and iproute2.

Risks: cleanup is called both in tests and trap; errors deleting already-removed namespace are ignored. Tests detect absence of crashes indirectly through command success, not deeper leak instrumentation.

Test signals: any failed key operation calls `fail` and final exit is nonzero. Kernel crash/hang would be an external failure signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vlan_hw_filter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf-xfrm-tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf-xfrm-tests.sh

Purpose: Tests combinations of VRF, XFRM/IPsec tunnel policies/states, xfrm interfaces, and qdisc delay to ensure VRF-routed traffic still matches XFRM policy and works with/without netem on the VRF device.

Important APIs/functions: namespace/veth/VRF setup helpers, `setup_xfrm()` adding IPv4/IPv6 XFRM policies and ESP states with fixed auth/enc keys and SPIs, `setup_xfrm_dev()` creating `xfrm0` with `if_id`, and `run_cmd_host1()` executing commands in host1. `log_test()` tracks pass/fail counts and optional pause.

Control flow: main cleans/sets up two namespaces connected by veth, enslaves host1 eth0 to VRF `red`, then runs `run_tests()` twice: once with no qdisc and once after adding `tc qdisc netem delay 100ms` to the VRF. `run_tests()` verifies ping without IPsec, address-based XFRM policy for IPv4/IPv6, IPv6 VRF selector behavior, and IPv4/IPv6 traffic over an xfrm device. Some known-failure selector cases are commented out.

State and persistence: ephemeral namespaces, VRF, XFRM state/policy databases, xfrm device, qdisc, routes, addresses, and sysctls. Cleanup flushes XFRM and deletes namespaces/devices. No files.

Dependencies and integration: requires root, VRF, XFRM/ESP algorithms, xfrm interface support, ping/ping6, tc netem, and `lib.sh`.

Risks: crypto algorithm availability and xfrm interface support can vary. Commented known failures document unresolved selector matching behavior. The second run reuses topology with qdisc, so cleanup between runs is focused on XFRM rather than full namespace rebuild.

Test signals: ping exit status under `ip vrf exec` is compared to expected 0; totals are printed and final status is nonzero on any failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf-xfrm-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf_route_leaking.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf_route_leaking.sh

Purpose: Comprehensive VRF route-leaking test for ICMP error route lookup, traceroute, fragmentation errors, and local TCP/UDP/ICMP connections in symmetric and asymmetric topologies across IPv4 and IPv6.

Important APIs/functions: uses namespace setup helpers, `create_vrf`, `setup_sym`, `setup_asym`, `check_connectivity`, `run_cmd_grep`, and `nettest`. Symmetric topology has h1-r1-h2 with blue/red VRFs and bidirectional route leaks; asymmetric topology uses h1/h2 bridges plus r1/r2 where return traffic uses r2 and red lacks a route back to n1.

Control flow: parses `-4`, `-6`, `-t`, `-p`, `-v`; expands named test groups; then dispatches each selected test through a `case`. Tests rebuild topology per scenario, validate base connectivity, and check traceroute hop, TTL exceeded messages, fragmentation/packet-too-big messages, local VRF ping, and local TCP/UDP via `nettest`.

State and persistence: namespaces h1/h2/r1/r2, bridges, veths, VRFs, routes, MTUs, forwarding sysctls, and background nettest servers are ephemeral. `cleanup` deletes namespaces after all tests and each setup begins with cleanup.

Dependencies and integration: requires root, VRF/veth/bridge/netns, ping or ping6, optional traceroute/traceroute6 for traceroute tests, generated `nettest`, and `lib.sh`.

Risks: grep patterns depend on ping/traceroute output text. Asymmetric topology intentionally lacks a red return leak; only TTL/traceroute style tests are suitable there. Missing traceroute prints SKIP-like text but returns from that individual test.

Test signals: pass/fail counters report each scenario. Grep success on ICMP/traceroute output and nettest exit status are the main correctness signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf_route_leaking.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf_strict_mode_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf_strict_mode_test.sh

Purpose: Tests the `net.vrf.strict_mode` sysctl semantics in the init namespace, a test namespace, and mixed namespace interactions. Strict mode prevents multiple VRFs from sharing a table ID.

Important APIs/functions: uses `modprobe vrf`, `/proc/sys/net/vrf/strict_mode`, `ip link add type vrf table`, `ip -d -o link show type vrf`, and `lib.sh` namespace helpers. Functions read/set strict mode, add/delete/configure VRFs, count VRFs by table ID, and log expected success/failure.

Control flow: validates root, `ip`, and strict_mode sysctl presence. `setup()` creates a test namespace. Default `TESTS="init testns mix"`: init tests add/configure VRFs, enable strict mode, expect duplicate table additions to fail, disable strict mode, add duplicates, and expect enabling to fail while duplicates exist. Testns tests do similar inside a namespace. Mix tests verify sysctl state isolation between init and testns and repeated idempotent enable/disable behavior.

State and persistence: mutates init namespace VRFs `vrf100..102` and test namespace VRFs, plus strict_mode sysctls. `cleanup()` deletes created VRFs/netns and resets init strict_mode to 0.

Dependencies and integration: requires root, VRF module/sysctl, iproute2, and `lib.sh`.

Risks: because it touches init namespace VRFs/sysctl, cleanup is important and failure mid-test could leave local VRFs until cleanup trap or manual removal. Exit code 2 from `ip link add` is expected for duplicate-table rejection and is shell/iproute dependent.

Test signals: logs each expected state transition and final pass/fail counts. SKIP returned when root/ip/VRF sysctl support is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf_strict_mode_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_policy.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_policy.sh

Purpose: XFRM policy resolution regression test covering overlapping policy tree merges, direct exceptions, wildcard/dummy policies, hthresh changes, policy lookup stability, and packet matching through an IPsec tunnel.

Important APIs/functions: builds ns1/ns2 hosts and ns3/ns4 IPsec gateways. `do_esp()` and `do_esp_policy()` install ESP states and out/fwd policies. `do_exception()` installs higher-priority direct tunnel and allow-bypass policies. `do_overlap()` creates overlapping block policies to stress inexact policy tree merges. `check_xfrm()` uses ping plus iptables `-m policy` FORWARD counters to detect whether traffic used IPsec. `check_hthresh_repeat()` and `check_random_order()` stress policy hash threshold transitions and insertion ordering.

Control flow: after root/ip/iptables checks, creates topology, configures IPv4/IPv6 addresses/routes/forwarding, installs iptables counters, installs ESP policies/states for both directions/families, adds dummy policies, validates `ip xfrm policy get`, verifies default IPsec match, adds exceptions, rechecks behavior before/after overlap policies, changes hthresh values, flushes/readds policies, tests repeated hthresh updates and random insertion lookup, then cleans namespaces.

State and persistence: temporary namespaces, veths, XFRM policy/state DBs, iptables rules/counters, and routes. No persistent files.

Dependencies and integration: requires root, XFRM/ESP crypto support, iproute2 xfrm, iptables policy match, ping, and `lib.sh`.

Risks: uses random addresses/order for stress, so failures may be intermittent but should expose tree bugs. iptables counter parsing is brittle but direct. Heavy policy insertion can take time.

Test signals: printed PASS/FAIL for policy-before-exception, exception behavior, hthresh changes, repeat updates, and random-order lookup. Final exit status `ret` captures failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_policy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_policy_add_speed.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_policy_add_speed.sh

Purpose: XFRM policy insertion performance and scalability smoke test. It inserts growing batches of IPv4 block policies and verifies the kernel reports the same number inserted.

Important APIs/functions: `do_dummies4()` generates `ip xfrm policy add ... action block` commands with nested loops over source/destination prefixes. `do_bench()` writes a batch file, times `ip -batch`, counts generated policies, and compares with `ip xfrm policy show | grep "action block" | wc -l`.

Control flow: creates one namespace, then tests batch sizes 100, 1000, 10000, and up to 100000 unless `KSFT_MACHINE_SLOW=yes`, where max is 10000. Each batch flushes existing policies before generating a new set and times insertion with a 4-minute timeout.

State and persistence: one temporary namespace and one temp batch file; cleanup deletes namespace and file. XFRM policies are ephemeral.

Dependencies and integration: requires root, iproute2 xfrm, timeout utility, and `lib.sh`. Intended as speed/regression telemetry rather than strict threshold benchmark.

Risks: no fixed performance threshold, only timeout and count mismatch. Large batches can be resource-intensive. Random-free deterministic generation may still stress memory/time.

Test signals: prints insertion count and elapsed ms; nonzero if timeout/cancel or policy count mismatch occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_policy_add_speed.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_state.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_state.sh

Purpose: XFRM/IPsec state behavior test for ICMP error source address and MTU exceeded handling over tunnel mode ESP across multi-hop IPv4 and IPv6 topologies.

Important APIs/functions: declares test table for unreachable and MTU cases. Uses namespace-set builders (`setup_ns_set_v4`, `v4x`, `v6`, `v6x`), `setup_namespaces`, `setup_network`, nftables ICMP/ESP filters, and `setup_xfrm_mode()` to install ESP policies/states with AEAD rfc4106(gcm(aes)) and `flag icmp` on relevant fwd/out policies/states. `run_test()` isolates each test in a subshell with cleanup trap.

Control flow: command-line options control pause/verbose/exit-on-fail and optional test names. For each listed test, `run_test()` invokes a named test function. Each test sets up a topology, verifies base ping to reachable endpoint, then runs a ping to unreachable or oversized destination and greps for expected ICMP source and MTU text. MTU tests adjust route MTUs on r2, r3, or s2 depending on scenario.

State and persistence: temporary namespaces a/r1/s1/r2/s2/r3/b or shortened x topology, veths, routes, sysctls, nftables rules, XFRM policy/state, and globals describing last command/output. Cleanup deletes all namespaces after each test. No files.

Dependencies and integration: requires root, iproute2, nft, ping, XFRM/ESP AEAD support, and `lib.sh`. Kselftest skip code is used when setup needs root and is unavailable.

Risks: grep patterns depend on ping output wording. `run_cmd_err` always returns 0 after capturing status in `rc`, so tests must inspect `$out`/`rc` explicitly; current test functions do that by grepping output. Complex dynamic namespace variable construction is sensitive to shell behavior.

Test signals: per-test `[ PASS ]`, `[SKIP]`, or failure output with command/output when verbose. Final exitcode is 0, 1, or skip depending on aggregate results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_state.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ynl.mk -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ynl.mk

Purpose: Makefile include for networking selftests that need YNL-generated rtnetlink/netlink family bindings and `libynl.a`.

Important APIs/variables: consumes `YNL_GENS`, `YNL_GEN_PROGS`, and `YNL_GEN_FILES`. Computes `YNL_OUTPUTS` under `$(OUTPUT)` and `YNL_SPECS` from `Documentation/netlink/specs/*.yaml`. Adds include paths for kernel UAPI headers, YNL lib, and generated headers to targets that depend on YNL.

Control flow: all YNL output binaries/files depend on `$(OUTPUT)/libynl.a`. A hash signature file `.libynl-$(YNL_GENS_HASH).sig` is created from `YNL_GENS`; changing families removes old signatures and forces rebuilding `libynl.a`. The lib target deletes any source-tree `tools/net/ynl/libynl.a`, invokes make in `tools/net/ynl` with `GENS="$(YNL_GENS)" RSTS="" libynl.a`, and copies the archive to `$(OUTPUT)`.

State and persistence: writes build artifacts in `$(OUTPUT)` and temporarily in `tools/net/ynl`. `EXTRA_CLEAN` removes YNL Python caches, library object/archive/dependency files, signature files, and output archive.

Dependencies and integration: included by selftest Makefiles using generated YNL C bindings, such as TUN/TAP tests that include `rt-*-user.h`. Depends on `sha1sum`, make, generated spec YAMLs, and top-level kernel source variables.

Risks: content changes within `YNL_GENS` list are tracked by hash, but changes to generator internals rely on make dependencies outside this snippet. It removes source-tree lib artifacts, which is expected for this build but can surprise manual builds.

Test signals: build success and correct regeneration of `libynl.a`; stale-family bugs appear as missing generated headers/symbols or link failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ynl.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/Makefile

Purpose: kselftest Makefile for nolibc tests, building both a `nolibc-test` binary without libc and a `libc-test` binary from the same sources for comparison.

Important APIs/variables: defines `TEST_GEN_PROGS := nolibc-test libc-test`, includes `../lib.mk`, compiler helpers, and `Makefile.include`. Defines `cc-option` through `__cc-option`. `nolibc-test` has custom `CFLAGS` with `-nostdlib -nostdinc -static`, nolibc and UAPI include paths, and `CFLAGS_NOLIBC_TEST`; `LDLIBS` uses `-lgcc` when not LLVM. Both targets depend on `NOLIBC_TEST_SOURCES`; nolibc target also orders after `headers`.

Control flow: normal kselftest build uses inherited rules for `TEST_GEN_PROGS`, with explicit flags/LDLIBS for nolibc. `libc-test` has an explicit compile/link recipe using `$(LINK.c)`. `help` delegates to `Makefile.nolibc help`.

State and persistence: writes build outputs under `$(OUTPUT)`. No runtime state.

Dependencies and integration: integrated with kernel selftests build system, nolibc headers under `tools/include/nolibc`, generated kernel headers, and optional architecture/compiler flags from `Makefile.include`.

Risks: static nolibc link is sensitive to compiler/architecture support and `-lgcc` availability outside LLVM. Missing generated headers break the ordered `headers` dependency.

Test signals: successful build of both generated programs; runtime behavior is in the binaries built from `NOLIBC_TEST_SOURCES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-ignore-errno.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-ignore-errno.c

Purpose: Tiny compile-only source that defines `NOLIBC_IGNORE_ERRNO` and includes nolibc via `<stdlib.h>` to ensure nolibc headers compile when errno support is intentionally ignored.

Important APIs/functions: no functions are defined. The important API is the preprocessor contract: `#define NOLIBC_IGNORE_ERRNO` before including nolibc headers.

Control flow: none at runtime; the file participates in compilation/linkage through the nolibc test source list.

State and persistence: no state.

Dependencies and integration: depends on include paths arranged by the nolibc Makefile. It validates header-level conditional compilation in nolibc.

Risks: because it is compile-only, it catches symbol/header failures but not runtime errno semantics.

Test signals: successful compilation is the signal; any conflict with `NOLIBC_IGNORE_ERRNO` should surface as a build error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-ignore-errno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-linkage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-linkage.c

Purpose: Nolibc linkage helper that exposes the address of `errno` and verifies constructor execution via a global bitmask.

Important APIs/functions: includes `nolibc-test-linkage.h` and `<errno.h>`. `linkage_test_errno_addr()` returns `&errno`, allowing tests to compare errno storage linkage. Global `linkage_test_constructor_test_value` starts at 0. Two `__attribute__((constructor))` functions set bit 0 and bit 1.

Control flow: constructors run before `main()` of the final test binary, mutating the global. The exported function is called by other test code to inspect errno address behavior.

State and persistence: one process-global integer bitmask; no persistent files.

Dependencies and integration: compiled into nolibc/libc test binaries with the companion header. Behavior differs meaningfully under nolibc vs libc and helps catch startup/linkage regressions.

Risks: constructor support can vary by architecture/link mode, especially with `-nostdlib -static`; that is exactly what the test aims to detect. The file itself does not assert; consumers must check the global/function.

Test signals: successful link plus downstream checks that both constructor bits are set and errno address semantics are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-linkage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-linkage.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-linkage.h

Purpose: Header declaring linkage-test symbols shared between nolibc test sources.

Important APIs/types/functions: include guard `_NOLIBC_TEST_LINKAGE_H`; declares `void *linkage_test_errno_addr(void);` and `extern int linkage_test_constructor_test_value;`.

Control flow: none; declarations are consumed by test code and implemented in `nolibc-test-linkage.c`.

State and persistence: exposes one external process-global integer owned by the C file.

Dependencies and integration: used by nolibc/libc test binaries to test errno linkage and constructor execution.

Risks: minimal. Any signature mismatch with the C implementation would be caught at compile/link time.

Test signals: successful compilation and downstream checks using the declared symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test-linkage.h -->
