# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/net_driver.h

## Purpose
`net_driver.h` is the central shared data-model and operation-contract header for the Falcon `ef4` network driver. It defines queue, channel, NIC, PHY, statistics, filter, MTD, interrupt, and feature abstractions used across probe, datapath, reset, ethtool, and hardware-specific implementations.

## Important APIs, Types, And Definitions
The header establishes limits and constants such as `EF4_MAX_CHANNELS`, TX queue type flags, MTU bounds, RX buffer sizing, flow-control bits, and interrupt modes. Core structures include DMA buffers (`ef4_buffer`, `ef4_special_buffer`), TX/RX buffer and queue rings (`ef4_tx_buffer`, `ef4_tx_queue`, `ef4_rx_buffer`, `ef4_rx_queue`), event-processing channels (`ef4_channel`, `ef4_channel_type`), interrupt context (`ef4_msi_context`), link state (`ef4_link_state`), PHY operations (`ef4_phy_operations`), hardware statistic descriptors, multicast hash storage, MTD partitions, the master `struct ef4_nic`, and the controller vtable `struct ef4_nic_type`.

Inline helpers retrieve channels and queues, iterate channels and per-channel queues, compute maximum frame length, combine fixed and configurable netdev features, and safely get TX insert buffers. The `ef4_nic_type` vtable is large and defines the hardware contract for probe/remove/init/fini, reset, port/MAC/PHY handling, stats, IRQs, TX/RX/event queues, filters, MTD, MAC address handling, register bases, DMA masks, RSS prefix information, scatter support, interrupt limits, and offload features.

## Control Flow
Most runtime control flow in the driver is mediated by the structures defined here. Generic code stores hardware state in `ef4_nic`, then dispatches hardware-specific behavior through `efx->type` and `efx->phy_op`. Iteration macros assume the `channel[]` array is densely populated up to `n_channels`. TX helpers account for paired offload/non-offload queues and optional high-priority queues. State fields distinguish uninitialized, ready, disabled, and PCI-error recovery phases.

## State And Persistence
`struct ef4_nic` persists nearly all driver state: PCI mappings, interrupt configuration, resource dimensions, RSS tables, queue/channel pointers, IRQ status DMA buffer, MTD list, NIC-specific private data, locks, port/link state, filter state, flush counters, VPD serial number, monitor work, statistics, and RX drop counters. Queue structs persist software ring indices, DMA descriptors, page recycle state, and completion statistics. Locking annotations in comments define ownership across RTNL, MAC lock, TX locks, spinlocks, and workqueues.

## Dependencies And Integration Points
The header depends heavily on Linux networking, PCI, ethtool, MDIO, I2C, MTD, workqueue, timer, and busy-poll APIs, plus local `enum.h`, `bitfield.h`, and `filter.h`. It is included by most driver files and is the primary integration point between generic netdev code, hardware-specific Falcon architecture code, PHY drivers, ethtool operations, MTD support, and interrupt/event datapaths.

## Risks
Because this header defines shared state contracts, layout or semantic changes have broad blast radius. Important risks include cacheline-sharing regressions in fast-path queue fields, mismatched vtable implementations, incorrect channel/queue dimensioning, lock-order violations around `mac_lock`/RTNL/TX locks, stale filter or MTD state, and misuse of queue iteration macros when channels are sparse. Several inline helpers use paranoid assertions only under debug builds.

## Test Signals
Good signals include successful probe/remove, channel and queue allocation, RX/TX traffic with multiple queue types, MSI/MSI-X/legacy interrupt modes, reset and recovery flows, ethtool stats and register dumps, PHY operations, MTD operations, filter insertion/RFS behavior, busy-poll/NAPI operation, and lockdep or KASAN coverage for lifecycle and ring-buffer mistakes.
