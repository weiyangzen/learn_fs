# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc.h

## Purpose
`igc.h` is the main private header for the Intel I225/I226 driver. It defines queue limits, adapter/ring/q_vector state, TX/RX buffer structures, PTP and AF_XDP metadata, TSN/FPE fields, NFC filter structures, feature flags, helper macros, and cross-module prototypes.

## Important APIs, Types, And Functions
Important types include `struct igc_adapter`, `struct igc_ring`, `struct igc_q_vector`, `struct igc_tx_buffer`, `struct igc_rx_buffer`, `struct igc_tx_timestamp_request`, `struct igc_xdp_buff`, `struct igc_nfc_rule`, and `struct igc_fpe_t`. Key helpers/macros include `igc_desc_unused()`, `igc_rss_type()`, `igc_test_staterr()`, `igc_rx_bufsz()`, `igc_rx_pg_order()`, `txring_txq()`, and descriptor accessors `IGC_RX_DESC`, `IGC_TX_DESC`, and `IGC_TX_CTXTDESC`. Prototypes cover up/down, open/close, ring resources, RSS, reset, stats, XSK wakeup, PTP, NFC, LED setup, and queue control.

## Control Flow
The header has only inline helpers, but it defines how data flows among implementation files. TX/RX paths share `struct igc_ring`; interrupts group rings through `struct igc_q_vector`; PTP paths use `tx_tstamp[]`, `tmreg_lock`, `timecounter`, and pin descriptors; TSN paths use gate and credit fields in each ring; XDP/AF_XDP paths use `xdp_prog`, `xdp_rxq`, and `xsk_pool`.

## State And Persistence
`struct igc_adapter` is the persistent per-device state spanning netdev, PCI, hardware stats, queue arrays, timers, workqueues, link state, interrupt masks, RSS indirection, PTP clock, hwtstamp config, TSN/Qbv/Qav/FPE settings, NFC rules, LED state, and firmware version. Rings persist descriptor memory, DMA addresses, queue indices, tail registers, flags, producer/consumer indices, stats, and XDP pool state.

## Dependencies And Integration Points
The header pulls in PCI, netdevice, ethtool, SCTP, PTP, timecounter, timestamping, hrtimer, and XDP APIs plus `igc_hw.h`. It is shared by the driver's main, ethtool, PTP, TSN, XDP, base, and diagnostics code.

## Risks
This is a high-blast-radius header: changes can affect almost every `igc` subsystem. Ring and adapter fields are accessed from IRQ, NAPI, workqueue, timer, rtnl, and ethtool contexts. TSN, PTP, XDP, and AF_XDP fields interact with queue scheduling and timestamping, so layout and locking comments must be respected. Several flag values overlap semantically and must be interpreted in the right field.

## Test Signals
Build all `igc` objects, run traffic across all queues, RSS, XDP/AF_XDP, PTP timestamping, TSN offloads, ethtool stats/ring/coalesce, reset, suspend/resume, and LED configurations. Lockdep and KCSAN are useful for shared adapter/ring state.
