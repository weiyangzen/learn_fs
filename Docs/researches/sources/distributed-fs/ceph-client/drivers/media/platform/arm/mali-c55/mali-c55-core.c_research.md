# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-core.c

Purpose: Implements the platform driver core for Mali-C55: MMIO/context access, media graph construction, async sensor binding, hardware capability probing, interrupt handling, runtime PM power sequencing, and platform probe/remove.

Important APIs/functions: Exports global and context register read/write/update helpers, `mali_c55_config_write()`, `mali_c55_get_active_context()`, `mali_c55_pipeline_ready()`, and platform driver entry points. Internal code creates media links, registers all sub-entities, parses firmware graph endpoints, and handles IRQs.

Control flow: Probe allocates state, maps IO, acquires clocks/resets, initializes reserved memory and vb2 DMA segment size, powers hardware, checks capabilities, initializes a shadow config context from ping space, enables runtime PM, registers media entities, then records IRQ number. Runtime resume powers on and requests a threaded IRQ; suspend frees IRQ and powers off. The ISR clears interrupt status, handles SOF by queueing events, programming next capture buffers, consuming params, filling previous stats, and swapping ping/pong config; plane interrupts complete capture buffers.

State and persistence: Persistent runtime state includes hardware capabilities, config-space shadow buffer, next ping/pong selector, media graph, notifier, IRQ number, and PM state. No disk persistence.

Dependencies and integration: Uses platform bus, OF/fwnode graph, clocks/resets, PM runtime, media controller, V4L2 async, vb2 DMA-contig, and all Mali-C55 entity registration functions.

Risks: Probe obtains `irqnum` after media init and runtime PM enable; resume requesting IRQ depends on valid sequencing. `readl_poll_timeout()` result in power-on safe-stop is not checked. Config writes currently use CPU `memcpy_toio`, so long copies happen in threaded IRQ context.

Test signals: Probe/remove, runtime suspend/resume, missing endpoint with TPG fallback, sensor async binding, capabilities without pong rejection, IRQ SOF/plane-done paths, ping/pong config swap, and media graph topology validation.
