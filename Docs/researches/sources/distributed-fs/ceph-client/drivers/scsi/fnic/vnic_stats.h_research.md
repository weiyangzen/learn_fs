# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_stats.h

## Purpose

`vnic_stats.h` defines firmware-populated vNIC transmit and receive statistics structures used by FNIC/ENIC-style stats dump commands.

## Important APIs, types, and data

- `struct vnic_tx_stats` contains successful frame/byte counters by traffic type, drops, errors, TSO count, and reserved expansion fields.
- `struct vnic_rx_stats` contains receive frame/byte counters, drops, no-buffer count, errors, RSS count, CRC errors, frame-size buckets, and reserved expansion fields.
- `struct vnic_stats` groups TX and RX stats for `CMD_STATS_DUMP`.

## Control flow

`vnic_dev_stats_dump()` allocates coherent `struct vnic_stats` memory and asks firmware to fill it. Higher-level code formats or exports the counters.

## State and persistence behavior

The stats memory is DMA-coherent and persists while the vNIC device object holds it. Counter values are firmware snapshots and can be cleared through `CMD_STATS_CLEAR`.

## Dependencies and integration points

It depends only on fixed-width integer types. It is used by `vnic_dev.c` and FNIC debug/stat reporting paths.

## Risks and edge cases

- Structure layout is firmware ABI; changing field order or size would break stats dumps.
- Reserved fields must remain reserved for compatibility.
- Counters are raw 64-bit firmware values; callers must handle wrap or reset semantics externally.

## Test signals

Stats tests should verify `CMD_STATS_DUMP` fills expected fields, `CMD_STATS_CLEAR` resets counters, and formatted output handles large 64-bit values.
