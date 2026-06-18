<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.h

## Purpose
Defines the Siena TX checksum-offload queue classifier used by the TX hot path to choose normal, inner-checksum, and outer-checksum TX queue types.

## Important APIs, Types, And Functions
- `efx_tx_csum_type_skb()` returns a bitmask of `EFX_TXQ_TYPE_OUTER_CSUM` and/or `EFX_TXQ_TYPE_INNER_CSUM`.
- Encapsulation handling distinguishes inner checksum offload from outer UDP tunnel checksum offload for GSO tunnel packets.

## Control Flow
The helper returns zero for SKBs without `CHECKSUM_PARTIAL`. For encapsulated packets whose checksum starts at the inner transport header, it selects inner checksum offload and adds outer checksum offload only for multi-segment UDP tunnel checksum GSO without `SKB_GSO_PARTIAL`. Non-encapsulated partial checksums use outer checksum offload.

## State And Persistence Behavior
The helper is stateless and only inspects SKB metadata. Its output affects transient TX queue selection in `efx_siena_hard_start_xmit()`.

## Dependencies And Integration Points
Depends on Linux SKB checksum/GSO helpers and EFX TXQ type constants. It is included by Siena `tx.c`.

## Risks And Test Signals
The function assumes advertised netdev features restrict packets to supported IPv4/IPv6 checksum cases. Test signals include encapsulated TCP/UDP GSO, UDP tunnel checksum offload, partial vs non-partial checksums, and correct TXQ selection without `WARN_ON_ONCE(!tx_queue)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.h -->
