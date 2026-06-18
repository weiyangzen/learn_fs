# sources/distributed-fs/ceph-client/drivers/dma/of-dma.c

## Purpose
`of-dma.c` provides the generic device-tree helper layer for DMA controllers, routers, and slave-channel requests. It maintains a global list of registered OF DMA providers and exports common translation helpers used by controller drivers.

## Important APIs, Types, and Functions
- `of_dma_list` and `of_dma_lock` store and protect registered `struct of_dma` providers.
- `of_dma_controller_register()` allocates and registers a DMA controller node with its `of_dma_xlate` callback and private data.
- `of_dma_controller_free()` removes and frees a controller registration for a device node.
- `of_dma_router_register()` registers a DMA router as an OF DMA provider using `of_dma_router_xlate()`.
- `of_dma_request_slave_channel()` resolves a client node's `dmas` and `dma-names` entries by name and calls the provider xlate callback.
- `of_dma_simple_xlate()` maps one-cell DMA specifiers to `__dma_request_channel()` filter parameters.
- `of_dma_xlate_by_chan_id()` maps a one-cell DMA specifier directly to a channel id in a `dma_device`.

## Control Flow
Controller drivers register their OF node and translation callback. Client drivers call `of_dma_request_slave_channel(np, name)`. The helper validates inputs and the `dmas`/`dma-names` properties, rotates the starting index using a static atomic to distribute duplicate names, parses each matching phandle, locks the provider list, finds the provider by node, calls its xlate callback, unlocks, drops the parsed node reference, and returns the first channel found. If a provider is missing, it returns `-EPROBE_DEFER`; if no matching channel exists, it returns `-ENODEV`. Router translation first asks the router to allocate/modify a target specifier, resolves the target provider, requests a real channel, stores router metadata on the channel, optionally calls `device_router_config`, and frees route data on failures.

## State and Persistence
State is an in-memory global linked list of OF DMA registrations plus one static `last_index` atomic used for approximate load distribution. No persistent storage is used. Router allocations store `chan->router` and `chan->route_data` until channel release.

## Dependencies and Integration Points
The file exports GPL symbols to DMA controller drivers and clients. It depends on Open Firmware helpers (`of_parse_phandle_with_args()`, property readers, node references), dmaengine request/release APIs, router callbacks, and `struct of_dma`/`struct dma_router` definitions from `linux/of_dma.h` and dmaengine internals.

## Risks and Edge Cases
- Provider lookup matches only `device_node *` identity; stale or duplicate registrations would affect all DMA clients for that node.
- `of_dma_request_slave_channel()` treats missing providers as probe deferral, so controller registration ordering directly affects client probe behavior.
- Router translation must balance the node reference taken by route allocation; this function explicitly calls `of_node_put()` on the translated spec node.
- `of_dma_xlate_by_chan_id()` returns `dma_get_slave_channel(candidate)`, so candidate existence does not guarantee availability.
- The local code uses `kzalloc_obj(*ofdma)`, which is tree-specific or macro-dependent; without that helper macro, this is a build risk.

## Test Signals
Validation should cover controller registration/free lifetime, duplicate `dma-names` distribution, missing provider deferral, simple one-cell filter translation, channel-id xlate behavior for unavailable channels, router allocate/config/free success and failure paths, and module builds for providers that include `linux/of_dma.h`.
