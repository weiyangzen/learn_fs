# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-tef.c

Purpose: Handles Transmit Event FIFO interrupts, completing transmitted echo SKBs, applying hardware timestamps, updating TX stats, advancing TEF/TX tails, and waking the TX queue.

Important APIs, types, and functions: `mcp251xfd_handle_tefif()` is the exported IRQ handler. Helpers read TEF tail, sanity-check tail state, compute TEF length from TX FIFO status, bulk-read TEF objects, process sequence-validated objects, and clear ECC tracking after success.

Control flow: The handler determines pending TEF count, reads with wraparound support, validates sequence numbers against software TEF tail, completes echo SKBs, then batches UINC transfers to advance hardware TEF tail. It updates TX tail/accounting, wakes the queue when space exists, and restarts TX coalescing timer when configured.

State and persistence behavior: Updates TEF head/tail, TX tail, netdev TX stats, echo SKB timestamps, and ECC state.

Dependencies and integration points: Works with TX sequence numbers from `mcp251xfd-tx.c`, ring UINC arrays, hardware timestamp conversion, RX offload echo helpers, and core IRQ handling.

Risks: TEF is authoritative for TX completion; sequence mismatches prevent stale FIFO data from freeing the wrong SKB. Incorrect length inference can stall or double-complete transmissions.

Test signals: TX completion wraparound, full FIFO completion, sequence mismatch erratum path, TX coalescing, echo timestamp correctness, sanity tail mismatch, and queue stop/wake stress.
