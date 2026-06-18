# sources/distributed-fs/ceph-client/net/mac802154/iface.c

## Purpose
`iface.c` implements mac802154 net_device lifecycle, interface creation/removal, WPAN and monitor netdev operations, MAC address/ioctl handling, hardware startup settings, concurrent-interface checks, IEEE 802.15.4 header creation/parsing, LLSEC parameter synchronization, and netdev rename tracking.

## Important APIs, Types, And Functions
Externally used functions include `mac802154_wpan_update_llsec()`, `ieee802154_if_add()`, `ieee802154_if_remove()`, `ieee802154_remove_interfaces()`, `ieee802154_iface_init()`, and `ieee802154_iface_exit()`. Netdev operations are `mac802154_wpan_open()`, `mac802154_slave_close()`, `ieee802154_subif_start_xmit`, `ieee802154_monitor_start_xmit`, `mac802154_wpan_ioctl()`, and `mac802154_wpan_mac_addr()`. Header operations are `ieee802154_header_create()`, `mac802154_header_create()`, and `mac802154_header_parse()`. Setup helpers include `ieee802154_setup_hw()`, `ieee802154_check_concurrent_iface()`, `ieee802154_if_setup()`, and `ieee802154_setup_sdata()`.

## Control Flow
Interface creation allocates a netdev with `ieee802154_if_setup()`, reserves headroom, allocates a name, chooses ARPHRD type by nl802154 iftype, sets device/net namespace, initializes `sdata` and embedded `wpan_dev`, performs type-specific setup, registers the netdev, and appends it to `local->interfaces` under `iflist_mtx` with RCU list semantics. Removal deletes from the list, synchronizes RCU, and unregisters the netdev.

Open flow checks concurrent running interfaces. Non-monitor interfaces cannot run concurrently with another non-monitor interface, and monitor coexistence requires identical MAC-layer settings when a single PHY setting would be shared. The first open interface replays hardware-backed settings with `ieee802154_setup_hw()` and starts the driver with the interface's required filtering. Close flow aborts scan/beacon activity when active, stops the netdev queue, decrements `open_count`, clears running state, and stops hardware when the last interface closes.

Header creation builds IEEE 802.15.4 frame control, sequence numbers, security fields from LLSEC params and skb control block overrides, source/destination addressing, and validates payload length against maximum payload. The generic netdev header path assumes extended addresses and intra-PAN addressing for datagram sockets. Header parse extracts a long source address when present.

## State And Persistence
Runtime state includes `local->open_count`, `sdata->state`, `sdata->required_filtering`, `local->addr_filt`, `wpan_dev` addressing/default MAC parameters, LLSEC params, netdev address fields, lowpan child address synchronization, and cached `sdata->name`. State exists only while netdevs/local PHY exist.

## Dependencies And Integration Points
The file depends on Linux netdevice APIs, nl802154/cfg802154, IEEE802.15.4 header helpers, `driver-ops.h`, LLSEC, MLME ops, TX entry points from `tx.c`, scan/beacon helpers, RTNL, RCU, and the netdevice notifier chain. It is the primary bridge between user-visible network interfaces and the mac802154 local/driver stack.

## Risks And Edge Cases
`mac802154_wpan_ioctl()` supports a debugging SIOCSIFADDR path and refuses changes while running, but still offers an older ioctl-based address path that can diverge from netlink expectations. `mac802154_wpan_mac_addr()` must keep lowpan device MAC addresses in sync and rejects changes while either WPAN or lowpan is running. `ieee802154_if_remove()` returns early if the global interface list is empty, but it does not explicitly verify the target is present before deletion in non-empty lists. `mac802154_slave_open()` sets the running bit before hardware setup and clears it on failure; first-open driver start failures must not leave `local->started` inconsistent with `driver-ops.h`.

Header creation depends on skb headroom and correct LLSEC parameter state. Security override combinations can reject frames when security is globally disabled or a zero security level is forced. Payload length is checked after pushing the header, so callers see an error after skb mutation.

## Test Signals
Tests should cover interface add/remove for node/coord/monitor, open/close first and last interface, concurrent monitor/non-monitor compatibility, driver setup failure rollback, ioctl and MAC address validation, lowpan address propagation, LLSEC parameter update calls, secure and insecure header creation, payload-too-large errors, header parse on malformed packets, netdev rename notifications, and RCU/list cleanup under unregister.
