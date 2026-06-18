# subset-b-006873 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/setup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/setup.c

## Purpose
`setup.c` provides the TCP-AO selftest process, namespace, thread, output, and sysctl lifecycle used by the tests in `tcp_ao/`. It wraps kselftest result printing so multi-threaded server/client tests do not interleave output, creates isolated parent and child network namespaces connected by a veth, assigns the per-thread local and peer addresses, and centralizes skip/fail/exit handling.

## Important APIs, Types, And Functions
The file exports `__test_msg()`, `__test_ok()`, `__test_fail()`, `__test_xfail()`, `__test_error()`, and `__test_skip()` as mutex-protected kselftest print adapters. Test lifecycle functions include `test_failed()`, `test_add_destructor()`, `open_netns()`, `unshare_open_netns()`, `switch_ns()`, `switch_save_ns()`, `switch_close_ns()`, `synchronize_threads()`, and `__test_init()`. It also exports thread-local `this_ip_addr` and `this_ip_dest`, global `test_family`, and optmem helpers `test_get_optmem()` and `test_set_optmem()`.

## Control Flow
`__test_init()` installs a SIGINT handler, checks required kernel config features for network namespaces, veth, and TCP-AO, sets the kselftest plan, seeds `rand()`, initializes namespaces and ftrace, creates the cross-namespace veth, configures the child namespace, optionally starts the peer thread there, switches back to the parent namespace, configures its endpoint, and invokes the primary peer function. The thread entry stores its endpoint addresses in thread-local globals before running the supplied test function. `synchronize_threads()` implements a reusable two-slot barrier between the server and client sides.

## State, Persistence, And Dependencies
State is mostly process-local: namespace fds, destructor list, failure/skip flags, barrier counters, `nr_threads`, and thread-local endpoint addresses. It mutates system state by unsharing network namespaces, creating veth links through helpers from the TCP-AO library, and potentially writing `/proc/sys/net/core/optmem_max`. The optmem path handles both old global and newer per-namespace sysctl behavior and registers a destructor to restore the saved value.

## Integration Points
All TCP-AO C tests use this file through `aolib.h` and `test_init()` wrappers. It integrates kselftest, namespace helpers, ftrace setup, link/address/route helpers, and the socket helpers in `sock.c`.

## Risks
The barrier assumes every participating thread reaches every stage; early returns can deadlock. The optmem adjustment is explicitly not re-entrant and is unsafe for parallel tests that alter the same sysctl. Namespace switching errors abort the process. The temporary thread argument in `__test_init()` is stack-backed, but the code relies on the new thread copying it before the parent continues past the synchronization-heavy test setup.

## Test Signals
Useful signals are clean kselftest pass/skip/fail accounting, deterministic veth setup in two namespaces, successful barrier progress, and restoration of `optmem_max` when changed. Failures usually surface as `test_error()` exits, timeout deadlocks, or missing kernel config skips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/sock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/sock.c

## Purpose
`sock.c` is the TCP-AO selftest socket utility layer. It creates listen/connect sockets bound to the test veth, prepares TCP-MD5 and TCP-AO socket option structures, reads TCP-AO per-namespace/per-socket/per-key counters, compares expected counter deltas, and provides client/server echo loops used by many TCP-AO behavior tests.

## Important APIs, Types, And Functions
Connection helpers include `__test_listen_socket()`, `test_wait_fd()`, `__test_connect_socket()`, `_test_skpair_connect_poll()`, `test_skpair_wait_poll()`, `test_server_run()`, `test_skpair_server()`, `test_client_verify()`, and `test_skpair_client()`. TCP option helpers include `__test_set_md5()`, `test_prepare_key_sockaddr()`, `test_get_one_ao()`, `test_get_ao_info()`, `test_set_ao_info()`, `test_cmp_getsockopt_setsockopt()`, and `test_cmp_getsockopt_setsockopt_ao()`. Counter helpers include `test_get_tcp_counters()`, `test_cmp_counters()`, `test_assert_counters_sk()`, `test_assert_counters_key()`, and `test_tcp_counters_free()`.

## Control Flow
Listen sockets are created nonblocking, bound to `SO_BINDTODEVICE`, bound to a supplied address, and listened on. Connect sockets are made nonblocking and optionally waited to completion unless asynchronous mode is requested. Polling helpers repeatedly call `select()`, inspect `SO_ERROR`, and can stop early when TCP-AO counter deltas meet an expected bitmask or a peer error flag is set. The echo server reads then writes back data; the client sends randomized chunks and verifies byte-for-byte echoes.

## State, Persistence, And Dependencies
No persistent state is stored, but the functions allocate counter/key dumps that callers must free through `test_tcp_counters_free()`. `test_get_tcp_counters()` depends on netstat parsing helpers and Linux TCP-AO UAPI getsockopts. It interprets missing AO info as a socket with no AO state. The code depends on `test_family`, `veth_name`, `this_ip_dest`, constants and macros from `aolib.h`, and kernel UAPI definitions for `TCP_AO_*`, `TCP_MD5SIG_EXT`, and `TCP_INFO`-related counters.

## Integration Points
Higher-level tests use this file as their handshake, traffic generation, and assertion substrate. It bridges direct socket syscalls, TCP-AO UAPI ABI validation, netstat counters, and the thread barrier from `setup.c`.

## Risks
Counter comparison assumes counters never decrease and that key dump order is stable between snapshots. Polling uses short sleeps and global timeouts, so slow systems can produce timeouts that look like protocol failures. `test_cmp_getsockopt_setsockopt()` contains special cases for `cmac(aes128)`/`cmac(aes)` translation and default MAC length, so new algorithm behavior may need updates. Some alloca-based buffers scale with requested test sizes.

## Test Signals
Strong signals include successful nonblocking connects, exact echo verification, AO/MD5 getsockopt fields matching the setsockopt input, expected counter bit deltas, no unexpected `SO_ERROR`, and per-key good/bad counters changing only when requested by the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/utils.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/utils.c

## Purpose
`utils.c` contains small shared utilities for the TCP-AO selftest library: random buffer filling, formatted file writes, and wildcard IPv4/IPv6 sockaddr constants.

## Important APIs, Types, And Functions
`randomize_buffer()` fills an arbitrary byte buffer using repeated `rand()` words plus a partial final word. `test_echo()` writes a formatted string to a named file with either truncate or append semantics using `test_snprintf()` from `aolib.h`. The file defines `addr_any6` and `addr_any4` as zero-address `sockaddr_in6` and `sockaddr_in` constants.

## Control Flow
`randomize_buffer()` returns immediately for zero length, writes full `int` words, then copies leftover bytes from one random integer. `test_echo()` opens the target file, formats the variadic message, writes it in one `fwrite()`, closes the file, frees the allocated string, and returns `0` only if the full formatted message was written.

## State, Persistence, And Dependencies
The only persistent side effect is writing the requested file in `test_echo()`, typically used for procfs/sysfs or tracing helper output. Random data depends on the process `rand()` seed established by `setup.c`. The file depends on `aolib.h` for formatting helpers, errno conventions, and common includes.

## Integration Points
The wildcard sockaddr constants are used by socket option tests that need "any address" AO keys or filters. `randomize_buffer()` feeds the echo/verification loops in `sock.c`. `test_echo()` is a generic utility for simple file configuration writes.

## Risks
The random data is not cryptographic and intentionally inherits global `rand()` state. `randomize_buffer()` does pointer arithmetic on `void *`, relying on GNU C behavior. `test_echo()` does not retry partial writes; it reports failure if `fwrite()` writes fewer bytes than requested.

## Test Signals
The expected signal is simple: randomized payloads should compare equal after echo, `test_echo()` should return zero for complete file writes, and wildcard sockaddr constants should produce accepted "any" TCP-AO option cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/restore.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/restore.c

## Purpose
`restore.c` verifies that an established TCP-AO connection can be checkpointed with TCP repair, killed, restored onto another socket, and continue exchanging authenticated traffic. It also deliberately corrupts restored TCP-AO repair fields to confirm mismatches break the connection and increment the expected AO counters.

## Important APIs, Types, And Functions
Core routines are `try_server_run()`, `test_get_sk_checkpoint()`, `test_sk_restore()`, `server_fn()`, and `client_fn()`. The test uses TCP repair helpers such as `test_enable_repair()`, `test_sock_checkpoint()`, `test_ao_checkpoint()`, `test_sock_restore()`, `test_add_repaired_key()`, `test_ao_restore()`, `test_disable_repair()`, `test_kill_sk()`, and `test_sock_state_free()`, plus AO counter and trace expectation helpers.

## Control Flow
The server iterates through five ports. For each port it listens, installs an AO key, accepts a client, performs a pre-migration echo, then attempts another echo after the client restores its socket. The client creates a matching AO socket, connects, verifies traffic, checkpoints TCP and AO state, kills the original socket, and restores a new socket. The first case uses valid state; subsequent cases increment send ISN, receive ISN, send SNE, or receive SNE before restore and register expected mismatch tracepoints.

## State, Persistence, And Dependencies
State is transient TCP repair image data in `struct tcp_sock_state`, `sockaddr_af`, and `struct tcp_ao_repair`. Network state lives in the two test namespaces created by `setup.c`. The test depends on TCP-AO, TCP repair support, ftrace event expectation helpers, netstat counters such as `TCPAOGood`/`TCPAOBad`, and the shared socket echo helpers.

## Integration Points
This test exercises the kernel TCP-AO repair ABI together with normal established TCP traffic. It integrates AO key installation, AO repair state restore, netstat deltas, per-socket counters, and tracepoint verification.

## Risks
The restore path is sensitive to barrier ordering between server and client. Fault cases rely on timeouts and counter changes to distinguish a broken authenticated connection from an unrelated scheduling delay. Incorrect cleanup of repaired sockets can leave peers in states where AO counters are unavailable. The test assumes tracepoint support when event expectations are registered.

## Test Signals
`main()` declares 21 planned checks. Passing signals include the valid restored connection staying alive, corrupted restore cases timing out or failing as expected, `TCPAOGood`/`TCPAOBad` increasing in the right direction, `test_assert_counters()` matching expected bitmasks, and AO mismatch tracepoints appearing for the corrupted fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/restore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/rst.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/rst.c

## Purpose
`rst.c` verifies that TCP reset segments on TCP-AO connections are correctly signed. It covers both active resets generated by local abort/listen-socket teardown paths and passive resets generated as replies from TIME_WAIT handling after sequence-number corruption.

## Important APIs, Types, And Functions
Important functions are `netstats_check()`, `close_forced()`, `test_server_active_rst()`, `test_server_passive_rst()`, `test_wait_fds()`, `test_client_active_rst()`, `test_client_passive_rst()`, `server_fn()`, and `client_fn()`. It uses AO key helpers, TCP repair checkpoint/restore helpers, counter helpers, and socket echo helpers from `aolib.h`.

## Control Flow
The active-reset path creates multiple client sockets against a server listen socket with backlog zero. One connection is accepted, another is queued, and a third is left in request state. Closing the listen socket and forcibly closing the accepted socket should reset established or queued clients with AO-signed RSTs. The passive-reset path establishes a connection, checkpoints the client, lets the server close into TIME_WAIT-related state, corrupts the client's outgoing sequence number within-window, restores the client, and verifies the resulting RST is authenticated and observed as `ECONNRESET`.

## State, Persistence, And Dependencies
State is transient socket and TCP repair state. Netstat snapshots track `TCPAORequired`, `TCPAOGood`, and `TCPAOBad` before and after each side's tests. The passive RST case includes a sleep for retransmit timing to let FIN/ACK processing settle. Dependencies include TCP-AO, TCP repair, nonblocking socket readiness, and test namespaces.

## Integration Points
The file covers reset code paths distinct from ordinary data transmission: `tcp_send_active_reset()` through transmit-skb handling and `tcp_v*_send_reset()` style passive replies through unicast reply handling. It integrates these kernel paths with user-visible `SO_ERROR`, AO counters, and repair-based sequence manipulation.

## Risks
The passive reset test is timing-sensitive and explicitly notes that waiting for server FIN processing is difficult from userspace. The active reset path assumes backlog and accept queue behavior. Packet loss, slow scheduling, or changed TCP state timing can produce timeout-style failures even when AO signing is correct.

## Test Signals
`main()` plans 15 checks. Passing signals are no increase in `TCPAORequired` or `TCPAOBad`, an increase in `TCPAOGood`, clients observing reset where expected, passive reset returning `-ECONNRESET`, and MKT counters showing only good packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/rst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/self-connect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/self-connect.c

## Purpose
`self-connect.c` tests TCP-AO behavior for TCP self-connect on loopback, where a single socket binds and connects to its own local address and port. It covers same key IDs, different send/receive key IDs, and TCP repair restore of self-connected AO sockets.

## Important APIs, Types, And Functions
The main helpers are `__setup_lo_intf()`, `setup_lo_intf()`, `tcp_self_connect()`, and `client_fn()`. The test uses `test_add_key()`, `test_add_repaired_key()`, `__test_connect_socket()`, `test_client_verify()`, `test_get_tcp_counters()`, `test_assert_counters()`, `test_enable_repair()`, `test_sock_checkpoint()`, `test_ao_checkpoint()`, `__test_sock_restore()`, `test_ao_restore()`, and trace expectations for `TCP_AO_RNEXT_REQUEST`.

## Control Flow
The single client thread configures loopback with either `127.0.0.1/8` or `::1/128`, adds a route to itself, and runs four self-connect scenarios. Each scenario creates one socket, installs AO keys, binds to the target local address and port, connects back to itself through `lo`, exchanges echo traffic, and checks AO counters. Restore scenarios checkpoint TCP and AO state, kill the original socket, restore onto a new port, reinstall repaired keys, restore AO state, and verify traffic again.

## State, Persistence, And Dependencies
The test mutates only the isolated test namespace loopback device, route table, and transient sockets. `local_addr` stores the loopback address. It depends on loopback routing, TCP-AO, TCP repair, ftrace expectation support for key rotation events, and shared TCP-AO helpers.

## Integration Points
Self-connect stresses a corner case where local and remote AO endpoint addresses are identical and both directions share one socket. It integrates AO key lookup, rnext/current-key behavior, route setup on `lo`, and repair restore using the same local and peer sockaddr.

## Risks
Self-connect behavior is unusual and may be sensitive to route selection and local address setup. Different key ID tests assume a predictable RNext negotiation trace. Restore changes the port, so mistakes in sockaddr port rewriting can make the restored flow fail for reasons unrelated to AO.

## Test Signals
`main()` plans 5 checks. Passing signals include successful traffic verification, `TCPAOGood` increasing, no unexpected counter deltas, and expected RNext trace events for different-key-ID scenarios, including the intentionally reversed repair key installation order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/self-connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/seq-ext.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/seq-ext.c

## Purpose
`seq-ext.c` verifies TCP-AO sequence-number extension behavior when 32-bit TCP sequence numbers wrap. It forces both directions near wraparound through TCP repair, migrates the connection to new ports to avoid stale packets, then confirms the connection survives and SNE counters increment.

## Important APIs, Types, And Functions
Key functions are `test_adjust_seqs()`, `test_sk_restore()`, `server_fn()`, and `client_fn()`. The test uses TCP repair checkpoint/restore helpers, AO repair helpers, `trace_ao_event_sne_expect()`, netstat counter reads, echo verification, and `test_assert_counters()`.

## Control Flow
The server and client first establish a normal AO connection and exchange `quota` bytes. Both sides then checkpoint TCP and AO state, kill their old sockets, increment their local ports, adjust incoming and outgoing sequence fields close to `UINT32_MAX`, restore onto the new endpoints, and exchange another `quota` bytes. The adjustments are asymmetric so send and receive rollover occur on different segments. The server registers expected send and receive SNE update tracepoints for both directions before the post-restore traffic.

## State, Persistence, And Dependencies
All state is transient socket state, repair images, AO repair images, and the global `client_new_port` used by the server restore. Netstat counters `TCPAOGood` and `TCPAOBad` provide namespace-level verification. Dependencies include TCP-AO repair ABI support, ftrace SNE tracepoint helpers, and the shared two-thread namespace harness.

## Integration Points
This is a high-value integration point between TCP repair, AO sequence extension tracking, port migration, counter accounting, and authenticated data transfer. It tests behavior that would be hard to reach through normal traffic alone.

## Risks
The test relies on exact sequence-state fields in `struct tcp_sock_state`; kernel repair ABI changes can break the setup. Barrier ordering between the two restored endpoints is critical. It checks `TCPAOBad` as a whole namespace counter after the test, so prior unexpected AO failures in the namespace would taint the result.

## Test Signals
`main()` plans 8 checks. Passing signals are successful pre- and post-migration echo, `TCPAOGood` increasing, `TCPAOBad` remaining zero, per-socket counters showing only good packets, expected SNE tracepoints, and nonzero `snd_sne` and `rcv_sne` in the final AO checkpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/seq-ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/setsockopt-closed.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/setsockopt-closed.c

## Purpose
`setsockopt-closed.c` is a broad TCP-AO UAPI validation test for closed or listening sockets. It verifies option size handling, invalid argument rejection, duplicate key detection, optmem pressure behavior, AO info setting/getting, and TCP_AO_GET_KEYS filtering semantics.

## Important APIs, Types, And Functions
The file centers on `__setsockopt_checked()`, `setsockopt_checked()`, `getsockopt_checked()`, `prepare_defs()`, `test_extend()`, `extend_tests()`, `test_optmem_limit()`, `test_einval_add_key()`, `test_einval_del_key()`, `test_einval_ao_info()`, `test_einval_get_keys()`, `duplicate_tests()`, `prepare_test_keys()`, `filter_keys_checked()`, and `filter_tests()`. It exercises `TCP_AO_ADD_KEY`, `TCP_AO_DEL_KEY`, `TCP_AO_INFO`, and `TCP_AO_GET_KEYS`.

## Control Flow
`client_fn()` prepares an auxiliary MD5 client address, then runs extension-size tests, invalid-input tests, key filtering tests, and duplicate detection. Each case creates a fresh socket through `prepare_defs()`, pre-installs the minimal AO state required for the command, mutates one field, and calls the checked wrapper with the expected errno. Successful AO add/info/get operations are verified by a follow-up getsockopt comparison or returned-size check.

## State, Persistence, And Dependencies
The test creates many short-lived sockets and closes each in the checked wrapper. `test_optmem_limit()` reads the current optmem value and adds keys until kernel allocation limits are hit. The test depends on TCP-AO UAPI structs, optional TCP-MD5 support for one conflict case, and helper functions for preparing default AO keys and verifying socket keys.

## Integration Points
This file is the main ABI conformance test for AO socket options. It ties kernel validation paths to exact userspace errno values, validates old/new structure size compatibility, confirms current/rnext key semantics, and checks `TCP_AO_GET_KEYS` filters by address, key IDs, current/rnext flags, and capacity reporting.

## Risks
Because the test expects exact errno values, intentional kernel ABI changes require updating it. It touches optmem behavior that changed from global to per-namespace across kernels; the harness handles that but parallel optmem tests are risky. Random key insertion order tests filter robustness but can complicate reproduction if ordering bugs appear.

## Test Signals
`main()` declares 126 planned checks. Passing signals include expected `EINVAL`, `ENOENT`, `EEXIST`, `EFAULT`, `EKEYREJECTED`, or `EMSGSIZE` results, accepted extended option sizes, rejected undersized/null options, optmem limit detection, matching getsockopt output, correct duplicate rejection, and accurate key filter match counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/setsockopt-closed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/unsigned-md5.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/unsigned-md5.c

## Purpose
`unsigned-md5.c` tests interactions among TCP-AO, TCP-MD5, and unsigned TCP connections. It verifies accept/connect outcomes, counter increments, trace events, post-establishment key-add restrictions, AO-required conflicts, and VRF/l3index intersection rules.

## Important APIs, Types, And Functions
Important routines include `setup_vrfs()`, `try_accept()`, `try_connect()`, `try_add_key_vrf()`, `test_continue()`, `open_add()`, `try_to_preadd()`, `try_to_add()`, `client_add_ips()`, `server_add_fail_tests()`, `client_add_fail_tests()`, `server_vrf_tests()`, `client_vrf_tests()`, `server_fn()`, and `client_fn()`. The file uses strategy flags such as `PREINSTALL_MD5_FIRST`, `PREINSTALL_AO`, `POSTINSTALL_AO`, `PREINSTALL_MD5`, and `POSTINSTALL_MD5`.

## Control Flow
The server adds routes for extra client addresses, then iterates through many listener configurations: AO-only, AO-required, MD5-only, unsigned, AO+MD5 matched or mismatched by client address, and both-key conflict cases. The client mirrors those cases with bound source addresses and expected faults. Later tests verify that adding AO/MD5 keys to established sockets fails where required and that AO and MD5 key l3index combinations are accepted or rejected according to the matrix embedded in the comments.

## State, Persistence, And Dependencies
State is transient sockets, AO/MD5 keys, optional VRF device `ksft-vrf`, extra client IPs, and netstat/ftrace counters. Optional tests skip when `KCONFIG_TCP_MD5` or `KCONFIG_NET_VRF` is unavailable. Shared volatile `sk_pair` communicates peer-side poll/connect errors across barrier stages.

## Integration Points
The file exercises the TCP authentication key lookup boundary between AO and legacy MD5. It integrates route setup, VRF l3index handling, AO-required mode, tracepoint expectations for AO and hash failures, and counter validation for both protocols.

## Risks
The test matrix is large and depends on exact key precedence, address matching, and errno behavior. Some cases use timeout as the expected failure mode, which can hide unrelated connection stalls. VRF cases require kernel and iproute2 support plus ifindex stability. Both sides must keep port ordering synchronized.

## Test Signals
`main()` plans 73 checks. Passing signals include expected successful connects, expected timeouts or `EKEYREJECTED` failures, correct `TCPAOGood`, `TCPAORequired`, `TCPAOKeyNotFound`, `TCPMD5NotFound`, and `TCPMD5Unexpected` counter increases, expected trace events, and accepted/rejected VRF key combinations matching the documented matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/unsigned-md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ecmp_failover.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ecmp_failover.sh

## Purpose
`tcp_ecmp_failover.sh` verifies that an established TCP flow using an ECMP route fails over to a remaining healthy nexthop after carrier loss on the active device. It covers both IPv4 and IPv6.

## Important APIs, Types, And Functions
Functions include `setup_server()`, `setup_client()`, `setup()`, `cleanup()`, `tcp_ecmp_failover()`, `test_ipv4()`, and `test_ipv6()`. It relies on `forwarding/lib.sh` for kselftest helpers, namespace setup, logging, command requirements, and tcpdump helpers.

## Control Flow
The script creates `client` and `server` namespaces connected by two veth pairs. Each namespace owns a dummy loopback-style endpoint address and installs equal-weight ECMP routes to the peer endpoint through both veth paths. The client disables normal TCP route refresh by raising `tcp_retries1` and enables `ignore_routes_with_linkdown` on both paths. `tcp_ecmp_failover()` starts tcpdump on both server veths, runs `socat` server and client streams, infers the active path from packet counts, brings that server-side veth down, captures on the remaining path, and fails if fewer than 1000 packets arrive after failover.

## State, Persistence, And Dependencies
The script mutates temporary namespaces, veths, dummy links, routes, and sysctls. It depends on root privileges through the forwarding library, plus `socat` and `tcpdump`. No persistent files are intended beyond temporary tcpdump artifacts cleaned by helpers.

## Integration Points
The test targets route cache invalidation and nexthop linkdown behavior for established TCP sockets. It integrates NETDEV_CHANGE, `RTNH_F_LINKDOWN`, `sk_dst_check()` invalidation, ECMP route lookup, and userspace packet capture.

## Risks
Packet count thresholds depend on timing and host scheduling. The initial active-path inference assumes one path dominates during the first capture window. Missing `ignore_routes_with_linkdown` support, tcpdump timing issues, or socat startup delays can cause false failures.

## Test Signals
Passing signals are logged `TCP IPv4 failover` and `TCP IPv6 failover` results with at least 1000 post-failover packets on the alternate veth. Failure signals include missing tools, namespace setup errors, no traffic after linkdown, or cleanup leaving namespaces behind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ecmp_failover.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_fastopen_backup_key.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_fastopen_backup_key.c

## Purpose
`tcp_fastopen_backup_key.c` stress-tests TCP Fast Open key rotation. It simulates multiple `SO_REUSEPORT` listeners behind a load balancer and verifies that staged primary/backup key rotation does not cause clients to present invalid cookies.

## Important APIs, Types, And Functions
Key functions are `get_keys()`, `set_keys()`, `build_rcv_fd()`, `connect_and_send()`, `is_listen_fd()`, `rotate_key()`, `run_one_test()`, `parse_opts()`, and `main()`. It uses `TCP_FASTOPEN`, `TCP_FASTOPEN_KEY`, `SO_REUSEPORT`, `MSG_FASTOPEN`, epoll, and optionally `/proc/sys/net/ipv4/tcp_fastopen_key`.

## Control Flow
`main()` parses `-4`, `-6`, `-s`, and `-r`, opens the proc fastopen key file, seeds random keys, and runs IPv4 or IPv6. `build_rcv_fd()` creates ten reuseport listeners, enables TFO, and installs the same initial key on each. `run_one_test()` loops 10000 times, sends one byte with `MSG_FASTOPEN`, accepts and receives the connection through epoll, and periodically rotates one listener. Rotation first installs a new backup key across listeners, then swaps backup and primary keys across listeners.

## State, Persistence, And Dependencies
State includes listener fds, process flags, current key length, random key material, and the proc fd. When not using socket options, the test writes the namespace-wide proc TFO key. It depends on TFO support, loopback networking, `SO_REUSEPORT`, and the wrapper script for namespace/sysctl setup and counter verification.

## Integration Points
This file is paired with `tcp_fastopen_backup_key.sh`, which runs it across IPv4/IPv6 and procfs/socket-option key paths. It exercises kernel TFO cookie validation while key rotation is partially rolled out across listeners.

## Risks
The test is randomized and long-running enough to expose race windows but may be sensitive to slow machines. Procfs writes use a fixed 128-byte buffer size rather than exact string length, which matches existing selftest behavior but is a point to watch. Key rotation state is static inside `rotate_key()`.

## Test Signals
The C program prints `PASS` on successful completion. The stronger end-to-end signal is the wrapper observing `TcpExtTCPFastOpenPassiveFail == 0` after each run mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_fastopen_backup_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_fastopen_backup_key.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_fastopen_backup_key.sh

## Purpose
`tcp_fastopen_backup_key.sh` is the harness for the TFO backup-key rotation test. It creates an isolated namespace, enables TCP Fast Open, runs the compiled C test in all mode combinations, and verifies no passive TFO cookie failures were recorded.

## Important APIs, Types, And Functions
Functions are `setup()`, `cleanup()`, and `do_test()`. It uses `ip netns`, namespace-local `sysctl net.ipv4.tcp_fastopen=3`, `ip tcp_metrics flush`, `nstat -az`, and the compiled `./tcp_fastopen_backup_key` binary.

## Control Flow
The script creates a temporary namespace, brings loopback up, enables client and server TFO, then calls `do_test()` sixteen times: IPv4/IPv6, procfs key path, socket-option key path, rotation path, and socket-option-plus-rotation path, with repeats. Each `do_test()` flushes TCP metrics to avoid stale cookies, executes the C binary with its option string, reads `TcpExtTCPFastOpenPassiveFail`, and fails if the counter is nonzero.

## State, Persistence, And Dependencies
State is limited to one temporary namespace and its TFO sysctl/counters. The trap deletes the namespace. The script depends on root privileges, `ip`, `nstat`, the compiled C binary in the current directory, and kernel TFO support.

## Integration Points
This wrapper provides the counter-based pass/fail signal missing from the C program alone. It connects TFO key rotation to the kernel `TcpExtTCPFastOpenPassiveFail` statistic and ensures old TCP metrics do not contaminate subsequent cases.

## Risks
Failure to delete the namespace could leave temporary state. `set -e` means unexpected command failures abort immediately through cleanup. It assumes `nstat` emits the passive-fail counter name and that local loopback TFO behavior matches the key rotation scenarios.

## Test Signals
Passing output is `all tests done` after all sixteen invocations, with each `TcpExtTCPFastOpenPassiveFail` value equal to zero. Any nonzero counter prints a failure and exits nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_fastopen_backup_key.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_inq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_inq.c

## Purpose
`tcp_inq.c` is a compact example and selftest for `TCP_INQ` ancillary data. It verifies that after a partial receive, the control message reports the remaining bytes in the TCP receive queue.

## Important APIs, Types, And Functions
The file defines `setup_loopback_addr()`, `start_server()`, and `main()`. It uses `TCP_INQ`, `TCP_CM_INQ`, `recvmsg()`, `cmsghdr` parsing, pthreads, loopback sockets, and `SO_REUSEADDR`.

## Control Flow
`main()` parses `-4`, `-6`, and `-p`, starts a listening socket on loopback, launches a server thread, connects a client, enables `TCP_INQ`, and performs a `recvmsg()` for half of an 8192-byte payload. The server accepts, sends exactly 8192 bytes, sleeps for one second to avoid FIN-related overestimation, and closes. The client scans control messages for `SOL_TCP/TCP_CM_INQ` and expects the in-queue value to equal the unsent half of the buffer.

## State, Persistence, And Dependencies
State is transient sockets, one server thread, and heap buffers. No persistent files are written. The test depends on Linux TCP_INQ support, pthreads, IPv4/IPv6 loopback, and control-message delivery from `recvmsg()`.

## Integration Points
This file validates the userspace API contract for TCP receive queue reporting through cmsg data. It is independent of namespace harnesses and can run directly against loopback.

## Risks
The server buffer is allocated but not initialized, which is acceptable because content is irrelevant. The server thread loops forever, but process exit ends it after the client test. The one-second sleep is a timing workaround for FIN overestimation and could be sensitive on very slow systems.

## Test Signals
Passing signal is `PASSED` and exit code zero. Failure signals include missing control message, `MSG_CTRUNC`, a receive length different from 4096, or `inq` not equal to 4096.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_inq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_mmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_mmap.c

## Purpose
`tcp_mmap.c` is a reference and performance selftest for TCP receive zero-copy via `TCP_ZEROCOPY_RECEIVE` and socket `mmap()`. It can run as a server or sender, supports optional sender zerocopy, hashing, pacing, buffer sizing, MSS tuning, and SHA-256 integrity verification.

## Important APIs, Types, And Functions
Major functions are `hash_zone()`, `mmap_large_buffer()`, `tcp_info_get_rcv_mss()`, `child_thread()`, `apply_rcvsnd_buf()`, `setup_sockaddr()`, `do_accept()`, `default_huge_page_size()`, `randomize()`, and `main()`. It uses `struct tcp_zerocopy_receive`, `TCP_ZEROCOPY_RECEIVE`, `SO_ZEROCOPY`, `MSG_ZEROCOPY`, `SO_RCVLOWAT`, `TCP_MAXSEG`, `SO_MAX_PACING_RATE`, OpenSSL EVP SHA-256 APIs, and hugepage or populated anonymous mappings.

## Control Flow
In server mode, `main()` listens and `do_accept()` spawns a detached `child_thread()` per connection. The child maps a large receive buffer, optionally maps the socket for zero-copy receive, polls, calls `getsockopt(TCP_ZEROCOPY_RECEIVE)`, accounts mmaped bytes, reads skip-hint bytes normally, hashes or digests data if requested, and reports throughput and CPU usage. In client mode, `main()` connects, optionally enables sender zerocopy and integrity hashing, then sends a 32 GiB stream from a large buffer, appending a SHA-256 digest when integrity mode is enabled.

## State, Persistence, And Dependencies
State is command-line configuration, heap/mmap buffers, socket mappings, per-thread throughput counters, optional digest state, and socket buffer settings. It depends on Linux TCP zero-copy receive support, OpenSSL, IPv4/IPv6 networking, and sufficient memory or fallback mapping capacity. No persistent files are written.

## Integration Points
This program is both documentation and a stress tool for the TCP mmap receive API. It integrates VM mapping behavior, TCP receive queues, socket options, sender pacing, and optional integrity verification.

## Risks
The default transfer size is very large, so runtime and resource usage are significant. Hugepage mapping may fail and falls back with a warning. `keepflag` is parsed but not functionally used in the visible code. The server loops forever. Integrity mode depends on OpenSSL availability and sends a digest after exactly `FILE_SZ` bytes.

## Test Signals
Useful signals are high mmap percentage when `-z` is enabled, correct SHA-256 when `-i` is enabled, no read or getsockopt errors, and throughput/cpu output showing successful receipt. Failures include mapping failures, connect/listen errors, digest mismatch, or unexpectedly low zero-copy coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_port_share.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_port_share.c

## Purpose
`tcp_port_share.c` tests TCP bind-bucket port-sharing behavior for IPv4 and IPv6. It verifies that a source port blocked by an explicit bind becomes reusable after close, and that an auto-bound connected socket can block reuse after `connect(AF_UNSPEC)` followed by explicit binding.

## Important APIs, Types, And Functions
The file uses the kselftest harness fixture API: `FIXTURE`, `FIXTURE_VARIANT`, `FIXTURE_SETUP`, `TEST_F`, and `TEST_HARNESS_MAIN`. Helpers include `disconnect()`, `getsockname_port()`, and `make_inet_addr()`. It uses `IP_BIND_ADDRESS_NO_PORT`, `SO_REUSEADDR`, `connect(AF_UNSPEC)`, loopback namespace setup, and `/proc/sys/net/ipv4/ip_local_port_range`.

## Control Flow
Fixture setup unshares a new network namespace, brings loopback up, adds IPv6 addresses, and constrains the ephemeral port range to one port. The first test connects from one source address, binds another socket to a different address on that same source port to block reuse, verifies a second connect fails with `EADDRNOTAVAIL`, closes the blocker, and verifies the second connect succeeds. The second test disconnects the first connected socket, rebinds it to a blocking address, triggers bind-bucket state update with another bind/close, and verifies a second source cannot reuse the port.

## State, Persistence, And Dependencies
State is contained in an unshared network namespace and includes loopback addresses, proc port-range settings, and sockets. The setup writes a namespace-local proc sysctl. It depends on kselftest harness support, `ip` command availability through `system()`, and IPv4/IPv6 loopback semantics.

## Integration Points
The test targets the kernel bind bucket and port-address sharing logic used by TCP ephemeral source port selection. It specifically covers `IP_BIND_ADDRESS_NO_PORT` and disconnect/rebind transitions.

## Risks
The fixture writes only the IPv4 local port range but tests IPv6 too, relying on shared port-range behavior. Failed assertions may leave sockets open until process exit. The use of `system("ip ...")` requires the `ip` tool and sufficient privileges.

## Test Signals
Passing signals are both fixture variants passing both tests, expected `EADDRNOTAVAIL` while blocked, successful reconnect after closing the blocker in the first case, and continued failure after disconnect/rebind in the second case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_port_share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bpf.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bpf.sh

## Purpose
`test_bpf.sh` is a minimal kselftest wrapper for the `test_bpf` kernel module. Loading the module runs the module's internal BPF tests; unloading cleans it up.

## Important APIs, Types, And Functions
The script has no functions. It calls `/sbin/modprobe -q test_bpf` and, on success, `/sbin/modprobe -q -r test_bpf`.

## Control Flow
If loading `test_bpf` succeeds, the script immediately removes it, prints `test_bpf: ok`, and exits zero. If loading fails, it prints `test_bpf: [FAIL]` and exits `1`.

## State, Persistence, And Dependencies
State is kernel module load state. The script depends on root/module-loading permissions, `/sbin/modprobe`, and a kernel build that provides the `test_bpf` module. No files are written.

## Integration Points
This is a bridge between kselftest shell execution and tests implemented inside a kernel module. It relies on module init returning success only when the module's BPF test suite passes.

## Risks
A missing module, disabled module loading, lockdown policy, or insufficient privileges all look like test failure rather than skip. If module unload fails silently, the script still reports success because removal is quiet and unchecked after a successful load.

## Test Signals
The only passing signal is successful module load followed by printed `test_bpf: ok`. Failure signal is failed `modprobe test_bpf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bpf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bridge_backup_port.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bridge_backup_port.sh

## Purpose
`test_bridge_backup_port.sh` validates Linux bridge backup port and backup nexthop ID behavior for VXLAN-backed VTEP-style topologies. It verifies failover forwarding, backup nexthop encapsulation choice, invalid nexthop handling, bidirectional ping, and churn resilience.

## Important APIs, Types, And Functions
Setup functions include `setup_topo_ns()`, `setup_topo()`, `setup_sw_common()`, `setup_sw1()`, `setup_sw2()`, `setup()`, and `cleanup()`. Test functions are `backup_port()`, `backup_nhid()`, `backup_nhid_invalid()`, `backup_nhid_ping()`, `backup_nhid_add_del_loop()`, and `backup_nhid_torture()`. Utility functions include `log_test()`, `run_cmd()`, `tc_check_packets()`, and `bridge_link_check()`.

## Control Flow
The script creates two namespaces connected by a veth underlay, each with a VLAN-aware bridge, dummy access port `swp1`, VXLAN port `vx0`, bridge VLAN 10, and underlay routes. Tests install static FDB entries, tc flower counters, and optional FDB nexthop groups. They send synthetic packets with `mausezahn`, toggle carrier or administrative state on `swp1`, and inspect egress/ingress packet counters to confirm traffic uses `swp1`, `vx0`, a VXLAN FDB entry, or a backup nexthop as expected. The torture test continuously deletes/replaces a nexthop group while sending traffic for 30 seconds.

## State, Persistence, And Dependencies
State is temporary namespaces, bridge/vxlan/veth/dummy devices, nexthop objects, FDB entries, tc qdiscs/filters, and packet counters. It depends on root, `ip`, `bridge`, `tc`, `mausezahn`, `jq`, and iproute2 support for `backup_nhid`. Cleanup removes the namespaces.

## Integration Points
The test links bridge forwarding, link state, VXLAN external mode, FDB nexthops, tc counter visibility, and nexthop object lifecycle. It directly exercises bridge link attributes `backup_port`, `nobackup_port`, and `backup_nhid`.

## Risks
Packet counter expectations are exact and can be affected by stray packets unless the topology is isolated. The invalid-nexthop test relies on VXLAN tx drop counters changing by one. The torture test is success-by-no-crash and has a fixed 30-second runtime. Tool support checks are essential because older iproute2 lacks required attributes.

## Test Signals
Passing signals include expected forwarding counters on `swp1`/`vx0`, backup nexthop ingress counters on the peer, tx-drop increments for invalid nexthops, ping success only while backup nhid is configured, and no crash during nexthop add/delete churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bridge_backup_port.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bridge_neigh_suppress.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bridge_neigh_suppress.sh

## Purpose
`test_bridge_neigh_suppress.sh` validates bridge neighbor suppression on VXLAN ports. It covers ARP and IPv6 Neighbor Solicitation suppression, unicast neighbor solicitation/reply behavior, and per-port versus per-VLAN suppression controls across two VLANs.

## Important APIs, Types, And Functions
Setup functions include `setup_topo_ns()`, `setup_topo()`, `setup_host_common()`, `setup_h1()`, `setup_h2()`, `setup_sw_common()`, `setup_sw1()`, `setup_sw2()`, `setup()`, and `cleanup()`. Test functions include `neigh_suppress_arp()`, `neigh_suppress_uc_arp()`, `neigh_suppress_ns()`, `neigh_suppress_uc_ns()`, `neigh_vlan_suppress_arp()`, and `neigh_vlan_suppress_ns()`, with common helpers for each protocol. `icmpv6_header_get()` builds a raw NS payload for mausezahn.

## Control Flow
The topology creates host namespaces `h1`/`h2`, switch namespaces `sw1`/`sw2`, VLAN subinterfaces 10 and 20, VLAN-aware bridges, VXLAN ports with tunnel mappings, and static all-zero VXLAN FDB entries. Tests install tc flower counters on VXLAN egress or host ingress/egress, run `arping`, `ndisc6`, or raw `mausezahn` traffic, toggle `neigh_suppress` and `neigh_vlan_suppress`, install bridge FDB and neighbor entries, and verify whether requests leave the VXLAN port.

## State, Persistence, And Dependencies
State is temporary namespaces, veths, VLAN subinterfaces, bridges, VXLAN devices, bridge FDB entries, neighbor table entries, tc filters, and host link states. The script depends on root, `ip`, `bridge`, `tc`, `arping`, `ndisc6`, `jq`, `mausezahn`, and iproute2 support for `neigh_vlan_suppress`.

## Integration Points
The test exercises bridge neighbor suppression decisions at the intersection of L2 FDB lookup, L3 neighbor entries on SVI interfaces, VXLAN tunnel VLAN mapping, and per-port/per-VLAN bridge attributes.

## Risks
Exact packet counter checks are sensitive to unexpected background traffic. The IPv6 raw packet helper hardcodes checksums and target address bytes for the test prefixes. Several paths depend on host link down/up behavior and delayed neighbor discovery timing. Tool version checks are required for newer bridge attributes.

## Test Signals
Passing signals are expected `arping`/`ndisc6` results, tc counters not increasing when suppression should occur, counters increasing when suppression is disabled or not configured for that VLAN, successful unicast ARP/NS reply delivery, and correct independence between VLAN 10 and VLAN 20 suppression state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bridge_neigh_suppress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_ingress_egress_chaining.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_ingress_egress_chaining.sh

## Purpose
`test_ingress_egress_chaining.sh` validates tc mirred chaining between ingress and egress paths. It sets up two veth pairs and confirms TCP benchmark traffic can traverse an ingress-to-egress redirection chain plus an egress-to-ingress shortcut.

## Important APIs, Types, And Functions
Functions are `fail()`, `cleanup()`, `config()`, and `test_run()`. The script uses `tc qdisc add ingress`, `tc qdisc add clsact`, flower filters, `act_mirred` redirect actions, `ip netns`, and the `udpgso_bench_rx`/`udpgso_bench_tx` test binaries.

## Control Flow
The script checks root privileges and required modules `act_mirred`, `cls_flower`, and `sch_ingress`, then creates randomized namespace and device names. `config()` creates two veth pairs, places one peer in a namespace, assigns addresses, brings links up, installs reciprocal ingress redirects between the two host-side veths, and installs an egress redirect from `peer1` back to `veth1`. `test_run()` starts the receiver and runs a namespaced sender using TCP mode toward `peer1`.

## State, Persistence, And Dependencies
State is temporary namespace, veth devices, tc qdiscs/filters, and benchmark processes. Cleanup kills `udpgso_bench_rx`, deletes veths, and removes the namespace. Dependencies include root, kernel tc modules, `ip`, `tc`, and compiled benchmark binaries.

## Integration Points
The test covers interaction between tc ingress qdisc, clsact egress hook, mirred redirect semantics, and veth delivery. It is intended to catch regressions in chaining an ingress redirect into an egress redirect.

## Risks
`killall -q -9 udpgso_bench_rx` is broad and can kill unrelated same-named processes. Module skip messages report only `act_mirred` even when a different module is missing. Random names reduce collision risk but do not eliminate it completely.

## Test Signals
Passing signal is successful completion of `udpgso_bench_tx -t` within the timeout and printed `Test passed`. Failure signal is sender timeout/error or setup command failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_ingress_egress_chaining.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_neigh.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_neigh.sh

## Purpose
`test_neigh.sh` validates the neighbor table `extern_valid` flag for IPv4 ARP and IPv6 NDISC entries. It checks allowed and rejected flag combinations, state transitions, interface events, and garbage collection survival.

## Important APIs, Types, And Functions
Functions include `run_cmd()`, `setup()`, `exit_cleanup_all()`, `extern_valid_common()`, `extern_valid_ipv4()`, and `extern_valid_ipv6()`. It uses shared `lib.sh` helpers such as `setup_ns`, `cleanup_all_ns`, `check_err`, `check_fail`, and `log_test`. It relies on `ip neigh`, `ip ntable`, `tc`, and `jq`.

## Control Flow
For each address family, the script creates two namespaces connected by a veth, assigns IPv4 and IPv6 addresses, and runs the same `extern_valid_common()` sequence. It adds valid entries, rejects invalid states and incompatible `use` combinations, toggles the flag via replace, combines an existing extern-valid entry with `managed`, tests removal on administrative down and survival across carrier down, forces reachable and stale transitions, then manipulates global neighbor table thresholds to verify survival through forced and periodic garbage collection.

## State, Persistence, And Dependencies
State is temporary namespaces, neighbor entries, tc drop filter on the peer, and global neighbor table threshold/base-reachable settings in the initial namespace. The script saves and restores the modified ntable values. It depends on root, `ip` support for `extern_valid`, `jq`, and tc.

## Integration Points
The test exercises neighbor UAPI validation, neighbor state machine transitions, probing counters, interface event cleanup, and GC protection semantics for externally validated entries.

## Risks
The forced and periodic GC tests modify global thresholds, so interruption before restoration can affect the host. Timing depends on `delay_probe`, retransmit, and GC intervals. The script must run in isolation from other tests using neighbor table thresholds. The final file as read ends after the loop without an explicit summary `exit`, relying on lib status behavior and trap cleanup.

## Test Signals
Passing signals are logged success for add, invalid add/replace rejection, flag replace behavior, managed coexistence, interface-down flush, carrier-down retention, reachable/stale transitions retaining `extern_valid`, nonzero probe count during failed resolution, and survival of extern-valid entries while ordinary stale entries are collected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_neigh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_so_rcv.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_so_rcv.sh

## Purpose
`test_so_rcv.sh` is a shell harness for receive-side socket control-message tests. It validates `SO_RCVPRIORITY` and `SO_RCVMARK` delivery for IPv4 and IPv6 using companion listener and sender binaries.

## Important APIs, Types, And Functions
The script defines `check_result()` and `cleanup()`. It uses `setup_ns` and `cleanup_ns` from `lib.sh`, arrays for hosts and test argument mappings, and executes `./so_rcv_listener` and `./cmsg_sender`.

## Control Flow
The script creates one temporary namespace, then loops over `127.0.0.1` and `::1` and over two tests: `SO_RCVPRIORITY` with `-P 2` and `SO_RCVMARK` with `-M 3`. For each case it starts the listener in the namespace, waits briefly, runs the sender with matching arguments, waits for the listener, records success or failure, and prints per-case status. At the end it exits kselftest fail if any case failed, otherwise pass.

## State, Persistence, And Dependencies
State is the temporary namespace, the background listener PID, and counters `TOTAL_TESTS`/`FAILED_TESTS`. It depends on root namespace operations through `lib.sh`, the two compiled helper binaries, and support for the receive socket options under test.

## Integration Points
This harness pairs sender-generated control metadata with listener-side cmsg validation. It runs both address families in the same isolated namespace to avoid host socket state.

## Risks
The fixed `sleep 0.5` for listener readiness can be flaky on overloaded systems. Associative array iteration order is unspecified, though tests are independent. If the sender fails, the script kills and waits for the listener before continuing.

## Test Signals
Passing signal is `OK - All 4 tests passed` and `KSFT_PASS`. Failure signal is any sender failure or nonzero listener exit, reported as `FAIL - N/4 tests failed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_so_rcv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_fdb_changelink.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_fdb_changelink.sh

## Purpose
`test_vxlan_fdb_changelink.sh` verifies VXLAN FDB behavior across `ip link set` changes. It checks that multiple default remote FDB entries survive changing the VXLAN remote and that multicast group membership updates correctly when the remote changes between multicast and unicast.

## Important APIs, Types, And Functions
Functions include `check_remotes()`, `test_set_remote()`, `fmt_remote()`, `change_remote()`, `check_membership()`, and `test_change_mc_remote()`. It uses `lib.sh` helpers such as `adf_ip_link_add`, `adf_ip_link_set_up`, `check_err`, `check_err_fail`, `check_command`, `tests_run`, and deferred cleanup.

## Control Flow
`test_set_remote()` creates a VXLAN device, appends two all-zero FDB default remote entries, changes the device remote to one of them with `ip link set`, and checks that two default remotes remain. `test_change_mc_remote()` creates a veth underlay and a VXLAN with multicast remote `224.1.1.1`, checks netstat group membership, changes the remote to `224.1.1.2`, checks membership moved, then changes to unicast `192.0.2.2` and checks no multicast membership remains.

## State, Persistence, And Dependencies
State is temporary links, VXLAN devices, FDB entries, multicast memberships, and deferred cleanup scopes from `lib.sh`. It depends on `ip`, `bridge`, and `netstat` for the multicast test. No persistent files are written.

## Integration Points
The test exercises VXLAN changelink paths and their effect on bridge FDB default remotes and IGMP/multicast group join/leave state on the underlay device.

## Risks
`check_remotes()` counts all-zero FDB rows and can be confused by unexpected entries on a non-isolated device name, though the helper-created device should be scoped. Multicast membership parsing depends on `netstat -n --groups` output format. The multicast test skips if `netstat` is unavailable.

## Test Signals
Passing signals are two default-remotes after append and after link-set, membership in only the configured multicast group after creation and MC-to-MC change, and no listed test groups after MC-to-unicast change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_fdb_changelink.sh -->
