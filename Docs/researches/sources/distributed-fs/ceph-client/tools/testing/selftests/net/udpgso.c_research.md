# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso.c

Purpose: Core UDP segmentation offload regression test. It sends UDP payloads at and beyond MTU/MSS boundaries over IPv4 and IPv6 and verifies send success/failure and receiver datagram segmentation lengths.

Important APIs/types/functions: defines `UDP_SEGMENT`, `UDP_MAX_SEGMENTS`, MTU/MSS constants, `struct testcase`, and IPv4/IPv6 testcase arrays. Uses `IP_MTU_DISCOVER`/`IPV6_MTU_DISCOVER` to prevent fragmentation, `IP_MTU`/`IPV6_MTU` reads for connected sockets, `sendmsg()` with UDP_SEGMENT cmsg or `setsockopt(SOL_UDP, UDP_SEGMENT)`, optional `MSG_MORE`, optional IPv6 hop options, and `recv()` checks.

Control flow: command-line flags select IPv4/IPv6, connected/connectionless, MSG_MORE, receive suppression, setsockopt-vs-cmsg, and a specific test ID. `run_test()` binds RX, sets timeout, creates TX, enables PMTU discovery, then runs all testcase rows for connectionless and/or connected paths. `run_one()` applies optional IPv6 extension headers, sets UDP_SEGMENT if requested, sends, checks whether failure was expected, clears hopopts, then receives exactly the expected full MSS datagrams and trailing datagram and checks no extras remain.

State and persistence: static global buffer and process-global config. Kernel state is only local UDP sockets and route MTU/loopback setup done externally by `udpgso.sh`. No persistent files.

Dependencies and integration: driven by `udpgso.sh`; requires kernel UDP GSO support and root or namespace privileges depending on setup. Uses standard sockets only.

Risks: error mapping treats `EMSGSIZE`, `ENOMEM`, and `EINVAL` as expected send failure classes. Receive validation depends on loopback/local MTU being configured to `CONST_MTU_TEST`. Extension header case tests a narrow IPv6 hopopts path.

Test signals: any mismatch in send expectation, path MTU, receive segment length/count, or unexpected extra datagram aborts with `error(1, ...)`; success prints `OK`.
