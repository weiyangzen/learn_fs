# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_xdp.h

## Purpose
`ena_xdp.h` declares ENA XDP interfaces and implements the inline RX-side XDP execution helper. It defines XDP MTU constraints, XDP queue range detection, ENA-local action bits, and attach eligibility checks.

## Important APIs, Types, And Functions
Macros include `ENA_XDP_MAX_MTU`, `ENA_IS_XDP_INDEX()`, and `ENA_XDP_FORWARDED`. `enum ENA_XDP_ACTIONS` maps PASS, TX, REDIRECT, and DROP to internal bit flags. `enum ena_xdp_errors_t` reports attach eligibility. Prototypes expose queue setup, program exchange, XDP NAPI poll, frame xmit, ndo xmit, ndo BPF handler, and RX queue info registration. Inline helpers are `ena_xdp_present()`, `ena_xdp_present_ring()`, `ena_xdp_legal_queue_count()`, `ena_xdp_allowed()`, and `ena_xdp_execute()`.

## Control Flow, State, And Integration
`ena_xdp_allowed()` rejects XDP when MTU exceeds the page-backed XDP buffer budget or when normal queues cannot be doubled for dedicated XDP TX rings. `ena_xdp_execute()` reads the ring BPF program, runs it, and translates kernel XDP verdicts. `XDP_TX` converts the buffer to an `xdp_frame`, sends it through the paired XDP TX ring under `xdp_tx_lock`, and returns the frame on xmit failure. `XDP_REDIRECT` calls `xdp_do_redirect()`. Drops, aborts, invalid actions, passes, TX, and redirects update per-RX-ring stats.

## Dependencies
The header depends on `ena_netdev.h`, Linux BPF trace/XDP APIs, SKB layout constants, page size, Ethernet/VLAN constants, and shared ENA stat helpers. It is included by both the RX path in `ena_netdev.c` and the implementation in `ena_xdp.c`.

## Risks And Test Signals
Risks include only supporting single-buffer XDP in the caller, MTU/headroom/tailroom calculation errors, stale BPF program reads, failed frame conversion, redirect flush requirements, and stat correctness. Test signals include XDP_DROP/PASS/TX/REDIRECT programs, invalid action warning paths, MTU boundary tests, queue-count legality tests, and stat increments in `ethtool -S`.
