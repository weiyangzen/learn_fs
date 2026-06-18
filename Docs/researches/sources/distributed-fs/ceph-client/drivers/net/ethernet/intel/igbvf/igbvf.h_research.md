# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/igbvf.h

## Purpose
`igbvf.h` is the main private header for the Intel VF driver. It defines driver limits, interrupt moderation constants, ring and adapter structures, board metadata, state bits, feature flags, descriptor access macros, and cross-file function prototypes.

## Important APIs, Types, And Functions
Core types include `struct igbvf_buffer`, `union igbvf_desc`, `struct igbvf_ring`, `struct igbvf_adapter`, and `struct igbvf_info`. Constants define default/min/max descriptor counts, ITR profiles, RX thresholds, VLAN/mac-filter limits, and `IGBVF_MAX_MAC_FILTERS`. Public prototypes expose lifecycle and resource APIs such as `igbvf_up()`, `igbvf_down()`, `igbvf_reinit_locked()`, `igbvf_setup_rx_resources()`, `igbvf_setup_tx_resources()`, and `igbvf_update_stats()`.

## Control Flow
The header does not execute logic, but it shapes control flow by defining state bits (`__IGBVF_TESTING`, `__IGBVF_RESETTING`, `__IGBVF_DOWN`) and the adapter fields used by reset, watchdog, NAPI, TX/RX, ethtool, and PCI probe/remove paths.

## State And Persistence
`struct igbvf_adapter` is the persistent per-netdev state. It tracks timers/work, active VLANs, ring pointers, hardware state, netdev/PCI pointers, stats, MSI-X entries, mailbox-backed hardware, WOL/PBA values, feature flags, link state, and reset timing. `struct igbvf_ring` stores descriptor memory, DMA address, indices, NAPI object, interrupt moderation state, per-ring stats, and a partially assembled RX skb.

## Dependencies And Integration Points
The header includes Linux netdevice, timer, VLAN, IO, and type headers plus `vf.h`. It is included by `netdev.c`, `ethtool.c`, and other driver-local files, binding VF hardware abstractions to kernel networking APIs.

## Risks
Structure layout and shared state are central to concurrency correctness. Ring fields are accessed from interrupt, NAPI, netdev, and ethtool contexts. Any change to buffer union semantics can break TX/RX DMA unmapping. Feature flags must remain synchronized with netdev feature changes and hardware workarounds.

## Test Signals
Build coverage is the first signal. Runtime coverage should exercise state transitions, ring allocation/free, VLAN filter restoration, MAC filter updates, reset while traffic is active, and stats updates across link changes.
