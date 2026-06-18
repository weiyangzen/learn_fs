# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-rx.c

Purpose: Handles MCP251xFD RX FIFO interrupts by reading hardware RX objects, converting them into SocketCAN SKBs, timestamping them, and advancing hardware/software FIFO tails.

Important APIs, types, and functions: `mcp251xfd_handle_rxif()` is the exported IRQ handler. Helpers compute FIFO length, sanity-check chip/software tail agreement, bulk-read objects from `map_rx`, convert hardware IDs/flags/DLC/data to CAN/CAN-FD frames, queue SKBs to RX offload, and issue batched UINC transfers.

Control flow: For each eligible RX ring, the code reads FIFOSTA, determines pending length, reads linear chunks from RAM, processes each object, and advances the FIFO tail in one SPI message per chunk. A stale timestamp advances only already accepted frames. RX coalescing restarts a timer to re-enable interrupts.

State and persistence behavior: Updates RX ring head/tail and last valid timestamp. SKB timestamps are derived from the shared timecounter. Hardware FIFO tail advances via prebuilt UINC transfers.

Dependencies and integration points: Depends on ring descriptors, timestamp setup, `can_rx_offload_queue_timestamp()`, CAN/CAN-FD DLC helpers, and regmap RAM reads.

Risks: Erratum handling depends on monotonic converted timestamps. FIFO length arithmetic relies on power-of-two counts. Allocation failures must still allow FIFO advancement to avoid stalls.

Test signals: RX standard/extended/RTR/CAN-FD/BRS/ESI frames, FIFO full/empty/wrap, RX coalescing, timestamp ordering across wrap, SKB allocation failure, and sanity tail mismatch tests.
