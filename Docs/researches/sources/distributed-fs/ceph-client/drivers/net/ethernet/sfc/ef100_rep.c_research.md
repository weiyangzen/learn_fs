<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.c

## Purpose
Implements EF100 VF representor netdevices for MAE/TC switching. Representors expose per-VF Linux netdevices, support TC flower/block offload binding, transmit through the parent EF100 TX path with representor context, receive packets queued from the parent RX path, and maintain software stats/devlink-port integration.

## Important APIs, Types, And Functions
- Netdev ops: `efx_ef100_rep_open()`, `efx_ef100_rep_close()`, `efx_ef100_rep_xmit()`, `efx_ef100_rep_get_port_parent_id()`, `efx_ef100_rep_get_phys_port_name()`, `efx_ef100_rep_setup_tc()`, `efx_ef100_rep_get_stats64()`.
- Lifecycle: `efx_ef100_vfrep_create()`, `efx_ef100_vfrep_destroy()`, `efx_ef100_fini_vfreps()`, `efx_ef100_init_reps()`, `efx_ef100_fini_reps()`.
- RX queueing: `efx_ef100_rep_rx_packet()` and NAPI poll `efx_ef100_rep_poll()`.
- Lookup/helpers: `efx_ef100_find_rep_by_mport()`, `ef100_mport_on_local_intf()`, `ef100_mport_is_vf()`.

## Control Flow
Creation allocates an etherdev with `struct efx_rep` private state, initializes lists/locks/default rule fields, adds it to `efx->vf_reps`, sets carrier/queue state based on the parent netdevice, configures netdev/ethtool ops, looks up the VF mport, configures a default TC rule, binds a devlink port, and registers the netdev. TX increments attempted TX stats and calls `__ef100_hard_start_xmit()` under the parent TX lock. RX copies a parent RX buffer into a new skb, queues it on `efv->rx_list`, and schedules NAPI; poll drains up to weight and reschedules if producer state advanced during delivery. Destruction unregisters the netdev, removes devlink/default rule/list membership, synchronizes RCU, and frees the netdev.

## State And Persistence
Representor state lives in `struct efx_rep`: parent pointer, netdev, message mask, mport, VF index, pseudo-ring write/read counters and size, default TC rule, list node, skb queue, spinlock, NAPI, atomic software stats, and devlink port pointer. This is runtime-only and tied to the parent PF/MAE lifetime.

## Dependencies And Integration Points
Depends on rhashtable for MAE mport cleanup, EF100 netdev shared TX, EF100 NIC private data, MAE enumeration/lookup, RX common buffers, TC bindings, and devlink helpers. It integrates with Linux representor semantics through port parent ID/name, TC setup, ethtool stats/ringparam, NAPI, and netdev registration.

## Risks And Edge Cases
The pseudo RX ring uses unsigned write/read arithmetic and drops when backlog exceeds `rx_pring_size`; very large user-set ring sizes can change memory pressure. RX copies with `GFP_ATOMIC`-style netdev allocation and drops on allocation failure. Lookup requires caller RCU protection plus internal list spinlock. TX stats count attempts, not success. Creation failure paths must undo devlink/default rules/list membership in the right order.

## Test Signals
Create/destroy VFs with MAE privilege, verify representor netdevices and devlink ports, check phys port names like `p%upf%uvf%u`, run traffic through VF representors, inspect software stats, exercise TC flower/block offloads, adjust representor RX ringparam, force RX backlog drops, and remove the parent PF while representors exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.c -->
