# Research Report: subset-b-006872

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_x_next_csid_l3vpn_test.sh
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_x_next_csid_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_x_next_csid_l3vpn_test.sh

Purpose: this kselftest validates Linux SRv6 End.X with the `next-csid` flavor in an L3 VPN topology. It builds four router namespaces and two host namespaces, configures IPv4 and IPv6 VPN service over compressed SID containers, and confirms both single-container and two-SID policy forwarding.

Important APIs and functions: the script sources `lib.sh` for `setup_ns`, `cleanup_all_ns`, and kselftest return codes. It uses `ip netns`, `ip -6 route ... encap seg6local action End.X`, `flavors next-csid lblen ... nflen ...`, `End.DT46`, VRF links, dummy links, proxy ARP/NDP, and `ping`. Key helpers include `build_ipv6_addr`, `build_csid`, `build_lcnode_func_prefix`, `set_end_x_nextcsid`, `set_end_x_ll_nextcsid`, `setup_rt_local_sids`, `__setup_l3vpn`, `csid_container_cfg_tests`, and the connectivity check wrappers.

Control flow: prerequisites check root, `ip`, `ping`, `sysctl`, `grep`, `cut`, iproute2 next-csid support, dummy device support, and VRF support. `setup` creates namespaces, router meshes, host VRFs, local SID lookup tables, reduced-encap policies, End.DT46 decap routes, and End.X next-csid adjacencies. Tests first validate C-SID layout acceptance and rejection, then router reachability, host gateway reachability, IPv6 and IPv4 VPN connectivity, and finally link-local next-hop variants for End.X.

State and persistence: all state is transient kernel namespace state. `SETUP_ERR` decides whether cleanup exits as skip or with accumulated `ret`. `nsuccess` and `nfail` track test accounting. Namespace names are shell variables created through `setup_ns`; routes and rules live only until `cleanup_all_ns` runs through the EXIT trap.

Dependencies and integration points: depends on Linux SRv6 seg6local, NEXT-C-SID support in kernel and iproute2, VRF strict mode, dummy netdev, IPv4 forwarding, IPv6 forwarding, and network namespace support. It integrates with `tools/testing/selftests/net/lib.sh` and kselftest skip/fail conventions.

Risks: the test is root-only and can be skipped by missing iproute2 features even when the kernel has support. It assumes specific return code `2` for invalid C-SID route additions. It also relies on shell `eval` namespace variables and on route command formatting remaining stable. The topology is dense, so setup failures can mask behavior as skips.

Test signals: success is observable through OK lines for valid and invalid C-SID container configurations, router pair pings, host gateway pings, IPv4/IPv6 host VPN pings, and repeated VPN pings after switching End.X next-hop programming to IPv6 link-local mode. Any failed ping or unexpected C-SID route return increments `nfail` and exits nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_x_next_csid_l3vpn_test.sh -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hencap_red_l3vpn_test.sh
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hencap_red_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hencap_red_l3vpn_test.sh

Purpose: this script tests SRv6 `H.Encaps.Red` L3 VPN behavior. It verifies reduced SRH encapsulation for IPv4 and IPv6 VPNs across four SRv6 routers and four hosts, including VPN isolation and optional per-route tunnel source (`tunsrc`) handling.

Important APIs and functions: it uses `ip route ... encap seg6 mode encap.red`, `seg6local action End`, `seg6local action End.DT46 vrftable`, VRF devices, proxy NDP/ARP, `ip6tables -t raw`, and namespace sysctls. Major helpers are `setup_rt_networking`, `setup_rt_local_sids`, `__setup_rt_policy`, `setup_rt_policy_ipv6`, `setup_rt_policy_ipv4`, `setup_hs`, `check_tunsrc_support`, `host_vpn_tests`, and `host_vpn_isolation_tests`.

Control flow: after root and command checks, the script verifies iproute2 has `encap.red`, confirms VRF availability, probes tunsrc support in a temporary namespace, then builds a full-mesh router topology and four access hosts. `setup` installs local End and End.DT46 SIDs, unreachable VRF defaults, and six SRv6 policies covering hs1/hs2 IPv4+IPv6 and hs3/hs4 IPv6. Runtime tests validate router reachability, host-to-gateway reachability, intended VPN connectivity, and cross-VPN isolation.

State and persistence: state is held in netns routing tables, VRFs, ip rules, ip6tables raw rules, and transient shell counters. `HAS_TUNSRC` changes whether deprecated `::dead:<rt>` addresses and tunsrc-specific decap filters are installed. The EXIT trap removes namespaces through `cleanup_all_ns`; no durable state is written.

Dependencies and integration points: relies on `lib.sh`, root, network namespaces, iproute2 SRv6 reduced encap support, VRF strict mode, ip6tables when tunsrc is available, and kernel seg6local End/End.DT46. It is part of selftests/net and reports through kselftest skip/fail exit codes.

Risks: optional tunsrc behavior is silently disabled if either route syntax or ip6tables support is missing, so a pass may not cover tunsrc. Isolation checks expect failed pings to return `1`, which can be fragile across ping variants. The script uses broad namespace names from `setup_ns` and many route entries, so partial setup errors become a skip via `SETUP_ERR`.

Test signals: passing output includes router connectivity, IPv4/IPv6 host-to-gateway checks for all hosts, positive hs1/hs2 and hs3/hs4 VPN reachability, and negative cross-VPN isolation, including IPv4-only isolation between hs2 and hs4. Counter variables produce a final passed/failed summary and nonzero status on test failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hencap_red_l3vpn_test.sh -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hl2encap_red_l2vpn_test.sh
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hl2encap_red_l2vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hl2encap_red_l2vpn_test.sh

Purpose: this selftest validates SRv6 `H.L2Encaps.Red` behavior for an L2 VPN. It tunnels host Ethernet frames carrying IPv4 or IPv6 over an SRv6 router fabric and decapsulates them with End.DX2 to the destination access interface.

Important APIs and functions: it uses `ip route ... encap seg6 mode l2encap.red`, `seg6local action End`, `seg6local action End.DX2 oif`, dummy devices, static neighbor entries, manual MAC assignment, and pings. Important helpers are `setup_rt_local_sids`, `__setup_rt_policy`, `setup_decap`, `set_mac_address`, `set_host_l2peer`, `setup_l2vpn`, `router_tests`, `host2gateway_tests`, and `host_vpn_tests`.

Control flow: root and tool checks are followed by iproute2 `l2encap.red` support and dummy device probing. `setup` creates four router namespaces and two host namespaces, meshes router veth links, assigns router underlay addresses, creates host access links, adds End local SIDs, then configures two directional L2 VPN paths. hs1 to hs2 uses a direct decap SID; hs2 to hs1 traverses rt4 and rt3 before End.DX2 at rt1.

State and persistence: all state is transient network namespace state. The script deliberately rewrites host and router-side access MAC addresses so L2 forwarding and static neighbor entries align with the remote host identity. `SETUP_ERR`, `ret`, `nsuccess`, and `nfail` track execution state, and the EXIT trap invokes namespace cleanup.

Dependencies and integration points: depends on root, network namespaces, iproute2 SRv6 l2 reduced encapsulation, kernel seg6local End and End.DX2, dummy netdev, sysctl, ping, and `lib.sh`. It integrates with kselftest by returning skip before setup completion and fail on connectivity failures.

Risks: Linux SRv6 L2 support is limited here to L2 frames carrying IPv4/IPv6, so other ethertypes are out of scope. The test depends on stable manually generated MAC addresses and static neighbor entries; neighbor learning changes or duplicate MACs would affect results. The destination-side `setup_decap "${rtsrc}"` naming is subtle because `rtsrc` is the decap router for the opposite direction.

Test signals: positive signals are full router mesh pings, host-to-gateway pings for IPv4 and IPv6, and bidirectional hs1/hs2 VPN pings for both protocols. Any unexpected ping failure logs a `[FAIL]` line and the final summary exits with failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_hl2encap_red_l2vpn_test.sh -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_iptunnel_cache.sh
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_iptunnel_cache.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_iptunnel_cache.sh

Purpose: this test checks that SRv6 lwtunnel encapsulation does not share `dst_cache` entries between forwarding input path and locally generated output path. It specifically catches a bug where forwarded traffic populates a per-CPU cache that later lets a local ping bypass its own route lookup.

Important APIs and functions: it uses `ip -6 route add ... encap seg6 mode encap`, `seg6local action End.DT6`, IPv6 rules matching `iif`, blackhole routes, static neighbors, `taskset`, and `ping`. Functions are `cleanup`, `check_prerequisites`, `setup`, and `test_cache_isolation`.

Control flow: the script checks root and tools, creates `NS_SRC`, `NS_RTR`, and `NS_DST`, wires them with two veth pairs, sets fixed MACs and static neighbors, and programs the router with an SRv6 encap route to `cafe::1`. The SID route is reachable only through table 100 for packets arriving on `veth-r0`, while the main table blackholes the SID. The test pins all pings to CPU 0, confirms local ping initially fails, forwards one ping from source to destination, then confirms local ping still fails.

State and persistence: network state is temporary and namespace-scoped. The critical state under test is kernel per-CPU destination cache inside the SRv6 lwtunnel path, not userland files. `RET` holds the final kselftest status and cleanup removes all namespaces on EXIT.

Dependencies and integration points: requires root, `ip`, `ping`, `sysctl`, `taskset`, IPv6 forwarding, SRv6 encap and End.DT6 support, policy routing, and `lib.sh`. It integrates as a standalone shell selftest with kselftest skip and fail codes.

Risks: taskset assumes CPU 0 is available to both namespace executions. Topology failures are reported as skips because they invalidate the cache-isolation signal. Static neighbor entries avoid ND noise but make the test sensitive to veth setup errors.

Test signals: a correct kernel prints `PASS: output path dst_cache is independent`. A failure prints `FAIL: output path used dst cached by input path` and exits with `ksft_fail`. If the first local ping succeeds or the forwarded ping fails, the test skips as a broken topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_iptunnel_cache.sh -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.c

Purpose: this C helper stress-tests `listen()` scalability for many IPv6 sockets that share a port with `SO_REUSEPORT`. It creates many VIP:443 groups and measures the time to transition all sockets to listening state.

Important APIs and functions: `bind_reuseport_sock6` allocates the socket array, builds IPv6 addresses starting at `2401:dead::1`, sets `SO_REUSEPORT`, binds each socket to port 443, and increments the low 32 bits for each VIP. `main` parses `<nr_vips> <nr_socks_per_vip>`, calls `listen(fd, 0)` for every socket, measures time with `CLOCK_MONOTONIC`, prints elapsed time, closes descriptors, and frees memory.

Control flow: all sockets are created and bound before any listen call. The listen loop is the measured region, so the result focuses on kernel listen path cost under many reuseport groups rather than bind cost. Any syscall failure aborts through `error(1, errno, ...)`.

State and persistence: process state consists of global `nr_socks_per_vip`, `nr_vips`, and the allocated fd array. Kernel state is a large set of bound/listening TCP IPv6 sockets; it disappears after close or process exit. No files are written.

Dependencies and integration points: built as a selftest helper and invoked by `stress_reuseport_listen.sh` inside a network namespace with `net.ipv6.ip_nonlocal_bind=1`, allowing bind to many unassigned VIP addresses. It uses standard libc, IPv6 sockets, and Linux `SO_REUSEPORT`.

Risks: the printed microsecond field uses `(end_ns - start_ns) / NSEC_PER_USEC`, not a remainder, so display formatting is coarse. Very large inputs can exhaust file descriptors or memory. The code increments `s6_addr32[3]` in host memory order, which is acceptable for generating distinct test addresses but not a generic address arithmetic helper.

Test signals: successful execution prints a line like `listen 24000 socks took ...` and exits zero. Any socket, setsockopt, bind, listen, malloc, or address conversion failure exits nonzero with a diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.sh
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.sh

Purpose: this shell wrapper prepares the namespace and resource limits for the `stress_reuseport_listen` binary. Its target workload is 300 VIPs with 80 reuseport sockets each, for 24,000 listening sockets.

Important APIs and functions: it sources `lib.sh`, uses `setup_ns` and `cleanup_ns`, changes `net.ipv6.ip_nonlocal_bind`, adjusts `ulimit -n`, and runs `ip netns exec $NS ./stress_reuseport_listen 300 80`. `setup` and `cleanup` are the only local functions.

Control flow: the script saves the current file descriptor limit, registers cleanup with EXIT, creates one namespace, enables IPv6 nonlocal bind inside it, raises the file descriptor limit to 24,100, and invokes the C helper. Cleanup removes the namespace and restores the saved limit.

State and persistence: transient shell state includes `NR_FILES`, `SAVED_NR_FILES`, and the namespace variable from `setup_ns`. Kernel state includes the namespace sysctl and sockets created by the child process. No persistent output is created beyond stdout/stderr.

Dependencies and integration points: depends on the compiled `stress_reuseport_listen` binary being in the current directory, root or sufficient privileges for namespace/sysctl operations, and `lib.sh`. It participates in kselftest by returning the helper's status unless setup or cleanup fails.

Risks: the script does not explicitly check that raising `ulimit -n` succeeded before running the helper. It assumes the current working directory inside kselftest contains the compiled binary. The namespace variable is unquoted in a few commands, relying on `setup_ns` to produce safe names.

Test signals: success is the helper's timing line and zero exit. Resource limit, namespace, sysctl, or helper failures cause nonzero exit and are visible in shell diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/stress_reuseport_listen.sh -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tap.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tap.c

Purpose: this kselftest verifies TAP/macvtap packet injection behavior with virtio net headers. It checks that valid UDP GSO and checksum-valid packets are accepted, and that a malformed GSO packet with invalid Ethernet protocol is rejected with `EINVAL`.

Important APIs and functions: device setup uses raw rtnetlink helpers `rtattr_add`, `rtattr_begin`, `dev_create`, `dev_delete`, `macvtap_fill_rtattr`, and `opentap`. Packet builders include `build_eth`, checksum helpers, `build_ipv4_header`, `build_udp_packet`, `build_test_packet_valid_udp_gso`, `build_test_packet_valid_udp_csum`, and `build_test_packet_crash_tap_invalid_eth_proto`. Tests use `kselftest_harness.h` fixtures and assertions.

Control flow: the fixture creates a dummy lower device and a macvtap device linked to it, opens `/dev/tap<ifindex>` with `IFF_TAP | IFF_NO_PI | IFF_VNET_HDR | IFF_MULTI_QUEUE`, and tears both devices down after each test. Each test builds a packet in a stack buffer, writes it to the tap fd, and asserts either full write length or `-1/EINVAL`.

State and persistence: kernel state is limited to temporary netdevices and an open tap file descriptor. Packet content is generated in memory. Fixture teardown deletes both devices and closes the fd; no persistent files are written.

Dependencies and integration points: requires root or capabilities for netlink device creation and `/dev/tap*` access, macvtap and dummy support, Linux virtio-net header definitions, and the selftest harness. It integrates with kselftest's fixture lifecycle and assertion reporting.

Risks: `dev_create` and `dev_delete` send netlink requests but do not read full ACK details, so failures may surface indirectly. The invalid packet builder intentionally lays out odd headers to exercise a crash path; maintenance should preserve that malformed structure. Device names are fixed (`xmacvtap0`, `xdummy0`) and can conflict with a dirty test environment.

Test signals: two valid packet tests expect `write()` to return the exact generated length. The regression test expects `write()` to fail with `EINVAL`; a successful write there indicates the kernel accepted malformed GSO metadata unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tap.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/Makefile
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/Makefile

Purpose: this Makefile builds the TCP-AO selftest suite for both IPv4 and IPv6 variants and links each program against a shared local static test library. It is the build integration point for the TCP-AO sources in this subset.

Important APIs and variables: `TEST_BOTH_AF` lists programs compiled for both address families, including `bench-lookups`, `connect`, `connect-deny`, `icmps-accept`, `icmps-discard`, and `key-management`. `TEST_IPV4_PROGS`, `TEST_IPV6_PROGS`, and `TEST_GEN_PROGS` derive output names. `LIBSRC` lists shared library sources, and `LIB`, `LIBOBJ`, `LIBDEPS`, `CFLAGS`, and `LDLIBS` define build products and flags.

Control flow: it includes `../../lib.mk`, builds `$(OUTPUT)/lib/libaotst.a` with `$(HOSTAR)`, compiles library objects from `./lib/*.c`, and makes every generated test depend on the library. Pattern rules build `%_ipv4` normally and `%_ipv6` with `-DIPV6_TEST`. Per-target flags add `-DTEST_ICMPS_ACCEPT` for `icmps-accept` and `-lm` for `bench-lookups`.

State and persistence: generated state is confined to `$(OUTPUT)` and the `$(OUTPUT)/lib` subdirectory. `EXTRA_CLEAN` records library objects and archive for cleanup. Source files are not modified.

Dependencies and integration points: depends on kernel headers via `$(KHDR_INCLUDES)`, selftest `lib.mk`, pthreads, and math library for benchmark statistics. It includes headers from `../../../../include/` and `./lib/`.

Risks: `icmps-accept.c` and `icmps-discard.c` share the same source body semantics, with target-specific behavior selected by compile flags; missing the per-target flag would invert the accept test. All tests are compiled twice, so source code must remain address-family-generic through `aolib.h` macros.

Test signals: build success creates IPv4 and IPv6 binaries in `$(OUTPUT)`. Correct target-specific behavior is visible in `icmps-accept_*` receiving `TEST_ICMPS_ACCEPT` and benchmark binaries linking successfully with `-lm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/Makefile -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/bench-lookups.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/bench-lookups.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/bench-lookups.c

Purpose: this TCP-AO benchmark measures lookup and update costs as the number of matching key tuples grows. It times key deletion, key re-addition, asynchronous deletion, and connect-time key selection for 512 through 8192 keys.

Important APIs and functions: it uses `test_add_key`, `TCP_AO_DEL_KEY`, `ip_route_add`, `ip_addr_add`, `test_connect_socket`, `test_wait_fd`, and shared namespace synchronization. Key functions include `gen_test_ips`, `test_add_routes`, `server_apply_keys`, `measure_call`, `bench_delete`, `bench_connect_srv`, `bench_connect_client`, `client_addr_setup`, `server_fn`, and `client_fn`. `bench_stats` stores min, max, count, mean, and Welford accumulation.

Control flow: for each key count, the server allocates deterministic odd test addresses, adds routes, raises optmem sizing, installs one AO key per address on the listener, and runs two connect benchmark phases. It then times worst-case and random key deletion plus restoration, and async deletion. The client adds local addresses and routes, binds to selected source addresses, installs the corresponding AO key, synchronizes with the server, and measures connect calls.

State and persistence: benchmark state lives in `bench_results`, global `test_ips`, per-socket TCP-AO key lists, and routes/addresses added to the test namespace. `test_set_optmem` changes socket optmem limits for the process/test environment. No persistent files are produced.

Dependencies and integration points: compiled twice for IPv4/IPv6 via the Makefile and links with `-lm` for `sqrt`. It relies on the TCP-AO selftest library for topology, socket helpers, and test reporting.

Risks: the "random-search" client phase currently calls `bench_connect_client(..., false)` in the inspected source, so it reuses sequential order while printing random-search text. The standard deviation print uses `sqrt((mean/1000000)/nr)` rather than `s2`, so it is not a true variance-derived standard deviation. High key counts require sufficient optmem and memory.

Test signals: output consists of `test_ok` benchmark lines with min/max/mean fields for add, delete worst case, delete random-search, delete async, connect worst case, and connect random-search. Syscall or connection failures abort the test through `test_error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/bench-lookups.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/config
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/config

Purpose: this kselftest config fragment documents kernel options needed for the TCP-AO selftests. It enables TCP-AO, supporting crypto algorithms, namespace/VRF infrastructure, tracepoints, IPv6 routing tables, TCP-MD5, and veth.

Important entries: `CONFIG_TCP_AO=y` is the primary feature. `CONFIG_TCP_MD5SIG=y` supports MD5 comparison tests. `CONFIG_CRYPTO_CMAC`, `CONFIG_CRYPTO_HMAC`, `CONFIG_CRYPTO_RMD160`, and `CONFIG_CRYPTO_SHA1` cover algorithms used by key tests. `CONFIG_IPV6` and `CONFIG_IPV6_MULTIPLE_TABLES` support IPv6 variants. `CONFIG_NET_L3_MASTER_DEV`, `CONFIG_NET_VRF`, and `CONFIG_VETH=m` support test topology and VRF coverage. `CONFIG_TRACEPOINTS=y` enables ftrace event validation.

Control flow: this is declarative data consumed by kselftest build/config tooling rather than executable code. It does not include conditionals or generated state.

State and persistence: the file persists desired kernel config symbols in the source tree. It does not change the running kernel; it informs configuration checks and build/test environments.

Dependencies and integration points: maps directly to runtime probes in `lib/kconfig.c` and skip messages in `aolib.h`. Missing required symbols cause test skips or failures depending on the helper and feature.

Risks: the fragment is not exhaustive for every algorithm used in `key-management.c`, which also references SHA-2, SHA-3, MD5, and AES-CMAC behavior through crypto names. Runtime FIPS mode can still disable non-FIPS algorithms even when symbols exist. `CONFIG_VETH=m` requires the module to be loadable in the test environment.

Test signals: indirect signal is reduced skip count from `kernel_config_has()` probes and successful execution of TCP-AO, TCP-MD5, VRF, veth, IPv6, and tracepoint tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/config -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect-deny.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect-deny.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect-deny.c

Purpose: this TCP-AO selftest validates that connections are denied or accepted correctly for mismatched authentication conditions. It covers non-AO/AO asymmetry, wrong password, wrong send or receive IDs, MAC length mismatch, wrong addresses, and prefix-based matching.

Important APIs and functions: it uses `TCP_AO_ADD_KEY`, `test_prepare_key`, `test_verify_socket_key`, `test_skpair_wait_poll`, `test_skpair_connect_poll`, `test_get_tcp_counters`, `netstat_get_one`, and ftrace expectation helpers. Core functions are `test_add_key_maclen`, `try_accept`, `server_fn`, `try_connect`, and `client_fn`. The shared `sk_pair` volatile variable propagates peer-side connection failures.

Control flow: server and client iterate through the same port sequence. For each case the server prepares a listener with or without AO keys and waits for readiness or expected timeout/key rejection. The client configures the corresponding AO key state, optionally registers expected TCP-AO/hash trace events, then attempts connect with polling. Both sides synchronize before preparation, counter checks, and close.

State and persistence: all state is per-process, per-socket, and namespace-local. TCP-AO counters are sampled before and after selected cases, and netstat counters such as `TCPAOKeyNotFound`, `TCPAORequired`, `TCPAOBad`, and `TCPAOGood` are checked for increments. No files are written.

Dependencies and integration points: built for IPv4 and IPv6 via `aolib.h` macros. It integrates with optional ftrace validation, TCP-AO counter helpers, and the shared two-thread test harness from the TCP-AO library.

Risks: expected failures depend on TCP retransmission timing and counter updates; the polling helpers mitigate but cannot remove all timing sensitivity. Some cases intentionally expect no counters, such as SYNACK no-key behavior. Prefix match uses prefix length 16 for both address families through clamping helpers, so interpretation differs by family.

Test signals: each scenario emits `test_ok` on expected accept, timeout, refusal, or key rejection. Counter assertions verify per-socket/per-netns AO counters, and ftrace destructor reports missing or unexpected trace events if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect-deny.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect.c

Purpose: this is the baseline positive TCP-AO connection test. It verifies that a client and server with matching AO keys can connect, exchange data, and increment TCP-AO good-packet counters.

Important APIs and functions: `server_fn` creates a listener with `test_listen_socket`, installs a default AO key with `test_add_key`, accepts one connection, and calls `test_server_run`. `client_fn` creates a TCP socket, installs the same key, connects with `test_connect_socket`, sends and verifies 20 messages through `test_client_verify`, and checks counters with `netstat_read`, `netstat_get`, `test_get_tcp_counters`, and `test_assert_counters`.

Control flow: `test_init(2, server_fn, client_fn)` sets up the two namespace peers. Server and client synchronize after key installation and after connection establishment. The client records netstat and per-socket counters before data transfer, performs the transfer, records counters again, prints netstat diffs, and validates that `TCPAOGood` increased by at least the number of packets.

State and persistence: state is per-socket AO key material, TCP counters, and temporary netstat snapshots. `netstat_free` and `test_assert_counters` release allocated counter state. No persistent files are written.

Dependencies and integration points: depends on TCP-AO support, the shared TCP-AO selftest library, network namespace/veth setup from the harness, and IPv4/IPv6 macros selected by the Makefile.

Risks: the server calls `test_fail` after `test_server_run` returns, meaning the server side is not expected to exit normally before the client/test harness ends. Counter expectations assume at least 20 good AO packets, but retransmission or aggregation can make exact counts unsuitable, so the test uses a lower-bound check for netstat and structured assertions for socket/key counters.

Test signals: success includes a `connect TCPAOGood ... sent 20` `test_ok` line and passing counter assertions. Any connect, key install, accept, verify, or counter mismatch reports failure or exits through `test_error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/connect.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-accept.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-accept.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-accept.c

Purpose: this source implements the TCP-AO ICMP interference test body. When built as `icmps-accept`, the Makefile defines `TEST_ICMPS_ACCEPT`, so the listener enables AO `accept_icmps` and the test expects matching ICMP hard errors to be accepted rather than ignored.

Important APIs and functions: the test uses `test_set_ao_flags`, `test_add_key`, `test_server_run`, `test_client_verify`, raw IPv4/IPv6 sockets, `TCP_REPAIR` and `TCP_QUEUE_SEQ` to obtain `rcv_nxt`, netstat readers, and TCP-AO counter helpers. Packet builders include `set_ip4hdr`, `icmp_interfere4`, `set_ip6hdr`, `icmp6_checksum`, `icmp6_interfere`, and `icmp_interfere`.

Control flow: the server listens with AO, sets `accept_icmps` according to the compile flag, accepts a connection, enables `IP_RECVERR` or `IPV6_RECVERR`, and runs `serve_interfered`. The client connects with AO, repeatedly sends valid data, obtains receive sequence state, and injects forged ICMP destination-unreachable packets matching the connection. The server checks destination-unreachable counters, AO dropped-ICMP counters, and whether data service failed or survived according to the build mode.

State and persistence: transient state includes packet counters, generated raw ICMP packets, TCP repair mode toggles, and netstat snapshots. In accept mode the expected state is that ICMPs are delivered as errors rather than counted as AO-dropped ICMPs. No durable files are modified.

Dependencies and integration points: compiled twice for IPv4/IPv6 and specifically with `-DTEST_ICMPS_ACCEPT` for this target. Requires raw socket privileges, TCP-AO support, TCP repair support, and the shared TCP-AO library.

Risks: source content is identical to `icmps-discard.c`; semantics depend entirely on the Makefile target flag. The raw packet construction is sensitive to kernel ICMP validation, sequence numbers, and address family layout. The code increments `icmps_sent` both in lower helpers and again in the loop, but that variable is not used as an assertion source.

Test signals: in accept mode, server failure with a hard error is considered OK, `TCPAODroppedIcmps` should not be required to increase, and counter assertions expect good AO traffic only. Destination unreachable counters must increase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-accept.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-discard.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-discard.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-discard.c

Purpose: this source implements the default TCP-AO ICMP discard test body. Built as `icmps-discard`, it does not define `TEST_ICMPS_ACCEPT`, so the test verifies RFC5925 default behavior: matching ICMP hard errors for established AO connections are ignored and counted as dropped.

Important APIs and functions: the file uses the same helpers as `icmps-accept.c`: `test_set_ao_flags`, `test_add_key`, `test_server_run`, raw ICMP/ICMPv6 packet generation, `TCP_REPAIR` receive-sequence reads, `netstat_read`, and `test_assert_counters`. Compile-time macros invert `test_icmps_fail` and `test_icmps_ok` depending on `TEST_ICMPS_ACCEPT`.

Control flow: server and client establish a valid AO connection. The client continuously sends verified data and injects forged destination-unreachable packets with embedded TCP headers matching the connection. The server serves a quota while `IP_RECVERR` or `IPV6_RECVERR` is enabled, then validates that destination-unreachable counters increased but the application connection survived.

State and persistence: all state is socket and namespace local. The key persistent signal during the run is counter deltas for `TCPAODroppedIcmps`, `InDestUnreachs` or `Icmp6InDestUnreachs`, and AO per-socket/per-namespace counters. No files are written.

Dependencies and integration points: built for IPv4 and IPv6 without the accept flag. It requires raw socket capability, TCP-AO, TCP repair, and the shared aolib network harness.

Risks: because it shares source text with `icmps-accept.c`, a build-system regression can silently change expected semantics. Raw ICMP injection is sensitive to checksum correctness and sequence selection. Timing depends on the server quota being long enough for injected ICMPs to arrive.

Test signals: a correct discard run reports delivered destination-unreachable packets, server survival, incremented `TCPAODroppedIcmps`, and `TEST_CNT_GOOD | TEST_CNT_AO_DROPPED_ICMP` counter deltas. A server hard-error failure is a test failure in this build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-discard.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/key-management.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/key-management.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/key-management.c

Purpose: this is the main TCP-AO key lifecycle test. It verifies adding, deleting, selecting, rotating, matching, dumping, and counter-accounting for AO master key tuples on closed, listening, and established sockets, including current-key and rnext-key behavior.

Important APIs and types: it uses `TCP_AO_ADD_KEY`, `TCP_AO_DEL_KEY`, `TCP_AO_INFO`, `TCP_AO_GET_KEYS`, `TCP_AO_REPAIR`, VRF helpers, ftrace expectations, and counter helpers. `struct test_key` models password, algorithm, client/server key IDs, MAC length, match flags, current/rnext flags, and expected counter usage. `struct key_collection` owns the generated key set. Important functions include `setup_vrfs`, `prepare_sk`, `test_del_key`, `try_delete_key`, `test_set_key`, `check_closed_socket`, `check_listen_socket`, `init_default_key_collection`, `key_collection_socket`, `verify_keys`, `verify_counters`, `start_server`, `run_client`, `try_unmatched_keys`, `check_current_back`, and `roll_over_keys`.

Control flow: the client thread first tests closed sockets and listen sockets, then established sockets. The server thread runs matching established scenarios in parallel. Tests cover deletion of ordinary/current/rnext keys, forced replacement during deletion, rejection of current/rnext changes on listeners, restriction of AO repair on listeners, current/rnext setup before connect, peer rnext requests that rotate current keys, rotation across 20 keys, and established-socket pruning of nonmatching address or VRF keys.

State and persistence: large transient state is stored in `collection.keys`; per-key flags are updated to indicate expected transmit use and skipped counter checks. Kernel state includes AO keys, AO info current/rnext fields, optional VRF route/device state, and per-key counters. FIPS mode is cached from `/proc/sys/crypto/fips_enabled` and removes non-FIPS algorithms from generation.

Dependencies and integration points: relies on TCP-AO, optional VRF, optional ftrace tracepoints, crypto algorithms, and all shared aolib socket/counter/topology helpers. The Makefile builds it for IPv4 and IPv6. It uses `TEST_WRONG_IP` and `TEST_NETWORK` macros for address-family-specific negative matching.

Risks: the test has intentional `test_xfail` paths for some listener current/rnext deletion behavior, so not every surprising result is a hard failure. Randomized key material and algorithm selection can make failures hard to reproduce unless the random seed is controlled by the broader harness. VRF-specific coverage is skipped when VRF support is absent.

Test signals: success emits 121 planned test results across key deletion, listener restrictions, key dumps, current/rnext verification, data-transfer survival, key rotation, counter assertions, and trace expectations. Failures identify the scenario name and key tuple details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/key-management.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/aolib.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/aolib.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/aolib.h

Purpose: this header is the central API contract for TCP-AO selftests. It defines logging wrappers, feature probes, address-family abstraction, namespace and netlink helpers, socket helpers, AO/MD5 key helpers, counter structures, repair helpers, and ftrace expectation APIs.

Important APIs and types: `union tcp_addr`, `enum test_fault`, `enum test_needs_kconfig`, `struct tcp_ao_counters`, `struct tcp_counters`, `struct tcp_sock_state`, and `enum trace_events` are key types. Important inline helpers include `test_init2`, `gen_tcp_addr`, `tcp_addr_to_sockaddr_in`, `test_listen_socket`, `test_connect_socket`, `test_set_md5`, `test_prepare_key`, `test_prepare_def_key`, `test_add_key_vrf`, `test_add_key`, `test_set_ao_flags`, `test_assert_counters`, `test_sock_checkpoint`, `test_sock_restore`, and trace expectation wrappers.

Control flow: tests include this header, then `test_init` or `test_init2` selects IPv4/IPv6 addresses based on `IPV6_TEST`, starts peer threads through library code, and uses helpers to build topology and sockets. AO keys are prepared as `struct tcp_ao_add`, installed through `setsockopt`, and verified through getsockopt comparison wrappers. Counter helpers compare before/after snapshots and free allocated key counter arrays.

State and persistence: the header declares thread-local `this_ip_addr` and `this_ip_dest`, global `test_family`, namespace cookies, and external helper state owned by library `.c` files. It defines constants such as `DEFAULT_TEST_PASSWORD`, `DEFAULT_TEST_ALGO`, and default prefixes. No persistent state is written by the header itself.

Dependencies and integration points: bridges Linux UAPI headers (`linux/tcp.h`, SNMP, bits), selftest library implementations (`setup.c`, `sock.c`, `utils.c`, `netlink.c`, `proc.c`, `repair.c`, `ftrace.c`), and Makefile address-family variants. It also works around missing `SOL_TCP` from libc header conflicts.

Risks: many helpers exit via `test_error`, so callers usually cannot recover from setup failures. Prefix clamping differs by family and can hide caller mistakes. Some APIs depend on optional kernel support and should be guarded with `kernel_config_has` or `should_skip_test`.

Test signals: tests using this header emit kselftest-compatible ok/fail/skip/xfail messages, structured counter assertions, and optional ftrace diagnostics for expected or unexpected TCP-AO tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/aolib.h -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace-tcp.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace-tcp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace-tcp.c

Purpose: this file implements TCP-AO-specific ftrace event matching for the selftest library. It lets tests register expected TCP hash/AO tracepoints and reports unexpected or missing events at tracer destruction.

Important APIs and types: `trace_event_names` maps `enum trace_events` to tracepoint names. `struct expected_trace_point` stores required event type, family, source/destination addresses, optional ports, L3 index, TCP flags, key IDs, MAC length, SNE, and match count. Public entry points are `__trace_event_expect` and `setup_aolib_ftracer`.

Control flow: tests add expectations through wrappers in `aolib.h`, which call `__trace_event_expect`. The ftrace line processor identifies event type with `check_event_type`, parses fields in `tracer_scan_event`, validates namespace cookie filtering, and calls `lookup_expected_event`. Expected lines are discarded; unexpected or unparsable lines are preserved. On destruction, `check_free_events` prints match stats and xfails unexpected trace lines.

State and persistence: expected tracepoints are held in a reallocating global array protected by `exp_tps_mutex`. Match counts accumulate during the run. `free_expected_events` releases the array from the tracer destructor. No trace output is persisted beyond test logs.

Dependencies and integration points: depends on `ftrace.c` for tracefs mounting, instance management, and tracer threads. It also depends on namespace cookies from `test_init_ftrace`, TCP tracepoint text formats, and `kernel_config_has(KCONFIG_FTRACE)`.

Risks: parser formats are tightly coupled to kernel tracepoint string layouts. `free_expected_events` sets `exp_tps = NULL` before `free(exp_tps)`, effectively leaking the old allocation; as test process lifetime is short, impact is limited but visible in code review. Missing ftrace support turns expectations into skips/no-ops.

Test signals: successful tracing reports either matched expectation counts or no unexpected trace events. Unexpected trace lines produce `test_xfail`, while expected-but-unseen events produce `test_fail`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace-tcp.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace.c

Purpose: this file provides generic tracefs/ftrace lifecycle support for TCP-AO selftests. It mounts a private tracefs, creates per-test tracing instances, runs reader threads on `trace_pipe`, and cleans up through registered destructors.

Important APIs and types: `struct test_ftracer` owns the pthread, instance path, trace pipe, callbacks, saved lines, condition variable, mutex, and linked-list node. Public functions include `create_ftracer`, `setup_trace_event`, `destroy_ftracer`, `tracer_get_savedlines_nr`, `tracer_get_savedlines`, `test_setup_tracing`, and `test_init_ftrace`.

Control flow: `test_init_ftrace` reads namespace cookies and probes ftrace support. `test_setup_tracing` ensures cookies differ, registers cleanup, mounts tracefs under a `ksft-ftrace-XXXXXX` temp directory, and calls TCP-AO-specific setup. `create_ftracer` creates an instance, disables trace options, sets buffer size, allocates saved-line storage, starts a trace reader thread, and links it into the global tracer list. Destruction waits briefly for expected events, cancels and joins the thread, removes the instance, and calls the caller's destructor.

State and persistence: global state includes `ftrace_path`, `ftrace_mounted`, namespace cookies, and a locked linked list of active tracers. Tracefs mount and instances are temporary filesystem state removed by cleanup. Saved trace lines are in-memory diagnostics.

Dependencies and integration points: depends on tracefs mount permission, pthreads, namespace switching helpers, `SO_NETNS_COOKIE`, `test_echo`, and TCP-AO event setup from `ftrace-tcp.c`.

Risks: tracefs mounting and unmounting require privileges and can fail in constrained environments. The tracer thread intentionally cancels blocking `getline`; cleanup must run to avoid leaked mounts. Buffer overflow is handled by stopping when saved-line capacity is reached, which can hide later events while preserving a diagnostic.

Test signals: ftrace setup success enables tracepoint validation. Cleanup reports tracer errors, unexpected thread termination, unmount/remove failures, and missing expected events through test logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/ftrace.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/kconfig.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/kconfig.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/kconfig.c

Purpose: this file implements runtime feature detection for TCP-AO selftests. Instead of trusting build-time config alone, it probes network namespaces, veth, TCP-AO, TCP-MD5, VRF, and ftrace availability.

Important APIs and functions: `struct kconfig_t` pairs cached error state with a probe function. Probe functions are `has_net_ns`, `has_veth`, `has_tcp_ao`, `has_tcp_md5`, `has_vrfs`, and `has_ftrace`. The public API is `kernel_config_has`, with skip messages exported through `tests_skip_reason`.

Control flow: `kernel_config_has` locks `kconfig_lock`, lazily runs the relevant probe if the cached state is `KCONFIG_UNKNOWN`, converts zero error to true, and unlocks. Probes create sockets, namespaces, veth devices, VRFs, or TCP-AO/MD5 keys as needed, then clean up local descriptors and namespace context.

State and persistence: state is a process-local `kconfig` array caching positive or negative probe results. Some probes temporarily create namespaces or devices through netlink helpers. No durable files are modified, though `has_ftrace` may mount tracefs via `test_setup_tracing`.

Dependencies and integration points: depends on aolib namespace, netlink, AO key, MD5, VRF, and tracing helpers. It is called by tests directly and by `should_skip_test` wrappers in `aolib.h`.

Risks: `has_tcp_md5` has a suspicious condition `errno != ENOPROTOOPT && errno == ENOMEM`, which only logs ENOMEM and may ignore other unexpected errors. Some probes use `test_error` on initialization failures, making feature detection fatal rather than skippable for infrastructure errors. Ftrace probing has side effects because it initializes tracing.

Test signals: missing optional features produce skip messages such as unsupported TCP-MD5, VRF, or ftrace. Missing required features cause tests using `should_skip_test` or setup code to skip or fail early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/kconfig.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/netlink.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/netlink.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/netlink.c

Purpose: this file provides low-level rtnetlink helpers for TCP-AO selftests. It creates veth pairs, assigns addresses, adds routes, brings links up, and creates VRF devices without shelling out to `ip`.

Important APIs and functions: public functions are `add_veth`, `ip_addr_add`, `ip_route_add`, `ip_route_add_vrf`, `link_set_up`, and `add_vrf`. Internal helpers include `netlink_sock`, `netlink_check_answer`, `rtattr_pack`, `rtattr_begin`, `rtattr_end`, `veth_pack_peerb`, `__add_veth`, `__ip_addr_add`, `__ip_route_add`, `__link_set_up`, and `__add_vrf`.

Control flow: each public function opens a `NETLINK_ROUTE` socket, builds an RTM request with nested attributes, sends it, waits for an `NLMSG_ERROR` ACK, closes the socket, and returns the kernel error code. Veth creation nests `IFLA_LINKINFO`, `IFLA_INFO_DATA`, and `VETH_INFO_PEER` with peer namespace fd. VRF creation nests `IFLA_VRF_TABLE`.

State and persistence: the helpers change kernel network namespace state by creating links, routes, addresses, and VRF devices. Sequence numbers are randomized per socket. There is no userspace persistent state beyond the created kernel objects.

Dependencies and integration points: used by `setup.c`, `kconfig.c`, `bench-lookups.c`, and key-management VRF setup through declarations in `aolib.h`. It depends on Linux rtnetlink UAPI, `randomize_buffer`, and interface names being visible in the current namespace.

Risks: `netlink_sock` uses `seq_nr++` instead of `(*seq_nr)++` when reusing an existing socket, so intended sequence advancement would not occur on reuse; current public wrappers open fresh sockets, limiting impact. Route additions hard-code host prefix lengths and route table fields, so they are not generic route helpers. Some functions return negative kernel error codes and callers must handle `-EEXIST` explicitly.

Test signals: successful helpers return zero. Failures print netlink diagnostics and return negative errno, causing callers to skip, fail, or call `test_error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/netlink.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/proc.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/proc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/proc.c

Purpose: this file reads and compares network statistics from procfs for TCP-AO tests. It abstracts `/proc/thread-self/net/netstat`, `snmp`, and `snmp6` into searchable in-memory counter lists.

Important APIs and types: `struct netstat` represents a counter family/header and linked-list node. `struct netstat_counter` stores a name and value. Public functions are `netstat_read`, `netstat_free`, `netstat_print_diff`, and `netstat_get`. Internal parsing helpers include `lookup_type`, `lookup_get`, `lookup_get_column`, `netstat_read_type`, and `snmp6_read`.

Control flow: `netstat_read` opens thread-self procfs paths so each test thread reads its current network namespace, parses paired header/value lines for netstat and snmp, then parses one-counter-per-line snmp6. `netstat_print_diff` walks two snapshots and prints changed or newly appeared counters. `netstat_get` searches all families for a named counter.

State and persistence: snapshots are heap-allocated linked lists owned by callers and freed with `netstat_free`. The code only reads procfs; it writes no persistent state. It intentionally avoids `/proc/net` because thread-leader namespace semantics can be wrong for multithreaded namespace tests.

Dependencies and integration points: used by TCP-AO connect, connect-deny, ICMP, and counter helpers. Depends on procfs availability and stable netstat/snmp formatting.

Risks: `netstat_print_diff` assumes the linked-list order and header progression are compatible between snapshots; new or reordered families could trigger confusing output or `test_error`. `lookup_type` uses `max(len, strlen(header_name))` with `strncmp`, effectively requiring full equality but relying on header length behavior. Parser failures are fatal through `test_error`.

Test signals: tests use this file to assert named counter deltas such as `TCPAOGood`, `TCPAOBad`, `TCPAORequired`, and ICMP unreachable counters. `netstat_print_diff` gives diagnostic context for counter changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/proc.c -->

## sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/repair.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/repair.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/repair.c

Purpose: this file provides simplified TCP repair helpers for established TCP-AO sockets. It checkpoints TCP sequence queues, options, windows, timestamps, and AO repair state, then restores them into a new repaired socket.

Important APIs and functions: public helpers are `__test_sock_checkpoint`, `test_ao_checkpoint`, `__test_sock_restore`, `test_ao_restore`, `test_sock_state_free`, `test_enable_repair`, `test_disable_repair`, and `test_kill_sk`. Internal helpers include `test_sock_checkpoint_queue`, `test_sock_restore_seq`, and `test_sock_restore_queue`. It uses `TCP_REPAIR`, `TCP_REPAIR_QUEUE`, `TCP_QUEUE_SEQ`, `TCP_REPAIR_WINDOW`, `TCP_REPAIR_OPTIONS`, `TCP_TIMESTAMP`, `TCP_AO_REPAIR`, `SIOCOUTQ`, `SIOCOUTQNSD`, and `SIOCINQ`.

Control flow: checkpointing records `TCP_INFO`, local socket address, repair window, output and input queue lengths/data, MSS, and timestamp option state. AO checkpointing separately reads `TCP_AO_REPAIR`. Restore binds the socket, switches to nonblocking mode, restores queue sequence numbers, optionally binds to a device, connects in repair mode, reinstalls negotiated TCP options, restores queued data and repair window, and lets callers restore AO state.

State and persistence: `struct tcp_sock_state` owns heap buffers for saved send and receive queues; callers must release them with `test_sock_state_free`. Kernel socket state is temporarily put into repair mode. No files are written.

Dependencies and integration points: declared in `aolib.h` and used by TCP-AO restore-style tests outside this subset. It depends on Linux TCP repair UAPI and TCP-AO repair support.

Risks: this is intentionally simplified and only targets established sockets; it is not a general CRIU-quality repair implementation. Queue restore sends in chunks and backs off chunk size only after send failure, so unusual socket states can be fragile. A likely bug passes `opt_nr * sizeof(opts[0])` as the length when setting `TCP_TIMESTAMP` instead of `sizeof(state->timestamp)`.

Test signals: callers observe success by restored sockets continuing data transfer with AO state intact. Any failed getsockopt, setsockopt, ioctl, bind, connect, send, or recv path aborts through `test_error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/repair.c -->
