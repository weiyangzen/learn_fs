# sources/distributed-fs/ceph-client/net/ncsi/ncsi-manage.c

## Purpose
This file is the NCSI device manager. It owns package/channel discovery, request allocation, link monitoring, channel selection, VLAN/filter programming, OEM command sequencing, reset/suspend/configure state machines, public device lifecycle APIs, and VLAN notifier entry points.

## APIs, Types, and Functions
Externally visible functions include `ncsi_channel_has_link()`, `ncsi_channel_is_last()`, monitor start/stop, topology lookup/add/remove helpers, request allocation/freeing, `ncsi_find_dev()`, `ncsi_process_next_channel()`, `ncsi_update_tx_channel()`, VLAN add/kill exports, `ncsi_register_dev()`, `ncsi_start_dev()`, `ncsi_stop_dev()`, `ncsi_reset_dev()`, and `ncsi_unregister_dev()`. Major static subsystems are `ncsi_channel_monitor()`, `ncsi_request_timeout()`, `ncsi_suspend_channel()`, VLAN filter helpers, OEM GMA/keep-PHY/SMAF helpers, `ncsi_configure_channel()`, `ncsi_choose_active_channel()`, `ncsi_check_hwa()`, `ncsi_probe_channel()`, `ncsi_dev_work()`, and `ncsi_kick_channels()`.

## Control Flow
Drivers call `ncsi_register_dev()` to allocate `ncsi_dev_priv`, initialize requests/timers/work, add the device to the global list, and register an `ETH_P_NCSI` packet handler. `ncsi_start_dev()` launches probing if topology has not been discovered. Probe flow deselects all packages, selects each package, discovers channels with CIS/GVI/GC/GLS, optionally sends Mellanox or Intel OEM commands, deselects packages, then checks hardware arbitration and chooses active channels.

Configuration flow selects a package, clears initial state, optionally retrieves/applies firmware MAC, clears and sets VLAN filters, enables/disables VLAN mode, programs MAC, broadcast and multicast filters, enables TX if selected, enables channel and AEN, reads link status, marks the channel active, starts the monitor, and moves to the next queued channel. Suspend flow selects the package, optionally refreshes link status, disables TX, disables channel, optionally deselects the package, marks the channel inactive, and resumes reset or queue processing. Link monitors periodically send GLS and force reshuffle if a channel stops responding.

## State and Persistence
Persistent state is in `ncsi_dev_priv`, global `ncsi_dev_list`, package/channel lists, request table, VLAN list, active package/channel pointers, `hot_channel`, whitelists, multi-package/channel flags, reset/reshuffle flags, and per-channel filters/modes/monitor timers. Requests persist from command transmit until response or timeout; event-driven request completion decrements `pending_req_num` and schedules the workqueue when a state step is complete.

## Dependencies and Integration
The file integrates with Ethernet drivers through exported NCSI lifecycle APIs, with packet RX through `ncsi_rcv_rsp`, with command TX through `ncsi_xmit_cmd`, with netlink through shared topology and reset helpers, with device tree for Mellanox multi-host detection, and with rtnetlink for MAC assignment. It uses spinlocks, RCU lists, timers, workqueues, skb packet handlers, and VLAN callbacks.

## Risks
This is the highest-risk NCSI file because it combines asynchronous timers, response callbacks, workqueue state machines, netlink mutations, and driver lifecycle. Race-prone areas include request timeout versus response receipt, resetting while config/suspend is in progress, queueing channels under different locks, VLAN list updates while configuration reads it, and unregister while work/timers/packet handlers are active. OEM stack-local payload buffers are safe only because transmission copies synchronously into skb before returning.

## Test Signals
Strong signals include emulated NCSI devices for successful and partial probe, request timeout handling, reset during config, AEN-triggered reshuffle, multi-package hardware-arbitration mode, preferred channel and mask changes through netlink, VLAN add/remove reconfiguration, MAC retrieval/application, channel monitor timeout, and clean unregister with no live timers or work.
