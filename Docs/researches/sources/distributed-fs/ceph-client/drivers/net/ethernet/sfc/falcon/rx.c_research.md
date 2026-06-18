<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/rx.c

## Purpose
Implements the Falcon-era EF4 receive data path: RX descriptor allocation, page DMA mapping/recycling, packet completion handling, GRO/SKB delivery, queue lifecycle, optional RFS acceleration, and multicast-recipient filter classification.

## Important APIs, types, and functions
- Public queue/data-path entry points: `ef4_rx_config_page_split`, `ef4_fast_push_rx_descriptors`, `ef4_rx_slow_fill`, `ef4_rx_packet`, `__ef4_rx_packet`, `ef4_probe_rx_queue`, `ef4_init_rx_queue`, `ef4_fini_rx_queue`, `ef4_remove_rx_queue`.
- Optional RFS APIs under `CONFIG_RFS_ACCEL`: `ef4_filter_rfs` and `__ef4_filter_rfs_expire`.
- Filter utility: `ef4_filter_is_mc_recipient`.
- Internal helpers manage page layout and DMA state: `ef4_init_rx_buffers`, `ef4_reuse_page`, `ef4_recycle_rx_page(s)`, `ef4_unmap_rx_buffer`, `ef4_free_rx_buffers`, `ef4_rx_packet_gro`, and `ef4_rx_mk_skb`.

## Control flow
Queue setup computes a power-of-two software ring, probes the NIC RX ring, initializes page recycling, and programs the hardware descriptor ring. Refill runs from NAPI or disabled-NAPI context and keeps the descriptor fill level above `fast_fill_trigger`; allocation failures schedule a slow-fill event so the queue is not left empty. Completion enters `ef4_rx_packet`, validates fragment count and length, DMA-syncs the buffers, skips the hardware prefix, recycles pages, flushes the previous prefetched packet, and stores the current packet in `channel->rx_pkt_*`. The second half, `__ef4_rx_packet`, reads prefix length if needed, diverts packets to loopback self-test when active, strips checksum flags if RX checksum offload is disabled, and delivers through GRO for TCP packets without a channel interception hook or through `netif_receive_skb`.

## State and persistence behavior
The file maintains per-queue counters (`added_count`, `removed_count`, `notified_count`, recycle counters, min fill, slow fill count) and a per-queue page recycle ring. DMA mapping state is stored in `struct ef4_rx_page_state` at the start of each page and per-buffer `dma_addr`, `page`, `page_offset`, `len`, and flags. Page reuse is allowed only when the page refcount proves the driver holds the only reference; otherwise the page is unmapped and released. No durable persistence exists; all state is in kernel memory and hardware DMA rings.

## Dependencies and integration points
Depends on Linux DMA, page, SKB, NAPI, GRO, RFS, flow dissector, checksum, IPv4/IPv6 helpers, and netdevice features. Driver dependencies include `net_driver.h`, `efx.h`, `filter.h`, `nic.h`, `selftest.h`, and `workarounds.h`. It calls NIC-type operations for descriptor notification and RFS filters, integrates with `ef4_loopback_rx_packet`, and schedules resets for hardware workaround paths.

## Risks and test signals
Key risks are DMA lifetime mistakes, page-recycle refcount races, fragment length validation errors, and missed queue refill causing RX starvation. Workaround `EF4_WORKAROUND_8071` intentionally leaks seriously overlength packets and schedules RX recovery, so reset and leak behavior should be monitored. Test signals include RX packet/drop/overlength counters, recycle success/fail/full counters, loopback self-test receive counts, GRO delivery, RFS insertion/expiration logs, and queue teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/rx.c -->
