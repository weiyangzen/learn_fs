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
