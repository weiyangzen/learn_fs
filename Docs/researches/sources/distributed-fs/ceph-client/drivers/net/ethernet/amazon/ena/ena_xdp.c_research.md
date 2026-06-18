# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_xdp.c

## Purpose
`ena_xdp.c` implements ENA XDP support beyond the inline execution helper: XDP TX frame mapping/submission, ndo XDP xmit, allocation and teardown of dedicated XDP TX queues, RX queue registration with the XDP core, XDP program attach/detach, and NAPI polling for XDP TX completions.

## Important APIs, Types, And Functions
Public APIs are `ena_xdp_xmit_frame()`, `ena_xdp_xmit()`, `ena_setup_and_create_all_xdp_queues()`, `ena_xdp_register_rxq_info()`, `ena_xdp_unregister_rxq_info()`, `ena_xdp_exchange_program_rx_in_range()`, `ena_xdp()`, and `ena_xdp_io_poll()`. Important internals are `ena_xdp_tx_map_frame()`, `ena_init_all_xdp_queues()`, `ena_destroy_and_free_all_xdp_queues()`, `ena_xdp_set()`, `validate_xdp_req_id()`, and `ena_clean_xdp_irq()`.

## Control Flow, State, And Integration
Attaching the first XDP program initializes a second set of TX rings (`xdp_first_ring = num_io_queues`, `xdp_num_queues = num_io_queues`), may bring the device down/up, exchanges program pointers on RX rings, adjusts RX headroom, and reduces `netdev->max_mtu` to `ENA_XDP_MAX_MTU`. Detach clears redirect features, tears down XDP queues, restores max MTU, and drops the old BPF program reference. XDP xmit chooses a dedicated XDP TX queue by CPU modulo queue count, serializes with `xdp_tx_lock`, maps frame data or LLQ push header into ENA TX descriptors, calls `ena_xmit_common()`, and rings the doorbell on flush. XDP NAPI cleans TX completions, validates XDP frame request IDs, unmaps DMA, returns frames, acks completions, unmasks interrupts, and updates NUMA hints.

## Dependencies
This file depends on `ena_xdp.h`, ENA netdev TX/resource helpers, Linux XDP/BPF APIs, DMA mapping via shared TX unmap code, NAPI, and queue topology from `ena_adapter`.

## Risks And Test Signals
Risks include XDP requiring twice as many queues, MTU enforcement, BPF program lifetime, RX headroom transitions, concurrent XDP_TX/XDP_REDIRECT locking, LLQ frame mapping, completion validation, and teardown while device is up. Test signals include XDP attach/detach while up/down, XDP_TX and XDP_REDIRECT traffic, ndo_xdp_xmit bulk sends, channel count changes with XDP active, max MTU changes, and completion cleanup under reset.
