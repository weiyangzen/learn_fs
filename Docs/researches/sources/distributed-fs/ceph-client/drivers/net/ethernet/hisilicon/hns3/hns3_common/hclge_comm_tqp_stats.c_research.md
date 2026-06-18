# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_tqp_stats.c

## Purpose

`hclge_comm_tqp_stats.c` implements shared per-TQP queue statistics helpers. It exposes ethtool stat values and names for TX/RX queue packet counters, updates cached counters by querying firmware for each queue, and resets cached TQP stats.

## Important Functions

- `hclge_comm_tqps_get_stats()` writes all TX queue packet counters followed by all RX queue packet counters into an ethtool data buffer.
- `hclge_comm_tqps_get_sset_count()` reports `num_tqps * 2`.
- `hclge_comm_tqps_get_strings()` emits stat names like `txq%u_pktnum_rcd` and `rxq%u_pktnum_rcd` using each TQP global index.
- `hclge_comm_tqps_update_stats()` loops over each TQP, sends `HCLGE_OPC_QUERY_RX_STATS` and `HCLGE_OPC_QUERY_TX_STATS`, and accumulates returned 32-bit descriptor values into 64-bit cached counters.
- `hclge_comm_reset_tqp_stats()` zeroes each cached TQP stats struct.

## Control Flow

Update flow obtains `handle->kinfo`, converts each `struct hnae3_queue *` back to `struct hclge_comm_tqp` with `container_of()`, sends a read command with the TQP index in descriptor data word zero, and adds firmware data word one to the cached RX/TX counter. Query flow does not contact hardware; it reads the cached values in stable TX-then-RX order.

## State and Persistence Behavior

The persistent state is `struct hclge_comm_tqp::tqp_stats`, held in memory per queue. Hardware appears to return 32-bit packet count deltas or readings; this module accumulates them into 64-bit software counters. Resetting stats clears only the cached software values. No on-disk state exists.

## Dependencies and Integration Points

The module depends on `hnae3_handle::kinfo.num_tqps` and `kinfo.tqp`, the common command queue, TQP stat opcodes from `hclge_comm_cmd.h`, `struct hclge_comm_tqp` from the companion header, and ethtool string formatting. It integrates with backend ethtool stats paths.

## Risks and Edge Cases

- The code assumes every `kinfo.tqp[i]` points to the embedded `q` member of a valid `struct hclge_comm_tqp`.
- A command failure returns immediately, leaving later queues stale and earlier queues already updated.
- Accumulating `desc.data[1]` without wrap handling details relies on firmware semantics.
- No explicit locking protects stats while updates and ethtool reads occur in this file.
- Name/count/order must remain synchronized with any caller-provided stat buffers.

## Test Signals

Validation should cover ethtool stat count and names, TX/RX ordering, successful per-queue firmware command traffic, partial failure behavior, reset-to-zero behavior, counter monotonicity under traffic, and race checks during concurrent stat update/read paths.
