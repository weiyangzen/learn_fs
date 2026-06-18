# subset-b-006874 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_mdb.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_mdb.sh

## Purpose
`test_vxlan_mdb.sh` is a Linux networking selftest for VXLAN multicast database (MDB) support on external, VNI-filtering VXLAN devices. It builds paired IPv4-underlay and IPv6-underlay namespace topologies, maps bridge VLANs 10, 20, and 4000 to VNIs 10010, 10020, and 14000, and tests both IPv4 and IPv6 overlay multicast traffic. The test is split into control-path coverage for `bridge mdb` operations and datapath coverage that injects multicast packets and checks encapsulation/forwarding with `tc flower` counters.

## Important APIs, Functions, and Types
The script is shell-based and sources `lib.sh` for kselftest helpers such as `setup_ns`, `cleanup_ns`, and `ksft_skip`. Local helpers are `log_test`, `run_cmd`, and `tc_check_packets`. Setup helpers `setup_common_ns`, `setup_common`, `setup_v4`, and `setup_v6` create netns pairs, veth underlays, bridges, VLAN subinterfaces, an external `vx0` VXLAN device, bridge VLAN tunnel mappings, and bridge VNI filters. Control-path helpers include `basic_common`, `star_g_common`, `sg_common`, `dump_common`, and `flush`. Datapath helpers include `encap_params_common`, `starg_exclude_ir_common`, `starg_include_ir_common`, `starg_exclude_p2mp_common`, `starg_include_p2mp_common`, `egress_vni_translation_common`, `all_zeros_mdb_common`, `mdb_fdb_common`, and `mdb_torture_common`.

## Control Flow
The main routine parses `-t`, `-c`, `-d`, pause, and verbose options, checks root and command availability, verifies `bridge mdb flush` support, cleans stale namespaces, then loops over selected tests. Each test calls `setup`, runs one scenario, and calls `cleanup`. `setup` creates both IPv4 and IPv6 underlay topologies before every scenario, which makes test cases independent but expensive. Control-path cases validate add/get/replace/delete, protocol and encapsulation attribute replacement, invalid combinations, large dump marker handling, and flush selectors. Datapath cases install MDB/FDB state, send traffic with `mausezahn`, and assert specific ingress counter increments in the receiving namespace.

## State and Persistence
All kernel state is transient: namespaces, veth links, bridges, VXLAN devices, VLAN tunnel mappings, VNI filters, routes, sysctls, MDB entries, FDB entries, qdiscs, and `tc` filters are recreated per test and removed through `cleanup_v4`, `cleanup_v6`, and the `EXIT` trap. The only filesystem persistence is temporary batch files from `mktemp` in `dump_common`; those are removed after use. Global shell counters `nsuccess`, `nfail`, and `ret` summarize the run.

## Dependencies and Integration Points
The script depends on root privileges, `ip`, `bridge`, `tc`, `mausezahn`, `jq`, and recent iproute2/kernel VXLAN MDB support. It integrates directly with kernel bridge MDB netlink APIs, VXLAN external/vnifilter behavior, bridge VLAN tunnel info, multicast forwarding, FDB fallback, route/sysctl behavior, and kselftest result conventions. It also relies on `tc flower` fields such as `enc_dst_ip`, `enc_key_id`, UDP ports, and packet counters as datapath observability.

## Risks and Test Signals
Primary risks are environmental flakiness from namespace setup, timing, `mausezahn` availability, iproute2 feature skew, and long runtime from full matrix execution plus the 30-second torture tests. The test is valuable because it checks both user-visible control-plane errors and real encapsulated traffic behavior, including source-filter modes, P2MP/IR destinations, egress VNI translation via PVID, all-zeros catchall behavior, MDB/FDB interaction, and use-after-free style race exposure. Passing signals are `[ OK ]` log lines, expected `bridge` return codes, exact `tc` packet counts, and a final nonzero `ret` only when failures are recorded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_mdb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_nh.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_nh.sh

## Purpose
`test_vxlan_nh.sh` validates VXLAN FDB nexthop group support. It checks that an FDB entry can point at an FDB nexthop group for basic IPv4/IPv6 transmission, that learning paths do not crash when refreshing entries involving nexthop-backed FDB state, and that proxy ARP/ND paths tolerate nexthop-backed FDB entries.

## Important APIs, Functions, and Types
The script sources `lib.sh`, defines `run_cmd` for optional verbose command execution, and uses `exit_cleanup_all` as the `EXIT` trap. `nh_stats_get` reads `ip -s -j nexthop show id 10` with `jq` to extract group packet stats. `tc_stats_get` delegates to `tc_rule_handle_stats_get`. `basic_tx_common` parameterizes address family, protocol, local/remote addresses, and prefix length. `proxy_common` parameterizes ARP/ND proxy coverage. Test functions are `basic_tx_ipv4`, `basic_tx_ipv6`, `learning`, `proxy_ipv4`, and `proxy_ipv6`.

## Control Flow
After option parsing, dependency checks, and an iproute2 nexthop-stats feature probe, the script creates one namespace per test. Basic transmit scenarios add a dummy route, attach a `tc flower` egress filter for UDP VXLAN packets, configure loopback local address, create FDB nexthop IDs `1` and group `10`, create `vx0`, add a static bridge FDB entry using `nhid 10`, inject one Ethernet frame with `mausezahn`, then busy-wait for both nexthop and `tc` packet counters to reach one. `learning` builds two local VXLAN devices and sends a packet that can trigger learning refresh against an entry using `nhid 10`. Proxy tests configure VXLAN `proxy`, a permanent neighbor entry, an FDB nexthop entry, and use `arping` or `ndisc6`.

## State and Persistence
State is per-netns kernel state: dummy links, loopback addresses, routes, nexthops, VXLAN links, bridge FDB entries, neighbor entries, and `tc` filters. No persistent files are created. Cleanup always uses `cleanup_all_ns` through the trap and between tests.

## Dependencies and Integration Points
Dependencies are root-capable networking, `mausezahn`, `arping`, `ndisc6`, `jq`, iproute2 nexthop FDB/stats support, `bridge`, `tc`, and `lib.sh` helpers. Integration points include kernel nexthop FDB objects, VXLAN static FDB resolution through `nhid`, VXLAN learning/localbypass behavior, proxy neighbor suppression, and `SO`-independent packet injection through raw Ethernet frames.

## Risks and Test Signals
Risks include missing iproute2 support, unavailable packet tools, counter timing, and the fact that learning/proxy tests mainly assert absence of crashes rather than packet counters. Strong signals are nexthop group packets reaching one, `tc` egress packets reaching one, successful `arping`/`ndisc6`, and no kernel failure during refresh/proxy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_nh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_nolocalbypass.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_nolocalbypass.sh

## Purpose
`test_vxlan_nolocalbypass.sh` verifies the VXLAN `localbypass`/`nolocalbypass` device option. It creates two VXLAN devices in the same namespace and confirms that local delivery is allowed by default, suppressed after `nolocalbypass`, and restored after setting `localbypass`.

## Important APIs, Functions, and Types
The script defines local `log_test`, `run_cmd`, and `tc_check_packets` helpers and uses `lib.sh` namespace cleanup helpers. `setup` creates namespace `ns1`, loopback VTEP addresses, `vx0` with `nolearning`, and `vx1` with a different destination port. `nolocalbypass` is the sole test and uses `bridge fdb`, `ip -d -j link show`, `jq`, `tc flower`, and `mausezahn`.

## Control Flow
Main parses `-t`, pause, and verbose flags; checks root and command availability; verifies `ip link help vxlan` includes `localbypass`; and then runs selected tests with setup/cleanup around each. The test adds an FDB entry on `vx0` pointing to a local loopback VTEP and port `4790`, installs a `tc` ingress counter on `vx1`, and installs a loopback ingress drop filter for encapsulated UDP port `4790`. It first checks JSON link data reports `localbypass == true`, sends one frame, and expects `vx1` ingress count one. It then sets `nolocalbypass`, confirms JSON reports false, sends again, and expects the `vx1` counter to remain one. Finally, it re-enables `localbypass`, sends again, and expects the counter to become two.

## State and Persistence
All state is in namespace `ns1`: VXLAN links, loopback addresses, FDB entries, qdiscs, filters, and packet counters. The script maintains only shell counters and exits with `ret`; no persistent files are written.

## Dependencies and Integration Points
Dependencies are root, `ip`, `bridge`, `mausezahn`, `jq`, `tc`, and kernel/iproute2 VXLAN localbypass support. It integrates with VXLAN local receive bypass semantics, bridge FDB remote-port selection, link JSON introspection, and `tc` packet counters.

## Risks and Test Signals
The main risk is feature skew: older iproute2 may not expose `localbypass`, and counter checks rely on short sleeps. The test’s signal is exact counter behavior across three sends and link JSON truth values, proving that the option toggles whether locally destined encapsulated traffic bypasses the underlay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_nolocalbypass.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_under_vrf.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_under_vrf.sh

## Purpose
`test_vxlan_under_vrf.sh` checks that VXLAN underlay devices continue to work when moved into a non-default VRF. It simulates two hypervisors and two VMs, verifies VM-to-VM overlay connectivity before the VRF move, moves both underlay `veth0` interfaces into a VRF, bounces the VXLAN devices, and verifies connectivity again.

## Important APIs, Functions, and Types
The script sources `lib.sh`, uses `set -e`, and defines `cleanup`, `setup-hv-networking`, and `setup-vm`. It uses `ip link add type vrf`, `ip link set ... vrf`, Linux bridges, VXLAN links bound to `dev veth0`, veth pairs, `bridge fdb add`, and `ping`.

## Control Flow
The script cleans any stale topology and supports a `clean` argument that exits after cleanup. It creates four namespaces: `hv_1`, `hv_2`, `vm_1`, and `vm_2`. A veth pair connects the hypervisors. Each hypervisor gets `vrf-underlay`, underlay address `172.16.0.x/24`, bridge `br0`, and `vxlan0` attached to the bridge. It confirms hypervisor underlay reachability, then creates a VM veth pair per side and connects each VM to its hypervisor bridge. Static flood FDB entries point each VXLAN device at the other hypervisor. A VM ping verifies default VRF operation. Then both underlay links are enslaved to `vrf-underlay`, both VXLAN devices are brought down/up, and a second VM ping verifies VRF underlay operation.

## State and Persistence
State is transient namespaces, root-namespace veth endpoints during construction, hypervisor bridges, VXLAN links, VRF devices, VM veth interfaces, addresses, and FDB entries. Cleanup deletes known root veth names and all namespaces. No persistent files are created.

## Dependencies and Integration Points
Dependencies include root, `ip`, `bridge`, `ping`, VRF kernel support, VXLAN support, and `lib.sh`. Integration points are VXLAN underlay device binding, VRF master changes, route table association through `type vrf table 1`, bridge/FDB forwarding, and namespace-based topology emulation.

## Risks and Test Signals
The script is intentionally direct and uses `set -e`, so any failed setup command aborts. Risks include kernel or iproute2 lack of VRF/VXLAN support and timing around link rebounce. Test signals are the printed `[ OK ]` checks for hypervisor connectivity, VM overlay connectivity in the default VRF, and VM overlay connectivity after the underlay enters the VRF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_under_vrf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_vnifiltering.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_vnifiltering.sh

## Purpose
`test_vxlan_vnifiltering.sh` validates the VXLAN VNI filtering API and datapath. It models hypervisors with multiple VM namespaces and overlapping VLANs, then verifies that external `vnifilter` VXLAN devices terminate only configured VNIs and interoperate with per-VNI remote/group configuration, multicast groups, traditional VXLAN devices, and metadata devices.

## Important APIs, Functions, and Types
The script sources `lib.sh` and defines `log_test`, `run_cmd`, `check_hv_connectivity`, `check_vm_connectivity`, `cleanup`, `setup-hv-networking`, `setup-vm`, and VNI-filter API cleanup/setup helpers. `setup-vm` is the central parameterized builder: it parses comma-separated VLAN/VNI attributes, creates VM VLAN interfaces and addresses, creates either traditional VXLAN devices or shared external `vnifilter`/metadata devices, enables bridge `vlan_tunnel`, adds tunnel mappings, and programs `bridge vni add` or FDB entries.

## Control Flow
Main checks root, `ip`, `ip link help vxlan` support for `vnifilter`, and `bridge vni` support. The API test creates a separate namespace and checks invalid and valid VNI-filter operations: `vnifilter` without `external`, duplicate VNI assignment across devices, VNI updates, per-VNI multicast group assignment, and immutable `vnifilter` flag changes. Datapath tests build two hypervisor namespaces, create IPv4 and IPv6 underlay addresses, verify hypervisor reachability, create VM namespaces and bridge/VXLAN mappings, then ping VM pairs. Variants cover inherited remote, per-VNI remote, inherited multicast group, per-VNI multicast group, and a mixed topology with traditional, metadata, and filtering VXLAN devices.

## State and Persistence
The script creates namespaces for hypervisors and VMs, root veth links, bridge devices, VXLAN devices, VLAN subinterfaces, VNI filters, FDB entries, and multicast group joins. `cleanup` removes expected root links and all namespaces after each test. No durable files are written; status is held in shell counters.

## Dependencies and Integration Points
Dependencies are root, `ip`, `bridge`, `ping`/`ping6`, kernel VXLAN external metadata and VNI-filter support, and `lib.sh`. It integrates with bridge VLAN filtering, bridge VLAN tunnel information, VXLAN collect-metadata mode, `bridge vni` netlink API, per-VNI remote/group attributes, VM namespace addressing, and multicast datapath behavior.

## Risks and Test Signals
There are several fragile areas: heavy namespace topology, shell parsing of `vattrs`, old iproute2 behavior, ping timing, and feature interactions with IPv6 multicast. Test signals are explicit API return-code expectations and successful VM pings for IPv4 and IPv6 default remote/group cases plus additional pings for mixed traditional/metadata devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_vnifiltering.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tfo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tfo.c

## Purpose
`tfo.c` is a small helper binary for TCP Fast Open passive-path testing. It can run as a server that enables passive TCP Fast Open, accepts one connection, reads data, captures `SO_INCOMING_NAPI_ID` from the accepted socket, and writes that NAPI ID to an output file. It can also run as a client that sends one message with `MSG_FASTOPEN`.

## Important APIs, Functions, and Types
Global configuration is held in `cfg_server`, `cfg_client`, `cfg_port`, `cfg_addr`, and `cfg_outfile`. `parse_address` accepts IPv6 text or IPv4 text mapped into an IPv6 sockaddr. `run_server` uses `socket(AF_INET6, SOCK_STREAM)`, `SO_REUSEADDR`, `TCP_FASTOPEN`, `bind`, `listen`, `accept`, `getsockopt(SO_INCOMING_NAPI_ID)`, `read`, and `fprintf`. `run_client` uses `sendto(..., MSG_FASTOPEN, ...)`. `parse_opts` handles `-s`, `-c`, `-h`, `-p`, and `-o`.

## Control Flow
`main` parses options, then dispatches to server or client mode. Server mode requires no `-h`; it binds to `in6addr_any` on the chosen port and writes the observed NAPI ID after accepting and reading. Client mode resolves the provided server address and sends `"Hello, world!"` in the SYN via `MSG_FASTOPEN`.

## State and Persistence
The helper has no long-lived state beyond the output file written by server mode. Socket state is local to one connection. `cfg_outfile` is dynamically allocated with `strdup` and not freed because process exit follows.

## Dependencies and Integration Points
Dependencies are libc, IPv6 sockets, TCP Fast Open support, Linux `SO_INCOMING_NAPI_ID`, and the caller providing a valid output path. It integrates with `tfo_passive.sh`, which supplies namespaces, netdevsim devices, passive TFO sysctl configuration, and validation that the output NAPI ID is nonzero.

## Risks and Test Signals
Risks include missing TFO support, IPv4-mapped IPv6 assumptions, lack of explicit validation that exactly one of `-s`/`-c` is supplied, and server failure if `-o` is omitted. The key signal is a successful client/server exchange and a nonzero NAPI ID written by the server after `accept`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tfo_passive.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tfo_passive.sh

## Purpose
`tfo_passive.sh` is an integration selftest for passive TCP Fast Open and NAPI ID propagation using `netdevsim`. It creates two simulated net devices in separate namespaces, links them through netdevsim sysfs, runs `tfo` server/client across the link, and verifies the accepted passive TFO socket has a nonzero incoming NAPI ID.

## Important APIs, Functions, and Types
The script sources `lib.sh`, defines random `NSIM_SV_ID` and `NSIM_CL_ID`, sysfs paths under `/sys/bus/netdevsim`, namespace names `nssv` and `nscl`, addresses, and port. `setup_ns` creates namespaces, moves netdevsim interfaces into them, assigns addresses, brings links up, and enables passive TFO using `sysctl net.ipv4.tcp_fastopen=519`. `cleanup_ns` deletes the namespaces.

## Control Flow
The script loads `netdevsim`, creates two devices through `new_device`, waits for udev, calls setup, opens namespace file descriptors, reads each interface index, and writes `fd:ifindex` pairs to `link_device`. It starts `./tfo` in server mode under the server namespace with a temp output file, waits for the local port to listen, then runs `./tfo` in client mode under the client namespace. After both processes finish it reads the server result, rejects zero NAPI ID, checks client/server exit statuses, unlinks and deletes netdevsim devices, removes namespaces, unloads `netdevsim`, and exits.

## State and Persistence
State includes netdevsim kernel devices, namespace file descriptors held by the shell, namespaces, IP addresses, passive TFO sysctl in the server namespace, a temporary output file, and sysfs link/unlink state. Cleanup removes namespaces and netdevsim devices on the success path; several failure branches manually call `cleanup_ns`.

## Dependencies and Integration Points
Dependencies are root, `modprobe`, `netdevsim`, sysfs control files, `udevadm`, `ip netns`, `sysctl`, `timeout`, the local `./tfo` binary, and `wait_local_port_listen` from `lib.sh`. Integration points are netdevsim device linking, namespace file descriptors, passive TCP Fast Open, NAPI ID reporting, and kselftest shell conventions.

## Risks and Test Signals
Risks include random netdevsim ID collision, missing netdevsim module, sysfs permission issues, stale devices after early failures, and reliance on the helper binary being built in the current directory. The decisive signals are successful netdevsim link setup, client/server zero exit status, and an output NAPI ID other than `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tfo_passive.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/timestamping.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/timestamping.c

## Purpose
`timestamping.c` is a standalone demonstrator and regression exerciser for Linux socket timestamping APIs. It sends PTPv1 or PTPv2 UDP multicast sync packets and prints transmit and receive timestamp metadata from software timestamp options, hardware timestamping, socket ioctls, and the error queue.

## Important APIs, Functions, and Types
The program uses `SO_TIMESTAMP`, `SO_TIMESTAMPNS`, `SO_TIMESTAMPING`, `SCM_TIMESTAMPING`, `SOF_TIMESTAMPING_*`, `SOF_TIMESTAMPING_BIND_PHC`, `SIOCSHWTSTAMP`, `SIOCGSTAMP`, `SIOCGSTAMPNS`, `IP_ADD_MEMBERSHIP`, `IP_MULTICAST_IF`, `IP_MULTICAST_LOOP`, `IP_PKTINFO`, and `IP_RECVERR`. `sync` and `sync_v2` are static PTP payloads. `sendpacket` emits one multicast sync. `recvpacket` calls `recvmsg` on normal or error queues. `printpacket` decodes control messages and optional ioctl timestamps. `main` parses options, configures the interface and socket, and runs the event loop.

## Control Flow
The program expects an interface name, optional PHC index, and option tokens. It opens a UDP socket, fetches the interface address, configures hardware timestamping according to requested flags, binds to PTP event port 319, binds the socket to the device, joins multicast group `224.0.1.130`, configures timestamp socket options, and prints effective option values. The infinite loop schedules a send every five seconds. Between sends it uses `select` on read and error sets, then attempts both normal `recvmsg` and `MSG_ERRQUEUE` reads and prints any ancillary data.

## State and Persistence
The program persists no files. Runtime state is the socket, interface hardware timestamping configuration, multicast membership, selected option flags, and loop timing. Because it may call `SIOCSHWTSTAMP`, it can alter hardware timestamp configuration on the selected network device for the duration and potentially beyond process exit depending on driver behavior.

## Dependencies and Integration Points
Dependencies include Linux timestamping headers, a network interface with an IPv4 address, multicast support, possible hardware timestamp support, and permission to configure interface timestamping. Integration points are PTP-like UDP traffic, socket ancillary data, device ioctls, error-queue timestamp delivery for transmitted packets, and PHC binding where supported.

## Risks and Test Signals
Risks include infinite runtime unless externally stopped, hardware/driver-specific `SIOCSHWTSTAMP` behavior, verbose output rather than structured pass/fail, and possible permission failures. Useful signals are successful option configuration, printed matching `SO_TIMESTAMPING` flags/PHC binding, received control messages containing software or raw hardware timestamps, `IP_RECVERR` timestamping origins, and matching returned packet payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/timestamping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tls.c

## Purpose
`tls.c` is a comprehensive kselftest harness for the Linux kernel TLS ULP. It validates TLS socket setup, supported cipher/version combinations, send/receive data paths, zero-copy/sendfile/splice behavior, control records, TLS 1.3 rekeying, error handling, polling/epoll readiness, record sizing, IPv6 socket operations, prequeue behavior, and edge cases around zero-length records and partial records.

## Important APIs, Functions, and Types
The file uses `kselftest_harness.h` fixtures and variants. `struct tls_crypto_info_keys` wraps all tested `linux/tls.h` crypto-info layouts and stores the active length. `tls_crypto_info_init` initializes the right crypto info for AES-GCM, ChaCha20-Poly1305, SM4, AES-CCM, and ARIA variants. `ulp_sock_pair` creates a connected TCP pair and enables `TCP_ULP` `"tls"` on both ends, marking `notls` when the kernel lacks TLS. `tls_send_cmsg`, `__tls_recv_cmsg`, and `tls_recv_cmsg` exercise `SOL_TLS` record type control messages. `memrnd`, `chunked_sendfile`, `test_mutliproc`, `parse_tls_records`, `tls_send_keyupdate`, and `tls_recv_keyupdate` support reusable test patterns.

## Control Flow
Two main fixtures drive most tests: `tls_basic` for setup without keys until individual tests install them, and `tls` with cipher/version variants that install TX on one endpoint and RX on the other. Variant setup skips FIPS-incompatible ciphers when `/proc/sys/crypto/fips_enabled` is set. Tests cover plain ULP pass-through, bad cipher/version rejection, record sequence wrap, sendfile and chunk boundaries, `MSG_MORE`/`MSG_EOR`, sendmsg and recvmsg scatter/gather, splice in both directions, peek semantics, low-water behavior, bidirectional TLS, blocking and nonblocking transfer, multiprocessing stress, control messages, shutdown/reuse, getsockopt validation, bad iov recovery, TLS 1.3 rekey and polling behavior, raw zero-length AES-CCM record sequences, malformed record/authentication errors, timeout behavior, partial-record poll/epoll readiness, TX max payload sizing, non-established ULP rejection, key-size acceptance, no-pad getsockopt/setsockopt, IPv6 operations, prequeued encrypted data, and data-steal race behavior.

## State and Persistence
State is mostly per-test socket state: connected TCP sockets, installed TLS TX/RX keys, record sequence numbers, pending open records, pipe buffers, temporary anonymous files, child processes, and poll/epoll waiters. The constructor reads but does not write `/proc/sys/crypto/fips_enabled`. Some tests create temporary files with `mkstemp` or `O_TMPFILE` and unlink/close them. No repository files are modified.

## Dependencies and Integration Points
Dependencies are Linux kTLS support, `linux/tls.h`, `linux/tcp.h`, TCP sockets, splice/vmsplice/sendfile support, epoll/poll, fork/wait, and the kselftest harness. Integration points include `TCP_ULP`, `SOL_TLS` options `TLS_TX`, `TLS_RX`, `TLS_RX_EXPECT_NO_PAD`, `TLS_TX_MAX_PAYLOAD_LEN`, `TLS_SET_RECORD_TYPE`, `TLS_GET_RECORD_TYPE`, kernel crypto implementations, FIPS mode policy, and TCP/TLS receive queue interactions.

## Risks and Test Signals
Risks include kernel feature skew by cipher, FIPS-mode skips, architecture differences in pipe sizing and nonblocking timing, forked-child failure propagation, and intentionally corrupted TLS records leaving sockets in error states. Strong signals are kselftest assertions over exact return values and `errno`, byte-for-byte plaintext equality, expected skips for unsupported TLS/FIPS cases, proper readiness transitions for poll/epoll, and successful behavior across every fixture variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tls.c -->
