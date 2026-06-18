# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-desc.c

## Purpose

`xgbe-desc.c` owns descriptor-ring memory management and packet buffer DMA mapping for the AMD XGBE driver. It allocates coherent descriptor rings and per-descriptor metadata, prepares RX page-backed buffers, maps TX skb data into DMA segments, releases DMA mappings and page references, and installs the descriptor-interface function table used by the runtime driver.

The file is the resource-management layer between Linux skbs/pages and hardware descriptor programming in `xgbe-dev.c`.

## Important APIs and Functions

- `xgbe_alloc_ring_resources()` allocates TX and RX ring descriptors/metadata for every active channel.
- `xgbe_free_ring_resources()` and `xgbe_free_ring()` unmap all per-descriptor resources, free metadata, free page pools, and free coherent descriptor memory.
- `xgbe_init_ring()` allocates one DMA-coherent `struct xgbe_ring_desc` array and one `struct xgbe_ring_data` array for a ring.
- `xgbe_alloc_pages()` allocates node-preferred compound pages, falls back to smaller orders and any NUMA node, and maps pages for device RX.
- `xgbe_set_buffer_data()` slices a shared page allocation into per-descriptor buffer descriptors and records which descriptor is responsible for unmapping an exhausted page allocation.
- `xgbe_map_rx_buffer()` ensures header and payload page allocations exist, then assigns RX header and buffer DMA slices to a descriptor.
- `xgbe_wrapper_tx_descriptor_init()` and `xgbe_wrapper_rx_descriptor_init()` populate descriptor pointers/DMA addresses in metadata, reset ring indices, and call hardware descriptor init hooks.
- `xgbe_unmap_rdata()` is the common cleanup routine for TX skb DMA, skb ownership, RX page references, RX DMA unmap ownership, saved RX packet state, and metadata reset.
- `xgbe_map_tx_skb()` maps an skb into one or more TX descriptors, including optional context descriptor reservation, TSO header mapping, linear payload segmentation, and fragmented skb page mapping.
- `xgbe_init_function_ptrs_desc()` publishes the descriptor operations through `struct xgbe_desc_if`.

## Control Flow

Open/start allocates channels elsewhere, then `alloc_ring_resources` walks each channel and initializes TX and RX rings. RX descriptor wrapper initialization maps buffers for every descriptor before giving the ring to hardware. For RX, header pages are order-0 and payload pages use `PAGE_ALLOC_COSTLY_ORDER` when possible; the driver can allocate separate header buffers for split-header/checksum mode or full-size header buffers when RX checksum offload is disabled.

Transmit starts in `xgbe-drv.c`, which computes required descriptors and calls `map_tx_skb`. This function reserves room for a context descriptor when TSO MSS or VLAN tag state must change, maps the TSO header separately if needed, maps the linear skb data in chunks no larger than `XGBE_TX_MAX_BUF_SIZE`, maps each skb fragment in chunks, stores the skb pointer in the final mapped descriptor, and returns the descriptor count. On any DMA mapping failure, it unmaps all descriptors mapped since the starting index and returns zero.

Cleanup paths call `unmap_rdata` whether descriptors are being reclaimed after TX completion, recycled after RX, or freed during close/restart. The cleanup routine deliberately handles both TX and RX state because the same metadata type backs both ring kinds.

## State and Persistence Behavior

The file persists ring state in `struct xgbe_ring`: descriptor count, coherent descriptor base/DMA address, metadata array, RX page allocation cursors, current and dirty indices, TX cached context state, and packet metadata. Per-descriptor state lives in `struct xgbe_ring_data`: descriptor pointer/DMA address, TX skb DMA mapping, RX buffer page references, RX state saved across NAPI budget exits, and packet accounting. All state is runtime-only and rebuilt on open, full restart, ring-count changes, and memory reallocation.

## Dependencies and Integration Points

Dependencies include DMA mapping APIs, page allocation/refcount APIs, skb fragment DMA helpers, NUMA allocation helpers, and the xgbe ring/channel/private structures. The file integrates with:

- `xgbe-drv.c` for open/close memory allocation, TX mapping, RX refresh, and cleanup.
- `xgbe-dev.c` for hardware descriptor initialization and descriptor reset callbacks.
- NAPI RX paths that may save partial-packet state in `rdata->state`.
- Netdev feature bits such as `NETIF_F_RXCSUM`, which influence RX split-header buffer sizing.

## Risks and Failure Modes

- On `xgbe_init_ring()` failure after descriptor allocation but before metadata allocation, cleanup is left to the caller's error path; the caller does call `xgbe_free_ring_resources`, so this ordering must remain intact.
- RX page-slicing correctness depends on `pa_unmap` ownership being assigned exactly when an allocation is exhausted. Refcount or unmap mistakes would produce page leaks, double unmaps, or DMA lifetime bugs.
- `xgbe_map_tx_skb()` assumes ring space was already checked by `xgbe_maybe_stop_tx_queue`; callers must keep descriptor count calculation in sync with mapping behavior.
- TSO and VLAN context reservation uses cached ring context. Incorrect cache state can under-reserve descriptors or emit stale context.
- DMA mapping failures are handled, but repeated failures can drop packets and should be visible through netdev alerts or TX errors.

## Test Signals

Stress TX with linear, fragmented, TSO, VLAN-tagged, and VXLAN/GSO skbs while watching DMA mapping warnings, descriptor leaks, and queue stalls. Stress RX under small MTU, jumbo MTU, RX checksum on/off, and low-memory conditions. Use driver unload/reload and repeated open/close to catch page/DMA leaks. KASAN, DMA_API_DEBUG, page refcount diagnostics, and high-throughput NAPI tests are strong signals for this file.
