# sources/distributed-fs/ceph-client/net/core/selftests.c

## Purpose

`selftests.c` provides a common library for generic PHY ethtool offline selftests. It builds synthetic Ethernet/IPv4/TCP or UDP packets, transmits them through device/PHY loopback, validates received packets through a temporary packet handler, and exposes standard ethtool selftest entry points for drivers that want reusable PHY loopback coverage.

## Important APIs, Types, And Functions

`net_test_get_skb()` is the exported packet builder. It takes a `struct net_device`, packet id, and `struct net_packet_attrs`, then constructs an skb containing Ethernet, IPv4, TCP or UDP, a `struct netsfhdr` selftest header with `NET_TEST_PKT_MAGIC`, optional payload, optional padding to `max_size`, checksum metadata, and device/protocol fields.

`net_test_loopback_validate()` is the receive packet handler used by loopback tests. It unshares and linearizes the skb, checks source/destination MAC addresses when requested, accounts for optional double VLAN offset, validates L4 protocol and destination port, verifies selftest magic and id, detects deliberately bad TCP checksums incorrectly marked `CHECKSUM_UNNECESSARY`, completes the test, and frees the skb.

`__net_test_loopback()` allocates `struct net_test_priv`, installs a temporary `packet_type` handler with `dev_add_pack()`, creates and transmits the skb through `dev_direct_xmit()`, waits for completion with a default timeout, maps validation state to `0`, `-ETIMEDOUT`, `-EIO`, `-ENETUNREACH`, or allocation errors, then removes the packet handler.

The test functions are `net_test_netif_carrier()`, `net_test_phy_phydev()`, `net_test_phy_loopback_enable()`, `net_test_phy_loopback_disable()`, `net_test_phy_loopback_udp()`, `net_test_phy_loopback_udp_mtu()`, `net_test_phy_loopback_tcp()`, and `net_test_phy_loopback_tcp_bad_csum()`. The exported ethtool helpers are `net_selftest()`, `net_selftest_get_count()`, and `net_selftest_get_strings()`.

## Control Flow

An ethtool-capable driver calls `net_selftest()`. The function rejects non-offline tests by setting `ETH_TEST_FL_FAILED`, resets the static packet id counter, and runs every entry in `net_selftests[]`. Failures other than `-EOPNOTSUPP` mark the ethtool result as failed; unsupported PHY operations are allowed to be reported without failing the entire suite.

Loopback tests create attributes, usually setting destination MAC to the device address and optionally enabling TCP, MTU-sized padding, or bad checksum mode. `__net_test_loopback()` registers the packet handler before sending so the looped frame can be captured. The validation callback completes the wait once the expected packet is seen, and the sender maps missing completion to timeout.

The bad TCP checksum test uses `net_test_get_skb()` to force checksum computation, then mutates the TCP checksum away from a valid value. Success means the driver did not falsely mark the bad checksum as hardware-verified; `-EIO` indicates the skb arrived with `CHECKSUM_UNNECESSARY`, which is treated as a serious RX path defect.

## State And Persistence Behavior

The only file-level state is `net_test_next_id`, a u8 packet identifier reset at the start of `net_selftest()` and incremented for each transmitted test packet. Per-test state is held in `struct net_test_priv`, including completion, result state, packet attributes, and packet handler. It is allocated and freed within `__net_test_loopback()`.

The tests temporarily change PHY loopback state through `phy_loopback(ndev->phydev, true/false, 0)`. That is persistent device state until disabled, so the ordered selftest array deliberately enables loopback before packet tests and disables it after them.

## Dependencies And Integration Points

The file integrates with ethtool selftest APIs, PHY library loopback control, skb allocation and checksum helpers, direct device transmit, packet type receive hooks, IPv4/TCP/UDP header helpers, and netdevice carrier/address state. It expects definitions from `net/selftests.h`, including `struct net_packet_attrs`, `struct netsfhdr`, `NET_TEST_PKT_SIZE`, `NET_TEST_PKT_MAGIC`, and `NET_LB_TIMEOUT`.

Drivers integrate by calling the exported helpers from their ethtool ops and using the string/count helpers to size result arrays.

## Risks And Edge Cases

The packet builder must keep skb head/tail layout consistent with the Ethernet/IP/L4/selftest header sizes. `max_size` changes both allocation/padding and UDP/IP length calculations; off-by-one errors would cause false loopback failures.

The validator assumes packets can be unshared and linearized in atomic context. Allocation or linearization failure silently leads to cleanup and no success completion, which the sender reports as timeout.

The static u8 id can wrap if the test list grows substantially, though the current list is small. Since each run resets it and waits per packet, wrap is not a practical issue today.

PHY loopback state is externally visible. If the enable test succeeds and a later step aborts unexpectedly outside this function's normal sequence, drivers still rely on the final disable test being run by `net_selftest()`.

The bad checksum result is nuanced: timeout can mean hardware dropped the frame before the driver saw it, while `-EIO` specifically means the driver incorrectly claimed a bad checksum was unnecessary to verify.

## Test Signals

Expected coverage is direct: invoke ethtool offline selftests on devices with and without PHYs, with carrier up/down, with PHY loopback support and without it, and inspect per-test return codes. Packet-level tests should cover UDP, MTU-sized UDP, TCP, and bad TCP checksum behavior. Driver validation should ensure packet handler cleanup, loopback disable, and ethtool string/count alignment.
