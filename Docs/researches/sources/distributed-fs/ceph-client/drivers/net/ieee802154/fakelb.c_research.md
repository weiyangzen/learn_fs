# sources/distributed-fs/ceph-client/drivers/net/ieee802154/fakelb.c

## Purpose
`fakelb.c` implements a deprecated in-kernel IEEE 802.15.4 loopback simulator. It creates a configurable number of fake mac802154 PHYs and forwards transmitted frames to other running fake PHYs on the same page/channel.

## Important APIs, types, and functions
`struct fakelb_phy` holds an `ieee802154_hw`, current page/channel, suspended state, and list nodes for all PHYs and currently-ifup PHYs. The mac802154 operations are `fakelb_hw_xmit()`, `fakelb_hw_ed()`, `fakelb_hw_channel()`, `fakelb_hw_start()`, `fakelb_hw_stop()`, and a no-op promiscuous setter. Module setup is handled by `fakelb_init_module()`, `fakelb_probe()`, `fakelb_add_one()`, and teardown by `fakelb_remove()`/`fakelb_del()`.

## Control flow
Module init registers a platform device and platform driver. Probe creates `numlbs` fake radios, initializes broad channel support across many 802.15.4 pages, registers each hw, and links it into `fakelb_phys`. Start adds a PHY to the ifup list; stop removes it. Transmit walks the ifup list under a read lock, clones the skb for every peer with matching page/channel, injects clones with `ieee802154_rx_irqsafe()`, then completes the original transmit.

## State and persistence
State is entirely in RAM: global PHY lists, current channel/page, and suspended/ifup membership. There is no configuration persistence beyond the module parameter `numlbs`.

## Dependencies and integration points
The file integrates with platform devices, mac802154/cfg802154, netdevice/skbuff APIs, module parameters, mutexes, and rwlocks. It is functionally replaced by `mac802154_hwsim`.

## Risks and test signals
Risks include deprecated behavior diverging from real filtering, no real promiscuous semantics, global list teardown interactions while devices are up, and possible skb clone allocation failure silently dropping peer delivery. Tests should validate module load/unload, `numlbs` creation, channel isolation, start/stop list membership, multi-peer loopback delivery, and removal while interfaces are down/up.
