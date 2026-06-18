# Research: subset-b-006858

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/busy_poller.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/busy_poller.c

Purpose: this C helper is an executable TCP receiver used by networking selftests to exercise per-epoll busy-poll parameters together with netdev NAPI configuration. It listens on a configurable IPv4 address and port, accepts one TCP connection, writes received stream data to a configured output file, and exits when the peer closes. Before serving traffic it programs NAPI parameters for a selected interface index through the YNL netdev family.

Important APIs and types: it uses `struct epoll_params`, `EPIOCSPARAMS`, `EPIOCGPARAMS`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, nonblocking TCP sockets, and `ioctl` against the epoll fd. The file carries local epoll ioctl definitions for older libc/kernel header combinations. Netdev integration is through generated YNL bindings in `netdev-user.h`: `ynl_sock_create`, `netdev_napi_get_dump`, `netdev_napi_set`, and request setters for `defer_hard_irqs`, `gro_flush_timeout`, `irq_suspend_timeout`, and optional threaded NAPI mode.

Control flow: `main` calls `parse_opts`, `setup_queue`, and `run_poller`. `parse_opts` validates all numeric bounds before writing globals such as `cfg_busy_poll_usecs`, `cfg_busy_poll_budget`, `cfg_ifindex`, and NAPI settings. `setup_queue` opens a YNL netdev socket, dumps NAPI objects for the interface, takes the first NAPI id, and applies the requested queue attributes. `run_poller` opens the output file, creates a nonblocking TCP listener, installs epoll busy-poll params with `EPIOCSPARAMS`, adds the listener to epoll, accepts a connection on listener events, then drains `EPOLLIN` reads until nonpositive return and writes each chunk with `write_chunk`.

State and persistence: persistent state is limited to the output file and kernel-side epoll/NAPI/socket settings. Runtime state is mostly global configuration plus fd-local epoll and socket registrations. The file descriptor for the output is closed when a hangup event is observed; there is no explicit fsync or truncation, so repeated runs can overwrite only from offset zero while leaving old trailing bytes if a new run is shorter.

Dependencies and integration points: requires root or sufficient net admin privileges for NAPI netdev operations, YNL generated netdev user headers/libraries, an ifindex, and kernel support for the epoll busy-poll ioctl. It is intended to be coordinated by a shell test that drives a sender and compares the captured output.

Risks and test signals: `setup_queue` assumes one NAPI object and does not null-check the dump result before dereferencing, so kernel/YNL failures can crash rather than emit a clean selftest failure. `bind` reports with `error(0, ...)` and then continues, which can lead to a later misleading listen or accept failure. The read loop treats all nonpositive reads as temporary completion and does not distinguish `EAGAIN` from fatal read errors. Good test signals are successful YNL NAPI programming, successful epoll ioctl, byte-for-byte output file content, and clean exit on `EPOLLRDHUP` or `EPOLLHUP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/busy_poller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/Makefile

Purpose: this kselftest makefile builds and registers the CAN raw-filter selftest in the `tools/testing/selftests/net/can` subtree. It declares `test_raw_filter.sh` as the executable test program and `test_raw_filter` as a generated binary.

Important APIs and variables: `top_srcdir = ../../../../..` points include paths at the kernel source root. `CFLAGS` enables warnings, optimization, debug info, the kernel UAPI include directory, and `$(KHDR_INCLUDES)`. `TEST_PROGS` and `TEST_GEN_FILES` are the kselftest/lib.mk contract variables consumed by `../../lib.mk`.

Control flow and integration: including `../../lib.mk` supplies the build/install/run rules. The generated C test depends on the kselftest harness and CAN UAPI headers, while the shell wrapper handles CAN interface setup.

State and dependencies: this file persists no runtime state. Build state is the compiled `test_raw_filter` artifact. It depends on the surrounding kselftest make infrastructure and suitable kernel headers.

Risks and test signals: the main risk is build/environment mismatch, especially missing or stale UAPI CAN headers. A successful signal is that `make` emits the `test_raw_filter` binary and the kselftest runner sees `test_raw_filter.sh` as the runnable program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/config

Purpose: this three-line kselftest config declares the kernel features needed by the CAN raw socket tests. It requests `CONFIG_CAN`, `CONFIG_CAN_DEV`, and `CONFIG_CAN_VCAN` as modules.

Important integration points: the selftest framework can use this file to determine required kernel configuration before running the test. `CONFIG_CAN` enables the CAN protocol stack, `CONFIG_CAN_DEV` supplies CAN network device support, and `CONFIG_CAN_VCAN` enables the virtual CAN device used by the default shell wrapper.

State and persistence: the file is declarative only. It does not mutate test state; it describes build/runtime prerequisites.

Risks and test signals: missing `vcan` support causes the wrapper's default `ip link add name vcan0 type vcan` path to skip or fail. A passing environment has the CAN stack and vcan module available, or an externally supplied physical CAN interface that satisfies the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/test_raw_filter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/test_raw_filter.c

Purpose: this kselftest harness validates CAN RAW socket filter semantics for standard-frame, extended-frame, and remote-transmission-request flag matching. For each variant it installs one `struct can_filter`, sends four frames carrying the same standard id with all EFF/RTR flag combinations, and verifies only the expected frames are received.

Important APIs and types: the test uses `PF_CAN`, `SOCK_RAW`, `CAN_RAW`, `struct sockaddr_can`, `struct can_frame`, `struct can_filter`, `CAN_RAW_FILTER`, `CAN_RAW_RECV_OWN_MSGS`, `SIOCGIFINDEX`, `CAN_SFF_MASK`, `CAN_EFF_MASK`, `CAN_EFF_FLAG`, `CAN_RTR_FLAG`, and the kselftest harness fixture/variant macros. The global `CANIF` is populated from the `CANIF` environment variable and identifies the interface under test.

Control flow: `main` requires `CANIF`, copies it into the global buffer, and calls `test_harness_run`. Fixture setup opens a CAN RAW socket, looks up the interface index, enables reception of frames sent by the same socket, and binds to the interface. `send_can_frames` sends four one-byte frames tagged with the current testcase id in `data[0]`. Each variant defines a filter id, mask, expected receive count, and ordered expected flags. `TEST_F(can_filters, test_filter)` installs the filter, sends frames, then loops one extra receive attempt: expected frames must arrive before a 50 ms `select` timeout, and the extra iteration must time out.

State and persistence: state is per-socket and per-variant. No files are written. Kernel state includes the bound CAN socket and its raw filter. The receive-own-message option deliberately loops transmitted frames back into the same socket to make the test self-contained on vcan.

Dependencies and integration points: the shell wrapper provides a vcan or physical CAN interface and exports `CANIF`. The Makefile builds this binary as `TEST_GEN_FILES`. It depends on kselftest harness headers and CAN kernel support.

Risks and test signals: ordering is assumed to match the order of writes that pass the filter. The 50 ms timeout can be fragile on slow or overloaded systems. `setsockopt` return values for `CAN_RAW_RECV_OWN_MSGS` and `CAN_RAW_FILTER` are not asserted, so failures there can show up as later receive mismatches. Strong signals are exact expected receive counts, id equality after masking with `CAN_SFF_MASK`, correct testcase byte, and flag equality after excluding `CAN_ERR_MASK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/test_raw_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/test_raw_filter.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/test_raw_filter.sh

Purpose: this shell wrapper prepares a CAN interface, runs the compiled `test_raw_filter` binary, and reports the result through common net selftest helpers.

Important APIs/functions: it sources `../lib.sh`, sets `ALL_TESTS` to `test_raw_filter`, and uses `setup`, `cleanup`, `tests_run`, `check_err`, and `log_test`. It exports `CANIF`, defaulting to `vcan0`, and `BITRATE`, defaulting to `500000` for physical CAN devices.

Control flow: `setup` creates a vcan link when `CANIF` starts with `vcan`; otherwise it configures the named device as CAN with the requested bitrate. It then brings the device up. `test_raw_filter` executes `./test_raw_filter`, checks the exit code, and logs the test. `cleanup` brings the device down and deletes it if it was a vcan created by this script. A trap ensures cleanup runs at exit.

State and persistence: the script mutates netdevice state by adding/deleting or reconfiguring a CAN link. It persists no files. State is scoped by the interface name and cleaned on normal exit.

Dependencies and integration points: depends on `ip`, CAN/vcan kernel support, root privileges or equivalent net admin capability, the generated `test_raw_filter` binary, and `lib.sh` kselftest functions.

Risks and test signals: non-vcan mode reconfigures a user-specified physical CAN device and may disrupt external state. `pwd` in `setup` is a noisy diagnostic. Successful signals are link setup, zero exit from the binary, and final `EXIT_STATUS` from `tests_run`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/test_raw_filter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_ip.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_ip.sh

Purpose: this script verifies IP-related send-time control message behavior across IPv4, IPv6, UDP, UDP with `MSG_MORE`, ICMP, and raw sockets. It checks IPv6 `DONTFRAG`, IPv4 TOS / IPv6 traffic class, IPv4 TTL / IPv6 hop limit, and basic IPv6 extension-header cmsg handling.

Important APIs and commands: it sources `lib.sh`, creates one namespace with `setup_ns`, configures a dummy interface with IPv4 and IPv6 addresses, runs `./cmsg_sender`, captures packets with `tcpdump --immediate-mode`, and uses policy routing rules plus prohibit routes to detect TOS/TCLASS control. `check_result` records total and failed cases.

Control flow: after verifying tcpdump support, it creates namespace connectivity and allows unprivileged ping sockets. The `IPV6_DONTFRAG` matrix sends 2000-byte packets with option sources `setsock`, `cmsg`, `both`, and conflicting values, expecting return code equal to the don't-fragment value. `test_dscp` installs a prohibit rule for one DSCP/TOS value, sends packets with setsockopt/cmsg combinations, checks tcpdump output for the expected field, and checks rejection when the prohibited value is used. `test_ttl_hoplimit` captures packets and greps decoded TTL/hlim. The final extension-header loop sends hop-by-hop, destination, and routing-destination options and treats non-crash success as the signal.

State and persistence: state is namespace-local routes, rules, dummy link addresses, and a temporary pcap file removed in `cleanup`. No persistent repository files are modified.

Dependencies and integration points: depends on `cmsg_sender`, tcpdump with immediate mode, `ip`, namespace support, and packet decoding strings stable enough for grep. It integrates with `cmsg_sender.c` option names: `-f/-F`, `-c/-C`, `-l/-L`, `-H`, `-p`, `-4`, and `-6`.

Risks and test signals: tcpdump startup uses a fixed short sleep and packet-count loops, so slow systems can be flaky. Grep-based packet validation depends on tcpdump formatting. Strong signals are expected sender return codes, prohibited-route failures for controlled TOS/class values, and decoded packet fields matching the cmsg-selected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_ip.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_sender.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_sender.c

Purpose: this reusable C helper sends packets with configurable socket options and ancillary data so shell tests can validate kernel cmsg behavior. It can send IPv4 or IPv6 UDP, UDP with `MSG_MORE`, ICMP/ICMPv6, or raw packets, and can set mark, priority, don't-fragment, TOS/TCLASS, TTL/HOPLIMIT, TXTIME, timestamping, and IPv6 extension-header ancillary data.

Important APIs and types: central state is the global `struct options opt`, including nested `sockopt`, `sock`, `mark`, `priority`, `txtime`, `ts`, and `cmsg` fields. It uses `getaddrinfo`, `socket`, `setsockopt`, `sendmsg`, `recvmsg(MSG_ERRQUEUE)`, `struct msghdr`, `struct cmsghdr`, `CMSG_SPACE`, `CMSG_LEN`, `SO_MARK`, `SO_PRIORITY`, `SO_TXTIME`, `SCM_TXTIME`, `SO_TIMESTAMPING`, `SO_TIMESTAMPING_OLD`, `IP_TOS`, `IP_TTL`, `IPV6_DONTFRAG`, `IPV6_TCLASS`, `IPV6_HOPLIMIT`, `IPV6_RECVERR`, and `IP_RECVERR`.

Control flow: `cs_parse_args` maps command-line options to `opt`. `memrnd` fills the payload. `main` resolves the destination, adjusts ICMPv6 protocol when needed, opens the socket, initializes ICMP/raw packet headers, applies persistent socket options in `ca_set_sockopts`, records realtime/monotonic start timestamps, builds the `msghdr`, and calls `cs_write_cmsg` to append ancillary records. It then sends `opt.num_pkt` messages and, for `MSG_MORE`, flushes with a zero-length write. If timestamping is enabled it polls the error queue through `cs_read_cmsg` until a send timestamp is observed or retry budget is exhausted.

State and persistence: the process owns one socket and one dynamically allocated payload buffer. It persists no files. Kernel-visible state is limited to the socket options and error queue. Return codes are intentionally stable for some cases, especially `ERN_SEND = 1`, because shell tests compare them.

Dependencies and integration points: included by multiple cmsg shell tests as `./cmsg_sender`. It assumes Linux socket ancillary semantics, timestamping definitions, and enough privilege for options such as `SO_MARK` in some configurations.

Risks and test signals: argument parsing uses `atoi`, so invalid numeric strings silently become zero. `malloc` is not checked before `memrnd`. Error-code labels for getaddrinfo/socket failure appear swapped in `main`, which can complicate diagnostics though most tests care about send success/failure. Strong signals are exact send length, expected return code, packet capture fields, tc filter counters, and printed `SCHED`/`SND` timestamp lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_sender.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_so_mark.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_so_mark.sh

Purpose: this script validates `SO_MARK` supplied either through `setsockopt` or through cmsg (`SCM_MARK` via `SO_MARK`) by proving that marked packets match a policy-routing rule and are rejected by a prohibit route.

Important APIs and commands: it uses `setup_ns`, `cleanup_ns`, namespace-local `ip rule add fwmark`, IPv4 and IPv6 prohibit routes in table 300, and `./cmsg_sender` options `-M` for setsockopt mark and `-m` for cmsg mark.

Control flow: the script creates one namespace, enables ping socket groups, creates a dummy interface with IPv4 and IPv6 addresses, and installs fwmark rules for both families. For each option source (`setsock`, `cmsg`, `both`), address family, and protocol (`u`, `i`, `r`), it first sends with `MARK + 1` and expects success, then sends with `MARK` and `-s` silent mode and expects sender return code 1 due to the prohibit route.

State and persistence: state is namespace-local link, addresses, rules, and routes. It is removed by the exit trap. No files are written.

Dependencies and integration points: depends on kernel support for `SO_MARK` cmsg handling, `cmsg_sender`, raw/ICMP/UDP socket support, and privilege to set marks and rules.

Risks and test signals: the script includes a dormant `diff` branch assignment that is never used because the `ovr` loop omits `diff`; that is harmless but suggests the matrix was reduced. Strong signals are the two return-code classes for every protocol/family/source combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_so_mark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_so_priority.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_so_priority.sh

Purpose: this script validates that `SO_PRIORITY` set by cmsg (`-Q`) and by setsockopt (`-P`) maps into VLAN egress priority and can be observed by tc flower filters. It covers IPv4 and IPv6 UDP, ICMP/ICMPv6, and raw traffic over a VLAN device.

Important APIs and commands: it requires `jq`, uses `ip netns`, `tc qdisc clsact`, `tc filter flower` with `vlan_prio`, JSON tc stats, a dummy lower device, a VLAN interface with `egress-qos-map 0:0 ... 7:7`, permanent neighbor entries, and `./cmsg_sender`.

Control flow: after creating the namespace and dummy/vlan devices, the script adds IPv4 and IPv6 addresses and static neighbors for normal and raw destinations. `create_filter` installs a flower egress filter on the lower dummy for a handle/priority/protocol/destination tuple. For each family, protocol, and priority 0..7, it checks the filter counter starts at zero, sends once with cmsg priority and expects one packet, then sends once with setsockopt priority and expects two packets.

State and persistence: all state is namespace-local tc, link, VLAN, address, and neighbor configuration. It is removed by `cleanup_ns`.

Dependencies and integration points: depends on `cmsg_sender`, tc flower, VLAN support, JSON output from tc, jq, and `ping_group_range` for ICMP. It also relies on priority-to-VLAN-qos propagation through the VLAN egress-qos-map.

Risks and test signals: the test is counter based, so extra matching packets can cause false failures. Raw traffic uses different destination addresses to avoid overlapping neighbor/filter state. Strong signals are tc JSON packet counters exactly 0, 1, then 2 for each filter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_so_priority.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_time.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_time.sh

Purpose: this script verifies transmit timestamping and `SCM_TXTIME` scheduling through `cmsg_sender`. It checks that packets without options print no timestamp output, that timestamping yields scheduler and send timestamps, and that a TXTIME delay is reflected in absolute and relative timing.

Important APIs and commands: it uses `setup_ns`, a dummy device, `tc qdisc replace dev dummy0 root fq` because TXTIME requires fq, `./cmsg_sender -t` for timestamping, `-d` for TXTIME delay, and shell filters `wc`, `sed`, and `awk` to parse output.

Control flow: the script creates a namespace and dummy IPv4/IPv6 connectivity, installs fq, then loops over IPv4 and IPv6 targets and UDP/ICMP/raw protocols. It verifies no output without timestamp options, exactly two lines with `-t`, one `SCHED ts0` line, one `SND ts0` line, a send timestamp greater than 1000 usec with `-d 1000`, and a send-minus-schedule delta greater than 500 usec. The last relative-delay check is treated as xfail on slow machines.

State and persistence: only namespace-local network and qdisc state is mutated. No files are written.

Dependencies and integration points: depends on `cmsg_sender` timestamp/error-queue logic, fq qdisc, Linux timestamping support, and root/net admin capabilities.

Risks and test signals: timestamp timing is scheduler-sensitive and can be flaky; the script has an explicit `KSFT_MACHINE_SLOW=yes` xfail path for the relative delay. Strong signals are expected printed timestamp line count and parsed `SCHED`/`SND` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_time.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/config

Purpose: this is the broad kernel configuration manifest for networking selftests. It declares modules and built-in features needed by many tests in `tools/testing/selftests/net`, including namespaces, virtual devices, tunnels, bridge/VRF/VLAN, netfilter/nftables, qdiscs, classifiers, actions, CAN, MPTCP, TLS, XFRM, MPLS, Open vSwitch, drop monitor, and BPF-related support.

Important entries: the files in this subset directly rely on entries such as `CONFIG_NET_NS`, `CONFIG_DUMMY`, `CONFIG_VETH`, `CONFIG_VLAN_8021Q`, `CONFIG_BRIDGE`, `CONFIG_BRIDGE_VLAN_FILTERING`, `CONFIG_NET_VRF`, `CONFIG_VXLAN`, `CONFIG_GENEVE`, `CONFIG_NET_DROP_MONITOR`, `CONFIG_NETDEVSIM`, `CONFIG_NET_SCH_FQ`, `CONFIG_NET_CLS_FLOWER`, `CONFIG_NET_ACT_GACT`, `CONFIG_CAN`, `CONFIG_CAN_DEV`, `CONFIG_CAN_VCAN`, and IPv4/IPv6 netfilter options. Busy-poll and NAPI tests additionally depend on netdev/YNL kernel interfaces not fully expressed by this manifest.

Control flow and state: the file is declarative; it is consumed by kselftest tooling or humans to prepare a kernel. It does not execute or persist runtime state.

Dependencies and integration points: it integrates at the repository/test-suite level rather than with one binary. The manifest helps CI builders avoid running tests against kernels missing mandatory features.

Risks and test signals: config coverage is necessary but not sufficient. User-space tools (`ip`, `bridge`, `tc`, `jq`, `tcpdump`, `tshark`, `dwdump`, `mausezahn`, generated helpers) must also exist and be recent enough. A strong signal is that skip paths in the scripts are not reached and the underlying kernel options match the features being exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/double_udp_encap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/double_udp_encap.sh

Purpose: this script validates segmentation and coalescing behavior for TCP over nested UDP tunnels. It builds two namespaces connected by veth, creates nested VXLAN or Geneve tunnel devices over IPv4 and IPv6, sends large TCP payloads with `udpgso_bench_tx`, receives with `udpgso_bench_rx`, and counts outer tunnel packets to verify GSO/GRO behavior.

Important APIs and commands: it sources `lib.sh`, uses YNL `pyynl/cli.py` for Geneve link creation, `ip link add type vxlan`, `ethtool -K` feature toggles, `iptables`/`ip6tables` length and BPF matches, `nfbpf_compile`, `jq`, `wait_local_port_listen`, `udpgso_bench_rx`, and `udpgso_bench_tx`.

Control flow: `create_ns` builds the base topology, creates outer and nested tunnel endpoints, assigns underlay and overlay addresses, adjusts nested MTUs, disables selected veth offloads, and sets TCP write memory. `create_ns_gso` enables tunnel GSO features on the source tunnel. `create_ns_gso_gro` additionally enables GRO on the destination veth and disables source veth TX offload. `run_test` computes expected segment counts, compiles a packet-offset BPF filter that identifies the double-encapsulated TCP stream, installs counters on source OUTPUT and destination INPUT, runs receiver and sender, then compares iptables packet counters against expected wire and received tunnel packet counts. `run_tests` iterates IPv4/IPv6, VXLAN/Geneve, no-GSO, GSO, fixed-ID-disabled IPv4, and Geneve GRO hint/csum/inner-proto-inherit scenarios.

State and persistence: it creates and deletes network namespaces and tunnel devices through `cleanup_all_ns`. Persistent files are not written. Kernel state includes offload settings, iptables rules, tunnel endpoints, and sysctls.

Dependencies and integration points: requires root, namespace support, VXLAN/Geneve, ethtool offload controls, bench binaries, BPF match support, iptables, and the YNL CLI. It integrates with generated net selftest binaries in the same directory.

Risks and test signals: packet-offset BPF filters are tightly coupled to encapsulation header layouts and options such as `USE_HINT` and `INHERIT`. TCP retransmissions can break accounting; the script wraps `run_tests` in `xfail_on_slow`. Strong signals are sender/receiver zero exits and exact tunnel packet counters for no-GSO, GSO, GRO, checksum, and short-last-packet cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/double_udp_encap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/drop_monitor_tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/drop_monitor_tests.sh

Purpose: this script verifies software and hardware drop-monitor reporting. It checks that active drops are captured by `dwdump` and decoded by tshark, and that inactive/drop-disabled cases produce no matching packets.

Important APIs and commands: it uses `lib.sh`, `setup_ns`, `netdevsim` sysfs (`/sys/bus/netdevsim/new_device` and `del_device`), `devlink trap set`, `tc clsact` with flower drop action, `mausezahn` traffic generation, `dwdump -o sw/hw`, `tshark`, `timeout`, and `udevadm settle`.

Control flow: startup validates root and required tools, then creates an initial namespace to derive command wrappers. `setup` loads `netdevsim`, creates a dummy interface, creates a netdevsim device inside the namespace, waits for udev, and brings its netdev up. `sw_drops_test` installs a tc egress flower drop for a destination IPv4 address, generates continuous UDP traffic with mausezahn, captures software drops, asserts at least one matching pcap record, stops traffic, captures again, and asserts zero matches. `hw_drops_test` toggles the netdevsim `blackhole_route` trap between `trap` and `drop` actions and checks hardware drop monitor output for `net_dm.hw_trap_name == blackhole_route`.

State and persistence: the script mutates module state, netdevsim devices, namespaces, tc filters, and temporary pcap files under `mktemp -d`. Cleanup deletes netdevsim device and namespace; per-test temp directories are removed.

Dependencies and integration points: requires a kernel with `NET_DROP_MONITOR` and `NETDEVSIM`, tshark with net_dm dissector, and user-space `dwdump`. It integrates with devlink traps and tc drop actions.

Risks and test signals: tool availability is the dominant skip source. `kill_process %%` relies on job control for the mausezahn background job. Hardware testing depends on netdevsim trap behavior. Strong signals are nonzero matching pcap lines during active drops and zero matching lines after traffic stops or trap action changes to drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/drop_monitor_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/epoll_busy_poll.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/epoll_busy_poll.c

Purpose: this C kselftest validates the epoll busy-poll ioctl API. It does not build a network traffic topology; it focuses on ioctl behavior, validation, default values, permission behavior, and error codes for `EPIOCGPARAMS` and `EPIOCSPARAMS`.

Important APIs and types: it uses the kselftest harness fixture macros, `struct epoll_params`, epoll ioctls, `epoll_create1`, `ioctl`, libcap functions `cap_get_proc`, `cap_get_flag`, `cap_set_flag`, `cap_set_proc`, `cap_free`, and capability `CAP_NET_ADMIN`. Like `busy_poller.c`, it supplies local ioctl definitions when headers lack them.

Control flow: fixture `invalid_fd` opens an AF_UNIX datagram socket, then `test_invalid_fd` confirms both epoll ioctls fail with `ENOTTY` on a non-epoll fd. Fixture `epoll_busy_poll` creates an epoll fd and snapshots process capabilities. `test_get_params` seeds the params struct with garbage, verifies `EPIOCGPARAMS` returns zeroed defaults, then checks an invalid userspace pointer yields `EFAULT`. `test_set_invalid` checks invalid padding, too-large `busy_poll_usecs`, invalid `prefer_busy_poll`, large budget with and without `CAP_NET_ADMIN`, and invalid pointer handling. `test_set_and_get_valid` writes valid values and reads them back. `test_invalid_ioctl` verifies an unknown ioctl number fails with `EINVAL`.

State and persistence: state is one epoll fd and temporary process effective capability changes. No files or network devices are modified. The teardown restores resource ownership but capability restoration occurs inside the test before invalid pointer checks.

Dependencies and integration points: requires libcap headers/library, kselftest harness, and kernel epoll busy-poll ioctl support. The test should run with `CAP_NET_ADMIN` for the privileged budget path.

Risks and test signals: because it drops and restores capabilities inside a test, failure before restoration could affect later assertions in the same process. It assumes `CAP_NET_ADMIN` is present at test start. Strong signals are exact errno checks for invalid fd, invalid userspace pointer, invalid fields, permission denial, valid set/get round trip, and unknown ioctl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/epoll_busy_poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-ipv4.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-ipv4.sh

Purpose: this tiny wrapper runs only the IPv4 portion of the functional networking address lookup suite.

Important behavior: it executes `./fcnal-test.sh -t ipv4`. The target harness expands `ipv4` into the IPv4 ping, TCP, UDP, bind, runtime, and netfilter test sets.

State and dependencies: this wrapper has no independent state, cleanup, or argument handling. All namespace, VRF, route, socket, process, and test-result behavior is delegated to `fcnal-test.sh`.

Integration points and risks: it must be run from a directory where `fcnal-test.sh` is executable and relative helper paths resolve. Its test signal is the exit status and summary emitted by the delegated harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-ipv4.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-ipv6.sh

Purpose: this wrapper selects the IPv6 portion of the functional networking address lookup suite.

Important behavior: it executes `./fcnal-test.sh -t ipv6`. The main harness maps that selector to IPv6 ping, TCP, UDP, bind, runtime, and netfilter tests, including link-local, multicast, VRF, and l3mdev permutations.

State and dependencies: the wrapper itself does not create state. All network namespaces, routes, sysctls, sockets, and cleanup are owned by `fcnal-test.sh`.

Integration points and risks: it depends on relative execution from the net selftest directory and on the main harness plus generated `nettest` helper. Its only direct test signal is the delegated command's exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-other.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-other.sh

Purpose: this wrapper runs the non-IPv4/non-IPv6 named use cases in the functional networking suite.

Important behavior: it executes `./fcnal-test.sh -t other`. The main harness expands `other` to `use_cases`, covering bridge enslaved to VRF, multicast link-local pings across multiple VRF interfaces, and SNAT over VRF.

State and dependencies: this file owns no independent state or cleanup. All setup and teardown are in `fcnal-test.sh`.

Integration points and risks: because the selected scenarios touch bridges, VLANs, br_netfilter, netfilter NAT, and VRFs, the wrapper indirectly requires a broad set of kernel and user-space features. Its direct signal is the harness summary and exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-other.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-test.sh

Purpose: this large functional-addressing harness validates Linux routing, VRF/l3mdev behavior, socket binding, protocol reachability, runtime device deletion, netfilter rejects, and several real-world VRF use cases. It covers IPv4 and IPv6 permutations for ping, TCP, UDP, raw/ICMP bind behavior, nonlocal bind, TCP MD5 keys, link-local addressing, multicast, and namespace-local policy/routing failures.

Important APIs and helpers: it sources `lib.sh`, relies on generated `nettest`, and uses `ping`, `ping6` or `ping -6`, `ip netns`, `ip vrf exec`, `iptables`, `ip6tables`, `sysctl`, `modprobe`, `rmmod`, `wait_local_port_listen`, and shell process controls. Core helpers include `log_test`, `log_test_addr`, `log_start`, `kill_procs`, `do_run_cmd`, `run_cmd*`, `setup_cmd*`, `set_sysctl`, `get_linklocal`, `create_vrf`, `create_ns`, `connect_ns`, `setup`, `setup_lla_only`, and cleanup functions.

Control flow: argument parsing expands `-t ipv4`, `-t ipv6`, or `-t other` into named test groups. `setup` creates namespaces `NSA` and `NSB`, loopback and veth addresses, unreachable defaults, forwarding/sysctl state, optional VRF `red` with table 1101, and reciprocal routes. Some MD5 duplicate tests add `NSC`. IPv4 groups exercise ping route selection, TCP global/device/VRF servers and clients, TCP MD5 and `SO_DONTROUTE`, UDP cmsg/device/IP_UNICAST_IF sends, address binding, runtime VRF deletion under active TCP/ping traffic, and netfilter TCP reset or ICMP port unreachable. IPv6 mirrors these categories with IPv6-specific link-local scope, multicast, `IPV6_UNICAST_IF`, IPv6 TCP MD5, LLA-to-GUA cases, and IPv6 runtime tests. `use_cases` covers bridge devices enslaved into a VRF with and without br_netfilter, link-local multicast ping across multiple VRF interfaces after link flaps, and IPv4/IPv6 SNAT on VRF egress.

State and persistence: all intended state is namespace-local, but the harness also loads/unloads `br_netfilter`, kills `nettest`/ping processes, changes sysctls inside namespaces, and manipulates iptables/ip6tables in namespace context. It writes no files. Cleanup explicitly removes VRF, routes, links, namespaces, and residual namespace processes.

Dependencies and integration points: requires root, net namespaces, VRF, veth, bridge, VLAN, netfilter, TCP MD5 support unless FIPS mode skips it, generated `nettest`, and current iproute2 behavior. The three wrapper scripts in this subset select coarse suites from this file.

Risks and test signals: the suite is broad and timing-sensitive; it uses sleeps around DAD, active traffic, and device deletion. It deliberately documents some existing odd behavior, such as IPv4 device-bound route lookup quirks and permissive binds that arguably should fail. It mutates module state for `br_netfilter`, which can affect concurrent tests. Strong signals are per-case return codes from `ping`/`nettest`, exact success/fail counts, zero `nfail`, and skip only when no tests ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fdb_flush.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fdb_flush.sh

Purpose: this script validates `bridge fdb flush` behavior for VXLAN and bridge devices. It checks flushing by device, VNI, source VNI, destination UDP port, destination IP, nexthop id, FDB state, FDB flags, combinations of arguments, remote attributes in multicast VXLAN entries, bridge VLAN, and mixed bridge/VXLAN master/self behavior.

Important APIs and functions: it uses `ip`, `bridge`, net namespaces, VXLAN links, bridge links with VLAN filtering, nexthop objects with `fdb`, and common shell helpers from `lib.sh`. Key local helpers are `run_cmd`, `log_test`, `fdb_add_mac_pool_1`, `fdb_add_mac_pool_2`, `fdb_check_n_entries_by_dev_filter`, `nexthops_add`, `vxlan_test_flush_by_state`, `vxlan_test_flush_by_flag`, `multicast_fdb_entries_add`, `setup`, and `cleanup`.

Control flow: startup checks root, `ip`, iproute2 flush syntax support (`[no]router`), and kernel VXLAN flush support. It then iterates selected tests, running fresh `setup; test; cleanup` for each. Setup creates a namespace, two VXLAN devices, and two VLAN-filtering bridges. Individual tests add deterministic MAC pools with attributes, assert baseline entry counts via filtered `bridge fdb show`, execute `bridge fdb flush` with specific selectors, and verify only intended entries disappeared. Bridge/VXLAN mixed tests check that bridge entries can be flushed even when the VXLAN driver rejects unsupported VLAN self flush with exit 255.

State and persistence: state is namespace-local links, bridges, VXLAN devices, FDB entries, VLAN membership, and nexthop objects. No files persist. Cleanup removes created links and namespace after every test case, reducing cross-case contamination.

Dependencies and integration points: requires recent iproute2 and kernel VXLAN FDB flush support. It exercises both bridge core and VXLAN driver FDB paths, including remote lists for multicast zero-MAC entries.

Risks and test signals: `log_test` declares local counters, so its counter variables are not useful for a final summary, but the script primarily uses immediate pass/fail output and command exit status. Grep-based entry counting can be sensitive to bridge output formatting. Strong signals are expected entry counts before and after each flush and the special expected 255 return for unsupported VXLAN VLAN flush with bridge-side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fdb_flush.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fdb_notify.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fdb_notify.sh

Purpose: this script checks that FDB add/delete operations generate a single notification, not duplicates, for bridge, VXLAN, and macvlan self/master paths.

Important APIs and functions: it sources `lib.sh`, uses `tests_run`, deferred cleanup helpers (`defer`, `defer_scope_push`, `defer_scope_pop`, `defer_scopes_cleanup`), `bridge monitor fdb`, `bridge fdb add/del`, and `adf_ip_link_add` / `adf_ip_link_set_master` helper wrappers.

Control flow: `do_test_dup` starts `bridge monitor fdb` into a temporary file, performs the requested FDB operation for MAC `00:11:22:33:44:55` and VLAN 1, stops the monitor through deferred cleanup, counts matching lines, and asserts exactly one notification. Test cases create the required topology, then call `do_test_dup` for add and delete on bridge self, VXLAN self, VXLAN master, macvlan self, and macvlan attached to a bridge.

State and persistence: it creates transient bridge, VXLAN, dummy, and macvlan devices through helper functions and temporary monitor output files. Deferred cleanup removes temp files and processes; final trap drains deferred scopes.

Dependencies and integration points: depends on bridge, VXLAN, macvlan, dummy devices, `bridge monitor`, and lib.sh advanced deferred fixture helpers. It integrates with the generic `tests_run` dispatcher through `ALL_TESTS`.

Risks and test signals: monitor startup is synchronized only by `sleep 0.5`, and notification delivery is observed after another fixed sleep, so very slow environments can be flaky. Strong signal is exactly one occurrence of the test MAC in the monitor log for each operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fdb_notify.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib-onlink-tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib-onlink-tests.sh

Purpose: this script validates IPv4 and IPv6 `onlink` route handling for valid and invalid nexthops across default table, VRF table, policy-routing table, and multipath routes.

Important APIs and functions: it uses `setup_ns`, `ip route add ... onlink`, `ip -6 route add ... onlink`, VRF creation (`ip link add type vrf table`), veth pairs, link-local lookup, and helper functions `run_ip`, `run_ip_mpath`, `run_ip6`, `run_ip6_mpath`, `valid_onlink_ipv4`, `invalid_onlink_ipv4`, `valid_onlink_ipv6`, and `invalid_onlink_ipv6`.

Control flow: `setup` creates two namespaces, a VRF `lisa` with table 1101, four veth pairs with odd ends in ns1 and even ends in ns2, enslaves selected ns1 interfaces to the VRF, assigns IPv4/IPv6 addresses, and installs IPv6 defaults. The IPv4 valid suite adds host routes via connected and recursive unicast gateways, including device mismatch and multipath combinations. IPv4 invalid cases expect iproute2 exit code 2 for local unicast gateways, multicast gateways, and missing nexthop device. IPv6 valid cases add unicast, recursive, v4-mapped, device mismatch, and multipath onlink routes. IPv6 invalid cases include local unicast, local link-local, multicast, VRF equivalents, and missing device.

State and persistence: all state is namespace-local routes, VRF, veths, and addresses. Cleanup removes the namespaces at the end. No files are written.

Dependencies and integration points: requires root, VRF, veth, IPv6, and iproute2 with onlink route syntax. It directly targets FIB nexthop validation paths.

Risks and test signals: expected failure code 2 is iproute2-specific and could change with tool behavior. `run_ip_mpath` contains an unused `dev` variable check, but the caller supplies device strings inside nexthop arguments so the tests still form intended commands. Strong signals are exact command return codes for every valid and invalid route addition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib-onlink-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthop_multiprefix.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthop_multiprefix.sh

Purpose: this script validates cached route exceptions when one nexthop object is shared by multiple IPv4 and IPv6 prefixes. It ensures path-MTU exceptions for different remote hosts remain distinct instead of being incorrectly shared through the common `fib_nh` / `fib6_nh`.

Important APIs and functions: it uses `setup_ns`, veth links, namespace sysctls for forwarding, `ip nexthop add`, routes using `nhid`, `taskset` to generate per-CPU cached routes, `ping`/`ping6`, MTU changes, and route lookup checks with `ip route get` / `ip -6 route get`. Key functions are `create_ns`, `setup`, `change_mtu`, `validate_v4_exception`, and `validate_v6_exception`.

Control flow: setup creates host namespaces h0..h3 and router r1, connects each host to r1, assigns IPv4/IPv6 subnets, adds nexthop ids 4 and 6 in h0 via r1, and routes h1-h3 prefixes through those shared nexthops. Main code pings each destination from each CPU to populate cached routes, then changes MTUs on h1, h2, and h3 links to 1300, 1350, and 1400. For each host it sends oversized pings to trigger PMTU exceptions and validates `route get` output contains the expected mtu. It then revalidates without more pings and deletes selected routes/nexthops to exercise cleanup paths.

State and persistence: state consists of namespaces, links, routes, nexthop objects, route cache exceptions, and MTU changes. Cleanup removes all namespaces. No files are written.

Dependencies and integration points: requires nexthop object support, IPv6, route exception reporting in `ip route get`, multiple CPUs or compatible `/sys/devices/system/cpu/online` parsing, and ping utilities.

Risks and test signals: parsing CPU ranges with `seq ${cpus/-/ }` handles simple ranges but not comma-separated CPU lists. Grep patterns depend on iproute2 route-get output format. Strong signals are successful initial pings and route-get output showing the distinct expected MTU for each destination in both families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthop_multiprefix.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthop_nongw.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthop_nongw.sh

Purpose: this script validates source-address selection and reachability for a route that uses a nexthop object without an explicit gateway. It creates a direct-device nexthop and verifies both `route get` and ping to a peer address work.

Important APIs and functions: it uses `setup_ns`, dummy and veth links, `ip nexthop add id 1 dev veth0`, `ip route add ... nhid 1`, `ip route get`, `ping`, plus local `run_cmd`, `log_test`, `setup`, and `cleanup` helpers.

Control flow: `setup` creates namespaces h1 and h2, gives h1 a dummy `eth0` with `192.168.0.1/24`, creates a veth pair, assigns h2 `192.168.1.1/32`, adds a default route in h2 through veth1, creates a gateway-less nexthop object in h1 on veth0, and adds a route to `192.168.1.1` through that nexthop. Main then checks route lookup and ping success.

State and persistence: namespace-local links, addresses, route, and nexthop object are removed by the exit trap. No files persist.

Dependencies and integration points: requires kernel nexthop object support and iproute2 support for gateway-less nexthops. It targets FIB behavior for directly connected nexthop objects.

Risks and test signals: the topology uses no ARP suppression beyond the comment's note, so neighbor behavior depends on normal veth semantics. Strong signals are zero exit from `ip route get` and one successful ping through the nexthop route.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthop_nongw.sh -->
