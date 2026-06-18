# subset-b-006866 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_inq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_inq.c

## Purpose
`mptcp_inq.c` is a focused kernel selftest helper for the `TCP_INQ` receive control-message and output-queue ioctl behavior when a TCP or MPTCP socket is used at either side of a loopback transfer. It creates a local client/server pair, enables `TCP_INQ` on the accepted socket, and verifies that `recvmsg()` returns `TCP_CM_INQ` ancillary data that matches bytes still queued for read, including EOF/FIN semantics.

## Important APIs, Types, And Functions
The helper uses `socket()`, `bind()`, `listen()`, `accept()`, `connect()`, `socketpair(AF_UNIX, SOCK_DGRAM)`, `recvmsg()`, `setsockopt(IPPROTO_TCP, TCP_INQ)`, `ioctl(TIOCOUTQ)`, `ioctl(SIOCOUTQNSD)`, and `ioctl(FIONREAD)`. It defines fallback constants for `IPPROTO_MPTCP` and `SOL_MPTCP`, and keeps global protocol selectors `pf`, `proto_tx`, and `proto_rx`. Key functions are `sock_listen_mptcp()`, `sock_connect_mptcp()`, `wait_for_ack()`, `connect_one_server()`, `get_tcp_inq()`, `process_one_client()`, `server()`, `client()`, and `main()`.

## Control Flow
`parse_opts()` accepts `-6`, `-t tcp|mptcp`, and `-r tcp|mptcp`. `main()` creates a Unix datagram socketpair, forks a server, waits for a `"conn"` readiness token, then forks a client. The server binds `127.0.0.1:15432` or `::1:15432`, accepts one connection, enables `TCP_INQ`, and runs `process_one_client()`. The client connects with the requested transmit protocol and runs `connect_one_server()`. The Unix socket coordinates phases: an initial small random transfer, a multi-megabyte transfer, and the final close path. The receiver polls `FIONREAD`, reads one byte through `recvmsg()`, checks `TCP_CM_INQ == expected_len - 1`, drains the rest, then repeatedly validates that in-queue values never exceed remaining data during the large transfer. After peer close, it checks the documented FIN behavior where `TCP_CM_INQ` reports `1` both before and after EOF.

## State, Persistence, And Dependencies
All state is transient: forked processes, loopback sockets, random buffers, and Unix-socket phase messages. There are no persistent files. The test depends on Linux TCP ancillary data support, MPTCP protocol support when selected, loopback availability, and libc/kernel headers with `linux/tcp.h` and sockios constants. `init_rng()` seeds children with `getrandom()` so payload sizes vary across runs.

## Integration Points
`mptcp_sockopt.sh` invokes this binary from a network namespace after checking for `mptcp_ioctl` support in `/proc/kallsyms`. That script runs protocol-mixed cases such as TCP sender to MPTCP receiver and MPTCP sender to TCP receiver, over IPv4 and IPv6. The helper therefore acts as the low-level assertion engine for shell-level MPTCP TCP_INQ coverage.

## Risks
The helper uses `assert()` for protocol invariants, so compiling with `NDEBUG` would remove important checks. It has fixed port `15432`, fixed 15-second alarms, and timing loops for queue drain/readiness, making it sensitive to slow or heavily loaded CI systems. `wait_for_ack()` assumes `TIOCOUTQ`/`SIOCOUTQNSD` convergence within five seconds. The test also relies on exact current `TCP_INQ` FIN semantics.

## Test Signals
Pass signals are zero exit status from both child processes and successful assertions for small-transfer, large-transfer, output-queue, and FIN cases. Failure signals include missing ancillary data, mismatched in-queue byte counts, queue values larger than expected data, short writes, connection setup failures, child signal termination, and timeout alarms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_inq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_join.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_join.sh

## Purpose
`mptcp_join.sh` is the broad MPTCP path-manager and MP_JOIN regression matrix. It validates subflow creation, ADD_ADDR/RM_ADDR signaling, endpoint flags, port-based endpoints, IPv4/IPv6/v4-mapped behavior, backup/fullmesh/laminar routing, syncookies, checksums, fast close, failover, userspace PM operations, event generation, and endpoint deletion/re-addition while data is flowing.

## Important APIs, Types, And Functions
The script sources `mptcp_lib.sh` and relies on `mptcp_connect`, `pm_nl_ctl` or `ip mptcp`, `ip netns`, `tc netem`, `iptables`, `ip6tables`, `ss`, `nstat`, and optional `tcpdump`. Its state variables configure each test indirectly: `addr_nr_ns1`, `addr_nr_ns2`, `test_linkfail`, `sflags`, `fastclose`, `fullmesh`, `speed`, `bind_addr`, and expected counters such as `join_syn_tx`, `join_syn_rej`, `join_csum_ns1`, and fallback expectations. Major helpers include `init_partial()`, `reset()`, `run_tests()`, `do_transfer()`, `pm_nl_set_endpoint()`, `chk_join_nr()`, `chk_add_nr()`, `chk_rm_nr()`, `chk_prio_nr()`, `chk_mptcp_info()`, `userspace_pm_*()`, `chk_evt_nr()`, and the grouped test functions listed in `all_tests_sorted`.

## Control Flow
The script builds an ordered test suite from `all_tests_sorted`, optionally restricts it with single-letter options or explicit test ids/names, and then invokes each selected group by function name. `reset()` finalizes the previous TAP result, creates or refreshes two namespaces, configures four veth pairs with IPv4 and IPv6 addresses, applies requested sysctls or packet filters, and creates temporary input/output files. `do_transfer()` starts an MPTCP listener and connector with `mptcp_connect`, optionally starts packet capture, starts a timeout watchdog, manipulates endpoints while the connection is live through `pm_nl_set_endpoint()`, waits for both sides, collects `nstat`, and compares transferred files. Each test then checks protocol counters and socket state. The tail of the script wires subtest groups for subflows, error paths, signal addresses, laminar endpoints, link failures, ADD_ADDR timeout, removals, runtime additions, IPv6, v4-mapped and mixed-family operation, backup and fullmesh changes, fast close, MP_FAIL, userspace PM, and endpoint lifecycle.

## State, Persistence, And Dependencies
Runtime state lives in temporary files, namespaces `ns1`/`ns2`, endpoint tables, MPTCP sysctls, iptables rules, tc qdiscs, background event listeners, and running `mptcp_connect` processes. Cleanup removes temp files and namespaces. The script requires root-like namespace privileges, MPTCP kernel support, `/proc/kallsyms`, `ip`, `tc`, `ss`, iptables/ip6tables, and test binaries in the same directory. Feature gates use `mptcp_lib_kallsyms_has()` and selected kernel-version checks to skip cases on older kernels.

## Integration Points
This is a central selftest entrypoint for `tools/testing/selftests/net/mptcp`. It integrates with `mptcp_lib.sh` for TAP output, feature checks, namespace management, PM abstraction, timeout handling, and counter reads. It integrates with `pm_nl_ctl.c` for low-level netlink commands unless `-i` selects `ip mptcp`. It also exercises `mptcp_connect`, `ss -M`, MPTCP MIB counters, and PM event delivery through `pm_nl_ctl events`.

## Risks
The script is intentionally stateful and timing-sensitive. Many checks depend on exact MIB counter values, but some tolerate retransmissions or flaky behavior. Packet filters and tc rules assume interface names, option offsets, and enough privilege. The indirect variable style makes local changes risky because stale environment variables can alter later tests if not reset. Some tests rely on fixed generated ports derived from the TAP counter, so ordering changes affect runtime behavior.

## Test Signals
Success is expressed through per-subtest TAP entries plus `[ OK ]` status lines. Strong signals include byte-identical transfers, expected MP_JOIN SYN/SYNACK/ACK counts, expected ADD_ADDR/RM_ADDR/MP_PRIO/MP_FAIL/MP_RST counters, expected `ss` MPTCP info, and expected event counts. Failures print socket stats, nstat deltas, file-tail diagnostics, failed test ids, and optional packet captures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_join.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_lib.sh

## Purpose
`mptcp_lib.sh` is the shared support library for MPTCP shell selftests. It standardizes kselftest return codes, colored status output, TAP result collection, feature gating, namespace lifecycle, transfer-file checks, timeout cleanup, MPTCP event capture, and path-manager command abstraction.

## Important APIs, Types, And Functions
The script exports event constants such as `MPTCP_LIB_EVENT_ESTABLISHED`, address-family constants, and global result state arrays such as `MPTCP_LIB_SUBTESTS`. Result helpers include `mptcp_lib_result_pass()`, `mptcp_lib_result_fail()`, `mptcp_lib_result_skip()`, `mptcp_lib_result_code()`, and `mptcp_lib_result_print_all_tap()`. Feature and environment helpers include `mptcp_lib_check_mptcp()`, `mptcp_lib_check_kallsyms()`, `mptcp_lib_kallsyms_has()`, `mptcp_lib_kversion_ge()`, and `mptcp_lib_check_tools()`. Runtime helpers include `mptcp_lib_ns_init()`, `mptcp_lib_ns_exit()`, `mptcp_lib_wait_timeout()`, `mptcp_lib_kill_group_wait()`, `mptcp_lib_nstat_init()`, `mptcp_lib_get_counter()`, `mptcp_lib_make_file()`, and PM wrappers such as `mptcp_lib_pm_nl_add_endpoint()`.

## Control Flow
Consumers source the library, call feature checks, create namespaces with `mptcp_lib_ns_init()`, run subtests, and report results through TAP helpers. The TAP path increments ids, detects duplicate subtest names, tracks elapsed time since the previous result, and treats flaky subtests as ignored unless `SELFTESTS_MPTCP_LIB_OVERRIDE_FLAKY=1` is set. Namespace initialization delegates to `setup_ns` from the parent `lib.sh`, then enables `net.mptcp.enabled` in each namespace. PM wrappers dispatch either to `ip -n <ns> mptcp ...` after `mptcp_lib_set_ip_mptcp()` or to `./pm_nl_ctl` through `ip netns exec`.

## State, Persistence, And Dependencies
State is process-global shell state: result arrays, counters, color variables, selected PM backend, and temporary `nstat` histories under `/tmp/<namespace>.nstat` and `/tmp/<namespace>.out`. Cleanup helpers remove those nstat files and namespaces. The library depends on `../lib.sh` for generic kselftest namespace utilities and on external tools selected by each test (`ip`, `tc`, `ss`, iptables variants).

## Integration Points
Nearly every shell script in the MPTCP selftest directory relies on this file for output and guard behavior. It bridges higher-level tests to `pm_nl_ctl.c`, `ip mptcp`, `mptcp_connect`, `ss`, and MPTCP MIB counters. Event parsing helpers are coupled to the textual format emitted by `pm_nl_ctl events`.

## Risks
Because it is sourced, all variables and functions share the caller's shell namespace. PM wrapper argument parsing uses positional scans and limited quoting, reflecting compatibility with existing tests. Kallsyms and kernel-version checks are only approximations for feature support, so backports can need `SELFTESTS_MPTCP_LIB_NO_KVERSION_CHECK=1`. Counter reads from `nstat` can be missing on older kernels, causing skips or feature-expectation failures.

## Test Signals
The library's direct signals are TAP output, `[ OK ]`, `[SKIP]`, `[FAIL]`/`[IGNO]` lines, duplicate-result diagnostics, and printed socket/nstat diagnostics. For callers, reliable signals are correct namespace setup/cleanup, successful tool detection, valid transfer comparison, expected PM output formatting, and non-empty event/counter values when a feature is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_sockopt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_sockopt.c

## Purpose
`mptcp_sockopt.c` is a C selftest helper for MPTCP socket option ABI behavior. It validates `SOL_MPTCP` options, per-subflow TCP info and addresses, `MPTCP_FULL_INFO`, packet/stat counters, forward/backward-compatible length handling, and normal inherited socket options such as `IP_TOS`.

## Important APIs, Types, And Functions
The file defines fallback UAPI structures for `mptcp_info`, `mptcp_subflow_data`, `mptcp_subflow_addrs`, `mptcp_subflow_info`, and `mptcp_full_info` if headers are older. `struct so_state` tracks previous MPTCP and TCP samples. Core functions are `do_getsockopt_bogus_sf_data()`, `do_getsockopt_mptcp_info()`, `do_getsockopt_tcp_info()`, `do_getsockopt_subflow_addrs()`, `do_getsockopt_mptcp_full_info()`, `do_getsockopts()`, `test_ip_tos_sockopt()`, `connect_one_server()`, `process_one_client()`, `server()`, `client()`, and `main()`.

## Control Flow
`main()` parses `-6`, seeds randomness, creates a pipe, forks a server, waits for listener readiness, then forks a client. The server listens on loopback MPTCP, accepts one connection, samples sockopts, echoes received data, waits for EOF, and checks post-transfer counters. The client connects over MPTCP, validates `IP_TOS` set/get corner cases, samples initial sockopts, writes a random buffer, reads the echo, and checks MPTCP and TCP byte counters. The option-specific functions verify sizes, kernel/user truncation, subflow count `1`, socket local/remote address equivalence, and `MPTCP_FULL_INFO` consistency with prior `MPTCP_INFO`, `TCP_INFO`, and address samples.

## State, Persistence, And Dependencies
State is transient process/socket state: one listener, one accepted socket, one client socket, a pipe for readiness, random transfer buffers, and sampled structs. No persistent output is written. The helper depends on MPTCP kernel support, `SOL_MPTCP` getsockopts, loopback networking, and packet-stat fields that may be absent on older kernels; the code tolerates shorter `MPTCP_INFO` by treating packet stats as unavailable.

## Integration Points
`mptcp_sockopt.sh` invokes this binary inside a sandbox namespace for IPv4 and IPv6. Its success contributes TAP subtests named `sockopt v4` and `sockopt v6`. The helper also indirectly tests kernel UAPI compatibility because it carries local structure definitions for builds against older headers.

## Risks
Many assertions assume exactly one subflow; if the environment or path manager creates additional subflows, the helper fails even if the API works. It uses fixed port `15432` and 15-second alarms. Some TCP byte counters may update asynchronously, so `do_getsockopt_tcp_info()` polls up to five times. `MPTCP_FULL_INFO` may legitimately return `EOPNOTSUPP`, which is treated as a skip-like message inside the helper, not a process skip.

## Test Signals
Pass signals are zero exit status, correct MPTCP/TCP byte deltas, expected subflow data layout behavior for good and bogus buffers, matching subflow addresses, and valid `IP_TOS` behavior. Failures identify getsockopt ABI regressions, incorrect length negotiation, wrong subflow counts, mismatched addresses, stale counters, or unexpected process exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_sockopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_sockopt.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_sockopt.sh

## Purpose
`mptcp_sockopt.sh` is the shell harness for MPTCP socket-option and TCP_INQ tests. It builds a two-namespace, four-link topology with endpoint signaling, verifies that MPTCP traffic uses marked packets on expected subflows, then runs the C helpers `mptcp_sockopt` and `mptcp_inq`.

## Important APIs, Types, And Functions
The script uses `mptcp_lib.sh` for feature checks, namespace setup, PM commands, TAP output, file generation, counters, and transfer comparison. Key functions are `init()`, `cleanup()`, `add_mark_rules()`, `check_mark()`, `do_transfer()`, `do_mptcp_sockopt_tests()`, `do_tcpinq_test()`, and `do_tcpinq_tests()`. External dependencies are `ip`, `iptables`, `ip6tables`, `mptcp_connect`, `mptcp_sockopt`, `mptcp_inq`, and either `pm_nl_ctl` or `ip mptcp`.

## Control Flow
After `-i` option parsing, the script checks MPTCP, kallsyms, and tools, creates namespaces `ns1`, `ns2`, and `ns_sbox`, and provisions four veth pairs. Both peers receive IPv4 and IPv6 addresses, routes, endpoint signals, and `8/8` PM limits. `add_mark_rules()` permits packets with the expected fwmark and drops unmarked TCP packets to catch marking regressions. `do_transfer()` runs `mptcp_connect` listener/client pairs, captures nstat, compares files, and checks iptables DROP counters. Then `do_mptcp_sockopt_tests()` runs `./mptcp_sockopt` and `./mptcp_sockopt -6` in the sandbox namespace if `mptcp_diag_fill_info` exists. `do_tcpinq_tests()` runs `mptcp_inq` across TCP/MPTCP transmit/receive combinations when `mptcp_ioctl` exists.

## State, Persistence, And Dependencies
State consists of temporary input/output files, three namespaces, endpoint tables, route state, iptables rules, and nstat histories. Cleanup removes temp files and namespaces. The script depends on root privileges for namespaces/firewall setup, MPTCP support, kallsyms visibility, and same-directory compiled helpers.

## Integration Points
This harness connects the lower-level C helpers to the kselftest environment and the MPTCP PM setup. It uses `mptcp_lib_pm_nl_*` wrappers so the same scenarios can use either the in-tree `pm_nl_ctl` utility or the system `ip mptcp` interface. It also tests interaction with `mptcp_connect` control-message options by passing `TIMESTAMPNS` and conditionally `TCPINQ`.

## Risks
The packet-marking rules are strict: unexpected unmarked TCP control traffic can fail the mark check. The test depends on iptables legacy/nft behavior matching the options used. Feature gates skip sockopt or TCP_INQ portions when symbols are missing, so full coverage requires a kernel exposing `mptcp_diag_fill_info` and `mptcp_ioctl`. Fixed port `12001` and timeout assumptions can be fragile under parallel runs.

## Test Signals
Signals include TAP records for IPv4/IPv6 transfer, mark checks, sockopt v4/v6, and TCP_INQ variants. Failures include nonzero client/server exits, file mismatches, nonzero DROP counters, missing helper support, and C helper assertion failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_sockopt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/pm_netlink.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/pm_netlink.sh

## Purpose
`pm_netlink.sh` is a path-manager netlink smoke and compatibility test. It validates endpoint add/get/dump/delete/flush behavior, endpoint id allocation and wraparound, flag changes, hard limits, duplicate handling, and receive/subflow limit setting for both `pm_nl_ctl` and optionally `ip mptcp`.

## Important APIs, Types, And Functions
The script sources `mptcp_lib.sh` and uses PM abstraction helpers for endpoint and limit operations. Local helpers include `format_limits()`, `get_limits()`, `format_endpoints()`, `get_endpoint()`, `change_address()`, `set_limits()`, `add_endpoint()`, `del_endpoint()`, `flush_endpoint()`, `show_endpoints()`, `change_endpoint()`, and `check()`. It uses `mptcp_lib_check_output()` to compare command stdout and return codes.

## Control Flow
After `-i` option parsing, it creates one namespace, captures default limits, and runs a linear sequence of assertions. It starts with empty endpoint dumps, adds simple and flagged endpoints, deletes one, verifies duplicate-add errors, fills endpoint ids through the hard limit, exercises ids `10..255`, flushes, and checks that unknown flags are ignored only by `pm_nl_ctl`. It then validates invalid limit updates do not change defaults, sets limits to `8/8`, tests explicit ids and id wraparound, and changes endpoint flags through `backup`, `nobackup`, and optionally `fullmesh`/`nofullmesh`/combined flags.

## State, Persistence, And Dependencies
State is contained in one temporary namespace, one stderr temp file, and the namespace-local MPTCP endpoint/limit tables. Cleanup removes the namespace and temp file. The test depends on MPTCP sysctls, `ip`, and either in-tree `pm_nl_ctl` or system `ip mptcp`.

## Integration Points
This is the focused PM netlink CLI/API conformance script used by the selftest suite. It exercises the formatting wrappers in `mptcp_lib.sh`, the `pm_nl_ctl.c` implementation, and the kernel path-manager UAPI. With `-i`, it cross-checks that `ip mptcp` output can be normalized to expected strings.

## Risks
The assertions compare exact stdout, so formatting changes in `ip mptcp` or `pm_nl_ctl` can fail the test even if kernel behavior is correct. The `unknown` flag case is intentionally not available through `ip mptcp`. Default limits are only asserted when `SELFTESTS_MPTCP_LIB_EXPECT_ALL_FEATURES=1`, which avoids false failures on older kernels but can hide default drift in normal runs.

## Test Signals
Pass signals are exact expected output and return codes for each `check()` plus final TAP output. Failures show command stderr or unexpected stdout. Important failure classes are duplicate address acceptance, id allocator regressions, hard-limit violations, incorrect flag changes, and limit-set validation bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/pm_netlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/pm_nl_ctl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/pm_nl_ctl.c

## Purpose
`pm_nl_ctl.c` is the in-tree command-line client for the MPTCP path-manager generic-netlink API used by the selftests. It can add/delete/get/dump/flush endpoint tables, set/get limits, set endpoint flags, send userspace-PM announce/remove/create-subflow/destroy-subflow commands, listen on an MPTCP socket, and stream PM multicast events in a parseable text format.

## Important APIs, Types, And Functions
The utility uses `NETLINK_GENERIC`, generic netlink controller commands, `linux/mptcp.h`, nested route attributes, and MPTCP PM commands such as `MPTCP_PM_CMD_ADD_ADDR`, `GET_ADDR`, `DEL_ADDR`, `SET_LIMITS`, `SET_FLAGS`, `ANNOUNCE`, `REMOVE`, `SUBFLOW_CREATE`, and `SUBFLOW_DESTROY`. Core functions are `init_genl_req()`, `nl_error()`, `do_nl_req()`, `resolve_mptcp_pm_netlink()`, `genl_parse_getfamily()`, `capture_events()`, `add_addr()`, `del_addr()`, `get_addr()`, `dump_addrs()`, `flush_addrs()`, `get_set_limits()`, `set_flags()`, `announce_addr()`, `remove_addr()`, `csf()`, `dsf()`, `add_listener()`, and `main()`.

## Control Flow
`main()` opens a generic netlink socket, resolves the MPTCP PM family id and event multicast group through `CTRL_CMD_GETFAMILY`, then dispatches on the first subcommand. Request builders manually append netlink attributes into a 1 KiB stack buffer after the generic-netlink header. Endpoint commands create nested `MPTCP_PM_ATTR_ADDR` attributes with family, IPv4/IPv6 address, id, flags, port, and interface index. Userspace PM commands additionally carry connection tokens and remote-address nests. Dump/get responses are parsed and printed in stable selftest-oriented lines. `events` joins the PM event multicast group and loops forever printing `type`, token, family, addresses, ports, ids, errors, backup, and server-side flags to stderr.

## State, Persistence, And Dependencies
The program has no persistent state. Kernel-visible state changes occur through the path-manager endpoint table or active MPTCP connections identified by token. `listen` creates a blocking MPTCP listener and pauses until killed. Dependencies are Linux generic netlink, MPTCP UAPI headers, interface index resolution, and privileges sufficient for PM netlink operations in the target namespace.

## Integration Points
Shell tests call this utility through `ip netns exec <ns> ./pm_nl_ctl ...`. `mptcp_lib.sh` wraps it behind `mptcp_lib_pm_nl_*` helpers, while `mptcp_join.sh`, `pm_netlink.sh`, and `userspace_pm.sh` depend on its exact output and event text. It is also the userspace-PM control path for creating/destroying subflows by token.

## Risks
All netlink messages are hand-built in fixed-size buffers, so adding attributes can risk overflow if not checked. Some numeric fields are parsed with `atoi()` and copied in host byte order to match current UAPI expectations; invalid inputs generally call `error(1, ...)`. Output format is part of the selftest contract and brittle. The event loop never exits on its own and must be killed by callers. The custom `unknown` flag is intentionally selftest-only.

## Test Signals
For command mode, success is zero exit and expected stdout or no error ACK. `nl_error()` prints kernel extack messages and exits on failure. For event mode, useful signals are lines containing expected event types and attributes consumed by `mptcp_lib_evts_get_info()` and event-count checks. For `listen`, creation/closure events and successful subflow connections are the observable outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/pm_nl_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/simult_flows.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/simult_flows.sh

## Purpose
`simult_flows.sh` tests MPTCP throughput and scheduler behavior when two subflows are available with different bandwidth and delay profiles. It verifies that simultaneous flows complete within an expected time budget and preserve data in both transfer directions.

## Important APIs, Types, And Functions
The script uses `mptcp_lib.sh`, `ip netns`, `tc netem`, `mptcp_connect`, optional `tcpdump`, `nstat`, and file comparison. Key functions are `setup()`, `cleanup()`, `do_transfer()`, and `run_test()`. Global knobs include `capture`, `bail`, `slack`, `timeout_poll`, `timeout_test`, and `MPTCP_LIB_SUBTEST_FLAKY`.

## Control Flow
`setup()` creates three namespaces: `ns1` as connector, `ns2` as router, and `ns3` as listener. Two `ns1` to `ns2` links carry MPTCP subflows, while `ns2` to `ns3` provides forwarding to the listener. It creates a small file and a large file, enables forwarding in `ns2`, configures one subflow endpoint on `ns1`, and increases timing slack on debug kernels. `run_test()` clears old qdiscs, installs matching netem rate/delay settings on both directions of each subflow link, computes a max runtime from transfer size and aggregate bandwidth, then calls `do_transfer()` twice: small-to-large and reverse. `do_transfer()` runs `mptcp_connect -T <max_time>` on both ends, enforces a watchdog, captures nstat, compares both output files, and optionally records pcap files.

## State, Persistence, And Dependencies
Runtime state includes three namespaces, veth links, qdiscs, forwarding sysctls, endpoint limits, temp files, optional capture files, and nstat histories. Cleanup removes temp files and namespaces. The test depends on MPTCP, `ip`, `tc`, `mptcp_connect`, namespace privileges, and optionally `tcpdump` when `-c` is selected.

## Integration Points
This is a performance-sensitive MPTCP selftest using the same library result/TAP system as other scripts. It integrates with PM wrappers to configure subflow endpoints and with `mptcp_connect`'s join/time-limit options to turn throughput into a pass/fail signal.

## Risks
Timing is inherently noisy. The script compensates with slack and marks some unbalanced-bandwidth cases flaky, but overloaded CI, debug kernels, or inaccurate virtual NIC accounting can still fail. The computed time budget assumes 10 percent header overhead and uses fixed transfer sizes. Optional packet capture can perturb timing.

## Test Signals
Pass signals are both peers exiting successfully, both file comparisons passing, no timeout process remaining, and TAP entries for balanced/unbalanced cases. Failures print client/server exit codes, socket/nstat diagnostics, file sizes, and capture logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/simult_flows.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/userspace_pm.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/userspace_pm.sh

## Purpose
`userspace_pm.sh` validates the userspace MPTCP path-manager API and event stream with long-lived IPv4 and IPv6 connections. It checks sysctl mapping, ADD_ADDR/RM_ADDR commands, CREATE_SUBFLOW/DESTROY_SUBFLOW commands, mixed IPv4-on-IPv6 subflows, MP_PRIO signaling, and listener-created/listener-closed events.

## Important APIs, Types, And Functions
The script sources `mptcp_lib.sh`, uses event constants, and drives `pm_nl_ctl ann`, `rem`, `csf`, `dsf`, `set`, `listen`, and `events`. Key functions are `cleanup()`, `make_connection()`, `check_expected()`, `verify_announce_event()`, `test_announce()`, `verify_remove_event()`, `test_remove()`, `verify_subflow_events()`, `test_subflows()`, `test_subflows_v4_v6_mix()`, `test_prio()`, `verify_listener_events()`, and `test_listener()`.

## Control Flow
After feature checks, the script verifies the legacy `path_manager` sysctl maps correctly to `pm_type`, enables userspace PM in two namespaces, builds one veth link with two IPv4 and two IPv6 addresses per side, starts `pm_nl_ctl events` in both namespaces, and creates one persistent IPv4 and one persistent IPv6 MPTCP connection using `mptcp_connect`. `make_connection()` extracts tokens, source ports, `server_side`, and `deny_join_id0` attributes from event files. Test sections then send invalid and valid announces/removals, verify event attributes on the peer, create and destroy subflows in both directions and both families, exercise a v4 subflow on a v6 MPTCP connection, send a userspace MP_PRIO flag update, and verify listener lifecycle events.

## State, Persistence, And Dependencies
State includes two namespaces, two long-lived MPTCP connections, background client/server `mptcp_connect` processes, event log temp files, a random payload file, PM tokens parsed from events, dynamic address ids, and fixed application/new ports. Cleanup kills all background processes, removes namespaces, and deletes temp files. Dependencies are MPTCP support, `/proc/sys/net/mptcp/pm_type`, `/proc/kallsyms`, `ip`, `mptcp_connect`, `pm_nl_ctl`, and PM event support for listener tests.

## Integration Points
The test is a standalone counterpart to the userspace-PM block inside `mptcp_join.sh`. It exercises the kernel's userspace PM netlink commands through `pm_nl_ctl.c` and validates event parsing helpers in `mptcp_lib.sh`. It also confirms the `path_manager=userspace|kernel` sysctl compatibility path when present.

## Risks
The script relies on sleeps after netlink operations rather than robust waits for every event, which can be fragile on slow systems. It parses the first matching event from temp files, so stale events must be cleared carefully. Random two-digit ids can theoretically collide with existing values if setup changes. `make_connection()` appears to wait for `${port}` even though it sets `app_port`, so correctness depends on the shared wait helper tolerating the value or the listener being ready by the following sleep in the observed environment.

## Test Signals
Pass signals are TAP entries for namespace setup, connection establishment with valid tokens and flags, expected announce/remove/subflow/listener event attributes, and expected MP_PRIO MIB counters. Failures identify missing userspace PM support, malformed or absent events, invalid token handling regressions, incorrect address ids/ports/families, or nonzero final return status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/userspace_pm.sh -->
