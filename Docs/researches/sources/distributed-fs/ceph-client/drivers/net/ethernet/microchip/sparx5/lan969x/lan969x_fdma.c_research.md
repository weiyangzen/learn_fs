# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_fdma.c

## Purpose
This file implements the LAN969x FDMA datapath using coherent descriptor memory plus page_pool-backed RX pages. It supplies family-specific init/deinit, NAPI polling, RX frame construction, TX descriptor management, and DMA-mapped transmit.

## Important APIs, Types, And Functions
Exports are `lan969x_fdma_init()`, `lan969x_fdma_deinit()`, `lan969x_fdma_napi_poll()`, and `lan969x_fdma_xmit()`. Important helpers include `lan969x_fdma_rx_dataptr_cb()`, `lan969x_fdma_tx_dataptr_cb()`, `lan969x_fdma_get_next_dcb()`, `lan969x_fdma_tx_clear_buf()`, `lan969x_fdma_rx_get_frame()`, `lan969x_fdma_rx_alloc()`, and `lan969x_fdma_tx_alloc()`.

## Control Flow
Initialization configures RX/TX FDMA structures, switches the common hardware into FDMA injection mode, sets a 64-bit DMA mask, allocates RX page_pool and coherent FDMA descriptors, allocates TX buffers and descriptors, and resets FDMA. RX dataptr callbacks allocate pages from the page pool and publish DMA addresses. NAPI first reclaims completed TX descriptors, then consumes RX frames while descriptors report data, builds recyclable skbs from pages, parses IFH, trims FCS if requested, stamps PTP, updates stats, and passes packets to GRO. Consumed descriptor chains are reloaded before interrupts are re-enabled. TX finds an unused descriptor, expands head/tailroom if needed, pushes IFH, appends FCS space, maps the skb, records completion state, adds a DCB, and reloads FDMA.

## State And Persistence
State lives in `sparx5->rx.fdma`, `sparx5->tx.fdma`, `sparx5->rx.page_pool`, `sparx5->rx.page[dcb][db]`, `sparx5->tx.dbs`, descriptor rings, skb ownership, DMA mappings, and per-netdev stats. No disk persistence exists.

## Dependencies And Integration Points
It depends on common FDMA helpers, page_pool APIs, Sparx5 IFH parsing, PTP RX timestamping, common FDMA reload/stop/injection functions, netdev stats, NAPI, GRO, and DMA mapping APIs. It is selected through LAN969x ops in `lan969x.c`.

## Risks And Edge Cases
`lan969x_fdma_rx_alloc()` leaks the page pool if coherent descriptor allocation fails. `lan969x_fdma_xmit()` returns after DMA mapping failure without undoing IFH/FCS skb mutation. TX descriptor reclamation skips PTP skbs because timestamp completion owns them, so timestamp loss can keep descriptors used. `lan969x_fdma_free_pages()` assumes every page pointer was allocated. RX warns and recycles on invalid source port.

## Test Signals
Exercise sustained RX/TX, GRO delivery, FCS feature toggling, bridge offload marks, PTP RX and TX timestamp ownership, descriptor exhaustion returning `-EBUSY`, DMA mapping failures, init error unwinding, and deinit after active traffic.
