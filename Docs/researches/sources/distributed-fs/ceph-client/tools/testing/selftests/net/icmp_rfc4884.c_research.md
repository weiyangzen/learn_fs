# sources/distributed-fs/ceph-client/tools/testing/selftests/net/icmp_rfc4884.c

Purpose: Kernel selftest for ICMP RFC 4884 extension reporting through the socket error queue. It synthesizes IPv4 and IPv6 ICMP destination-unreachable packets that quote UDP datagrams with and without RFC 4884 extension blocks, then checks `ee_rfc4884.len` and `SO_EE_RFC4884_FLAG_INVALID` returned by `recvmsg(MSG_ERRQUEUE)`.

Important APIs and types: Uses `kselftest_harness` fixtures and variants, raw ICMP sockets, datagram sockets with `IP_RECVERR_RFC4884` or `IPV6_RECVERR_RFC4884`, `struct sock_extended_err`, `struct icmp_ext_hdr`, `struct icmp_extobj_hdr`, IPv4/IPv6/UDP headers, `poll`, `recvmsg`, `sendto`, `unshare(CLONE_NEWNET)`, and loopback `ioctl` setup.

Control flow: Fixture setup creates a fresh network namespace and brings `lo` up. Packet builders construct original UDP datagrams, optional RFC 4884 objects, and complete ICMPv4/v6 errors. Variants enumerate small, minimum, large, absent-extension, bad-checksum, and bad-length cases for both address families. The test opens a bound UDP socket, enables error queue options, sends a crafted raw ICMP packet to loopback, waits for `POLLERR`, and validates the single relevant control message.

State and persistence: State is local to one test namespace and one fixture variant. No persistent files are written. Constants for source/destination ports, payload bytes, and minimum quoted datagram length define expected offsets.

Dependencies and integration: Integrates Linux ICMP, IPv6, and error-queue UAPI behavior with kselftest. It requires root or capabilities for raw sockets and net namespace setup.

Risks: Hand-built packet layout, checksum math, and RFC 4884 length units are delicate. The test assumes the kernel surfaces malformed extension metadata rather than silently dropping all malformed packets. It only inspects the first matching error cmsg.

Test signals: Passing variants prove valid extensions report payload offsets only when enough original datagram bytes are present, no-extension cases report zero, and malformed extension checksum or object length sets the invalid flag.
