# Research Group: subset-b-009353

This grouped report covers the strace network, netlink, nfnetlink, and nlattr test sources assigned to `subset-b-009353`. Each file section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-sockaddr.c -->
# sources/test-tools/strace/tests/net-sockaddr.c

Purpose: exercises strace decoding of many `struct sockaddr` variants by issuing `connect(-1, sockaddr, len)` calls that reliably fail with `EBADF` while still forcing strace to inspect the user-supplied address bytes. It covers normal, truncated, oversized, abstract, and unknown address forms.

Important APIs, types, and helpers: `connect`, `sockaddr_un`, `sockaddr_in`, `sockaddr_in6`, optional `sockaddr_ipx`, AX.25 `full_sockaddr_ax25`, `sockaddr_x25`, `sockaddr_nl`, `sockaddr_ll`, optional Bluetooth HCI/SCO/RFCOMM/L2CAP structures, `TAIL_ALLOC_OBJECT_*`, `tail_memdup`, `midtail_alloc`, `fill_memory`, `pidns_print_leader`, `pidns_pid2str`, `ifindex_lo`, and endian/network helpers such as `htons`, `htonl`, `inet_addr`, and `inet_pton`.

Control flow: `main` initializes pid namespace testing, then calls per-family check functions. Each check prepares one or more address objects, varies length or field values, performs a failing `connect`, and prints the expected decoded trace line. UNIX tests cover pathname, abstract namespace, shifted pointers, and excessive/short lengths; IPv4/IPv6 tests cover full decoding and `sa_data` fallbacks; AX.25/X.25/PACKET/NETLINK/Bluetooth tests verify family-specific symbolic decoding and raw fallback behavior.

State and persistence: the test has no persistent state. It mutates stack/tail-allocated address buffers in place and prints expectations. It depends on the current pid and loopback ifindex for pid namespace and interface-name rendering, and optional compile-time feature macros gate IPX and Bluetooth cases.

Dependencies and integration points: integrates with the strace test harness through `tests.h`, `pidns.h`, `netlink.h`, allocation helpers, `RVAL_EBADF`, and generated xlat tables in strace itself. It depends on Linux UAPI headers for network families and on `/proc`/namespace support indirectly for pid and interface annotations.

Risks and edge cases: this file intentionally probes decoder boundaries: short reads, user pointers shifted near allocation tails, non-NUL UNIX names, abstract UNIX names, invalid family numbers, optional kernel header differences, and symbolic loopback rendering. Regressions are likely if sockaddr length validation, family dispatch, pid namespace translation, or optional field guards change.

Test signals: success is the exact stdout stream ending in `+++ exited with 0 +++`; the syscalls should fail consistently with `EBADF`, so the signal is decoder output rather than kernel networking success.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-sockaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-tpacket_req.c -->
# sources/test-tools/strace/tests/net-tpacket_req.c

Purpose: verifies `setsockopt` decoding for `SOL_PACKET` ring setup options that carry `struct tpacket_req`, especially `PACKET_RX_RING` and, when available, `PACKET_TX_RING`.

Important APIs, types, and helpers: `setsockopt`, `SOL_PACKET`, `PACKET_RX_RING`, optional `PACKET_TX_RING`, `struct tpacket_req`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `sprintrc`, and `ARG_STR`.

Control flow: `main` calls `test_tpacket_req` for each supported option. The helper first sends an unknown option with `NULL`, then a normal `struct tpacket_req`, then an oversized optlen that should make strace print the raw pointer rather than a structured object.

State and persistence: only the global `errstr` stores the formatted syscall result between the syscall wrapper and the expected-output print. No filesystem or socket state is persisted because fd `-1` guarantees failure after argument decoding.

Dependencies and integration points: relies on Linux `if_packet.h` option definitions and the strace decoder for packet socket options. The test harness provides tail allocation and symbolic return formatting.

Risks and edge cases: the key boundary is optlen equality versus optlen larger than `sizeof(struct tpacket_req)`. Kernel/header availability of `PACKET_TX_RING` changes coverage at compile time.

Test signals: expected output should show unknown option as `PACKET_???`, normal ring fields by name, and oversized optval as `%p`, ending with `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-tpacket_req.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-tpacket_stats-success.c -->
# sources/test-tools/strace/tests/net-tpacket_stats-success.c

Purpose: creates an injected-success variant of `net-tpacket_stats.c` by defining `INJECT_RETVAL 42` before including the shared source. It checks the same decoder paths when strace syscall injection makes `getsockopt` appear successful.

Important APIs, types, and helpers: inherits all code from `net-tpacket_stats.c`, particularly `getsockopt`, `PACKET_STATISTICS`, `struct tp_stats`, and `sprintrc`; adds the `INJECT_RETVAL` compile-time control.

Control flow: there is no local function body. The included file compiles with an extra return-value assertion and appends `(INJECTED)` to expected return text when the injected return value matches.

State and persistence: no local state. The included code uses stack/tail-allocated optlen and stats buffers; this wrapper only changes compile-time behavior.

Dependencies and integration points: integrated through the strace test suite’s injection machinery. The source must be built in a test configuration where syscall injection causes the expected synthetic return value.

Risks and edge cases: if the included implementation changes the injection contract or the expected return value, this thin wrapper will fail. It also shares all optlen boundary risks from the base file.

Test signals: output mirrors `net-tpacket_stats.c` but successful calls should include injected return formatting and the program must fail early if the observed return differs from `42`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-tpacket_stats-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-tpacket_stats.c -->
# sources/test-tools/strace/tests/net-tpacket_stats.c

Purpose: validates `getsockopt(SOL_PACKET, PACKET_STATISTICS)` decoding for packet socket statistics, including partial optlen reads and complete `tp_packets`, `tp_drops`, and `tp_freeze_q_cnt` fields.

Important APIs, types, and helpers: `getsockopt`, `struct tp_stats`, `socklen_t`, `offsetof`, `offsetofend`, `PRINT_FIELD_U`, `print_quoted_hex`, `TAIL_ALLOC_OBJECT_CONST_PTR`, and optional `INJECT_RETVAL` behavior.

Control flow: `main` allocates a stats buffer and repeatedly sets `optlen` to full, zero, truncated-at-field, exact-field, and oversized lengths. `get_tpacket_stats` performs the syscall, records/validates the return, then prints either the raw pointer, a partially quoted field, or an incrementally decoded struct based on the original optlen.

State and persistence: `errstr` is the only global state. The kernel call uses fd `-1`, so no persistent socket state is created. The function mutates local optlen variables to simulate the decoder’s view of returned lengths.

Dependencies and integration points: depends on packet socket UAPI definitions and the strace test formatting helpers. The file is also included by `net-tpacket_stats-success.c` to exercise injected success.

Risks and edge cases: most risk sits in off-by-one optlen handling around field boundaries and in differentiating failed calls from injected success. A decoder change that prints partial integers incorrectly will be caught here.

Test signals: expected output enumerates every optlen boundary and ends with `+++ exited with 0 +++`; in injected builds each syscall result must match `INJECT_RETVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-tpacket_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-y-unix.c -->
# sources/test-tools/strace/tests/net-y-unix.c

Purpose: tests `strace -y` style file descriptor annotation for live UNIX stream sockets. It verifies socket inode rendering while performing a real bind/listen/connect/accept/send/receive sequence.

Important APIs, types, and helpers: `socket(AF_UNIX, SOCK_STREAM)`, `bind`, `listen`, `getsockopt(SO_PASSCRED)`, `getsockname`, `connect`, `accept4`, `getpeername`, `setsockopt`, `sendto`, `recvfrom`, `close`, `unlink`, `inode_of_sockfd`, `tail_memdup`, and `TAIL_ALLOC_OBJECT_CONST_PTR`.

Control flow: the test creates a pathname UNIX listener, prints socket fd inode annotations, accepts one normal connection, sends data, closes both ends, then repeats with `SO_PASSCRED` enabled to trigger abstract-peer behavior in accepted address reporting. It cleans up the socket pathname and prints every syscall expectation.

State and persistence: creates a temporary `net-y-unix.socket` filesystem socket and removes it at the end. Runtime state includes three socket descriptors and their inode values; no state should remain after `unlink` and `close`.

Dependencies and integration points: requires `/proc/self/fd/` for descriptor-to-inode annotation, UNIX domain sockets, and strace fd path decoding. It integrates with the broader `-y` tests by expecting `<socket:[inode]>` annotations rather than full endpoint details.

Risks and edge cases: stale socket path cleanup, accepted socket address lengths, abstract auto-bound client names, and platform differences in UNIX credential behavior can affect output. The test skips only if required proc/socket operations are unavailable.

Test signals: expected output includes fd annotations as `socket:[inode]`, successful UNIX socket lifecycle calls, a data transfer, cleanup, and `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-y-unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-yy-inet.c -->
# sources/test-tools/strace/tests/net-yy-inet.c

Purpose: provides the parameterized IPv4 implementation for `strace -yy` endpoint annotation tests. It builds a loopback TCP client/server pair and verifies that descriptors are printed with local and peer addresses/ports.

Important APIs, types, and helpers: `socket`, `bind`, `getsockname`, `listen`, `connect`, `accept4`, `getpeername`, `getsockopt(SO_SNDBUF)`, `setsockopt(SOL_TCP, TCP_MAXSEG)`, `sendto`, `recvfrom`, `close`, `inet_ntop`-style socket address fields, `inode_of_sockfd`, and macro parameters such as `ADDR_FAMILY`, `SOCKADDR_TYPE`, `LOOPBACK`, `TCP_STR`, and `INPORT`.

Control flow: the file creates a loopback listener with port zero, obtains the assigned port, connects a second socket, accepts the connection, verifies names/options, sends and receives a short payload, and closes descriptors. Macro definitions make the same body reusable for IPv6 through `net-yy-inet6.c`.

State and persistence: all state is ephemeral TCP socket state on loopback. The assigned listener/client ports and inode-derived fd annotations are runtime values used in expected output; no filesystem state persists.

Dependencies and integration points: depends on loopback networking, `/proc/self/fd/`, TCP socket support, and strace `-yy` formatting. The file is directly included by the IPv6 wrapper after redefining address-family macros.

Risks and edge cases: loopback availability, kernel option defaults, port allocation, and macro correctness are important. The test avoids fixed ports but still relies on deterministic local endpoint rendering.

Test signals: expected output shows `<TCP:[127.0.0.1:port]>` and connected `<TCP:[src->dst]>` annotations, successful option calls, payload transfer, clean closes, and the exit marker.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-yy-inet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-yy-inet6.c -->
# sources/test-tools/strace/tests/net-yy-inet6.c

Purpose: builds the IPv6 version of the `net-yy-inet.c` test by defining address-family, field, loopback, and formatting macros before including the shared implementation.

Important APIs, types, and helpers: inherits the TCP lifecycle from `net-yy-inet.c` with `AF_INET6`, `struct sockaddr_in6`, `IN6ADDR_LOOPBACK_INIT`, `sin6_port`, `TCPv6`, and IPv6 address formatting fields.

Control flow: local source has no runtime body beyond macro definitions. The included implementation binds `::1`, connects a TCPv6 client, accepts, transfers data, and checks `-yy` fd endpoint output.

State and persistence: uses only ephemeral IPv6 loopback sockets and dynamic ports. No files or long-lived kernel objects are persisted.

Dependencies and integration points: depends on IPv6 loopback support, TCPv6, `/proc/self/fd/`, and the shared test body’s macro contract. It is sensitive to systems where IPv6 is disabled.

Risks and edge cases: macro mismatch would corrupt expected field names; missing IPv6 support should produce a skip/failure depending on harness behavior. Scope-id formatting must remain stable as `SA_FIELDS` is set to `sin6_scope_id=0`.

Test signals: same as the IPv4 shared test, but annotations and sockaddr text should use `[::1]`, `AF_INET6`, `TCPv6`, and IPv6-specific fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-yy-inet6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-yy-netlink.c -->
# sources/test-tools/strace/tests/net-yy-netlink.c

Purpose: checks `-yy`/socket descriptor annotation for netlink sockets, especially transition from unbound socket inode display to protocol/pid-aware `NETLINK:[SOCK_DIAG:pid]` display.

Important APIs, types, and helpers: `socket(AF_NETLINK, SOCK_RAW, NETLINK_SOCK_DIAG)`, `bind`, `getsockname`, `close`, `struct sockaddr_nl`, `inode_of_sockfd`, `tail_memdup`, and configurable `PRINT_SOCK` formatting macros.

Control flow: `main` creates a netlink socket, records the inode when annotation is enabled, binds the socket to the process pid, calls `getsockname`, closes it, and prints expected fd annotations for unbound and bound states.

State and persistence: socket state is transient. The bind uses `getpid()` as `nl_pid`; no filesystem or persistent kernel state is left after close.

Dependencies and integration points: requires `/proc/self/fd/`, `NETLINK_SOCK_DIAG`, Linux netlink headers, and strace fd annotation modes. `PRINT_SOCK` allows the same logic to support different expected annotation levels.

Risks and edge cases: pid namespace translation, kernel netlink pid assignment behavior, and annotation mode changes can alter output. Binding may fail on systems lacking the protocol, leading to skip.

Test signals: output should show socket creation, bind, getsockname, close, and the descriptor annotation selected by `PRINT_SOCK`, followed by the normal exit marker.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-yy-netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/net-yy-unix.c -->
# sources/test-tools/strace/tests/net-yy-unix.c

Purpose: tests rich `strace -yy` UNIX socket endpoint annotations, including socket protocol names, inode pairs, pathname endpoints, and auto-bound abstract names.

Important APIs, types, and helpers: `socket(AF_UNIX)`, optional `getxattr("system.sockprotoname")`, `bind`, `listen`, `getsockopt`, `getsockname`, `connect`, `accept4`, `getpeername`, `setsockopt(SO_PASSCRED)`, `sendto`, `recvfrom`, `close`, `unlink`, `inode_of_sockfd`, `xasprintf`, and tail allocation helpers.

Control flow: creates a pathname listener, discovers a socket protocol label, accepts and transfers through a first client, then creates a second client with `SO_PASSCRED` to exercise abstract peer names. Every lifecycle call is mirrored by a precise expected-output `printf`.

State and persistence: creates `net-yy-unix.socket` and removes it at the end. Descriptor state and inode relationships are runtime-only. Optional xattr lookup allocates and frees a proc fd path.

Dependencies and integration points: requires `/proc/self/fd/`, UNIX stream sockets, optional extended attributes, and the strace `-yy` fd path machinery. It is a higher-detail counterpart to `net-y-unix.c`.

Risks and edge cases: output depends on kernel support for `system.sockprotoname`, abstract auto-bind names, and stable inode relationship rendering. Cleanup is important to avoid stale socket files between runs.

Test signals: expected traces include `<UNIX:[inode,"path"]>`, connected inode arrows, optional abstract `@"..."` annotations, successful data transfers, cleanup, and `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/net-yy-unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_audit--pidns-translation.c -->
# sources/test-tools/strace/tests/netlink_audit--pidns-translation.c

Purpose: compiles the audit netlink test with pid namespace translation enabled by defining `PIDNS_TRANSLATION` before including `netlink_audit.c`.

Important APIs, types, and helpers: inherits `sendto`, `struct nlmsghdr`, `AUDIT_GET`, `NETLINK_AUDIT`, `pidns_print_leader`, `pidns_pid2str`, and `create_nl_socket` from the included file.

Control flow: this wrapper has no independent runtime control flow. The included implementation initializes pid namespace testing, sends an audit netlink header whose `nlmsg_pid` is `getpid()`, and prints the translated pid suffix.

State and persistence: no persistent state beyond the temporary netlink socket. The compile-time define changes how pid namespace annotations are expected.

Dependencies and integration points: integrates with the pid namespace variant of strace tests. It depends on the base audit netlink decoder test and the harness support for running pid namespace translation checks.

Risks and edge cases: failures can arise from pid namespace support, base file changes, or mismatch between host and translated pid output.

Test signals: the output should match the base audit test with pid namespace translation details included for `nlmsg_pid`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_audit--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_audit.c -->
# sources/test-tools/strace/tests/netlink_audit.c

Purpose: verifies decoding of audit netlink message headers, specifically `AUDIT_GET` with request flags and pid namespace-aware `nlmsg_pid` rendering.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_AUDIT)`, `sendto`, `struct nlmsghdr`, `AUDIT_GET`, `NLM_F_REQUEST`, `getpid`, `PIDNS_TEST_INIT`, `pidns_print_leader`, and `pidns_pid2str`.

Control flow: `main` skips if `/proc/self/fd/` is unavailable, creates an audit netlink socket, then `test_nlmsg_type` sends one header-only audit request and prints the decoded netlink header.

State and persistence: the only state is an open netlink fd during the test and the current pid value embedded in the message header. No durable audit configuration is changed because the payload is just a test request sent nonblocking.

Dependencies and integration points: depends on Linux audit netlink headers and strace’s pid namespace test support. The file is included by the pidns translation wrapper for alternate expected output.

Risks and edge cases: audit netlink availability and permission behavior may vary, but the expected result is captured via `sprintrc`. Pid rendering must stay synchronized with namespace helper expectations.

Test signals: output should show `nlmsg_type=AUDIT_GET`, `nlmsg_flags=NLM_F_REQUEST`, the pid field, and the exit marker.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_crypto.c -->
# sources/test-tools/strace/tests/netlink_crypto.c

Purpose: tests `NETLINK_CRYPTO` decoding for crypto netlink message types, flags, and `struct crypto_user_alg` payloads.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_CRYPTO)`, `sendto`, `struct nlmsghdr`, `CRYPTO_MSG_*`, `struct crypto_user_alg`, `TEST_NETLINK_OBJECT_EX`, `TEST_NETLINK_`, `midtail_alloc`, `fill_memory_ex`, `PRINT_FIELD_X`, and `PRINT_FIELD_U`.

Control flow: `main` creates a crypto netlink socket, checks type decoding with `CRYPTO_MSG_NEWALG`, checks flag decoding for get/new/del/update operations, sends structured `crypto_user_alg` payloads with short and long string fields, and finally sends an unknown message type with raw bytes.

State and persistence: no persistent crypto state is intended. All messages are test buffers sent nonblocking; fd and memory buffers are transient.

Dependencies and integration points: uses Linux `cryptouser.h`, strace netlink test macros, and the `netlink_protocols` xlat macros for symbolic protocol names.

Risks and edge cases: string truncation with fixed-size `cru_*` arrays, unknown flag combinations, and unknown message types are deliberate edge cases. Header availability can affect constants.

Test signals: output must show symbolic crypto message names, correct flag rendering or `NLM_F_???` fallback, structured `crypto_user_alg` fields, raw unknown payload, and normal exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_generic.c -->
# sources/test-tools/strace/tests/netlink_generic.c

Purpose: verifies generic netlink (`NETLINK_GENERIC`) decoding for basic `genlmsghdr` messages and selected generic netlink attributes.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_GENERIC)`, `struct genlmsghdr`, `GENL_ID_CTRL`, `TEST_NETLINK_OBJECT_EX_`, `TEST_NETLINK`, `TEST_NLATTR_`, `xasprintf`, `midtail_alloc`, and `CTRL_ATTR_*` constants from `linux/genetlink.h`.

Control flow: the test sends a header for `CTRL_CMD_GETFAMILY`, exercises unknown generic-netlink commands, uses initialized header callbacks for nlattr tests, checks unknown attributes and short/string attribute rendering, then emits an `NLMSG_DONE` test.

State and persistence: all state is synthetic message memory and a temporary generic netlink socket. There is no persistent generic netlink family modification.

Dependencies and integration points: relies on `test_netlink.h` and `test_nlattr.h` macros to construct aligned netlink messages and expected output. It checks strace’s generic netlink control-family xlat behavior.

Risks and edge cases: malformed lengths, unknown attribute ids, abbreviated long strings, and callback consistency between `init_genlmsghdr` and `print_genlmsghdr` are the relevant failure surfaces.

Test signals: output should decode `nlctrl`, generic netlink header fields, `CTRL_ATTR_*` names, raw unknown attributes, and `NLMSG_DONE`, ending with `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_inet_diag.c -->
# sources/test-tools/strace/tests/netlink_inet_diag.c

Purpose: exercises receive-side decoding for `NETLINK_INET_DIAG` by creating a real TCP listener and reading diagnostic netlink responses.

Important APIs, types, and helpers: `socket(AF_INET, SOCK_STREAM)`, `bind`, `listen`-style setup through fd 0, `socket(AF_NETLINK, SOCK_RAW, NETLINK_INET_DIAG)`, `sendto`/request helpers, `recvfrom`, `struct inet_diag_req_v2`, `struct inet_diag_msg`, `NETLINK_INET_DIAG`, and `inet_diag` UAPI headers.

Control flow: setup creates an IPv4 loopback TCP socket, binds it, creates a netlink inet diag socket, sends a diagnostic request, then receives and prints decoded response messages, including normal and truncated cases handled by helper functions.

State and persistence: runtime state is a loopback TCP socket and a netlink diagnostic socket. No filesystem or durable network configuration is modified.

Dependencies and integration points: depends on inet diag kernel support, loopback TCP, and strace’s netlink receive decoder. It complements send-side `netlink_sock_diag.c` by validating responses from the kernel.

Risks and edge cases: kernel response contents can vary with inet diag implementation, permissions, or socket state. The test uses controlled local sockets to reduce nondeterminism, but receive buffer length and errno handling remain important.

Test signals: expected traces include socket setup, netlink request/response decoding for inet diag structures, and successful exit or skip when required protocols are unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_inet_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_kobject_uevent.c -->
# sources/test-tools/strace/tests/netlink_kobject_uevent.c

Purpose: tests decoding of `NETLINK_KOBJECT_UEVENT` payloads, including libudev-style monitor frames, kernel uevent strings, concatenated records, and malformed/truncated data.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_KOBJECT_UEVENT)`, `sendto`, `sprintrc`, `struct udev_monitor_netlink_header` from `netlink_kobject_uevent.h`, `htonl`, `print_quoted_string`, and buffer-filling helpers.

Control flow: helper `send_uevent` sends arbitrary buffers and captures the result. Test functions print expected decoding for monitor headers with magic/properties, arrays of environment strings, plain quoted strings, empty input, and raw hexadecimal fallback.

State and persistence: all data is synthetic user-space buffers sent to a transient netlink socket. No udev or kernel device state is changed.

Dependencies and integration points: uses the strace kobject uevent decoder and local header definitions for monitor metadata. It exercises both structured and unstructured payload branches.

Risks and edge cases: NUL-separated string parsing, network-endian header fields, short buffers, embedded empty strings, and fallback from structured to raw printing are primary risks.

Test signals: expected output should show `sendto` payloads as decoded uevent objects where possible and quoted/raw bytes otherwise, with stable syscall return formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_kobject_uevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_netfilter.c -->
# sources/test-tools/strace/tests/netlink_netfilter.c

Purpose: validates broad `NETLINK_NETFILTER` decoding for base nfnetlink batch messages, netfilter subsystem identifiers, nf_tables payloads, and unknown data.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_NETFILTER)`, `sendto`, `struct nlmsghdr`, `struct nfgenmsg`, `struct nfnetlink_msg`, `NFNL_MSG_BATCH_*`, `NFNL_SUBSYS_*`, `NFT_MSG_*`, `TEST_NETLINK`, `TEST_NETLINK_`, and `TEST_NETLINK_OBJECT_EX_`.

Control flow: tests header-only message types and flags, `NLMSG_DONE`, netfilter family generation messages, batch begin/end markers, nf_tables message types with `nfgenmsg`, unsupported/unknown type fallbacks, and partial object reads.

State and persistence: sends synthetic netlink buffers nonblocking over a temporary socket; it does not install nftables rules or change kernel netfilter configuration.

Dependencies and integration points: depends on Linux netfilter/nf_tables headers and strace netlink helper macros. It forms the generic base around which the more focused `nfnetlink_*` files test subsystem-specific type names.

Risks and edge cases: message type packing combines subsystem id and command id, making xlat regressions likely if masks shift. Short `nfgenmsg` reads and unknown command fallbacks are explicit boundaries.

Test signals: expected output shows nfnetlink batch names, `NFNL_SUBSYS_*`/`NFT_MSG_*` decoding, family/version/res_id fields, raw fallback, and clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_netfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_netlink_diag.c -->
# sources/test-tools/strace/tests/netlink_netlink_diag.c

Purpose: receives and validates netlink diagnostic messages for netlink sockets, exercising decoder handling of `struct netlink_diag_msg` response data.

Important APIs, types, and helpers: `socket(AF_NETLINK, SOCK_RAW, NETLINK_SOCK_DIAG)`, `bind`, `recvfrom`, `struct netlink_diag_req`, `struct netlink_diag_msg`, `NETLINK_SOCK_DIAG`, `SOCK_DIAG_BY_FAMILY`, and netlink/sock_diag headers.

Control flow: the test opens and binds a netlink socket to create a target, opens a sock_diag netlink fd, sends a request for netlink socket diagnostics, then reads decoded responses using local helper logic.

State and persistence: all sockets are transient. The bound netlink socket exists only to provide predictable diagnostic output.

Dependencies and integration points: depends on sock_diag support for netlink sockets and strace receive-side netlink diag decoding. It complements send-side netlink diagnostic structure tests.

Risks and edge cases: kernel-specific diagnostic fields, port ids, cookies, and response ordering can vary; the controlled socket setup mitigates this but still relies on kernel support.

Test signals: expected trace should include creation/bind of the target netlink socket and decoded `NETLINK_DIAG` response messages, with normal exit or skip for unavailable support.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_netlink_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_nlctrl.c -->
# sources/test-tools/strace/tests/netlink_nlctrl.c

Purpose: deeply tests generic netlink control-family (`nlctrl`) decoding, including command headers, primitive attributes, nested operations, multicast groups, policy descriptions, operation policies, and known family-specific command tables.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_GENERIC)`, `struct genlmsghdr`, `GENL_ID_CTRL`, `CTRL_CMD_*`, `CTRL_ATTR_*`, `NL_POLICY_TYPE_ATTR_*`, `TEST_NETLINK_OBJECT_EX_`, `TEST_NLATTR`, `TEST_NLATTR_`, `TEST_NLATTR_EX_`, `check_x16_nlattr`, `check_u32_nlattr`, `xasprintf`, and xlat constants for devlink, ethtool, ioam6, mptcp, netdev, nl80211, seg6, taskstats, tcp_metrics, and thermal.

Control flow: `main` creates a generic netlink socket and shared message buffer, then runs header decoding for all control commands, unknown/x16/u32/string attributes, nested `CTRL_ATTR_OPS`, nested multicast groups, nested policy entries with 64-bit and 32-bit bounds, operation policy arrays, family-specific operation tables, and `NLMSG_DONE`.

State and persistence: all state is synthetic aligned `nlattr` trees in stack or tail-allocated buffers. The test performs no real control-family queries or family registration changes.

Dependencies and integration points: heavily integrates with `test_netlink.h`, `test_nlattr.h`, xlat tables, and many Linux generic netlink UAPI headers. It is a high-value regression test for nested nlattr rendering.

Risks and edge cases: nested attribute array formatting, xlat availability across kernel header versions, attribute alignment, unknown command fallback, and long generated expected strings are the main maintenance risks.

Test signals: output must decode `nlctrl` headers, primitive and nested attributes, policy type names and values, known family command names, unknown command comments, `NLMSG_DONE`, and the exit marker.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_nlctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_protocol.c -->
# sources/test-tools/strace/tests/netlink_protocol.c

Purpose: stress-tests generic netlink message framing and protocol-level decoding independent of a specific family, including null buffers, short buffers, multi-message arrays, `NLMSG_ERROR`, and `NLMSG_DONE`.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_SOCK_DIAG)`, `sendto`, `struct nlmsghdr`, `NLMSG_NOOP`, `NLMSG_ERROR`, `NLMSG_DONE`, `struct nlmsgerr`, `NLMSG_HDRLEN`, tail/midtail allocation, `print_quoted_hex`, and `sprintrc`.

Control flow: the test sends null and zero-length buffers, EFAULT pointers, too-short byte strings, single and multiple aligned netlink messages, intentionally truncated multi-message sequences, many `NLMSG_ERROR` payload variants with nested original headers, and `NLMSG_DONE` payload variants.

State and persistence: uses only a temporary netlink socket and synthetic buffers. It does not rely on kernel message semantics because malformed buffers are expected.

Dependencies and integration points: validates strace’s generic netlink parser before family-specific dispatch. It integrates with allocation helpers that place buffers near inaccessible memory to exercise pointer fault handling.

Risks and edge cases: length arithmetic, alignment, nested error message decoding, EFAULT display, empty payload rendering, and multi-message array boundaries are all fragile and explicitly covered.

Test signals: expected output should distinguish `NULL`, empty strings, raw byte strings, arrays of messages, truncated `...`, structured errors/done values, unknown flags, and normal exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_route.c -->
# sources/test-tools/strace/tests/netlink_route.c

Purpose: provides broad route netlink (`NETLINK_ROUTE`) message decoding coverage for rtnetlink header types, flags, common payload structures, unsupported message families, and newer route objects such as nexthops and interface stats.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `sendto`, `struct nlmsghdr`, `ifinfomsg`, `ifaddrmsg`, `rtmsg`, `ndmsg`, `ndtmsg`, `tcmsg`, `tcamsg`, `ifaddrlblmsg`, `dcbmsg`, `netconfmsg`, `br_port_msg`, `rtgenmsg`, `nhmsg`, `if_stats_msg`, `TEST_NL_ROUTE_`, `TEST_NETLINK_`, and `ifindex_lo`.

Control flow: `main` checks basic type/flag decoding and `NLMSG_DONE`, then runs per-message-family helpers for link, address, route, neighbor, rules, traffic control, actions, prefix fallbacks, neighbor table, ND user options, address labels, DCB, netconf, MDB, route generator messages, interface stats, nexthops, linkprop, VLAN, MDB get, tunnel, and other unsupported/unknown slots. Each structured helper tests short read, exact read, and under-read paths.

State and persistence: sends synthetic rtnetlink messages only. It uses the loopback ifindex for symbolic interface output but does not change links, routes, qdiscs, or netfilter state.

Dependencies and integration points: depends on many Linux rtnetlink UAPI headers and strace xlat tables for route message ids, address families, flags, scopes, protocols, and interface indices. The `TEST_NL_ROUTE_` macro is the integration point for consistent boundary testing.

Risks and edge cases: rtnetlink constants evolve frequently; newer constants may vary by headers. Boundary risks include family-only payloads, unknown families, short reads, unknown message ids, bitmask formatting, and symbolic ifindex resolution.

Test signals: output should show route message names and structured fields for every supported payload, raw/data fallbacks for unsupported messages, unknown comments for gaps, and a clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_selinux.c -->
# sources/test-tools/strace/tests/netlink_selinux.c

Purpose: verifies `NETLINK_SELINUX` message and payload decoding for SELinux enforcement, policy load, and AVC denial notifications.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_SELINUX)`, `sendto`, `struct nlmsghdr`, `SELNL_MSG_*`, `struct selnl_msg_setenforce`, `struct selnl_msg_policyload`, `struct selnl_msg_avc`, `TEST_NETLINK_`, and `TEST_NETLINK_OBJECT`.

Control flow: `main` opens a SELinux netlink socket, sends a header-only `SELNL_MSG_SETENFORCE` type test, then sends structured messages for setenforce, policyload, and avc payloads through the netlink test macros.

State and persistence: messages are synthetic and nonblocking; the test does not alter SELinux state.

Dependencies and integration points: relies on Linux `selinux_netlink.h` and strace’s netlink object decoder. It is a compact family-specific decoder test.

Risks and edge cases: SELinux netlink availability and header definitions may differ by system. Decoder risks are mostly message type names and small payload struct field formatting.

Test signals: expected output shows SELinux message names and fields, syscall result formatting, and `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_selinux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_sock_diag.c -->
# sources/test-tools/strace/tests/netlink_sock_diag.c

Purpose: exercises send-side decoding of `NETLINK_SOCK_DIAG` requests and diagnostic messages across UNIX, NETLINK, PACKET, INET, and optional SMC families.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_SOCK_DIAG)`, `sendto`, `SOCK_DIAG_BY_FAMILY`, `TCPDIAG_GETSOCK`, `TEST_SOCK_DIAG`, `unix_diag_req/msg`, `netlink_diag_req/msg`, `packet_diag_req/msg`, `inet_diag_req`, `inet_diag_req_v2`, `inet_diag_msg`, optional `smc_diag_req/msg`, `inet_pton`, `ifindex_lo`, and cookie printing macros.

Control flow: `main` checks message type and dump flags, odd/unknown family payloads in request and dump contexts, then structured request/response payloads for each supported socket family. Each `TEST_SOCK_DIAG` invocation covers family-only, family-plus-extra, exact object, and short-read decoding.

State and persistence: all payloads are synthetic and sent through a temporary sock_diag netlink fd. The file resolves constant IP addresses into in-memory structs but does not create real network connections.

Dependencies and integration points: depends on many diagnostic UAPI headers and strace xlat tables for socket families, TCP states, packet protocols, diag show flags, and cookies. Optional AF_SMC support is compile-time gated.

Risks and edge cases: diagnostic UAPI version differences, optional SMC availability, endian-sensitive port/address printing, bitmask formatting, and short-read pointer fallback are key risks.

Test signals: expected output should decode each diagnostic structure with symbolic families/states/options, show unknown family fallbacks, and finish with `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_sock_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_unix_diag.c -->
# sources/test-tools/strace/tests/netlink_unix_diag.c

Purpose: receives and validates UNIX socket diagnostic netlink responses for a controlled UNIX stream socket.

Important APIs, types, and helpers: `socket(AF_UNIX, SOCK_STREAM)`, `bind`, `socket(AF_NETLINK, SOCK_RAW, NETLINK_SOCK_DIAG)`, `sendto`/request construction, `recvfrom`, `struct unix_diag_req`, `struct unix_diag_msg`, `UNIX_DIAG_*`, `SOCK_DIAG_BY_FAMILY`, and `assert`.

Control flow: the test creates and binds a UNIX socket path, opens a sock_diag netlink fd, sends a request for UNIX diag data, and receives decoded responses using local helper functions for normal and edge response payloads.

State and persistence: creates a temporary `netlink_unix_diag_socket` pathname and socket state. Cleanup/close semantics are expected to leave no durable state.

Dependencies and integration points: depends on UNIX socket support, sock_diag support for AF_UNIX, and strace receive-side netlink decoder logic.

Risks and edge cases: response fields such as inode/cookie and available attributes can vary by kernel. The controlled pathname helps stabilize name decoding, but missing sock_diag support should be handled by skip/failure paths.

Test signals: expected trace includes controlled socket setup and decoded `unix_diag_msg` responses with UNIX-specific fields and attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_unix_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_xfrm.c -->
# sources/test-tools/strace/tests/netlink_xfrm.c

Purpose: verifies `NETLINK_XFRM` message type and flag decoding for IPsec/XFRM netlink operations.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_XFRM)`, `sendto`, `struct nlmsghdr`, `XFRM_MSG_NEWSA`, `XFRM_MSG_GETSA`, `XFRM_MSG_DELSA`, `XFRM_MSG_ALLOCSPI`, and `NLM_F_*` flags.

Control flow: `main` opens an XFRM netlink socket, sends one header for type decoding, then sends multiple headers combining XFRM message types with dump/create/delete-style flags to verify symbolic flag rendering.

State and persistence: sends only header-only nonblocking test messages and does not change XFRM state or security associations.

Dependencies and integration points: depends on Linux `xfrm.h` constants and strace’s netlink protocol/type xlat tables.

Risks and edge cases: flag interpretation depends on message type context; changes in XFRM constants or decoder-specific flag sets can affect expected strings.

Test signals: output should show symbolic XFRM message names, context-sensitive `NLM_F_*` combinations, syscall result strings, and normal exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/netlink_xfrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/newfstatat.c -->
# sources/test-tools/strace/tests/newfstatat.c

Purpose: is a thin architecture/test alias for the generic `fstatat.c` test. It compiles the shared implementation under the `newfstatat` test name.

Important APIs, types, and helpers: inherits from `fstatat.c`, which exercises the `newfstatat`/`fstatat`-style syscall decoder, stat structures, path arguments, directory fd handling, and flag decoding.

Control flow: no local runtime logic exists; the preprocessor includes `fstatat.c` directly.

State and persistence: local file adds no state. Any temporary files or paths are managed by the included shared test.

Dependencies and integration points: integrates with strace’s syscall-name matrix where the same stat-at behavior may be exposed through architecture-specific syscall names. Build-system selection decides this source’s role.

Risks and edge cases: all behavior depends on the included file. If `fstatat.c` changes assumptions about syscall names or wrappers, this alias test may need expected-output updates.

Test signals: same as the shared fstat-at test, but attributed to the `newfstatat` source/test binary.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/newfstatat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_acct.c -->
# sources/test-tools/strace/tests/nfnetlink_acct.c

Purpose: tests nfnetlink accounting subsystem type decoding for `NFNL_SUBSYS_ACCT` messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_NETFILTER)`, `sendto`, `struct nlmsghdr`, `NFNL_SUBSYS_ACCT`, `NFNL_MSG_ACCT_*`, `NFNL_MSG_BATCH_BEGIN`, and `NLM_F_REQUEST`.

Control flow: the file sends header-only nfnetlink messages for accounting command names and selected flag combinations, including known and unknown command values, then prints expected symbolic names.

State and persistence: synthetic messages only; no accounting objects are created or deleted.

Dependencies and integration points: relies on `nfnetlink.h`, `nfnetlink_acct.h`, and strace’s nfnetlink message-type decoder.

Risks and edge cases: subsystem/command packing and command availability across kernel headers are the primary risks. Unknown command fallback must remain stable.

Test signals: expected output shows `NFNL_SUBSYS_ACCT<<8|...` style symbolic decoding and exits cleanly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_cthelper.c -->
# sources/test-tools/strace/tests/nfnetlink_cthelper.c

Purpose: verifies nfnetlink conntrack-helper subsystem message name and flag decoding.

Important APIs, types, and helpers: `NETLINK_NETFILTER`, `NFNL_SUBSYS_CTHELPER`, `NFNL_MSG_CTHELPER_*`, `struct nlmsghdr`, `sendto`, `create_nl_socket`, and `sprintrc`.

Control flow: sends header-only netfilter netlink messages for helper get/new/delete commands, with request/dump and create-style flags, plus unknown command coverage.

State and persistence: no helper configuration is changed because only synthetic messages are sent nonblocking through the test socket.

Dependencies and integration points: depends on `nfnetlink_cthelper.h` constants and the shared nfnetlink decoder.

Risks and edge cases: command constants may be absent or differ on older headers; flag decoding is command-context-sensitive.

Test signals: expected output contains symbolic CTHelper message names, relevant `NLM_F_*` flags, unknown fallback comments, and normal exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_cthelper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_ctnetlink.c -->
# sources/test-tools/strace/tests/nfnetlink_ctnetlink.c

Purpose: validates nfnetlink conntrack subsystem message decoding for `NFNL_SUBSYS_CTNETLINK`.

Important APIs, types, and helpers: `NFNL_SUBSYS_CTNETLINK`, `IPCTNL_MSG_CT_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends known conntrack command headers, combines them with request/dump/create/delete flags, and includes unknown command values for fallback coverage.

State and persistence: does not manipulate real conntrack entries; all messages are test buffers.

Dependencies and integration points: depends on `nfnetlink_conntrack.h` and strace nfnetlink xlat tables.

Risks and edge cases: conntrack command name coverage is sensitive to kernel UAPI evolution and strace xlat synchronization.

Test signals: expected output shows packed subsystem/type names for conntrack commands and stable syscall return formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_ctnetlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_ctnetlink_exp.c -->
# sources/test-tools/strace/tests/nfnetlink_ctnetlink_exp.c

Purpose: checks nfnetlink conntrack expectation subsystem message decoding for `NFNL_SUBSYS_CTNETLINK_EXP`.

Important APIs, types, and helpers: `NFNL_SUBSYS_CTNETLINK_EXP`, expectation `IPCTNL_MSG_EXP_*` constants, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends header-only expectation netlink messages across known commands, flag combinations, and unknown command values.

State and persistence: no conntrack expectations are installed or modified; messages are nonblocking synthetic decoder inputs.

Dependencies and integration points: shares `nfnetlink_conntrack.h` with the base conntrack test and targets strace’s subsystem-specific message table.

Risks and edge cases: packed type decoding must distinguish CT and CT_EXP subsystems even when command names are similar.

Test signals: expected output has expectation-specific symbolic names, request/dump/create flags where appropriate, and clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_ctnetlink_exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_cttimeout.c -->
# sources/test-tools/strace/tests/nfnetlink_cttimeout.c

Purpose: tests nfnetlink conntrack-timeout subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_CTNETLINK_TIMEOUT`, `IPCTNL_MSG_TIMEOUT_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends timeout command headers with known get/new/delete/default-style message ids and flag combinations, plus unknown command coverage.

State and persistence: does not change timeout policies; all inputs are synthetic netlink headers.

Dependencies and integration points: depends on `nfnetlink_cttimeout.h` and strace’s nfnetlink message xlat handling.

Risks and edge cases: timeout command sets include extra/default messages compared with simpler nfnetlink subsystems, so table completeness is important.

Test signals: expected output should show timeout subsystem names and fallback comments for unknown ids.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_cttimeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_ipset.c -->
# sources/test-tools/strace/tests/nfnetlink_ipset.c

Purpose: verifies nfnetlink ipset subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_IPSET`, `IPSET_CMD_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends representative ipset command headers and unknown command ids to ensure symbolic and fallback type printing.

State and persistence: no ipsets are created, listed, or destroyed; the socket sends synthetic messages only.

Dependencies and integration points: uses `linux/netfilter/ipset/ip_set.h` and strace nfnetlink decoding.

Risks and edge cases: ipset command tables vary across kernels; unknown fallback formatting must remain deterministic.

Test signals: expected output decodes packed `NFNL_SUBSYS_IPSET` command values and exits normally.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_ipset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_nft_compat.c -->
# sources/test-tools/strace/tests/nfnetlink_nft_compat.c

Purpose: checks nf_tables compatibility subsystem message decoding for `NFNL_SUBSYS_NFT_COMPAT`.

Important APIs, types, and helpers: `NFNL_SUBSYS_NFT_COMPAT`, `NFT_MSG_COMPAT_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends compatibility get/new/delete-style header-only messages, expected flag variants, and unknown command values.

State and persistence: does not alter nftables compatibility objects; messages are decoder-only inputs.

Dependencies and integration points: depends on `nf_tables_compat.h` and strace netfilter xlat tables.

Risks and edge cases: compatibility command names overlap conceptually with nftables but live in a distinct subsystem; decoder packing must preserve that distinction.

Test signals: output should show `NFT_MSG_COMPAT_*` names under `NFNL_SUBSYS_NFT_COMPAT`, unknown fallbacks, and normal exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_nft_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_nftables.c -->
# sources/test-tools/strace/tests/nfnetlink_nftables.c

Purpose: validates nf_tables nfnetlink message type decoding for `NFNL_SUBSYS_NFTABLES`.

Important APIs, types, and helpers: `NFNL_SUBSYS_NFTABLES`, `NFT_MSG_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: emits header-only nftables commands across known message names and common request/dump/create/delete flags, plus unknown command slots.

State and persistence: does not create or modify nftables tables/chains/rules. It only feeds synthetic messages to strace.

Dependencies and integration points: uses `nf_tables.h` and the strace nfnetlink/nftables xlat tables.

Risks and edge cases: nftables UAPI evolves regularly, so command-name tables and unknown fallback behavior are important.

Test signals: expected trace contains packed nftables message names with correct flag rendering and the exit marker.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_nftables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_osf.c -->
# sources/test-tools/strace/tests/nfnetlink_osf.c

Purpose: tests nfnetlink passive OS fingerprinting subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_OSF`, `NFNL_MSG_OSF_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends known OSF message headers and unknown ids to verify type-name lookup and fallback behavior.

State and persistence: no OSF signatures are modified; messages are synthetic decoder probes.

Dependencies and integration points: depends on `nfnetlink_osf.h` and strace nfnetlink xlat tables.

Risks and edge cases: small subsystem command tables are easy to regress through missing constants or incorrect packed type masks.

Test signals: output should show OSF command names and normal syscall result formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_osf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_queue.c -->
# sources/test-tools/strace/tests/nfnetlink_queue.c

Purpose: verifies nfnetlink queue subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_QUEUE`, `NFQNL_MSG_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends representative queue message types and an unknown type through a netfilter netlink socket.

State and persistence: no packets are queued or verdicts applied; this is header-only decode coverage.

Dependencies and integration points: depends on `nfnetlink_queue.h` and strace’s nfnetlink message-name tables.

Risks and edge cases: command constants and fallback comments must match the packed subsystem/type representation.

Test signals: expected output contains `NFQNL_MSG_*` symbolic names and exits cleanly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_ulog.c -->
# sources/test-tools/strace/tests/nfnetlink_ulog.c

Purpose: tests nfnetlink log/ulog subsystem message decoding.

Important APIs, types, and helpers: `NFNL_SUBSYS_ULOG`, `NFULNL_MSG_*`, `NETLINK_NETFILTER`, `struct nlmsghdr`, `sendto`, and `create_nl_socket`.

Control flow: sends known ulog/log command headers and unknown ids to verify symbolic type rendering.

State and persistence: no logging configuration is changed; synthetic headers are sent only for strace decoding.

Dependencies and integration points: uses `nfnetlink_log.h` and the shared nfnetlink decoder.

Risks and edge cases: decoder must distinguish ULOG/LOG command names from queue and nftables commands despite shared protocol packing.

Test signals: output includes `NFULNL_MSG_*` names or unknown comments and the normal exit marker.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nfnetlink_ulog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr.c -->
# sources/test-tools/strace/tests/nlattr.c

Purpose: stress-tests generic netlink attribute parsing and rendering with UNIX diag messages, including malformed lengths, nesting, arrays, abbreviated strings, and unknown attribute types.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_SOCK_DIAG)`, `sendto`, `struct nlmsghdr`, `struct unix_diag_msg`, `struct nlattr`, `NLA_F_NESTED`, `UNIX_DIAG_*`, `DEFAULT_STRLEN`, `print_quoted_hex`, and helper-constructed message buffers.

Control flow: builds netlink messages containing UNIX diag payloads and attributes, then sends sequences with too-short attributes, exact attributes, nested attributes, arrays, unknown ids, long string payloads, and trailing data. Each send is paired with hand-written expected output.

State and persistence: all state is synthetic buffers and one sock_diag netlink fd. No real socket diagnostics are queried or persisted.

Dependencies and integration points: validates the low-level nlattr decoder that many protocol-specific tests depend on. Uses Linux rtnetlink/sock_diag/unix_diag headers for constants and structure sizes.

Risks and edge cases: attribute length arithmetic, alignment padding, nested array delimiters, default string abbreviation, and unknown type rendering are the main fragile points.

Test signals: expected trace shows structured attributes where valid, raw pointers/hex for malformed data, abbreviation markers, and a final `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_br_port_msg.c -->
# sources/test-tools/strace/tests/nlattr_br_port_msg.c

Purpose: tests route-netlink attributes attached to `struct br_port_msg` multicast database messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct br_port_msg`, `RTM_NEWMDB`/bridge rtnetlink constants, `TEST_NLATTR_`, `test_nlattr.h`, and `ifindex_lo`.

Control flow: initializes and prints a bridge port message header, then sends one or more attributes through the nlattr macro framework to verify attribute names and payload formatting.

State and persistence: no bridge or multicast database state is changed; data is synthetic.

Dependencies and integration points: depends on `linux/if_bridge.h`, `linux/rtnetlink.h`, and the strace route nlattr decoder.

Risks and edge cases: bridge attribute constants and interface-index symbolic rendering can vary with headers/environment.

Test signals: expected output shows a route netlink message with decoded `br_port_msg` header and bridge-specific attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_br_port_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_cachereport-Xabbrev.c -->
# sources/test-tools/strace/tests/nlattr_cachereport-Xabbrev.c

Purpose: compiles the cache-report nlattr test with abbreviated xlat output enabled by defining `XLAT_ABBREV`.

Important APIs, types, and helpers: inherits `nlattr_cachereport.c`, including `RTM_NEWCACHEREPORT`, `CACHE_REPORT_*`, `TEST_NLATTR_*`, `XLAT_ABBREV`, and address-family xlat helpers.

Control flow: no local runtime logic. The included source runs the same cache-report attribute cases but prints xlat values in abbreviated mode.

State and persistence: no local state and no persistent route changes.

Dependencies and integration points: integrates with strace `-Xabbrev` expected-output variants for xlat formatting.

Risks and edge cases: any change in the base file or xlat mode formatting affects this wrapper.

Test signals: same structural output as `nlattr_cachereport.c`, with abbreviated symbolic xlat rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_cachereport-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_cachereport-Xraw.c -->
# sources/test-tools/strace/tests/nlattr_cachereport-Xraw.c

Purpose: compiles the cache-report nlattr test with raw xlat output enabled by defining `XLAT_RAW`.

Important APIs, types, and helpers: inherits `nlattr_cachereport.c` and changes only xlat rendering mode through `XLAT_RAW`.

Control flow: no independent control flow; the included base executes all cache-report nlattr cases.

State and persistence: no local persistent state.

Dependencies and integration points: used by the strace `-Xraw` output mode tests for xlat values in route cache-report attributes.

Risks and edge cases: raw numeric formatting must stay aligned with the base test’s expected values.

Test signals: base cache-report traces should show raw numeric xlat output instead of symbolic-only forms.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_cachereport-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_cachereport-Xverbose.c -->
# sources/test-tools/strace/tests/nlattr_cachereport-Xverbose.c

Purpose: compiles the cache-report nlattr test with verbose xlat output enabled by defining `XLAT_VERBOSE`.

Important APIs, types, and helpers: inherits `nlattr_cachereport.c` and its route-cache attribute tests, with `XLAT_VERBOSE` controlling value rendering.

Control flow: no local runtime logic; the base file’s `main` is compiled in verbose xlat mode.

State and persistence: no added state and no route table modification.

Dependencies and integration points: validates strace `-Xverbose` formatting for the same nlattr cases covered by the base file.

Risks and edge cases: verbose xlat strings can change when tables are renamed or constants are added.

Test signals: output should match the base cache-report cases with verbose xlat value presentation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_cachereport-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_cachereport.c -->
# sources/test-tools/strace/tests/nlattr_cachereport.c

Purpose: tests route-netlink cache report (`RTM_NEWCACHEREPORT`) attribute decoding, including address-family dependent multicast route cache payloads and xlat rendering modes.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct rtgenmsg`, `RTM_NEWCACHEREPORT`, `CACHE_REPORT_*`, `struct mfcctl`, `struct mf6cctl`, `TEST_NETLINK_`, `TEST_NLATTR_`, `TEST_NLATTR_OBJECT_EX_`, `xlat/addrfams.h`, and global `af`/`af_str` formatting state.

Control flow: initializes route-generator messages, sends bare cache report messages, then tests attributes for IPv4 and IPv6 multicast cache reports with normal, short, and object-specific payloads. It adapts expected output according to xlat mode macros.

State and persistence: uses global variables to track the current address family string for expected output. No kernel route cache state is changed.

Dependencies and integration points: relies on route, IPv4 multicast, IPv6 multicast, and xlat headers plus strace nlattr helper macros. Included by three wrapper files for xlat output variants.

Risks and edge cases: address-family-specific object size differences, xlat mode conditionals, and short object reads are the major risks.

Test signals: expected output decodes `RTM_NEWCACHEREPORT`, `rtgen_family`, cache report attributes, IPv4/IPv6 multicast fields, and xlat-mode-specific values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_cachereport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_crypto_user_alg.c -->
# sources/test-tools/strace/tests/nlattr_crypto_user_alg.c

Purpose: verifies crypto-user netlink attribute decoding for `struct crypto_user_alg` messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_CRYPTO)`, `struct crypto_user_alg`, `CRYPTOCFGA_*`, `CRYPTOCFGA_REPORT_*`, `TEST_NLATTR`, `TEST_NLATTR_OBJECT_EX`, `check_*_nlattr` helpers, and crypto xlat constants.

Control flow: initializes a crypto-user algorithm header, prints it, then tests attributes such as priority, report type names, larval/hash/skcipher/rng reports, and object payloads with fixed strings and numeric fields.

State and persistence: all crypto algorithm data is synthetic message memory; no kernel crypto algorithm registration is modified.

Dependencies and integration points: depends on `linux/cryptouser.h`, `test_nlattr.h`, and strace crypto nlattr decoders.

Risks and edge cases: fixed-size string arrays, report type xlat values, object-size checks, and optional constants can affect expected output.

Test signals: expected output shows decoded `CRYPTOCFGA_*` attributes and structured crypto report objects with symbolic fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_crypto_user_alg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_dcbmsg.c -->
# sources/test-tools/strace/tests/nlattr_dcbmsg.c

Purpose: tests attributes on rtnetlink DCB (`struct dcbmsg`) messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct dcbmsg`, `RTM_GETDCB`/DCB command constants, `TEST_NLATTR_`, and `test_nlattr.h`.

Control flow: initializes and prints a DCB message header, then uses the nlattr framework to send DCB attributes with expected decoded names and payloads.

State and persistence: no DCB configuration is queried or changed; messages are synthetic.

Dependencies and integration points: depends on `linux/dcbnl.h`, `linux/rtnetlink.h`, and the route nlattr decoder.

Risks and edge cases: DCB command and attribute constants can differ by header version. Short payload handling is covered by helper macros.

Test signals: expected trace includes decoded DCB header fields and DCB attribute output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_dcbmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_fib_rule_hdr.c -->
# sources/test-tools/strace/tests/nlattr_fib_rule_hdr.c

Purpose: validates nlattr decoding for FIB rule messages, including address attributes, interface names, priorities, marks, uid ranges, and l3mdev/table fields.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct fib_rule_hdr`, `FRA_*`, `FR_ACT_*`, `TEST_NLATTR_`, `TEST_NLATTR_OBJECT`, `inet_pton`, `linux/fib_rules.h`, and IPv4/IPv6 address helpers.

Control flow: builds a FIB rule header, sends primitive attributes and object attributes for IPv4/IPv6 addresses and rule metadata, and loops through selected family-specific cases.

State and persistence: no real routing rules are added or removed; all messages are synthetic.

Dependencies and integration points: route nlattr decoder, fib rules UAPI, xlat tables for actions, flags, and attribute names.

Risks and edge cases: address-family-dependent payload interpretation, uid range object size, and unknown/raw attribute fallbacks are key boundaries.

Test signals: expected output shows decoded FIB rule header fields and structured `FRA_*` attribute payloads.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_fib_rule_hdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifaddrlblmsg.c -->
# sources/test-tools/strace/tests/nlattr_ifaddrlblmsg.c

Purpose: tests route-netlink attributes attached to interface address-label messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct ifaddrlblmsg`, `IFAL_*`, `RTM_NEWADDRLABEL`, `TEST_NLATTR_`, `TEST_NLATTR`, and `ifindex_lo`.

Control flow: initializes an address label header and sends attributes such as address and label values through the nlattr test macros.

State and persistence: no address labels are configured; messages are synthetic.

Dependencies and integration points: depends on `linux/if_addrlabel.h`, route netlink constants, and strace route nlattr decoding.

Risks and edge cases: attribute payload sizes and ifindex rendering are the likely regressions.

Test signals: expected trace decodes the `ifaddrlblmsg` header and `IFAL_*` attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifaddrlblmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifaddrmsg.c -->
# sources/test-tools/strace/tests/nlattr_ifaddrmsg.c

Purpose: validates nlattr decoding for interface address messages across IPv4, IPv6, and non-IP family contexts.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct ifaddrmsg`, `IFA_*`, `IFA_F_*`, `RTM_NEWADDR`, `TEST_NLATTR_`, `TEST_NLATTR`, `TEST_NLATTR_OBJECT`, `inet_pton`, and the `SET_IFA_FAMILY` helper macro.

Control flow: initializes an ifaddr header, switches address families, then tests local/address/broadcast/anycast/cacheinfo/flags attributes with family-appropriate formatting.

State and persistence: no interface addresses are created or modified. Family selection is in local message buffers only.

Dependencies and integration points: depends on `linux/if_addr.h`, route netlink decoder tables, and nlattr helpers.

Risks and edge cases: IPv4 versus IPv6 address length interpretation, flag bitmask rendering, and raw fallback for unexpected families are the main risks.

Test signals: expected output decodes `IFA_*` attributes with correct address and cacheinfo formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifaddrmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifinfomsg.c -->
# sources/test-tools/strace/tests/nlattr_ifinfomsg.c

Purpose: provides broad nlattr coverage for interface info (`struct ifinfomsg`) route messages, including link names, MTUs, qdisc/ifalias strings, link stats, maps, proto-down reason arrays, nested AF-specific attributes, and many numeric/flag attributes.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct ifinfomsg`, `IFLA_*`, `struct rtnl_link_stats`, `struct rtnl_link_stats64`, `struct rtnl_link_ifmap`, `TEST_NLATTR_`, `TEST_NLATTR`, `TEST_NLATTR_OBJECT`, `TEST_NLATTR_OBJECT_MINSZ`, `TEST_NESTED_NLATTR_OBJECT_EX_`, and helpers from included `nlattr_ifla.h`/`nlattr_ifla_af_inet6.h`.

Control flow: initializes an ifinfo header and systematically sends attributes of varying primitive/object/string/nested forms. It covers exact objects, minimum-size objects, raw pointer fallbacks, long strings, byte arrays, nested attributes, and loops over repeated proto-down reason values.

State and persistence: no link state is changed. All interface data is synthetic, with loopback ifindex used where symbolic output is expected.

Dependencies and integration points: depends on `linux/if_link.h`, route netlink attribute xlat tables, `test_nlattr.h`, and local headers that factor nested IFLA/AF_INET6 cases.

Risks and edge cases: this is a high-risk decoder surface because attribute coverage spans many kernel versions. Object size evolution, nested attribute alignment, long string truncation, and bitmask formatting can all break expectations.

Test signals: expected output should decode numerous `IFLA_*` attributes, structured link stats/maps, nested AF_SPEC/INET6 objects, unknown/fallback values, and the normal exit line.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifinfomsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla.h -->
# sources/test-tools/strace/tests/nlattr_ifla.h

Purpose: shared helper header for interface-link nlattr tests, factoring common `ifinfomsg` header initialization/printing and reusable attribute checks.

Important APIs, types, and helpers: `struct ifinfomsg`, `hdrlen`, `init_ifinfomsg`, `print_ifinfomsg`, `ifindex_lo`, `PRINT_FIELD_*`, and `test_nlattr.h` macros used by including C files.

Control flow: as a header, it defines static helper functions rather than a `main`. Including tests call these helpers to initialize the netlink header and print a consistent ifinfo prefix before testing attributes.

State and persistence: no persistent state. It provides compile-time shared code and uses only caller-provided message buffers.

Dependencies and integration points: depends on Linux interface/rtnetlink headers and is integrated into route `IFLA_*` nlattr tests, especially `nlattr_ifinfomsg.c` and related files.

Risks and edge cases: because functions are `static` in a header, every includer gets its own copy; signature or expected-output changes must stay aligned with all callers.

Test signals: not executable alone. Its correctness is observed through including tests whose expected output starts with the shared `ifinfomsg` prefix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_af_inet6.h -->
# sources/test-tools/strace/tests/nlattr_ifla_af_inet6.h

Purpose: shared helper header for nested `IFLA_AF_SPEC`/IPv6 interface-link attribute tests.

Important APIs, types, and helpers: IPv6 link attribute constants such as `IFLA_INET6_*`, nested nlattr macros including `TEST_NESTED_NLATTR_OBJECT_EX_` and `TEST_NESTED_NLATTR_ARRAY_EX_`, IPv6 cache/config/stats structures, and caller-provided `init_msg`/`print_msg` callbacks.

Control flow: defines static helper functions that build nested IPv6 AF_SPEC attribute payloads and arrays, covering flags, cacheinfo, conf arrays, stats arrays, token/address generation mode, and unknown/truncated nested objects. Including tests invoke these helpers from their own `main`.

State and persistence: no runtime persistence; all state is synthetic nested attribute memory provided to strace through sendto.

Dependencies and integration points: depends on Linux `if_link.h` IPv6 attribute definitions and the strace nlattr test macro framework. It is integrated into interface-info nlattr coverage.

Risks and edge cases: nested array length alignment, evolving IPv6 per-interface attribute constants, and object-size changes are the main maintenance risks.

Test signals: not a standalone test. Including tests should emit decoded nested IPv6 AF_SPEC attributes with structured object/array formatting and appropriate fallback on malformed payloads.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_af_inet6.h -->
