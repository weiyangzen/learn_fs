# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tap.c

Purpose: this kselftest verifies TAP/macvtap packet injection behavior with virtio net headers. It checks that valid UDP GSO and checksum-valid packets are accepted, and that a malformed GSO packet with invalid Ethernet protocol is rejected with `EINVAL`.

Important APIs and functions: device setup uses raw rtnetlink helpers `rtattr_add`, `rtattr_begin`, `dev_create`, `dev_delete`, `macvtap_fill_rtattr`, and `opentap`. Packet builders include `build_eth`, checksum helpers, `build_ipv4_header`, `build_udp_packet`, `build_test_packet_valid_udp_gso`, `build_test_packet_valid_udp_csum`, and `build_test_packet_crash_tap_invalid_eth_proto`. Tests use `kselftest_harness.h` fixtures and assertions.

Control flow: the fixture creates a dummy lower device and a macvtap device linked to it, opens `/dev/tap<ifindex>` with `IFF_TAP | IFF_NO_PI | IFF_VNET_HDR | IFF_MULTI_QUEUE`, and tears both devices down after each test. Each test builds a packet in a stack buffer, writes it to the tap fd, and asserts either full write length or `-1/EINVAL`.

State and persistence: kernel state is limited to temporary netdevices and an open tap file descriptor. Packet content is generated in memory. Fixture teardown deletes both devices and closes the fd; no persistent files are written.

Dependencies and integration points: requires root or capabilities for netlink device creation and `/dev/tap*` access, macvtap and dummy support, Linux virtio-net header definitions, and the selftest harness. It integrates with kselftest's fixture lifecycle and assertion reporting.

Risks: `dev_create` and `dev_delete` send netlink requests but do not read full ACK details, so failures may surface indirectly. The invalid packet builder intentionally lays out odd headers to exercise a crash path; maintenance should preserve that malformed structure. Device names are fixed (`xmacvtap0`, `xdummy0`) and can conflict with a dirty test environment.

Test signals: two valid packet tests expect `write()` to return the exact generated length. The regression test expects `write()` to fail with `EINVAL`; a successful write there indicates the kernel accepted malformed GSO metadata unexpectedly.
