# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_txrx.h

## Purpose
Defines shared funeth Tx/Rx queue constants, state enums, queue statistics, queue data structures, IRQ wrapper, inline descriptor/doorbell helpers, and function prototypes used across `funeth_main.c`, `funeth_tx.c`, `funeth_rx.c`, `funeth_ethtool.c`, and tracepoints.

## APIs and Types
Important constants include descriptor sizes, max gather-list descriptors, CQE info offset, interrupt doorbell encodings, Rx tailroom, and XDP headroom. Enums describe queue init states (`DESTROYED`, `INIT_SW`, `INIT_FULL`) and IRQ states. Types include `funeth_txq_stats`, `funeth_rxq_stats`, `funeth_tx_info`, `funeth_txq`, `funeth_rxbuf`, `funeth_rx_cache`, `funeth_rxq`, and `fun_irq`. Macros `FUN_QSTAT_INC` and `FUN_QSTAT_READ` wrap synchronized 64-bit stats. Inline helpers locate Tx descriptors, ring SQ doorbells, and derive NUMA node from IRQ affinity.

## Control Flow and Integration
The state model lets main code allocate queues in software first, advance them to hardware resources, and later free down to a requested state. Tx and Rx datapaths use the stats and queue fields directly; ethtool relies on the same stat layouts for string/count ordering. IRQ structs bind NAPI to either Tx or Rx queues and hold MSI-X affinity state.

## State and Persistence
This header defines the in-memory persistent state of active queues. Counters are free-running until queues are freed, then selected totals are folded into `funeth_priv`. Ring producer/consumer counters and CQ phase/head fields are central to hardware synchronization.

## Dependencies and Risks
Depends on netdevice, XDP, and `u64_stats_sync`. Because this header fixes structure layout shared by many files, changes risk breaking stats ordering, cacheline assumptions, queue teardown, and tracepoint compilation. Test signals include 32-bit stat consistency, ethtool stat count/name matching, queue creation/free across all init states, XDP-enabled builds, and high-rate traffic to exercise doorbell and producer/consumer wrap.
