
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lpc32xx-dmamux.c -->
# sources/distributed-fs/ceph-client/drivers/dma/lpc32xx-dmamux.c

Purpose: implements an OF DMA router for the LPC32xx DMA mux signals whose routing is controlled through SSP and I2S clock-control syscon bits. It maps a small fixed table of ambiguous DMA request signals to selected peripheral functions.

Important APIs and control flow: `lpc32xx_dmamux_probe()` allocates router state, gets the parent syscon regmap, initializes the spinlock and `dma_router`, and registers `of_dma_router_register()`. `lpc32xx_dmamux_reserve()` expects three args, finds a fixed `lpc32xx_muxes[]` entry by request signal, validates a binary mux select value, obtains the first `dma-masters` phandle, marks the entry busy under lock, writes the target bit with `regmap_update_bits()`, rewrites the specifier to two args for the downstream master, and returns the mux entry as route data. `lpc32xx_dmamux_release()` clears the busy flag.

State and persistence behavior: fixed mux entries store signal number, names for select values, mux register/bit, current mux value, and busy flag. Hardware routing persists in the syscon bit after release; software only prevents concurrent conflicting use while a route is reserved.

Dependencies and integration points: depends on OF DMA router support, syscon/regmap from the parent node, OF platform lookup, spinlocks/guard helpers, and compatible `nxp,lpc3220-dmamux`. The fixed table covers signal 3, 10, 11, 14, and 15 routing between SPI/SSP/UART/I2S/none functions.

Risks and test signals: risks include debug messages using `name_sel1` in both select cases, error text printing the wrong argument for invalid mux value, no regmap error checking, no hardware reset on release, and only table-listed signals being routable. Test signals include successful reservation for each fixed signal, `-EBUSY` on duplicate active route, correct SSP/I2S syscon bit updates, downstream DMA specifier rewrite, and client transfers through both select-0 and select-1 routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lpc32xx-dmamux.c -->
