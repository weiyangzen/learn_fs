<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/of_dma.h

## Purpose
This header declares OF integration for the DMAEngine API, allowing DMA controllers and routers to be registered by DT node and allowing clients to request channels by phandle/name.

## Important APIs, types, and functions
`struct of_dma` records a controller/router list entry, OF node, translation callback, optional route allocation callback, router pointer, and controller data. `struct of_dma_filter_info` carries capability masks and filter callbacks. APIs include `of_dma_controller_register()`, `devm_of_dma_controller_register()`, `of_dma_controller_free()`, `of_dma_router_register()`, `of_dma_router_free`, `of_dma_request_slave_channel()`, `of_dma_simple_xlate()`, and `of_dma_xlate_by_chan_id()`.

## Control flow
DMA controller drivers register a node plus translation callback. DMA clients parse their `dmas` property and name, then `of_dma_request_slave_channel()` locates the provider and calls its xlate/router callbacks to return a `struct dma_chan`. The devm wrapper registers the controller and installs cleanup with `devm_add_action_or_reset()`. Disabled `CONFIG_DMA_OF` returns `-ENODEV`, `ERR_PTR(-ENODEV)`, `NULL`, or no translation.

## State and persistence
Persistent runtime state is the registered OF DMA controller/router list and provider-private `of_dma_data`. The header's devm cleanup ties registration lifetime to the device.

## Dependencies and integration points
It depends on `linux/of.h`, DMAEngine, DMA router support, device-managed cleanup, and phandle argument parsing from `of.h`.

## Risks and test signals
Risks include leaking controller registrations, wrong `#dma-cells` interpretation, route allocation lifetime bugs, returning NULL vs ERR_PTR inconsistently, and using the simple xlate for nontrivial hardware. Test controller registration/free, devm cleanup on probe failure, named DMA channel lookup, router allocation/release, invalid phandles, and disabled `CONFIG_DMA_OF` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_dma.h -->
