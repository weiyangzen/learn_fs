# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_network.h

Purpose: Defines the LiquidIO per-netdev state, RX/TX buffer helpers, queue state helpers, and external network-facing function contracts.

Important APIs, types, and functions: `struct lio` is the central per-interface private structure: interface state, IQ/OQ indexes, gather-list pools, Octeon device pointer, link info, queue sizes, capabilities, PTP state, workqueues, and stats work. `struct octnic_gather` describes DMA gather components. Inline RX helpers allocate SKBs/pages, map pages, recycle page halves, reuse buffers, destroy/free buffers, and map ring buffer addresses. TX queue helpers stop, wake, and start netdev subqueues. `wait_for_pending_requests()` waits for ordered soft-command drain. Declarations expose feature, queue setup, interrupt, ethtool, stats, speed/FEC, and MTU operations.

Control flow: Main LiquidIO netdev code uses this header to allocate receive buffers for DROQs, map DMA addresses into rings, reclaim buffers, and coordinate queue start/stop with link state and IQ pressure.

State and persistence: State is volatile per-interface and per-buffer state in atomics, workqueues, DMA mappings, SKB control blocks, PTP fields, and linked lists. It is rebuilt at probe/open.

Dependencies and integration: Depends on netdevice, PTP, LiquidIO common protocol types, `octeon_droq`, `octeon_iq`, and response-manager constants. It bridges the generic Linux network stack to LiquidIO queue machinery.

Risks: SKB control block reuse requires consistent `struct octeon_skb_page_info` layout. DMA mapping failures, NUMA page mismatch, page refcount checks, and queue-index modulo logic are key correctness points. Atomic ifstate helpers are simple read-modify-write sequences, not compare-and-swap loops.

Test signals: RX allocation failure and recycle fallback, DMA map/unmap balance, page reuse across NUMA nodes, TX subqueue wake accounting, pending request drain on shutdown, MTU bounds, and PTP timestamp receive paths.
