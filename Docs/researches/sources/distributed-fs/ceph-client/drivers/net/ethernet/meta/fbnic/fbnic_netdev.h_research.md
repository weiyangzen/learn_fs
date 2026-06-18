# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_netdev.h

## Purpose
`fbnic_netdev.h` defines `struct fbnic_net`, the per-netdev private state shared across FBNIC netdev, phylink, time, RSS, and TX/RX modules, plus prototypes for lifecycle, queue, PTP, RX mode, and phylink helpers.

## Important APIs, Types, And Functions
The central type is `struct fbnic_net`. It stores XDP program, TX/RX ring arrays, NAPI vectors, netdev/device back-pointers, queue sizes, coalescing settings, HDS threshold, phylink objects, AUI/FEC, timestamp conversion state, queue counts, RSS tables/key/hash options, accumulated stats, hardware timestamp config, and pause state. Public declarations cover open/up/down, netdev allocation/register/free/unregister, queue reset, ethtool setup, PTP/time setup, RX mode sync/clear, phylink ethtool helpers, and split-frame validation.

## Control Flow
The header establishes cross-file call boundaries: PCI allocates/registers the netdev, netdev open drives TX/RX allocation and firmware ownership, phylink updates AUI/FEC/link state, time code updates `time_high`/`time_offset`, and RPC/TXRX code uses RSS and queue state.

## State And Persistence
Most runtime network state for an FBNIC interface is persisted in `struct fbnic_net` for the life of the registered netdev. The time fields use `u64_stats_sync` to make 64-bit offset reads safe on 32-bit machines. Ring statistics can be accumulated into base stats after rings are destroyed, keeping counters visible across queue lifecycle changes.

## Dependencies And Integration Points
It includes phylink, CSR, RPC, and TXRX headers, making it the common dependency surface for major driver modules. Constants such as `FBNIC_MAX_NAPI_VECTORS`, `FBNIC_MIN_RXD_PER_FRAME`, and tunnel GSO features are shared by netdev and queue code.

## Risks
Because this header joins many modules, layout or semantic changes have wide blast radius. Queue count limits must remain compatible with ring arrays and hardware queue limits. Time fields require correct synchronization discipline. RSS table dimensions must match hardware and RPC definitions.

## Test Signals
Build coverage across all fbnic modules is the main static signal. Runtime signals include stable open/close, queue resizing, RSS programming, PTP timestamp conversion, XDP attach, phylink creation/destruction, and stats continuity after resource destruction.
