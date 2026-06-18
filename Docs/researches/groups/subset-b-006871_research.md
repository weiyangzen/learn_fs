# subset-b-006871 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink.sh

## Purpose

`rtnetlink.sh` is a broad kselftest shell harness for exercising rtnetlink-driven network configuration paths through iproute2. It creates a dummy base device and then runs many independent `kci_test_*` cases that cover routing rules, route lookup, address lifetime expiry, traffic control objects, tunnels, bridge/FDB/neighbour operations, VRF, XFRM/IPsec, MACsec, bonding, mngtmpaddr, address protocol fields, and operational state reporting.

## Important APIs, Types, and Functions

The script sources `lib.sh` for kselftest helpers such as `ksft_skip`, `setup_ns`, `cleanup_all_ns`, `require_command`, and `slowwait`. Its local helpers are `check_err`, `check_fail`, `run_cmd*`, `run_cmd_grep*`, and `end_test`, which maintain the per-test `ret` status while allowing the script to continue after failed commands. Test entry points are listed in `ALL_TESTS` and can be overridden with `-t`.

Important external APIs are `ip link`, `ip route`, `ip rule`, `ip addr`, `ip netconf`, `ip tunnel`, `ip xfrm`, `bridge fdb`, `ip neigh`, `tc`, `sysctl`, `ifconfig`, `jq`, `uuidgen`, `modprobe`, `udevadm`, `ping`, and debug/sysfs files for netdevsim. Several tests rely on rtnetlink extensibility exposed by iproute2: VXLAN/FOU/GRE/GRETAP/ERSPAN link kinds, `seg6` is not used here, but VRF, bridge, VLAN, MACsec, team, bond, and netdevsim all exercise netdevice and routing notifications.

## Control Flow

Startup requires `jq`, root privileges, and runnable `ip` and `tc`. `kci_test_rtnl` creates `test-dummy0`, iterates through `${TESTS:-$ALL_TESTS}`, invokes each named function, accumulates failures, and deletes the dummy device. Individual tests create and tear down local devices or temporary namespaces as needed.

The control flow is deliberately failure-tolerant. `run_cmd` records unexpected nonzero exit codes, `run_cmd_fail` records commands that unexpectedly succeed, and grep variants validate expected iproute2 output. Most tests use a local `ret=0` so failures are isolated to that test, then call `end_test` with a PASS/FAIL/SKIP line.

## State and Persistence Behavior

The script mutates kernel networking state: devices, routes, rules, XFRM states and policies, neighbours, FDB entries, sysctls, netdevsim instances, debugfs mounts, and temporary namespaces. Cleanup is mostly inline in each test, with a final dummy deletion. Some sysctls are saved/restored, such as `fib_multipath_hash_policy` and `promote_secondaries`; others are scoped to temporary namespaces.

Persistent risk is highest around tests that touch global state: XFRM flushes, debugfs/netdevsim device creation, module loading/unloading, and bridge/bond/team devices in the initial namespace. Most namespace-based tests reduce cross-test leakage.

## Dependencies and Integration Points

This is integrated into `tools/testing/selftests/net` and validates kernel rtnetlink handlers through user-facing iproute2 commands rather than direct netlink messages. It depends on optional kernel features and modules including dummy, bridge, VLAN, VRF, VXLAN, FOU, GRE/ERSPAN, MACsec, team, bonding, XFRM/IPsec offload, netdevsim, IPv6 temporary addresses, and neighbour/FDB protocol support.

## Risks and Edge Cases

The script is sensitive to iproute2 version, missing kernel modules, missing `ifconfig` or `jq`, root privileges, and system policy around debugfs/module loading. Tests that expect command failure can produce false results if iproute2 syntax changes. `run_cmd_common` executes commands from expanded strings, so unusual arguments with shell metacharacters would be unsafe, although inputs are hard-coded.

Concurrency-sensitive coverage includes IPv6 addrlabel add/delete races, interface alias sysfs writes, temporary IPv6 address regeneration, and netdev lock paths for MACsec/VLAN and team/bridge/macvlan. These are regression-oriented and may be timing-sensitive on slow machines.

## Test Signals

Success is a zero exit from `kci_test_rtnl` and per-case PASS lines. Meaningful signals include expected route/neighbour/FDB JSON or text output, cleaned-up address lifetimes, correct XFRM monitor line counts, successful IPsec offload accounting in netdevsim debugfs, expected failure of invalid VXLAN changes, correct address protocol filtering through `jq`, and tenant/device cleanup without residual links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink_notification.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink_notification.sh

## Purpose

`rtnetlink_notification.sh` verifies that rtnetlink multicast notifications are emitted for multicast and anycast address changes. It creates a dummy interface, watches iproute2 monitor streams, and checks that expected add/delete notifications appear.

## Important APIs, Types, and Functions

The script sources `lib.sh` for `defer`, `kill_process`, `check_err`, `log_test`, `tests_run`, `EXIT_STATUS`, and `require_command`. `kci_test_mcast_addr_notification` runs `ip monitor maddr`; `kci_test_anycast_addr_notification` runs `ip monitor acaddress`. Both use `mktemp`, background monitors, `grep -cE`, and a fixed dummy device name `test-dummy1`.

## Control Flow

Startup checks for root and the `ip` command. Each test starts an `ip monitor` process, defers removal of the temp file and monitor kill, waits briefly for subscription setup, creates/activates/deletes a dummy interface, then counts matching monitor lines. If the monitor process exits immediately, the test treats iproute2 support as missing and skips.

## State and Persistence Behavior

The only intended kernel state is transient: one dummy link and a sysctl write enabling IPv6 forwarding on that dummy for the anycast case. Temp files are removed through `defer`, and monitor processes are killed. No persistent report state is written by the source script.

## Dependencies and Integration Points

This integrates with rtnetlink notification paths and iproute2 monitor subcommands. It depends on dummy link support, IPv4 multicast default address notification, IPv6 all-nodes multicast notification, IPv6 anycast behavior for link-local routes under forwarding, and root privileges.

## Risks and Edge Cases

The test relies on sleeps rather than explicit synchronization with monitor readiness. It assumes exactly four multicast matches and two anycast matches; extra notifications or changed iproute2 formatting can produce false failures. If dummy creation fails, later cleanup relies on deletion commands not being needed.

## Test Signals

Expected success is a kselftest OK for both cases. Multicast notification should produce two add and two delete matches for `224.0.0.1` and `ff02::1`; anycast should produce add/delete matches for `fe80::` after enabling IPv6 forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink_notification.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/run_afpackettests -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/run_afpackettests

## Purpose

`run_afpackettests` is a small shell runner for AF_PACKET selftests. It gates on root privileges and executes `psock_fanout`, `psock_tpacket`, and `txring_overwrite` inside network namespaces.

## Important APIs, Types, and Functions

The file is a POSIX shell script using `id -u`, `echo`, and `./in_netns.sh`. It defines the kselftest skip exit code `ksft_skip=4` and accumulates failures in `ret`. `psock_tpacket` is additionally gated on `/proc/kallsyms`.

## Control Flow

After root validation, the script prints a banner for each AF_PACKET executable, runs it through `in_netns.sh`, and emits `[PASS]`, `[FAIL]`, or `[SKIP]`. It exits nonzero if any non-skipped test fails.

## State and Persistence Behavior

State is limited to namespaces created by `in_netns.sh` and any transient packet sockets or links created by the invoked binaries. This wrapper does not persist files or mutate global state except through its children.

## Dependencies and Integration Points

It integrates with compiled AF_PACKET test binaries and the shared namespace wrapper. `psock_tpacket` depends on kallsyms visibility because it inspects kernel symbol-related behavior.

## Risks and Edge Cases

The script assumes it is run from the directory containing `in_netns.sh` and the compiled test binaries. Missing root exits with skip, while missing executables would surface as command failures. The variable `msg` in the root error path is not initialized, so the diagnostic can be sparse.

## Test Signals

Useful signals are the printed per-test PASS/FAIL/SKIP lines and final exit status. A successful run exercises packet fanout, tpacket behavior when kallsyms is available, and TX ring overwrite coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/run_afpackettests -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/run_netsocktests -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/run_netsocktests

## Purpose

`run_netsocktests` is the minimal shell wrapper for the generic socket syscall selftest binary `socket`.

## Important APIs, Types, and Functions

It uses POSIX shell, prints a banner, executes `./socket`, and converts the child exit code into `[PASS]` or `[FAIL]` plus the wrapper exit status.

## Control Flow

There is a single command path: run the local `socket` binary, fail immediately on nonzero status, otherwise exit zero after printing `[PASS]`.

## State and Persistence Behavior

The wrapper itself maintains no persistent state. Any socket creation state is local to the child process and released when file descriptors close.

## Dependencies and Integration Points

It depends on the compiled `socket` test binary being present in the current working directory. It is part of the net selftest runners used by kselftest automation.

## Risks and Edge Cases

The wrapper does not check root because the child test does not require it. Missing or non-executable `./socket` is reported as a failure. It does not propagate kselftest skip semantics because the child does not expose a skip mode.

## Test Signals

The sole signal is `./socket` exit status, surfaced as `[PASS]` or `[FAIL]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/run_netsocktests -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.c

## Purpose

`rxtimestamp.c` validates receive timestamp socket options and control messages across raw IP, UDP, and TCP sockets over IPv4 and IPv6 loopback. It checks legacy `SO_TIMESTAMP`, `SO_TIMESTAMPNS`, and `SO_TIMESTAMPING` flag combinations.

## Important APIs, Types, and Functions

Core data structures are `struct options`, `struct tstamps`, `struct socket_type`, `struct test_case`, and `struct sof_flag`. Static arrays enumerate socket types and timestamping test cases. Important functions are `print_test_case`, `do_send`, `do_recv`, `config_so_flags`, `run_test_case`, and `main`.

The key kernel APIs are `socket`, `bind`, `listen`, `connect`, `accept`, `setsockopt(SO_TIMESTAMP/SO_TIMESTAMPNS/SO_TIMESTAMPING/SO_REUSEADDR)`, `recvmsg`, ancillary data parsing with `CMSG_FIRSTHDR`/`CMSG_NXTHDR`, and `struct scm_timestamping` from `linux/net_tstamp.h`.

## Control Flow

`main` parses long options to select protocols, address families, test number, payload size, strict mode, or list mode. It iterates selected socket types and test cases for IPv4 and/or IPv6. `run_test_case` creates source and destination sockets, binds destination loopback, listens and accepts for TCP, configures timestamp options on the receive socket, sends a payload, and validates the received control messages.

## State and Persistence Behavior

Global mutable state includes `next_port`, `op_size`, and enabled flags inside the static test and socket arrays. Runtime socket state is short-lived per case. Timestamp configuration is per-socket and released on close. The program does not persist files or kernel configuration.

## Dependencies and Integration Points

It uses kselftest helpers for `ARRAY_SIZE` and standard Linux timestamping ABI headers. `rxtimestamp.sh` runs it inside a fresh namespace. It depends on loopback networking, raw socket permissions for IP tests, and kernel support for the timestamp options being validated.

## Risks and Edge Cases

Raw IPv4 receives include the IPv4 header and therefore adjust expected payload size. `SO_TIMESTAMPING` setup is followed by a fixed sleep because option effects can be asynchronous. Hardware timestamp tests on loopback expect no hardware timestamp. `warn_on_fail` softens one software timestamping case unless strict mode is requested.

## Test Signals

Success prints `PASSED.` with zero failures. Failures identify missing or unexpected cmsgs, truncation, wrong payload size, or nonzero timestamp slots where none are expected. `--list_tests` is a useful inventory signal for the encoded test matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.sh

## Purpose

`rxtimestamp.sh` is the namespace wrapper for the `rxtimestamp` receive timestamp test binary.

## Important APIs, Types, and Functions

The script is four lines: bash shebang, SPDX tag, and `./in_netns.sh ./rxtimestamp $@`. It forwards all caller arguments to the compiled C test.

## Control Flow

Execution immediately enters `in_netns.sh`, which provides isolation, then runs `rxtimestamp` with unchanged options. The wrapper exit status is the child status.

## State and Persistence Behavior

No local state is persisted. Network namespace setup and teardown are delegated to `in_netns.sh`; timestamp sockets are owned by the child process.

## Dependencies and Integration Points

It depends on `in_netns.sh` and `rxtimestamp` being present in the current directory. It integrates the C test into the net selftest namespace convention.

## Risks and Edge Cases

Argument forwarding is unquoted as `$@`; in shell this still expands positional parameters as separate words only when quoted, so arguments with spaces would be split. Normal kselftest options are simple and unaffected.

## Test Signals

Signals are inherited from `rxtimestamp`: zero exit and `PASSED.` indicate success; any child error fails the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sample_map_ret0.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sample_map_ret0.bpf.c

## Purpose

`sample_map_ret0.bpf.c` is a tiny XDP eBPF program intended to always load successfully while exercising map-definition and map-lookup verifier/control paths.

## Important APIs, Types, and Functions

It uses libbpf-style `SEC` and BTF map declaration macros from `bpf_helpers.h`. The file declares a hash map `htab` keyed by `__u32` with `long` values and an array map `array` with two entries. The `SEC("xdp") int func()` program calls `bpf_map_lookup_elem` on both maps and returns 0 only if both lookups are non-null.

## Control Flow

The XDP entry initializes zero keys, looks up the hash map, returns 1 on miss, looks up the array map using a 64-bit zero variable passed to a `__u32` key map, returns 1 on miss, and otherwise returns 0. For control-path loading tests, the verifier and loader behavior matter more than packet semantics.

## State and Persistence Behavior

Persistent state is limited to BPF map definitions when the object is loaded. Runtime map contents determine whether the program returns 0 or 1, but the source itself does not populate maps.

## Dependencies and Integration Points

It depends on kernel BPF/XDP support, libbpf helper macros, and build rules that compile `.bpf.c` objects. It is likely used by loader selftests that need a simple program with maps.

## Risks and Edge Cases

The array lookup uses `key64` even though the declared key type is `__u32`; verifier acceptance of the pointer size and BTF metadata is part of the intended coverage. If maps are empty, the hash lookup returns null and the program returns 1, which is acceptable for load-path tests but not a packet-pass program.

## Test Signals

Useful signals are successful BPF object compilation, verifier load success, map creation, and no unexpected verifier rejection around map lookups or section metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sample_map_ret0.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sample_ret0.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sample_ret0.bpf.c

## Purpose

`sample_ret0.bpf.c` is the simplest possible sample XDP eBPF program: it returns 0 unconditionally and is meant to exercise loader control paths.

## Important APIs, Types, and Functions

The file defines its own `SEC(name)` macro using GCC section attributes and marks `func` in the `xdp` section. There are no helpers, maps, or packet arguments.

## Control Flow

The only control flow is `func()` returning 0.

## State and Persistence Behavior

It has no maps, mutable globals, or persisted state. Loading the object creates only the program object expected by the test harness.

## Dependencies and Integration Points

It depends on the BPF compiler and kernel loader accepting a minimal XDP section. It integrates with network/BPF selftests that need a guaranteed-load sample.

## Risks and Edge Cases

Because it omits a context argument and helper includes, it is useful for loader permissiveness checks but not for realistic XDP packet processing. Any build rule expecting libbpf metadata may need to handle this minimal style.

## Test Signals

The expected signal is successful compilation and BPF load, with no verifier complexity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sample_ret0.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_hello.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_hello.c

## Purpose

`sctp_hello.c` is a small SCTP client/server helper used by `sctp_vrf.sh` to test SCTP listener lookup, VRF binding, and `l3mdev_accept` behavior.

## Important APIs, Types, and Functions

`set_addr` fills `sockaddr_in` or `sockaddr_in6` based on the selected family. `do_client` creates an `SOCK_STREAM` SCTP socket, optionally binds a local source address and port, connects to the server, performs a zero-length receive, and closes. `main` dispatches between server and client modes; server mode optionally sets `SO_BINDTODEVICE`, binds, listens, accepts one client, and exits.

## Control Flow

CLI mode determines execution: `client -4|-6 IP PORT [IP PORT]` or `server -4|-6 IP PORT [IFACE]`. Server setup is blocking at `accept`; client returns success only when `connect` succeeds. The helper is intentionally single-connection and short-lived.

## State and Persistence Behavior

All state is per-process socket state. Optional `SO_BINDTODEVICE` pins the listening SCTP socket to a device or VRF name. No files or kernel configuration are persisted.

## Dependencies and Integration Points

It depends on SCTP kernel support, `IPPROTO_SCTP`, and the `sctp_vrf.sh` topology. It integrates with `ss` polling in the shell script, which waits for the listening socket bound to the expected interface.

## Risks and Edge Cases

Error handling prints simple messages and often returns `-1` without closing already-open sockets on early failures. The zero-length `recv` is a synchronization placeholder rather than data validation. Invalid IPv6 text is not deeply diagnosed.

## Test Signals

The main signal is process exit status under `timeout` in `sctp_vrf.sh`: successful connect/accept is pass for allowed cases, and timeout or connect failure is pass for denied cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_hello.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_vrf.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_vrf.sh

## Purpose

`sctp_vrf.sh` validates SCTP behavior with VRFs and `net.sctp.l3mdev_accept`. It builds two client namespaces that use identical addresses and one server namespace with two VRFs, then checks which clients can connect to SCTP listeners under different bind and sysctl settings.

## Important APIs, Types, and Functions

The script sources `lib.sh`, loads `sctp` and `sctp_diag`, and uses `setup_ns`/`cleanup_ns`. Functions include `setup`, `cleanup`, `start_server`, `stop_server`, `wait_client`, `do_test`, `do_testx`, and `testup`. It uses `ip netns exec`, `ip link`, `ip route`, `ss -S`, `sysctl net.sctp.l3mdev_accept`, and the `sctp_hello` helper.

## Control Flow

`setup` creates `CLIENT_NS1`, `CLIENT_NS2`, and `SERVER_NS`, adds two veth pairs, configures duplicate client IPv4/IPv6 addresses, creates `vrf-1` and `vrf-2` in the server namespace, and installs per-VRF routes. `testup` runs 12 expectations for one address family, toggling `l3mdev_accept` and binding the server to no device, physical veth, or VRF. The main path runs `testup` once for IPv4 and once for IPv6.

## State and Persistence Behavior

State is scoped to temporary namespaces, veth devices, VRFs, routes, and SCTP sockets. Cleanup waits for clients, kills `sctp_hello`, and deletes namespaces. The SCTP sysctl changes are inside the server namespace.

## Dependencies and Integration Points

The test depends on SCTP, SCTP diagnostic support, VRF/l3mdev behavior, `ss`, `timeout`, and the compiled `sctp_hello` helper. It integrates with kernel socket lookup paths that decide whether unbound or bound SCTP listeners can accept packets arriving through VRF devices.

## Risks and Edge Cases

The client namespaces intentionally share the same addresses, so routing and VRF isolation must be correct for the test to mean anything. Poll loops time out after about three seconds, which can be sensitive on slow systems. Missing SCTP modules or helper binaries cause setup failure.

## Test Signals

Success is all 12 IPv4 and all 12 IPv6 cases printing `[PASS]`. Expected denies are as important as expected allows, especially no-bind behavior when `l3mdev_accept=0` and device/VRF-specific listener matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_vrf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_bind_sendto_listen.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_bind_sendto_listen.c

## Purpose

`sk_bind_sendto_listen.c` is a regression test for IPv6 TCP sockets bound to the wildcard address when `MSG_FASTOPEN` send attempts happen before a later `listen`.

## Important APIs, Types, and Functions

The program uses `socket(AF_INET6, SOCK_STREAM, IPPROTO_IP)`, `setsockopt(SO_REUSEADDR)`, `bind` to `[::]:20000`, `sendto(..., MSG_FASTOPEN, ...)`, `listen`, and `close`. It uses `error(3)` for diagnostics.

## Control Flow

It creates `fd1`, enables reuse, binds, and performs a zero-length fast-open `sendto` to the same wildcard address. Then it creates `fd2`, enables reuse, binds to the same address, expects a second `MSG_FASTOPEN` `sendto` to fail, and finally verifies that `listen(fd2, 0)` succeeds. Cleanup closes both descriptors.

## State and Persistence Behavior

Only local socket binding state exists. `SO_REUSEADDR` permits the second bind in the tested state. No persistent network configuration is changed.

## Dependencies and Integration Points

It depends on IPv6 TCP support and the kernel TCP Fast Open send path accepting `MSG_FASTOPEN` semantics. It integrates with socket bind/listen state transition regression coverage.

## Risks and Edge Cases

The test intentionally uses wildcard `::` as a destination, which is unusual but targets a specific kernel corner case. It expects the second fast-open send to fail; if it succeeds, that is a failure even though success would look superficially harmless. Port 20000 conflicts could make the first bind fail.

## Test Signals

Zero exit means first bind/send path and second bind/listen path behaved as expected. Nonzero exit pinpoints which socket operation violated the expected state transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_bind_sendto_listen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_connect_zero_addr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_connect_zero_addr.c

## Purpose

`sk_connect_zero_addr.c` tests that an IPv6 TCP client can connect to a listener bound to the wildcard zero address on the same port.

## Important APIs, Types, and Functions

It uses `socket`, `setsockopt(SO_REUSEADDR)`, `bind([::]:20000)`, `listen`, `connect` to the same zero sockaddr, and `close`.

## Control Flow

The program creates a listening socket on `[::]:20000`, then creates a second socket and calls `connect` using the same zero-address sockaddr. Success requires the kernel to resolve that corner case consistently enough for loopback-style connection establishment.

## State and Persistence Behavior

State is per-process socket state and local TCP listen/connect state. It does not alter sysctls, devices, or files.

## Dependencies and Integration Points

It depends on IPv6 TCP and local socket routing behavior. It is a narrow socket API regression test in the net selftest suite.

## Risks and Edge Cases

Port collisions can cause false failure. The error label says `bind fd2` for a connect failure, so diagnostics are slightly misleading. The test does not accept a connection; it only verifies `connect` return behavior.

## Test Signals

Zero exit indicates connect-to-zero-address behavior remains accepted for the tested listener setup. Any syscall failure returns nonzero with `error(3)` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_connect_zero_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_so_peek_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_so_peek_off.c

## Purpose

`sk_so_peek_off.c` validates `SO_PEEK_OFF` receive peek offset behavior for TCP and UDP over IPv4 and IPv6.

## Important APIs, Types, and Functions

Functions include `afstr`, `sk_peek_offset_probe`, `sk_peek_offset_set`, `sk_peek_offset_get`, `sk_peek_offset_test`, `do_test`, and `main`. It uses `setsockopt/getsockopt(SO_PEEK_OFF)`, `socket`, `bind`, `getsockname`, `listen`, `connect`, `accept`, `send`, and `recv` with `MSG_PEEK` and `MSG_TRUNC`.

## Control Flow

For each protocol, `do_test` probes IPv4 and IPv6 support. If neither family supports the option, the protocol is skipped. Supported families run a socket-pair style test: set initial peek offset to 0, send `ab`, peek one byte and expect offset 1, peek beyond the last byte and expect only `b` plus offset 2, then consume/truncate the message and expect offset reset to 0.

## State and Persistence Behavior

All state is per-socket. The key persistent-in-kernel state under test is the receive socket's peek offset, which advances on peek and rewinds after consuming data. It is destroyed when the socket closes.

## Dependencies and Integration Points

The program depends on Linux `SO_PEEK_OFF` support for stream/datagram sockets and kselftest exit codes. It integrates with protocol receive queue behavior and socket option plumbing.

## Risks and Edge Cases

`SO_PEEK_OFF` may be unsupported for a family/protocol combination, so the test distinguishes skip from failure. TCP uses `accept` and a separate receive socket, while UDP receives on the bound socket; cleanup must handle both. The test sends only a two-byte message, so it covers basic offset mechanics rather than large queue behavior.

## Test Signals

Expected output reports that TCP/UDP with MSG_PEEK_OFF works correctly for supported families. Exit is `KSFT_PASS`, `KSFT_FAIL`, or `KSFT_SKIP` depending on support and validation results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_so_peek_off.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.c

## Purpose

`skf_net_off.c` tests classic socket BPF access through `SKF_NET_OFF` when packets arrive from a TAP device, including fragmented/NAPI-frags skb layout. It verifies that a raw IPv6 UDP socket can receive a packet and that an attached filter can inspect network-header-relative fields.

## Important APIs, Types, and Functions

Key functions are `tun_open`, `sk_set_filter`, `raw_open`, `tun_write`, `raw_read`, `parse_opts`, and `main`. The test uses `/dev/net/tun`, `ioctl(TUNSETIFF)`, `IFF_TAP`, optional `IFF_NAPI | IFF_NAPI_FRAGS`, `socket(PF_INET6, SOCK_RAW, IPPROTO_UDP)`, `SO_ATTACH_FILTER`, classic BPF instructions, `writev`, `recvmsg`, and `SO_RCVTIMEO`.

## Control Flow

Options select a TAP interface (`-i`), attach the BPF filter (`-f`), and request NAPI frags mode (`-F`). `main` opens the raw socket, opens the TAP, writes an Ethernet + IPv6 + UDP + payload frame to the TAP fd, then reads the UDP header and payload from the raw socket. The filter accepts only host packets with IPv6 next-header UDP and destination port `cfg_dst_port`.

## State and Persistence Behavior

The program attaches per-socket classic BPF state and opens a TAP file descriptor for an already configured interface. It does not create the interface itself. Packet data is transient; all descriptors close before exit.

## Dependencies and Integration Points

It depends on a prepared TAP interface with IPv6 peer addressing, disabled GRO, and early-demux configuration supplied by `skf_net_off.sh`. It integrates with kernel skb header offset handling, raw IPv6 sockets, TUN/TAP, and classic BPF ancillary offsets `SKF_AD_OFF` and `SKF_NET_OFF`.

## Risks and Edge Cases

The IPv6 UDP checksum is set to zero, which is normally invalid for IPv6 UDP but accepted in this controlled raw-path scenario only if the stack path permits it. Filter offsets assume no IPv6 extension headers. The test is sensitive to GRO/early-demux because those can linearize or pull headers before the targeted code path.

## Test Signals

Success prints the received payload and `OK`. Failures appear as `error(3)` exits for TUN open/configuration, filter attach, frame write, raw receive timeout, or unexpected received length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.sh

## Purpose

`skf_net_off.sh` creates the isolated TAP environment for `skf_net_off` and runs the executable in three modes: no filter, filtered linear skb, and filtered NAPI-frags skb.

## Important APIs, Types, and Functions

It uses `mktemp -u` to name a namespace, `ip netns`, `ip tuntap`, `ip link`, IPv6 address assignment, `ethtool -K gro off`, `sysctl net.ipv4.ip_early_demux=0`, and `ip netns exec`.

## Control Flow

The script creates a namespace, registers cleanup on exit, brings loopback and `tap1` up, sets a fixed MAC address and IPv6 peer address, disables GRO and early demux, then runs `./skf_net_off -i tap1`, `./skf_net_off -i tap1 -f`, and `./skf_net_off -i tap1 -f -F`.

## State and Persistence Behavior

All devices and sysctl mutations are namespace-scoped. `cleanup` deletes the namespace at exit. No output artifacts are persisted.

## Dependencies and Integration Points

It depends on TUN/TAP, ethtool, IPv6, raw socket permissions, and the compiled `skf_net_off` binary. It integrates the C test with kselftest's isolated namespace pattern.

## Risks and Edge Cases

There is no explicit root check; failures surface from `ip`/`tuntap` commands. Cleanup assumes namespace creation succeeded. If `ethtool` is missing or the kernel lacks NAPI frags support, later program modes fail.

## Test Signals

Each mode should reach `OK` from the C helper. The most important signal is that the filtered fragmented mode succeeds, proving `SKF_NET_OFF` remains correct with non-linear skb layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_incoming_cpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_incoming_cpu.c

## Purpose

`so_incoming_cpu.c` verifies that `SO_INCOMING_CPU` can steer `SO_REUSEPORT` TCP listeners according to the CPU that processes incoming SYN packets.

## Important APIs, Types, and Functions

The file uses `kselftest_harness.h` fixtures and variants. Key helpers are `write_sysctl`, `setup_netns`, `set_so_incoming_cpu`, `create_server`, `create_servers`, `create_clients`, and `verify_incoming_cpu`. It uses `unshare(CLONE_NEWNET)`, `sched_setaffinity`, `get_nprocs`, `setsockopt(SO_REUSEPORT/SO_INCOMING_CPU)`, `getsockopt(SO_INCOMING_CPU)`, `bind`, `listen`, `connect`, and `accept`.

## Control Flow

Fixture setup creates a new net namespace, brings loopback up, narrows local port range, disables `tcp_tw_reuse`, determines CPU/server counts, and initializes a loopback sockaddr. Four variants set `SO_INCOMING_CPU` before reuseport, before listen, after listen, or after all listeners are listening. Tests create one listener per CPU, pin the client process to each CPU in turn, open many connections, and verify each listener accepts only connections with matching incoming CPU.

## State and Persistence Behavior

State is mostly namespace-local sockets and sysctls. Global process CPU affinity is changed during client creation and not explicitly restored, but the test process exits afterward. Server fds are closed in teardown.

## Dependencies and Integration Points

It depends on at least two CPUs, loopback TCP, `ip` command availability for namespace setup, and kernel support for `SO_INCOMING_CPU` with reuseport selection. It integrates with the kernel's TCP accept queue, incoming CPU tagging, and reuseport listener selection.

## Risks and Edge Cases

CPU affinity calls can fail under restricted cpusets. The test scales listener count to online processors and client count to available ephemeral ports, so very large systems can be heavy. The extra no-CPU listener cases ensure unspecified CPU sockets do not steal traffic, but they also rely on nonblocking accept returning `-1`.

## Test Signals

Harness success across all variants and three tests indicates CPU-based listener selection works before and after listen setup. Failures usually show as failed accepts, wrong `SO_INCOMING_CPU` values, or client connection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_incoming_cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_netns_cookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_netns_cookie.c

## Purpose

`so_netns_cookie.c` tests `SO_NETNS_COOKIE`, ensuring sockets report nonzero cookies and distinct network namespaces have distinct cookie values.

## Important APIs, Types, and Functions

It uses `socket(AF_INET, SOCK_STREAM)`, `getsockopt(SOL_SOCKET, SO_NETNS_COOKIE)`, `unshare(CLONE_NEWNET)`, and 64-bit cookie storage. A fallback `#define SO_NETNS_COOKIE 71` supports older headers.

## Control Flow

The program creates a TCP socket in the initial namespace, reads and validates its cookie, unshares into a new network namespace, creates another TCP socket, reads and validates its cookie, then verifies the two cookies differ.

## State and Persistence Behavior

The only kernel state is a new network namespace and two sockets. Cookies are kernel-assigned namespace identifiers and persist for namespace lifetime, not beyond this process after exit.

## Dependencies and Integration Points

It depends on permission to `unshare(CLONE_NEWNET)` and kernel support for `SO_NETNS_COOKIE`. It integrates with socket namespace metadata and getsockopt ABI compatibility.

## Risks and Edge Cases

Unprivileged namespace restrictions can cause skip-like environmental failure, but the program returns a normal error. Header fallback can compile even when the running kernel lacks support, in which case getsockopt fails.

## Test Signals

Zero exit means both cookies are nonzero and distinct. Error output includes function/line and `errno` text through `pr_err`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_netns_cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_rcv_listener.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_rcv_listener.c

## Purpose

`so_rcv_listener.c` validates receive-side ancillary reporting for socket metadata set on sent packets: `SO_RCVMARK` receives `SO_MARK`, and `SO_RCVPRIORITY` receives `SO_PRIORITY`.

## Important APIs, Types, and Functions

`struct options` stores the selected value, sender option name, receiver cmsg type, host, and service. `parse_args` selects `-M` for mark or `-P` for priority. `main` creates an IPv4 or IPv6 UDP socket, enables the receive option, binds, receives one datagram with `recvmsg`, and scans control messages.

## Control Flow

The program is a listener. It chooses AF_INET6 when the host string contains `:`, otherwise AF_INET. After binding, it blocks in `recvmsg` and looks for a `SOL_SOCKET` cmsg whose type is the corresponding sender option (`SO_MARK` or `SO_PRIORITY`) and whose payload equals the requested value.

## State and Persistence Behavior

State is per-socket. The receive option configures ancillary delivery for one socket and disappears on close. No sender is created by this program; it must be paired with an external transmitter.

## Dependencies and Integration Points

It depends on kernel support for `SO_RCVMARK` and `SO_RCVPRIORITY` and on a test harness that sends UDP packets with `SO_MARK` or `SO_PRIORITY` set. It integrates with cmsg delivery in UDP receive paths for IPv4 and IPv6.

## Risks and Edge Cases

The option names are easy to confuse: the received cmsg type is checked against the sender-side option identifier stored in `opt.name`, while the receiver is configured with `opt.rcvname`. The program blocks until a packet arrives and has no timeout. It accepts numeric services only despite usage mentioning service names.

## Test Signals

Success prints `Received value: N` and exits zero. Failures include bind/setsockopt/recv errors, missing cmsg, or mismatched received value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_rcv_listener.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.c

## Purpose

`so_txtime.c` is the command-line exerciser for the `SO_TXTIME` API. It sends or receives timestamp-scheduled one-byte UDP packets and validates delivery timing, packet order, and transmit error-queue behavior.

## Important APIs, Types, and Functions

Important globals configure clock, port, variance, start time, socket mark, rx/tx mode, packet list, expected error-queue cmsg level/type, and source/destination sockaddrs. Core functions are `gettime_ns`, `do_send_one`, `do_recv_one`, `do_recv_verify_empty`, `do_recv_errqueue_timeout`, `recv_errqueue_msgs`, `start_time_wait`, `setsockopt_txtime`, `setup_tx`, `setup_rx`, `do_test_tx`, `do_test_rx`, `setup_sockaddr`, `parse_io`, `parse_opts`, and `main`.

Kernel APIs include `setsockopt(SO_TXTIME)` with `SOF_TXTIME_REPORT_ERRORS`, `getsockopt(SO_TXTIME)`, `SCM_TXTIME` cmsgs, `sendmsg`, `recv`, `recvmsg(MSG_ERRQUEUE)`, `poll(POLLERR)`, `SO_EE_ORIGIN_TXTIME`, and optional `SO_MARK`.

## Control Flow

`parse_opts` selects IPv4 or IPv6, `CLOCK_TAI` or monotonic, source/destination addresses, rx mode, start time, mark, and a comma-separated payload/delay stream. TX mode connects a UDP socket, enables `SO_TXTIME`, waits for the synchronized start, sends each packet with optional `SCM_TXTIME`, and drains error-queue messages until all expected reports or max delivery time. RX mode binds, waits for the same start, receives packets in expected order, checks arrival time against configured variance, then verifies the queue is empty.

## State and Persistence Behavior

State is per-process globals and per-socket txtime configuration. `glob_tstart` is the local reference time for converting relative delays to absolute delivery times. No files or sysctls are changed by this program; qdisc state is configured by `so_txtime.sh`.

## Dependencies and Integration Points

It depends on UDP, socket timestamping ABI headers, `SO_TXTIME`, error queues, and a qdisc that honors txtime for strict scheduling tests, typically `fq` or `etf`. It integrates with the shell wrapper that runs TX and RX instances in separate namespaces with synchronized start times.

## Risks and Edge Cases

Timing assertions are sensitive to scheduler latency; `KSFT_MACHINE_SLOW` downgrades excessive variance. Negative delays omit `SCM_TXTIME` and mean immediate send. Error queue parsing must match IPv4 `IP_RECVERR` or IPv6 `IPV6_RECVERR` cmsg types. The max packet count is eight, and malformed payload streams are not deeply validated.

## Test Signals

TX logs dropped packets with `missed txtime` or `invalid txtime` reasons from the error queue. RX logs payload delay and expected delay. Success is zero exit; failures indicate timing variance, payload mismatch, unexpected delivery, missing error-queue semantics, or `SO_TXTIME` getsockopt mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.sh

## Purpose

`so_txtime.sh` is the regression wrapper for `SO_TXTIME`. It creates two network namespaces connected by veth, configures addresses and qdiscs, and runs paired TX/RX instances of `so_txtime`.

## Important APIs, Types, and Functions

Functions are `cleanup`, `run_test`, `do_test`, and `do_fail_test`. The script uses `ip netns`, `ip link`, IPv4/IPv6 address assignment, `tc qdisc`, `date +%s%N --date`, and `ip netns exec`.

## Control Flow

After namespace/veth setup, it installs `fq` on the TX veth and runs several expected-success monotonic-clock tests. Then it attempts to replace the qdisc with `etf clockid CLOCK_TAI delta 400000`; if supported, it runs expected-failure and expected-success TAI tests. TX and RX are synchronized with a start time 0.1 seconds in the future.

## State and Persistence Behavior

All network devices, addresses, and qdiscs are namespace-scoped. Cleanup deletes both namespaces. The script accumulates `ret` and may convert failures to success under `KSFT_MACHINE_SLOW` when not a skip.

## Dependencies and Integration Points

It depends on root privileges, veth, IPv4/IPv6, `tc` support for `fq` and optionally `etf`, GNU `date --date`, and the `so_txtime` binary. It integrates `SO_TXTIME` with qdisc scheduling behavior.

## Risks and Edge Cases

`set -e` is disabled during test execution so individual failures accumulate. Timing is tight and can be noisy on slow or virtualized machines. If `etf` is unavailable, the script returns skip only if no earlier failure occurred.

## Test Signals

Success prints `OK. All tests passed`. Important signals include expected immediate-send behavior, delayed delivery order, reordered txtime delivery, ETF rejecting invalid or missed txtime cases, and proper skip when ETF is not supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/so_txtime.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/socket.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/socket.c

## Purpose

`socket.c` is a compact syscall validation test for expected success and failure combinations of socket domain/type/protocol arguments.

## Important APIs, Types, and Functions

`struct socket_testcase` records `domain`, `type`, `protocol`, expected result, and whether `EAFNOSUPPORT` is acceptable. `tests[]` covers invalid `AF_MAX`, TCP stream, TCP datagram mismatch, UDP datagram, and UDP stream mismatch. `run_tests` calls `socket`, compares `errno`, and closes successful fds.

## Control Flow

`main` calls `run_tests` and returns its result. The loop continues until a mismatch, then prints the expected and actual error strings and exits nonzero.

## State and Persistence Behavior

Only transient file descriptors are created. There is no persistent state or network configuration mutation.

## Dependencies and Integration Points

It depends on standard socket syscall behavior and kselftest's `ARRAY_SIZE`. It allows `EAFNOSUPPORT` for configured protocol families so kernels without IPv4 support can skip those cases implicitly.

## Risks and Edge Cases

The error message for unexpected success uses `strerror_r(errno)` after a successful socket call, where `errno` may be stale. The expected matrix is intentionally small and does not cover IPv6 or raw sockets.

## Test Signals

Zero exit means all socket argument combinations matched expectations. Nonzero output identifies the first mismatch with domain, type, protocol, expected error, and actual error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt46_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt46_l3vpn_test.sh

## Purpose

`srv6_end_dt46_l3vpn_test.sh` validates SRv6 `End.DT46` behavior for dual-stack IPv4/IPv6 L3VPNs. It builds two tenant VPNs across two SRv6 routers and verifies same-tenant connectivity and cross-tenant isolation for both IP families.

## Important APIs, Types, and Functions

The script sources `lib.sh` and uses `setup_ns`/`cleanup_all_ns`. Major functions are `log_test`, `cleanup`, `setup_rt_networking`, `setup_hs`, `setup_vpn_config`, `setup`, connectivity check helpers, `router_tests`, `host2gateway_tests`, `host_vpn_tests`, and `host_vpn_isolation_tests`. It uses `ip -6 route ... encap seg6 mode encap`, `encap seg6local action End.DT46 vrftable`, VRF devices, IPv6 rules to a localsid table, proxy ARP/NDP, and unreachable defaults.

## Control Flow

Startup requires root, `ip`, and VRF strict-mode support. `setup` creates a veth underlay between `rt_1` and `rt_2`, creates four host namespaces for tenants 100 and 200, attaches hosts to router VRFs, and installs bidirectional SRv6 encapsulation and decapsulation routes. It then pings router underlay, host-to-gateway paths, same-tenant VPN paths, and all cross-tenant combinations expecting failure.

## State and Persistence Behavior

All route, VRF, veth, sysctl, and namespace state is temporary. Cleanup deletes underlay links and all namespaces. Per-tenant VRF tables 100 and 200 and localsid table 90 exist only inside router namespaces.

## Dependencies and Integration Points

It depends on SRv6, seg6local `End.DT46`, VRF strict mode, IPv4/IPv6 forwarding, proxy ARP/NDP, and iproute2 SRv6 syntax. It integrates with kernel SRv6 decapsulation into VRF table lookup for both IPv4 and IPv6 inner packets.

## Risks and Edge Cases

The script assumes fixed tenant IDs and overlapping host prefixes across tenants, so VRF isolation is central. If proxy ARP/NDP or unreachable default routes are misconfigured, failures can look like SRv6 bugs. It checks feature presence only for VRF, not specifically `End.DT46` before setup.

## Test Signals

Success is zero failures in the printed summary. Critical signals are IPv4 and IPv6 host connectivity within tenant 100 and 200, host-to-gateway reachability, router underlay reachability, and expected ping failures between tenants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt46_l3vpn_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt4_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt4_l3vpn_test.sh

## Purpose

`srv6_end_dt4_l3vpn_test.sh` validates SRv6 `End.DT4` for IPv4 L3VPN service over an IPv6 underlay with two tenants.

## Important APIs, Types, and Functions

It has the same structural helpers as the DT46 script but configures only IPv4 host addressing and `encap seg6local action End.DT4 vrftable`. It uses VRFs, localsid table 90, IPv6 underlay routes, IPv4 proxy ARP, and `ip route ... encap seg6 mode encap` for IPv4 host routes.

## Control Flow

The script creates two router namespaces connected by veth, four host namespaces in tenants 100 and 200, per-tenant VRFs on each router, bidirectional SRv6 policies for same-tenant host pairs, and then runs router, host-gateway, same-tenant, and cross-tenant ping checks.

## State and Persistence Behavior

State is limited to temporary namespaces and devices. VRF tables 100/200 and localsid table 90 are namespace-local. Cleanup deletes links and namespaces after summary.

## Dependencies and Integration Points

Dependencies include root, `ip`, VRF strict mode, SRv6 End.DT4 support, IPv6 forwarding underlay, IPv4 forwarding in routers, and proxy ARP. It integrates IPv4 inner packet decapsulation with VRF route lookup.

## Risks and Edge Cases

The test does not run IPv6 host payloads; it uses IPv6 only for the SRv6 transport. The repeated `veth-t100`/`veth-t200` names in different namespaces are intentional. Feature detection may skip only VRF absence, so missing End.DT4 appears as setup/test failure.

## Test Signals

Success means same-tenant IPv4 pings pass in both directions, gateway pings pass, router underlay pings pass, and cross-tenant pings fail as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt4_l3vpn_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt6_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt6_l3vpn_test.sh

## Purpose

`srv6_end_dt6_l3vpn_test.sh` validates SRv6 `End.DT6` for IPv6 L3VPN service over an IPv6 underlay with two isolated tenants.

## Important APIs, Types, and Functions

It mirrors the DT4/DT46 topology helpers but uses IPv6 host addresses, proxy NDP, IPv6 forwarding, and `encap seg6local action End.DT6 vrftable`. Encapsulation routes target host `/128` routes in tenant VRFs.

## Control Flow

After root, `ip`, and VRF checks, setup creates router and host namespaces, connects hosts through per-tenant VRFs, installs bidirectional SRv6 policies and localsid rules, and runs router connectivity, host-to-gateway, same-tenant VPN, and cross-tenant isolation tests.

## State and Persistence Behavior

All namespace, veth, VRF, route, rule, and sysctl changes are temporary and cleaned at script end. IPv6 DAD is disabled in relevant namespaces to avoid timing delays.

## Dependencies and Integration Points

It depends on SRv6 End.DT6, VRF, IPv6 forwarding, proxy NDP, and iproute2 seg6 support. It integrates decapsulated IPv6 packet lookup into the specified VRF table.

## Risks and Edge Cases

Like the other DT tests, missing End.DT6 support is not preflighted separately. Proxy NDP is required for host L2 reachability. Overlapping tenant IPv6 prefixes make isolation tests meaningful but can complicate diagnosis.

## Test Signals

Expected success is all IPv6 same-tenant and host-gateway pings passing, all cross-tenant pings failing, and zero failed tests in the summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dt6_l3vpn_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx4_netfilter_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx4_netfilter_test.sh

## Purpose

`srv6_end_dx4_netfilter_test.sh` validates that SRv6 `End.DX4` decapsulation and forwarding work when lightweight-tunnel netfilter hooks are enabled and raw-table rpfilter rules are installed.

## Important APIs, Types, and Functions

The script is standalone and defines `ksft_skip`. Functions include `setup_rt_networking`, `setup_rt_netfilter`, `setup_hs`, `setup_vpn_config`, `host_tests`, and `router_netfilter_tests`. It uses IPv6 underlay routing, IPv4 host routes, `encap seg6local action End.DX4 nh4 ... dev ...`, `sysctl net.netfilter.nf_hooks_lwtunnel=1`, and `iptables -t raw -A PREROUTING -m rpfilter --invert -j DROP`.

## Control Flow

Setup creates two router namespaces and two host namespaces for one tenant, installs bidirectional SRv6 encapsulation and End.DX4 decapsulation routes, and first checks host connectivity without netfilter. Then it enables lwtunnel netfilter hooks and rpfilter in both routers and repeats the host connectivity tests.

## State and Persistence Behavior

All devices, namespaces, routes, sysctls, and iptables rules are temporary. Cleanup deletes veth links and any `rt-*` or `hs-*` namespaces. State is less isolated by name than some lib.sh-based scripts, so namespace name collisions are possible.

## Dependencies and Integration Points

It depends on SRv6 End.DX4, IPv4/IPv6 forwarding, iptables raw table, rpfilter match, lwtunnel netfilter hook support, and root privileges. It integrates SRv6 decapsulation with netfilter PREROUTING behavior.

## Risks and Edge Cases

The header comment has some copy/paste wording, but the route action is correctly `End.DX4`. Cleanup greps broad namespace patterns. Missing iptables or rpfilter support is not preflighted and will surface as failure.

## Test Signals

Both host pings should pass before and after netfilter hook/rpfilter setup. A failure after enabling hooks suggests lwtunnel/netfilter integration rejected decapsulated SRv6 traffic incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx4_netfilter_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx6_netfilter_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx6_netfilter_test.sh

## Purpose

`srv6_end_dx6_netfilter_test.sh` validates SRv6 `End.DX6` forwarding with lightweight-tunnel netfilter hooks and IPv6 raw-table rpfilter rules.

## Important APIs, Types, and Functions

It mirrors the DX4 netfilter test with IPv6 host addressing and `encap seg6local action End.DX6 nh6 ... dev ...`. `setup_rt_netfilter` enables `net.netfilter.nf_hooks_lwtunnel` and installs `ip6tables -t raw PREROUTING -m rpfilter --invert -j DROP`.

## Control Flow

The script builds two routers and two hosts, configures IPv6 SRv6 encapsulation and End.DX6 decapsulation routes, verifies host connectivity, enables netfilter hooks/rpfilter in both routers, and verifies host connectivity again.

## State and Persistence Behavior

State is temporary namespaces, veth links, IPv6 routes, sysctls, and ip6tables rules. Cleanup deletes broad `rt-*` and `hs-*` namespace names plus underlay links.

## Dependencies and Integration Points

It depends on SRv6 End.DX6, IPv6 forwarding/proxy NDP, ip6tables raw table, rpfilter match, lwtunnel netfilter support, and iproute2 seg6 support. It tests the integration between SRv6 decapsulation and IPv6 netfilter PREROUTING.

## Risks and Edge Cases

Some comments refer to End.DX4 or ARP due to copy/paste, but the implementation uses IPv6 and End.DX6. Missing ip6tables/rpfilter support is not checked early. Namespace cleanup patterns may remove unrelated similarly named test namespaces.

## Test Signals

The signal is successful bidirectional IPv6 pings both before and after netfilter is enabled. The printed summary should show zero failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_dx6_netfilter_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_flavors_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_flavors_test.sh

## Purpose

`srv6_end_flavors_test.sh` tests SRv6 End behavior with the PSP flavor. It builds a four-router IPv6 topology, installs inline SRv6 policies, and verifies that PSP behaves like normal End when not penultimate and pops the SRH when it is penultimate.

## Important APIs, Types, and Functions

The script defines namespace naming helpers using a random suffix, topology helpers (`create_router`, `create_host`, `add_link_rt_pairs`, `get_network_prefix`), SRv6 helpers (`setup_rt_local_sids`, `__setup_rt_policy`, `setup_rt_policy_ipv6`), host/router setup, connectivity checks, and feature probes (`test_iproute2_supp_or_ksft_skip`, `test_kernel_supp_or_ksft_skip`, `test_dummy_dev_or_ksft_skip`). It uses `encap seg6local action End`, `End flavors psp`, and `encap seg6 mode inline`.

## Control Flow

Preflight requires root and tools `ip`, `ping`, `sysctl`, `grep`, `cut`, `sed`, `sort`, and `xargs`, plus dummy and PSP support in iproute2/kernel. Setup creates routers 1-4, hosts 1-2, full inter-router veth links, host links, local SID tables, and two policies: host 1 to 2 traverses rt3, rt4 with PSP but not penultimate, and rt2 with PSP as penultimate; host 2 to 1 uses rt1 PSP as penultimate. It then runs all-pairs router connectivity, host-gateway checks, and host-to-host SRv6 checks.

## State and Persistence Behavior

All namespaces have a unique suffix and are removed in `cleanup`. `SETUP_ERR` controls whether cleanup exits skip when setup fails. Routes, dummy devices, proxy NDP, and sysctls are namespace-local.

## Dependencies and Integration Points

It depends on SRv6 End, PSP flavor support, inline SRH insertion, dummy devices, IPv6 forwarding, and iproute2 flavor syntax. It integrates with kernel SRH processing and PSP header-removal semantics.

## Risks and Edge Cases

Because the test checks reachability rather than packet capture, it infers PSP behavior from successful forwarding. It does not directly inspect whether the SRH was removed. Setup uses `set -e`, so unexpected command failure routes to cleanup as skip before tests run.

## Test Signals

Success includes all router pair pings, host-to-gateway pings, and bidirectional host pings over PSP policies. Preflight skip messages distinguish missing userspace or kernel PSP support from behavioral failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_flavors_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_next_csid_l3vpn_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_next_csid_l3vpn_test.sh

## Purpose

`srv6_end_next_csid_l3vpn_test.sh` validates the SRv6 End NEXT-C-SID flavor in an IPv4/IPv6 L3VPN topology. It covers compressed SID containers for reduced encapsulation, transition from a C-SID container to a regular SID, and validation of locator-block/node-function length parameters.

## Important APIs, Types, and Functions

The script sources `lib.sh` and defines helpers for router/host namespace creation, inter-router links, IPv6 address construction (`build_ipv6_addr`), C-SID construction (`build_csid`, `build_lcnode_func_prefix`), local SID setup, VPN policy setup (`__setup_l3vpn`, `setup_ipv4_vpn_2sids`, `setup_ipv6_vpn_1sid`), connectivity checks, C-SID config tests, and feature probes. It uses `encap seg6 mode encap.red`, `encap seg6local action End flavors next-csid lblen ... nflen ...`, and `End.DT46 vrftable`.

## Control Flow

Preflight checks root, `ip`, `ping`, `sysctl`, `grep`, `cut`, iproute2 NEXT-C-SID support, dummy device support, and VRF strict mode. Setup creates four routers and two hosts, a mesh of inter-router links, per-host VRFs, default unreachable routes, NEXT-C-SID local behaviors for each router, localsid rules for regular and compressed locator prefixes, IPv6 one-SID VPN policies, and IPv4 two-SID VPN policies. Runtime first tests valid/invalid C-SID container configurations, then router connectivity, host-gateway connectivity, and IPv4/IPv6 VPN connectivity.

## State and Persistence Behavior

State is namespace-scoped through `setup_ns`/`cleanup_all_ns`: veth links, dummy devices, VRFs, route tables 90 and 91, proxy ARP/NDP, forwarding sysctls, and local SID routes. `SETUP_ERR` causes cleanup to return kselftest skip if setup fails before the test phase.

## Dependencies and Integration Points

It depends on kernel and iproute2 support for SRv6 NEXT-C-SID flavor, `encap.red`, End.DT46, VRF strict mode, dummy devices, IPv4/IPv6 forwarding, and compressed SID locator layout. It integrates with SRv6 compressed SID processing and L3VPN decapsulation into a VRF.

## Risks and Edge Cases

The script constructs IPv6 addresses from hex strings manually, so formatting bugs would change the effective SID. The C-SID config matrix expects invalid route-add attempts to return status 2, which may vary with iproute2 error behavior. It validates reachability, not packet headers, so it infers reduced encapsulation and C-SID advancement from forwarding success.

## Test Signals

Important signals are acceptance/rejection of each C-SID container configuration, all-pairs router reachability, host-gateway IPv4/IPv6 reachability, and bidirectional host VPN reachability for IPv6 one-SID and IPv4 two-SID policies. The summary should report zero failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_next_csid_l3vpn_test.sh -->
