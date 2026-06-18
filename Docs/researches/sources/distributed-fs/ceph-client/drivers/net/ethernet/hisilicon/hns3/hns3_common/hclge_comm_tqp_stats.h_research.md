# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_tqp_stats.h

## Purpose

`hclge_comm_tqp_stats.h` defines the shared TQP stats data structures and public helper APIs used by HNS3 PF/VF code to expose per-queue packet counters through ethtool.

## Important APIs and Types

- `HCLGE_COMM_QUEUE_PAIR_SIZE` documents that each TQP contributes two stats: TX and RX.
- `struct hclge_comm_tqp_stats` stores cached 64-bit software counters for TX and RX packet records queried through firmware opcodes `0x0B03` and `0x0B13`.
- `struct hclge_comm_tqp` embeds the generic `struct hnae3_queue`, device pointer, stats, global queue index, and allocation flag.
- Public prototypes cover stats extraction, string-set count, stat name emission, firmware update, and reset.

## Control Flow and Integration

The header establishes the container layout used by `container_of(kinfo->tqp[i], struct hclge_comm_tqp, q)`. Backend code allocates TQPs as `struct hclge_comm_tqp`, exposes their embedded `hnae3_queue` through `hnae3_knic_private_info::tqp`, and calls these helpers from ethtool stats operations.

## State and Persistence Behavior

Per-TQP stats and allocation state are in-memory driver state. The embedded `hnae3_queue` ties the common stats object to generic HNAE3 queue users. Stats persist until reset, explicit reset helper invocation, or queue teardown.

## Dependencies

The header includes Linux types, `etherdevice.h`, and `hnae3.h`. The implementation also requires common command queue types and firmware opcodes.

## Risks and Edge Cases

- The embedded queue layout is contractual; callers that allocate a plain `hnae3_queue` cannot use these helpers safely.
- The global `index` is used in firmware queries and stat names, so it must match hardware queue numbering.
- Counter semantics depend on firmware and are not documented beyond 32-bit opcode comments.

## Test Signals

Tests should confirm layout assumptions, ethtool stat count equals `num_tqps * 2`, stat names use global queue indices, firmware update commands use the correct index, and reset clears cached counters.
