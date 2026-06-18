# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_netdev.h

## Purpose
`ena_netdev.h` is the central ENA netdev state and interface header. It defines driver constants, queue index mapping, IRQ/NAPI/ring/buffer/stat structures, adapter state, flags, and cross-file prototypes shared by core netdev, ethtool, XDP, and PHC code.

## Important APIs, Types, And Functions
Important types include `struct ena_irq`, `struct ena_napi`, `struct ena_tx_buffer`, `struct ena_rx_buffer`, `struct ena_stats_tx`, `struct ena_stats_rx`, `struct ena_ring`, `struct ena_stats_dev`, and `struct ena_adapter`. Constants define module version/name, BAR indices, MSI-X vector layout, ring sizes, RX buffer limits, MTU minimums, RSS table size, queue index conversions, watchdog timeouts, and LLQ/MMIO behavior. Inline helpers include `ena_reset_device()`, `ena_increase_stat()`, and `ena_ring_tx_doorbell()`. Prototypes expose ethtool setup, stats dumping, queue parameter/count updates, RX copybreak, TX common/unmap, IO ring/resource helpers, up/down lifecycle, interrupt unmasking, NUMA updates, and invalid request ID handling.

## Control Flow, State, And Integration
This header does not implement the main control flow, but it defines the state machine used by it. `ena_adapter` stores global device state: `ena_com_dev`, netdev, PCI device, queue counts, ring sizes, MTU/offload limits, MSI-X count, PHC, flags, TX/RX rings, NAPI entries, IRQ table, reset work, timer, watchdog state, devlink, XDP program/ring range, and stats. `ena_ring` stores per-queue software resources and ENA common SQ/CQ handles. `ena_reset_device()` records a reset reason and sets the reset trigger with ordering.

## Dependencies
The header depends on Linux networking, interrupt, DIM, XDP/BPF, devlink, VLAN, and ENA common/ethernet communication headers. It is included by `ena_netdev.c`, `ena_ethtool.c`, `ena_xdp.h`, and `ena_phc.c`.

## Risks And Test Signals
Risks include cacheline-sensitive hot-path structures, hard maximums such as `ENA_PKT_MAX_BUFS`, queue index conversion mistakes, XDP rings sharing the TX ring array, and flags whose ordering controls reset behavior. Test signals are compile-time structure/API compatibility, all queue-count permutations, XDP-enabled versus disabled ring initialization, 32-bit stat synchronization, and reset reason propagation.
