# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_stats.h

## Purpose
`vnic_stats.h` defines the firmware statistics block returned by Cisco vNIC stats dump commands.

## Important APIs, types, and functions
- `struct vnic_tx_stats` contains TX frame/byte counters, drops, errors, and TSO count.
- `struct vnic_rx_stats` contains RX frame/byte counters, drops/no-buffer/errors/RSS/CRC, and size-bucket counters.
- `struct vnic_gen_stats` defines a generic DMA map error counter but is not included in `struct vnic_stats` here.
- `struct vnic_stats` combines TX and RX stats.

## Control flow and state
`vnic_dev_stats_dump()` allocates a coherent `struct vnic_stats` and passes its DMA address to firmware. Firmware writes this structure; the driver reads counters later.

## Dependencies and integration points
ENIC ethtool/statistics paths depend on this ABI. It is tied to `CMD_STATS_DUMP` and firmware counter layout.

## Risks and test signals
Struct layout drift or wrong size in devcmd corrupts stats reporting. Test with ethtool stats under traffic, counter rollover expectations, and firmware stats dump failure handling.
