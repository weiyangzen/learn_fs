# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_fragmentation.c

Purpose: Regression test for IPv6 UDP fragmentation on loopback after stable backport issues around cork `dontfrag` state.

Important APIs and types: Uses `unshare(CLONE_NEWNET)`, `ioctl(SIOCSIFMTU)`, `SIOCGIFFLAGS`, `SIOCSIFFLAGS`, IPv6 UDP socket, `sendmsg`, loopback MTU set to 1500, and an 8192-byte payload.

Control flow: `setup` enters a new network namespace, sets loopback MTU below the send size, and brings loopback up. `main` constructs a UDP destination at `::1` port 9, prepares a large iovec, opens an IPv6 datagram socket, retries briefly on `EADDRNOTAVAIL` while loopback settles, and requires `sendmsg` to return the full payload length rather than `EMSGSIZE` or a short write.

State and persistence: Only the private namespace's loopback MTU and link state change. No persistent state.

Dependencies and integration: Requires namespace privileges and standard IPv6 UDP support. It uses `kselftest.h` exit codes.

Risks: It tests successful send, not fragment reception. A very slow namespace address setup can require the retry path.

Test signals: `[PASS] sendmsg() returned 8192` confirms the kernel fragmented instead of failing with `EMSGSIZE`.
