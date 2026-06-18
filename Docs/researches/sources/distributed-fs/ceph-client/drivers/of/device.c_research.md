# sources/distributed-fs/ceph-client/drivers/of/device.c

## Purpose
`device.c` bridges devicetree nodes to `struct device`. It handles driver match lookup, DMA/IOMMU setup from DT properties, restricted DMA pool assignment, modalias generation, uevent metadata, and stable bus ID construction.

## Important APIs, types, and functions
Exports include `of_match_device()`, `of_dma_configure_id()`, `of_device_get_match_data()`, `of_device_modalias()`, `of_device_uevent()`, `of_device_uevent_modalias()`, and `of_device_make_bus_id()`. `of_dma_set_restricted_buffer()` is the internal helper that detects a compatible and available `restricted-dma-pool` memory-region.

## Control flow and state
`of_match_device()` refuses reused OF nodes and delegates to `of_match_node()`. `of_dma_configure_id()` finds the DMA parent, parses `dma-ranges`, clamps DMA masks, sets `bus_dma_limit` and `dma_range_map`, configures IOMMU, applies architecture DMA ops, and falls back to restricted DMA pools when no IOMMU is active. It preserves error semantics for deferred IOMMU probes by clearing temporary maps and freeing the parsed map.

Modalias and uevent paths expose OF name, full path, type, compatible list, alias entries, and module alias strings to user space. `of_device_make_bus_id()` uses translated `reg` addresses when possible, otherwise prepends parent names until a unique-looking device name is built.

## Dependencies and integration
The file integrates with DMA direct mapping, `of_iommu_configure()`, reserved-memory device setup, platform devices, module autoloading, and the global `aliases_lookup` protected by `of_mutex`.

## Risks and test signals
Main risks are stale or conflicting `dma_range_map`, `-EPROBE_DEFER` handling, non-set `dev->dma_mask`, restricted DMA pool selection when multiple memory regions exist, modalias buffer truncation, and reused OF nodes. Runtime signals include DMA mask logs, IOMMU probe ordering, module autoload events, and sysfs/uevent environment contents.
