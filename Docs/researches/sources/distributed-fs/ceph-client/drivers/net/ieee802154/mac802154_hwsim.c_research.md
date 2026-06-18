# sources/distributed-fs/ceph-client/drivers/net/ieee802154/mac802154_hwsim.c

## Purpose
`mac802154_hwsim.c` is the newer IEEE 802.15.4 software radio simulator for mac802154. It creates simulated radios, forwards frames over directed graph edges, supports configurable link LQI, and exposes a generic-netlink control API for adding/removing radios and edges.

## Important APIs, types, and functions
State is split into `struct hwsim_phy`, RCU-protected `struct hwsim_pib`, directed `struct hwsim_edge`, and RCU-protected `struct hwsim_edge_info`. mac802154 operations are `hwsim_hw_xmit()`, `hwsim_hw_receive()`, ED/channel/filter/start/stop/promiscuous setters. Netlink commands are implemented by `hwsim_new_radio_nl()`, `hwsim_del_radio_nl()`, `hwsim_get_radio_nl()`, `hwsim_dump_radio_nl()`, `hwsim_new_edge_nl()`, `hwsim_del_edge_nl()`, and `hwsim_set_edge_lqi()`.

## Control flow
Module init registers the generic-netlink family, creates a platform device, and registers the platform driver. Probe creates two initial radios and subscribes them to one another. TX reads the sender PIB under RCU, walks outgoing edges, skips suspended endpoints, matches page/channel, clones the skb, and calls `hwsim_hw_receive()` on the endpoint. Receive optionally enforces level-4 IEEE 802.15.4 frame-field filtering before injecting into mac802154.

## State and persistence
All simulator topology and radio state is volatile. Radios have monotonically assigned IDs, a current PIB, suspended flag, and edge list. PIB and edge info updates allocate replacement objects and publish them with RCU.

## Dependencies and integration points
The driver integrates mac802154/cfg802154 with generic netlink, rtnetlink context for PIB updates, RCU, platform device infrastructure, skbuff cloning, and multicast notifications on a `config` group.

## Risks and test signals
Risks include RCU/list mutation correctness, validation gaps in nested netlink attributes, typo-sensitive ABI constants from the header, frame filtering divergence from hardware, and topology cleanup when deleting radios referenced by edges. Test signals include initial two-radio connectivity, netlink add/delete/get/dump radio, edge add/delete/set-LQI, channel filtering, promiscuous vs filtered receive, multicast notifications, and repeated module unload under active topology changes.
