# sources/distributed-fs/ceph-client/drivers/net/dummy.c

## Purpose
This file implements the dummy network device driver. The device accepts packets for transmission, timestamps and accounts them, then drops them, giving users a routable/testable interface with no real hardware.

## Important APIs, Types, and Functions
- `dummy_xmit()` updates lightweight TX stats, timestamps the skb, frees it, and succeeds.
- `dummy_get_stats64()` returns per-CPU lightweight TX counters.
- `dummy_dev_init()` selects `NETDEV_PCPU_STAT_LSTATS` and sets lockdep classes.
- `dummy_change_carrier()` toggles carrier state.
- `dummy_setup()` applies Ethernet setup, no-ARP/no-multicast/no-queue flags, live address changes, software offloads, random MAC, and zero MTU bounds.
- `dummy_validate()` checks optional rtnetlink MAC addresses.
- `dummy_link_ops` registers rtnetlink kind `dummy`.

## Control Flow
Module init registers rtnetlink link ops and creates `numdummies` initial devices in `init_net`. Rtnetlink can create more. TX is terminal: skb accounting and free only. Module exit unregisters the link kind and lets netdev core clean devices.

## State and Persistence
State is netdev core state: per-CPU TX stats, carrier, MAC, feature flags, and device instances. `numdummies` is a load-time module parameter. Devices are freed by netdev core through `needs_free_netdev`.

## Dependencies and Integration Points
The driver uses rtnetlink, Ethernet helpers, ethtool timestamp info, netdev lightweight stats, skb timestamping, and `MODULE_ALIAS_RTNL_LINK("dummy")`.

## Risks and Edge Cases
Since TX always succeeds while dropping packets, dummy devices can mask routing mistakes. The multicast callback is intentionally empty. Initial automatic devices are only created in `init_net`; other namespaces use rtnetlink.

## Test Signals
Load with varied `numdummies`, create/delete with `ip link`, validate MAC errors, toggle carrier, check TX counters, inspect ethtool timestamp info, and unload cleanly.
