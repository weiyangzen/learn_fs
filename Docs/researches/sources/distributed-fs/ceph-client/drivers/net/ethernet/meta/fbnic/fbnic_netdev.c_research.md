# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_netdev.c

## Purpose
`fbnic_netdev.c` binds FBNIC hardware to the Linux `net_device` model. It allocates/registers the netdev, handles open/stop, MAC address and RX filter programming, MTU/XDP/timestamp configuration, queue stats, and netdev feature advertisement.

## Important APIs, Types, And Functions
Important public functions are `__fbnic_open()`, `fbnic_netdev_alloc()`, `fbnic_netdev_free()`, `fbnic_netdev_register()`, `fbnic_netdev_unregister()`, `fbnic_reset_queues()`, `__fbnic_set_rx_mode()`, `fbnic_clear_rx_mode()`, and `fbnic_check_split_frames()`. Netdev ops include open, stop, transmit, features check, set MAC, change MTU, async RX mode, stats, BPF setup, and hwtstamp get/set. Queue stat ops expose per-RX/TX and base counters.

## Control Flow
Allocation creates an Ethernet netdev, initializes `struct fbnic_net`, default queue sizes/coalescing, HDS threshold, RSS tables/key/masks, feature flags, MTU limits, XDP capabilities, and phylink. Registration derives a permanent MAC from PCI DSN and refuses invalid DSN-derived addresses.

Open names IRQs, allocates NAPI vectors and ring resources, binds queues to netdev, tells firmware the host has ownership, starts PTP time refresh, initializes firmware heartbeat, requests MAC IRQs, initializes BMC RPC/RSS, and resumes phylink. On failure it unwinds in reverse. Stop frees MAC IRQs, suspends phylink while preserving BMC link when present, downs datapath, stops time, releases ownership, unbinds queues, and frees resources.

RX mode synchronization programs host unicast, multicast, broadcast, promiscuous/all-multicast, and BMC all-multicast filters through RPC shadow TCAM helpers, then writes MACDA/action/TCE TCAMs. Timestamp configuration normalizes Linux hwtstamp filters to supported broader filters and reinitializes RSS/action rules when RX timestamping changes.

## State And Persistence
`struct fbnic_net` stores queue arrays, NAPI vectors, phylink handles, AUI/FEC, RSS state, time offset/cache, queue counts, accumulated stats after ring destruction, timestamp config, XDP program, and pause state. Netdev feature flags persist while registered. Hardware filter state is mirrored in `fbnic_dev` TCAM arrays and flushed through RPC writers.

## Dependencies And Integration Points
This file integrates with firmware ownership/heartbeat, MAC IRQ handling, phylink, PTP time, RSS/RPC filtering, TX/RX rings, ethtool ops, XDP, netdev queue management, and hardware stats. It depends heavily on `fbnic_txrx.c`, `fbnic_rpc.c`, `fbnic_phylink.c`, and firmware helpers declared elsewhere.

## Risks
Open/stop unwind ordering is critical because firmware ownership, time workers, IRQs, NAPI, and ring memory have strict dependencies. RX filter space is limited; overflow promotes to promiscuous/all-multicast modes. XDP is constrained by HDS threshold unless programs support fragments. Timestamp filtering is intentionally broader than requested, reported as `HWTSTAMP_FILTER_SOME`, which can surprise tests expecting exact filtering.

## Test Signals
Signals include successful register/unregister, valid DSN-derived MAC, open/stop leak-free cycles, RX mode changes for unicast/multicast/promisc/allmulti, hwtstamp filter normalization and rule rewrite, XDP attach rejection when MTU exceeds HDS threshold for non-frag XDP, correct queue stats after ring teardown, and expected netdev feature masks.
