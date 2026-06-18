## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/core.c

Purpose: rtnetlink and netdevice integration for `lowpan` interfaces backed by IEEE 802.15.4 WPAN devices. It creates/deletes virtual lowpan netdevices, registers packet receive support and fragment infrastructure, and tears lowpan devices down when the underlying WPAN device is unregistered.

Important APIs/types/functions: `lowpan_setup()` initializes broadcast address, hard header length, flags, no-queue private flag, netdev/header ops, free-on-unregister, and netns immutability. `lowpan_newlink()` validates `IFLA_LINK`, resolves an `ARPHRD_IEEE802154` backing device, rejects duplicate lowpan attachment, copies hardware address, calculates headroom/tailroom, sets neighbor private size, registers through `lowpan_register_netdevice()`, and stores the reverse pointer in `wdev->ieee802154_ptr->lowpan_dev`. `lowpan_dellink()` clears that pointer, unregisters, and drops the held backing dev reference. `lowpan_open()` and `lowpan_stop()` maintain global `open_count` and install/remove packet handlers through `lowpan_rx_init()`/`lowpan_rx_exit()`.

Control flow and state: module init first initializes fragment infrastructure, then registers rtnl link ops, then netdevice notifier. On lower WPAN `NETDEV_UNREGISTER`, the notifier deletes the attached lowpan interface if present. Open lowpan interfaces share one packet_type registration tracked by `open_count`.

Dependencies and integration points: integrates with rtnl link kind `lowpan`, generic lowpan registration, IEEE 802.15.4 netdevice private state, IPv6 header size, netdevice notifier chain, and 6LoWPAN fragment subsystem.

Risks: `open_count` is global and not visibly locked in this file; open/stop are serialized by netdevice core but changes must preserve that assumption. `lowpan_dellink()` can be called from notifier context with `head == NULL`; any unregister behavior changes must preserve safe deletion. The lowpan device is netns immutable because the backing phy/device relationship is fixed.

Test signals: `ip link add link wpanX name lowpanX type lowpan`, duplicate lowpan rejection, deletion, backing-device unregister auto-cleanup, open/close packet handler registration, and module load/unload under active/inactive devices.
