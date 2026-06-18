# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map_data.c

Purpose: Implements RMNET MAP data-plane mechanics: MAP header insertion, ingress deaggregation, downlink checksum validation, uplink checksum metadata generation, MAPv5 next-header processing, and uplink TX aggregation.

Important APIs and functions: `rmnet_map_add_map_header()` pushes MAP headers and optional padding. `rmnet_map_deaggregate()` extracts one MAP packet from an aggregate skb. `rmnet_map_checksum_downlink_packet()` validates CKSUMV4 trailers. `rmnet_map_checksum_uplink_packet()` dispatches CKSUMV4 or CKSUMV5 metadata generation. `rmnet_map_process_next_hdr_packet()` handles MAPv5 checksum headers. `rmnet_map_tx_aggregate()`, `rmnet_map_tx_aggregate_init()`, `rmnet_map_update_ul_agg_config()`, and `rmnet_map_tx_aggregate_exit()` manage uplink aggregation.

Control flow: Downlink CKSUMV4 validates IPv4 header checksum, rejects fragments, supports TCP/UDP, handles optional IPv4 UDP checksum zero, and compares trailer checksum to pseudo-header complement. IPv6 validation is compiled behind `CONFIG_IPV6` and rejects extension-header cases by only looking at `nexthdr`. Uplink CKSUMV4 pushes a UL checksum header for CHECKSUM_PARTIAL packets and complements transport checksum fields; otherwise it zeros the metadata and counts software checksum. MAPv5 pushes or consumes a next header and uses a validity bit to set `CHECKSUM_UNNECESSARY`. Aggregation either sends immediately, copies a first skb into a larger aggregate buffer, appends later skbs via frag_list, and flushes on count, byte, or timer thresholds.

State and persistence: Stats are updated in `rmnet_priv->stats`. Aggregation state persists in `struct rmnet_port`: `skbagg_head`, tail, count, state, time stamps, hrtimer, work item, spinlock, and `egress_agg_params`. Exit cancels timer/work and frees a pending aggregate.

Dependencies and integration: Uses SKB helpers, checksum helpers from IPv4/IPv6 stacks, hrtimers/workqueues, and port configuration from ethtool coalescing.

Risks and test signals: High-risk areas are packet length/padding math, MAPv5 invalid next-header behavior, IPv6 extension-header limitations, aggregation ownership of SKBs, timer/work races, and linearization failure handling. Tests should include IPv4/IPv6 TCP/UDP checksum pass/fail, fragments, unsupported protocols, aggregate boundary sizes, sparse traffic bypass, timer flush, count flush, and teardown with pending aggregate.
