<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.c

## Purpose
Owns EF100 netdevice creation, registration, open/stop, transmit entry, notifier integration, and netdevice teardown. It bridges PCI/NIC probe state from `ef100.c` and `ef100_nic.c` into the Linux networking stack.

## Important APIs, Types, And Functions
- `ef100_probe_netdev()` allocates `alloc_etherdev_mq()`, configures features, probes datapath caps/PHY/channels/filter table, gets MAC address, registers devlink/netdev/notifiers, and performs PF-only MAE/SR-IOV setup.
- `ef100_remove_netdev()` closes and unregisters the netdevice, disables SR-IOV, tears down devlink/TC/filter/channel/PHY state, and frees `net_device`.
- `ef100_net_open()` and `ef100_net_stop()` implement interface up/down.
- `__ef100_hard_start_xmit()` is shared by the PF netdevice and representor TX path.
- `ef100_netdev_ops`, `ef100_netdev_event()`, and `ef100_netevent_event()` integrate Linux netdev and netevent callbacks.

## Control Flow
Probe exits early when firmware reports no active network port. Otherwise it allocates a netdev with private storage pointing back to `efx_probe_data`, enables supported offloads except RX-FCS/RX-all by default, applies TSO limits from EF100 design parameters, initializes caps/PHY/channels/filtering/RSS/MAC/devlink, registers the netdev, runs PF-only representor/TC/devlink-port setup, then registers netdevice and netevent notifiers. Open probes interrupts, sizes channels, frees/reallocates VIs, retries with fewer channels when VI allocation is short, probes channels, remaps the BAR to allocated VI count, initializes NAPI/filters/interrupts/stats, starts queues, polls PHY, and attaches representors. Stop detaches representors, stops queues, shuts down datapath/statistics/interrupts/filters/NAPI/channels/VIs in reverse order.

## State And Persistence
State includes the allocated `net_device`, `efx->name`, feature flags, queue limits, registered notifier blocks, devlink lock/registration state, filter table, channels, PHY data, interrupt resources, and `efx->state` transitions among probed, net down, and net up. No disk persistence exists; state is kernel runtime plus firmware allocations.

## Dependencies And Integration Points
Depends on common SFC netdev helpers, MCDI port/filter functions, EF100 NIC functions, EF100 TX implementation, EF100 ethtool ops, SR-IOV, TC/MAE, encap actions, RX common code, Linux notifier APIs, rtnl locking, and devlink helpers. Representor TX calls `__ef100_hard_start_xmit()` from `ef100_rep.c`.

## Risks And Edge Cases
Probe failure after partial devlink registration or notifier setup requires careful cleanup; this file mostly jumps to `fail` and relies on remove-style cleanup. VI allocation retry changes `efx->max_channels`, so channel/interrupt assumptions must be recalculated. `ef100_net_open()` returns directly on `efx_probe_channels()` failure rather than going through `fail`, which is notable for cleanup review. TX drops always return `NETDEV_TX_OK` after freeing the skb and incrementing stats. Notifier forwarding is conditional on MAE privilege.

## Test Signals
Signals include netdevice registration/unregistration, `ip link set up/down`, interrupt allocation, NAPI creation, VI shortage retry behavior, TX under normal and no-channel conditions, RSS default table programming, MAC address provisioning for PF/VF, devlink registration, SR-IOV disable on removal, and TC/netevent callbacks when `grp_mae` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.c -->
