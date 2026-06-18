# sources/distributed-fs/ceph-client/include/linux/amba/pl08x.h

## Purpose
Defines the platform-facing contract for ARM PrimeCell PL08x DMA controllers. It supplies channel descriptors, DMA bus-width/burst enums, controller-wide platform data, and the optional `pl08x_filter_id()` DMA-engine filter used by board/platform code to match DMA slave channels.

## Important APIs, Types, And Functions
`struct pl08x_channel_data` describes one logical peripheral channel with `bus_id`, signal range, mux value, FIFO/device `addr`, single-vs-burst behavior, and permitted AHB buses. `struct pl08x_platform_data` aggregates channels, memcpy defaults, signal acquire/release callbacks, LLI/memory bus masks, and the `dma_slave_map` table. `enum pl08x_burst_size` and `enum pl08x_bus_width` encode hardware transfer sizing. `pl08x_filter_id()` is declared only with `CONFIG_AMBA_PL08X`; otherwise it returns false.

## Control Flow, State, And Persistence
The header itself has no runtime state. It defines static platform configuration consumed during PL08x driver probe and DMA channel matching. The stateful path is delegated to platform callbacks: `get_xfer_signal()` reserves/muxes a signal before transfer and `put_xfer_signal()` releases it afterward.

## Dependencies And Integration Points
Depends on `linux/dmaengine.h` for `dma_addr_t`, `dma_chan`, and slave maps, and `linux/interrupt.h` for platform integration. Consumers include AMBA platform registration code and DMA clients that request channels by `bus_id`.

## Risks And Test Signals
Incorrect signal ranges, mux values, or bus masks can cause channel conflicts, silent transfer stalls, or DMA to the wrong peripheral FIFO. Tests should cover DMA slave matching, memcpy defaults, mux callback failure paths, concurrent channel allocation, and build coverage with and without `CONFIG_AMBA_PL08X`.
