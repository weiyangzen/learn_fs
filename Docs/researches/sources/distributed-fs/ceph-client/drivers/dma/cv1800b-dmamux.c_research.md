# sources/distributed-fs/ceph-client/drivers/dma/cv1800b-dmamux.c

Purpose: DMA router/DMAMUX driver for Sophgo CV1800/SG2000 SoCs. It maps peripheral request IDs and CPU interrupt targets onto physical DMA channels before delegating to the master DMA controller.

Important APIs/types/functions: `struct cv1800_dmamux_data` owns the `dma_router`, syscon regmap, lock, free/reserved map lists, and peripheral bitmap. `struct cv1800_dmamux_map` records channel, peripheral, and CPU. Core callbacks are `cv1800_dmamux_route_allocate`, `cv1800_dmamux_free`, `cv1800_dmamux_probe`, and `cv1800_dmamux_remove`.

Control flow: probe obtains the parent syscon regmap, preallocates route map objects for channel IDs 0..7, pushes them onto the free list, sets `route_free`, and registers with `of_dma_router_register`. Allocation validates two DMA spec cells: peripheral ID and CPU ID. It rewrites the spec to one cell for the downstream master, parses `dma-masters`, chooses an existing reserved map for duplicate peripheral/CPU or consumes a free channel, programs channel remap and interrupt mux bits, returns the channel ID in `dma_spec->args[0]`, and returns the route data. Free clears channel remap and interrupt mux selection under the spinlock.

State and persistence: Runtime state is in free/reserved lockless lists, bitmap of mapped peripherals, per-map channel/peripheral/CPU fields, and syscon registers. State is not persisted across probe.

Dependencies/integration: OF DMA router API, regmap/syscon parent, platform device lookup, spinlock guard helpers, and the downstream DMA master referenced by `dma-masters`.

Risks: Peripheral ID validation uses `devid > MAX_DMA_MAPPING_ID`, allowing ID 42 while bitmap size is 42 bits indexed 0..41; this should be scrutinized. Reserved maps are never moved back to free in `route_free`, so the design appears to keep per-peripheral reservations for reuse. Concurrent route allocation is spinlock-protected, but list/bitmap semantics are subtle.

Test signals: DT route allocation for valid/invalid cells, repeated requests for same peripheral/CPU, exhaustion of eight channels, route-free register state, interrupt mux CPU selection, and bitmap boundary tests around peripheral 41/42.
