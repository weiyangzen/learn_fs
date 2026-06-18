# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdma.c

## Purpose
`altera_msgdma.c` implements the modular SGDMA backend for the Altera Triple-Speed Ethernet driver. It provides the `struct altera_dmaops` callbacks used by the main TSE driver to reset mSGDMA engines, control interrupts, post TX/RX descriptors, count TX completions, and read RX response status.

## Important APIs and functions
- `msgdma_initialize()`, `msgdma_uninitialize()`, and `msgdma_start_rxdma()` are no-op hooks because mSGDMA descriptor FIFOs do not need the SGDMA-style descriptor memory setup.
- `msgdma_reset()` resets RX and TX mSGDMA CSR blocks, polls the `RESETTING` status bit with `ALTERA_TSE_SW_RESET_WATCHDOG_CNTR`, warns on timeout, and clears status bits.
- `msgdma_enable_rxirq()`, `msgdma_disable_rxirq()`, `msgdma_enable_txirq()`, and `msgdma_disable_txirq()` manipulate the global interrupt bit in RX/TX CSR control registers.
- `msgdma_clear_rxirq()` and `msgdma_clear_txirq()` clear IRQ status bits.
- `msgdma_tx_buffer()` writes an extended descriptor into the TX descriptor port from a `tse_buffer` DMA address and length.
- `msgdma_tx_completions()` estimates completed TX descriptors from `rw_fill_level`, producer/consumer indexes, and busy status.
- `msgdma_add_rx_desc()` posts an RX descriptor to write into a receive buffer and request completion/error/early IRQs.
- `msgdma_rx_status()` reads response FIFO entries and returns `(status << 16) | length`.

## Control flow
The main TSE driver calls `init_dma()` during open, `reset_dma()` while starting/stopping, preposts RX buffers with `add_rx_desc()`, starts NAPI/IRQs, and calls `tx_buffer()` for SKB transmission. TX completion polling uses `tx_completions()` to advance `tx_cons`. RX NAPI calls `get_rx_status()` to learn whether a response is available and how many bytes/status bits were returned.

## State and persistence behavior
This backend stores no private state beyond fields in `struct altera_tse_private`: CSR/descriptor/response MMIO pointers and TX/RX producer/consumer counters owned by the main driver. mSGDMA hardware FIFOs and status registers are volatile.

## Dependencies and integration points
It depends on `altera_tse.h`, `altera_utils.h`, and `altera_msgdmahw.h` for private state, CSR accessors, bit definitions, and descriptor offsets. It is installed in `altera_tse_main.c` match data as the MSGDMA variant.

## Risks and edge cases
TX completion counting is derived from fill-level and busy bits, so off-by-one errors can leak or prematurely free TX buffers. Reset relies on finite polling and only warns on timeout after proceeding to clear status. RX status returns zero when no response FIFO entry exists, making zero-length/error encoding important. Descriptor writes go directly to MMIO ports and must preserve ordering expected by hardware.

## Test signals
Test mSGDMA reset timeout/warning paths, IRQ enable/disable/clear, TX posting and completion accounting under queue pressure, RX descriptor posting and response parsing, error response bits, and DMA mask behavior for 64-bit descriptor address fields.
