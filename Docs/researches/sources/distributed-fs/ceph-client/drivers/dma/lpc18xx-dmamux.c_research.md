
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lpc18xx-dmamux.c -->
# sources/distributed-fs/ceph-client/drivers/dma/lpc18xx-dmamux.c

Purpose: implements an OF DMA router for the LPC18xx/43xx DMA mux. It maps client DMA specifiers onto a single DMA master while programming CREG mux bits and reserving each mux line until the DMA route is released.

Important APIs and control flow: `lpc18xx_dmamux_probe()` allocates router state, looks up the `nxp,lpc1850-creg` syscon regmap, reads local and master `dma-requests`, allocates one mux state per master request, initializes the spinlock and `dma_router`, then registers `of_dma_router_register()`. `lpc18xx_dmamux_reserve()` expects three DMA args: mux number, mux value, and downstream request. It validates the mux and mux value, substitutes `dma_spec->np` with the first `dma-masters` phandle, marks the mux busy under lock, updates `LPC18XX_CREG_DMAMUX`, rewrites args to the downstream two-argument format, and returns the mux state as route data. `lpc18xx_dmamux_free()` clears the busy flag.

State and persistence behavior: each `lpc18xx_dmamux` entry stores the selected mux value and busy flag. The hardware mux selection persists in the CREG syscon register; freeing a route only clears software busy state and does not reset the hardware bits. Locking protects busy/value changes and register updates.

Dependencies and integration points: depends on OF DMA router APIs, OF platform device lookup, syscon/regmap, spinlocks, a parent/peer DMA master referenced by `dma-masters`, and compatible `nxp,lpc1850-dmamux`. Downstream DMA clients see the rewritten specifier and acquire channels from the real master.

Risks and test signals: risks include no hardware reset on route free, reliance on `of_find_device_by_node()` succeeding for the router node, lack of `regmap_update_bits()` error checking, using master request count for mux array sizing while also reading local `dma-requests`, and route conflicts returning `-EBUSY`. Test signals include invalid arg/mux/value rejection, successful route reservation rewriting to master args, busy detection for duplicate mux claims, correct CREG bitfield writes, and DMA client operation through the selected downstream request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lpc18xx-dmamux.c -->
