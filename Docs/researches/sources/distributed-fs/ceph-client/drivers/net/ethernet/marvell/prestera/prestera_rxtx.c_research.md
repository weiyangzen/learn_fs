# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_rxtx.c

## Purpose
This file implements Prestera packet RX/TX over switch SDMA. It creates DMA descriptor pools and circular RX/TX rings, handles the RX event from firmware/hardware, converts Prestera DSA-tagged CPU packets to normal Linux skbs, adds DSA tags for transmitted packets, and integrates RX processing with NAPI.

## Important APIs, types, and functions
Internal types include `struct prestera_sdma_desc`, `struct prestera_sdma_buf`, `struct prestera_rx_ring`, `struct prestera_tx_ring`, `struct prestera_sdma`, and `struct prestera_rxtx`. Public functions are `prestera_rxtx_switch_init()`, `prestera_rxtx_switch_fini()`, `prestera_rxtx_port_init()`, and `prestera_rxtx_xmit()`.

Key helpers include descriptor initializers, `prestera_sdma_rx_skb_alloc()`, `prestera_sdma_rx_skb_get()`, `prestera_rxtx_process_skb()`, `prestera_sdma_rx_poll()`, `prestera_sdma_rx_init/fini()`, `prestera_sdma_tx_init/fini()`, `prestera_sdma_tx_recycle_work_fn()`, `prestera_rxtx_handle_event()`, and `prestera_sdma_xmit()`.

## Control flow
Switch init allocates `sw->rxtx`, requests SDMA mode from hardware with `prestera_hw_rxtx_init()`, creates a DMA pool for 16-byte descriptors, initializes eight RX rings of 1000 descriptors each, initializes one TX ring, registers the RXTX event handler, creates a dummy NAPI netdev, and enables NAPI.

The RX event handler masks SDMA RX interrupts and schedules NAPI. `prestera_sdma_rx_poll()` walks all RX queues until budget or all queues are done, identifies CPU-owned descriptors, trims the backing skb to descriptor packet length, swaps in a fresh DMA buffer, parses the Prestera DSA header, resolves the ingress `prestera_port`, removes the DSA header with checksum adjustment, restores the Ethernet header layout, applies VLAN accel metadata, reports devlink traps, and batches packets into `netif_receive_skb_list()`.

Transmit starts in `prestera_rxtx_xmit()`, which ensures DSA headroom, pushes the DSA header, shifts destination/source MAC fields, builds the tag, then calls `prestera_sdma_xmit()`. The SDMA TX path serializes with `tx_lock`, maps the skb for DMA, fills descriptor buffer and length, throttles by burst/waiting for the queue start bit, marks the descriptor DMA-owned, starts the TX queue, and schedules recycling work.

## State and persistence behavior
Runtime state consists of descriptor rings, skb pointers, DMA mappings, a work item, a NAPI object, and hardware SDMA registers. No on-disk state is persisted. Descriptor ownership bits are the synchronization contract with hardware, with memory barriers before handing RX/TX descriptors to DMA. TX buffers remain `is_used` until the recycle worker sees CPU ownership and unmaps/frees the skb.

## Dependencies and integration points
The file integrates with `prestera_hw_*` register/event APIs, `prestera_dsa_parse/build()`, `prestera_port_find_by_hwid()`, `prestera_devlink_trap_report()`, Linux DMA pools, NAPI, skb VLAN acceleration, and netdev RX delivery. `prestera_rxtx_port_init()` sets port headroom for DSA tags.

## Risks and edge cases
RX allocation fallback copies from the old buffer if replacing the DMA skb fails; this avoids dropping but adds allocation/copy complexity. `dma_map_single()` for RX uses `skb->len`, which is zero for a newly allocated skb in normal Linux skb semantics; this is suspicious because the intended DMA length is the available buffer size. TX descriptor exhaustion drops packets but still returns `NETDEV_TX_OK`, relying on stats rather than queue backpressure. `prestera_rxtx_xmit()` returns `NET_XMIT_DROP` after modifying skb headroom if DSA build fails, so callers depend on normal ndo semantics for freeing. Large packets above `PRESTERA_SDMA_BUFF_SIZE_MAX` are not supported by this ring format.

## Test signals
Test with mocked SDMA registers and descriptors for RX budget handling, interrupt mask reenable, DSA parse failure, unknown ingress port, VLAN tag propagation, devlink trap reporting, TX descriptor busy drops, burst wait timeout, TX recycle unmap/free, init unwind at each allocation/register step, and port headroom setup.
