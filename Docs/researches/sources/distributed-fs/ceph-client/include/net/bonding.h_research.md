# sources/distributed-fs/ceph-client/include/net/bonding.h

## Purpose
This is the common internal header for the Linux bonding driver. It defines the bond/slave core data structures, parameters, list traversal primitives, locking expectations, inline state transitions, monitoring helpers, transmit helpers, sysfs/proc/debug/netlink hooks, and mode integration points for 802.3ad, TLB, and ALB.

## Important APIs, Types, And Constants
- Slave list macros wrap lower-device adjacency lists and provide RTNL and RCU traversal variants.
- Netpoll helpers optionally block or query netpoll transmit under `CONFIG_NET_POLL_CONTROLLER`.
- `struct bond_params` stores user-configured mode, monitoring intervals, ARP/NS targets, LACP/ALB options, primary and failover behavior, peer notifications, transmit queue/hash parameters, and actor settings.
- `struct slave` stores the lower netdevice, parent bond, link timing, ARP receive timestamps, link state, active/backup/inactive/RX-disabled flags, speed/duplex, queue ID, permanent MAC, priority, 3ad/ALB per-slave state, netpoll, sysfs object, delayed notification work, and cached stats.
- `struct bonding` stores the master netdevice, active/current/primary slave RCU pointers, usable/all slave arrays, mode-specific locks, counters, work items, mode-specific state, params, debug/proc/sysfs hooks, IPsec state, and XDP program pointer.
- Inline helpers classify modes, read active slave, test link/transmit eligibility, set active/backup/inactive/RX-disabled flags, stage/commit link states, validate ARP/NS targets, read/write last TX/RX timestamps, propagate NAPI/netpoll data, and search slave MACs or target arrays.
- Exported functions cover enslave/release, transmit hashing, carrier updates, active slave selection, sysfs/debug/proc creation, XDP checks, netlink lifecycle, work initialization/cancel, VLAN path verification, slave array updates, and work rearming.

## Control Flow And State
Bond creation initializes `struct bonding`, parameters, work items, and mode-specific substructures. Enslaving attaches a lower netdevice, creates a `struct slave`, links it into lower adjacency lists, initializes mode-specific state, and exposes sysfs. Monitor work (`mii_work`, `arp_work`, `alb_work`, `ad_work`, multicast and notification work) updates link state and mode behavior. Inline state helpers queue lower-state and slave events immediately or defer notification by setting `should_notify`/`should_notify_link`. Transmit paths use mode-specific hash/selection functions and `bond_slave_can_tx()` to choose a usable slave or drop through `bond_tx_drop()`.

## State And Persistence Behavior
Bond and slave state is in-memory per net namespace. `bond_net` tracks namespace-level device lists and proc/sysfs roots. RCU protects active/current/primary slave pointers and slave arrays for read-side packet paths; RTNL protects slave-list mutation; `mode_lock` protects 3ad/TLB/ALB mode-specific state; `stats_lock` protects aggregate stats; optional `ipsec_lock` protects offload state. Parameters persist while the bond netdevice exists and are visible through sysfs/proc/netlink.

## Dependencies And Integration Points
The header depends on netdevice, timers, procfs, if_bonding UAPI, cpumask, IPv6, netpoll, inetdevice, etherdevice, reciprocal division, link attributes, bonding mode headers, XDP/BPF, and optional XFRM/debug/proc/netpoll features. It is included across `drivers/net/bonding/*` and exposes hooks to rtnetlink, sysfs, procfs, debugfs, XDP feature negotiation, netpoll, IPsec offload, IPv4 ARP, and IPv6 neighbor solicitation.

## Risks
- Locking rules are central: RCU reads, RTNL writes, and mode-specific spinlocks must be respected to avoid races in packet paths and workqueues.
- Inline state helpers both mutate flags and trigger notifications; incorrect `notify` usage can suppress or duplicate userspace/lower-state events.
- `bond_is_active_slave_dev()` assumes a valid slave pointer from `rx_handler_data`; callers must ensure the device is enslaved or guard against NULL in surrounding code.
- Link and active/backup flags drive transmit eligibility; divergence can cause traffic on down/inactive slaves or unnecessary drops.
- Parameters such as ARP/NS targets have fixed array limits and sentinel zero/any values that must be preserved.

## Test Signals
- Bonding tests should exercise enslave/release, all modes, active slave changes, carrier/min-links, ARP and NS monitoring, failover MAC policies, primary reselection, peer notifications, queue IDs, and transmit hashing.
- Concurrency tests should stress slave removal, work cancellation, RCU readers, netpoll, XDP program changes, and mode changes.
- ABI tests should cover sysfs/proc/netlink exposure of parameters and slave state.
