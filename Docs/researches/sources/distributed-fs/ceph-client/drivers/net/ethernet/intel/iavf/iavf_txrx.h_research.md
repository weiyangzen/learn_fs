# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_txrx.h

## Purpose
Defines the IAVF Tx/Rx data-path ABI used across the driver: interrupt moderation constants, RSS defaults, descriptor accounting helpers, Tx flags, per-ring/per-vector state structures, queue stats, and data-path function prototypes.

## Important APIs, Types, and Functions
Important types include `struct iavf_tx_buffer`, `struct iavf_queue_stats`, `struct iavf_tx_queue_stats`, `struct iavf_rx_queue_stats`, `struct iavf_ring`, and `struct iavf_ring_container`. Key macros and helpers include `IAVF_DESC_UNUSED` from `iavf_type.h`, `IAVF_RX_INCREMENT`, `IAVF_RX_NEXT_DESC`, `iavf_txd_use_count`, `iavf_xmit_descriptor_count`, `iavf_maybe_stop_tx`, `iavf_chk_linearize`, `txring_txq`, ITR conversion macros, Tx flag bit definitions, and default RSS hash masks. Function prototypes expose descriptor setup/free, Rx buffer allocation, NAPI poll, hung detection, linearization checks, and transmit entry points.

## Control Flow
Most code is declarative or inline. Descriptor-count helpers walk skb head/frags to estimate Tx descriptors. Stop helpers perform a fast unused-descriptor check before calling the slower queue-stop path. Linearization helpers enforce hardware scatter-gather limits, calling into the implementation only for complex TSO cases.

## State and Persistence
`struct iavf_ring` is the central persistent in-memory state for one Tx or Rx queue, including descriptor memory, DMA base, software buffer arrays, tail register pointer, counters, flags, queue index, count, current indices, descriptor format, stats, q_vector/VSI backreferences, RCU header, partial Rx skb, PTP pointer, Rx buffer sizing, and queue shaper data. `struct iavf_ring_container` persists per-interrupt aggregate traffic and ITR state.

## Dependencies and Integration Points
Depends on Linux netdevice/skbuff/page-pool concepts, Intel `libie` packet type definitions, descriptor definitions from `iavf_type.h`, and netdev queue APIs. Included by Tx/Rx implementation, main queue allocation/configuration, interrupt setup, ethtool stats, and virtchnl queue programming paths.

## Risks
This header encodes hardware limits and shared state layout. Incorrect descriptor accounting can cause ring overruns or unnecessary queue stops. Flag bit drift between queue configuration, Tx offload code, and Rx metadata extraction can break VLAN or timestamp behavior. `struct iavf_ring` is cacheline-aligned and hot in the data path, so layout changes can have performance side effects.

## Test Signals
Compile coverage for all users, Tx descriptor accounting unit-style checks with fragmented skbs, queue stop/wake stress, RSS hash defaults via ethtool, ITR setting changes, VLAN tag-location behavior, timestamp flag behavior, and performance regression tests on multi-queue traffic.
