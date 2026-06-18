# sources/distributed-fs/ceph-client/include/net/selftests.h

## Purpose
This header defines a small generic network selftest interface for drivers/devices that support ethtool self-tests with loopback packets.

## Important APIs, Types, And Functions
`struct net_packet_attrs` describes packet addresses, TCP/UDP ports, timeout, size bounds, id, queue mapping, VLAN/checksum traits, and checksum corruption. `struct net_test_priv` tracks a packet, packet handler, completion, VLAN data, and result. `struct netsfhdr` is the test payload header with version, magic, and id. Constants define packet size, magic value, and default timeout. APIs are `net_test_get_skb()`, `net_selftest()`, `net_selftest_get_count()`, and `net_selftest_get_strings()`, with no-op stubs unless `CONFIG_NET_SELFTESTS` is enabled.

## Control Flow
Drivers call the selftest entry point from ethtool test operations. Enabled builds generate skb test packets, install a packet handler, wait for completion, and fill result buffers/strings.

## State And Persistence
State is per test invocation through `net_test_priv`; no persistent global state is declared here.

## Dependencies And Integration Points
It depends on ethtool and netdevice APIs and integrates with driver ethtool self-test callbacks and packet receive hooks.

## Risks And Test Signals
Risks include false failures from timeout sizing, queue mapping mismatch, packet handler leaks, checksum/VLAN coverage gaps, and stubs hiding untested builds. Test signals are ethtool self-test runs on supported devices, loopback packet receipt, bad-checksum negative tests, VLAN variants, and disabled-config compile checks.
