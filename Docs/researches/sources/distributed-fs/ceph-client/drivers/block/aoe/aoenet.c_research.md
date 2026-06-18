# sources/distributed-fs/ceph-client/drivers/block/aoe/aoenet.c

Purpose: network transport layer for AoE. It filters allowed interfaces, queues transmit skbs to a dedicated kthread, registers an Ethernet packet handler for `ETH_P_AOE`, validates incoming AoE responses, dispatches ATA/config responses, and exposes the `aoe_iflist` module/boot parameter.

Important APIs and functions: `is_aoe_netif()` checks whether a net_device is allowed by the whitespace/comma-separated `aoe_iflist`. `set_aoe_iflist()` updates that list from userspace. `aoenet_xmit()` moves skbs from caller queues to the global transmit queue and wakes the tx kthread. `tx()` drains `skbtxq` and calls `dev_queue_xmit()`, dropping netdev refs after send. `aoenet_rcv()` is the packet_type receive callback; it ensures init_net, allowed interface, sufficient header linearization, response bit, non-user tag, no AoE error, and dispatches by command. `aoenet_init/exit()` set up the tx queue/kthread and packet handler.

Control flow: transmit callers prepare skbs with `skb->dev` held, call `aoenet_xmit()`, and return; the tx kthread serially sends packets. Receive path gets all AoE Ethernet packets from `dev_add_pack()`, shares/checks skb, pushes Ethernet header back into length accounting, handles protocol errors, then calls `aoecmd_ata_rsp()` or `aoecmd_cfg_rsp()`. ATA response handling may consume the skb asynchronously; config handling is synchronous.

State and persistence: global state includes `aoe_iflist`, tx waitqueue, `ktstate`, `txlock`, and `skbtxq`. Interface filtering persists until module parameter/user write changes it.

Dependencies and integration points: depends on Linux netdevice packet handlers, init network namespace, sk_buffs, `dev_queue_xmit()`, netdev refs, AoE protocol structures, char control path for interface list updates, and command response handlers.

Risks: only `init_net` is supported. Misconfigured `aoe_iflist` can hide devices or transmit on unintended interfaces when empty means all interfaces. Receive path drops vendor commands silently and logs protocol errors rate-limited. Test signals include interface allowlist parsing, packet receive on allowed/disallowed netdevs, tx queue drain under drops, AoE error packet logging, ATA/config dispatch, and cleanup after packet handler removal.
