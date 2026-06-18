## sources/distributed-fs/ceph-client/drivers/dma/dw/of.c

Purpose: Device-tree parsing and OF DMA controller registration for classic DW DMA.

Important APIs/types/functions: `dw_dma_parse_dt()`, `dw_dma_of_controller_register()`, `dw_dma_of_controller_free()`, and internal `dw_dma_of_xlate()`.

Control flow: DT parsing reads `dma-masters`, `dma-channels`, allocation order, priority, block size, deprecated `data_width`, preferred `data-width`, `multi-block`, `snps,max-burst-len`, and protection-control properties into platform data. OF xlate expects 3 or 4 arguments: request line, memory master, peripheral master, and optional channel mask; it validates ranges, creates `dw_dma_slave`, and requests a DMA_SLAVE channel through `dw_dma_filter()`.

State and persistence: parsed platform data is devm-allocated for device lifetime. OF controller registration exists while the driver is bound.

Dependencies and integration: integrates with OF DMA bindings, platform driver probe, and shared channel filter.

Risks and test signals: binding argument/range errors can silently prevent clients from obtaining channels; deprecated and current data-width handling must remain compatible. Test DT probe, DMA client phandles with and without channel masks, invalid property rejection, and OF unregister on remove.
