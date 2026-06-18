# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/cmsg.c

## Purpose
This file allocates, sends, queues, and dispatches NFP Flower control messages between host driver and firmware. It covers representor port modification/reification, MAC representor advertisement, firmware control-message RX dispatch, MTU acknowledgement handling, merge hints, tunnel neighbor events, QoS stats, and LAG retransmission handling.

## Important APIs, types, and functions
- `nfp_flower_cmsg_alloc()` creates a control skb with `struct nfp_flower_cmsg_hdr`.
- `nfp_flower_cmsg_mac_repr_start()` and `nfp_flower_cmsg_mac_repr_add()` build the physical MAC representor advertisement.
- `nfp_flower_cmsg_portmod()` notifies firmware of link/MTU state; `nfp_flower_cmsg_portreify()` asks firmware to create/destroy a port representation.
- `nfp_flower_cmsg_rx()` is the immediate RX entry from `app_flower.ctrl_msg_rx`.
- `nfp_flower_cmsg_process_rx()` drains high-priority then low-priority queues and dispatches each deferred message.
- Internal handlers process MTU ACKs, portmod link updates, portreify ACKs, and merge hints.

## Control flow
Outgoing messages allocate an skb, fill the Flower header and type-specific payload, then call `nfp_ctrl_tx()`. Incoming messages first validate version. Flow stats, MTU ACKs, tunnel-neighbor ACKs, and port reify ACKs are handled immediately because they are urgent or avoid RTNL/workqueue deadlocks. Other messages are queued into high priority (`PORT_MOD`) or low priority queues with a hard length cap and processed by `cmsg_work`. The work item splices both queues locally before dispatch, so producers can continue queuing while processing runs.

## State and persistence
The file manages in-memory skb queues, wait/ack state in `priv->mtu_conf`, and counters such as `reify_replies`. Messages may be consumed, freed, or stored by the LAG layer for retransmission. No persistent state is written.

## Dependencies and integration points
It integrates with `nfp_app_ctrl_msg_alloc()`, `nfp_ctrl_tx()`, representor lookup, RTNL/RCU netdev handling, tunnel route/keepalive helpers, Flower stats and QoS handlers, flow merge, LAG, and the structures/constants in `cmsg.h`.

## Risks
Queue overload drops control messages after `NFP_FLOWER_WORKQ_MAX_SKBS`, which protects memory but may delay firmware synchronization until higher-level recovery. Portmod RX takes RTNL and changes carrier/MTU, so immediate MTU ACK handling is intentionally separate. Merge hints are advisory but must hold `nfp_fl_lock` while looking up subflows. LAG may retain skbs, so ownership is conditional via `skb_stored`.

## Test signals
Test valid/invalid cmsg versions, high-priority portmod ordering, MTU ACK wait wakeup, reify wait wakeup, queue overflow warnings, merge-hint validation for wrong flow counts/lengths, tunnel request dispatch, and LAG data/XON/SYNC messages retaining or consuming skbs correctly.
