<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.h

## Purpose
`rmnet_config.h` defines the shared RMNET configuration data structures for real-device ports, mux endpoints, aggregation state, virtual device stats, private netdev state, and configuration helper prototypes.

## Important APIs, Types, and Data
- `RMNET_MAX_LOGICAL_EP` limits mux endpoint buckets to 255.
- `struct rmnet_endpoint` maps a mux ID to an egress virtual netdev and hlist node.
- `struct rmnet_egress_agg_params` and aggregation fields in `struct rmnet_port` track MAP egress aggregation.
- `struct rmnet_port` represents one real device registered with rmnet, including data format, mode, mux endpoint buckets, bridge links, rmnet device pointer, aggregation locks/timers/work, and counts.
- `struct rmnet_vnd_stats`, `struct rmnet_pcpu_stats`, and `struct rmnet_priv_stats` hold virtual-device and checksum statistics.
- `struct rmnet_priv` is per-rmnet-netdev private state with mux ID, real device, percpu stats, GRO cells, and checksum stats.
- Declares rtnl ops and configuration helpers.

## Control Flow
The header contains no executable flow. It defines state that data-path handlers, virtual-device code, MAP aggregation, and rtnetlink configuration code share.

## State and Persistence
`struct rmnet_port` persists while a real device is associated with rmnet. `struct rmnet_priv` persists for each virtual rmnet netdev. Aggregation timers/work and skb aggregation pointers persist across packets until flushed.

## Dependencies and Integration Points
Includes skb/time and GRO cells support. It is included by config, handlers, virtual-device, MAP data, and MAP command files.

## Risks and Edge Cases
- Aggregation state has its own spinlock and timer/work items; cleanup ordering must cancel or flush them before freeing the port.
- `muxed_ep` uses 255 hlist heads, so mux ID validation must reject 255 and higher.
- Statistics mix u64 sync-protected per-CPU counters and plain private counters; readers must use matching synchronization.
- Bridge and virtual-device modes share fields in `struct rmnet_port`, so mode transitions must be explicit.

## Test Signals
Creating/deleting rmnet links, data-path demux by mux ID, aggregation flush/cleanup, GRO cell behavior, and per-CPU stats reads validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.h -->
