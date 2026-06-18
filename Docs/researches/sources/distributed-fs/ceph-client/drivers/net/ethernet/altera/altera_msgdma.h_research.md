# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdma.h

## Purpose
`altera_msgdma.h` declares the mSGDMA backend callback functions exported to the Altera TSE main driver.

## Important APIs
The declarations cover reset, IRQ enable/disable/clear, TX submission/completion, RX descriptor posting/status, initialization, uninitialization, and RX DMA start: `msgdma_reset()`, `msgdma_tx_buffer()`, `msgdma_tx_completions()`, `msgdma_add_rx_desc()`, `msgdma_rx_status()`, and related helpers.

## Control flow and integration
`altera_tse_main.c` binds these functions into a `struct altera_dmaops` instance for MSGDMA devicetree matches. The header provides prototypes only.

## State and persistence behavior
No state is stored in this header. All functions operate on `struct altera_tse_private` and hardware registers.

## Dependencies and integration points
It requires the forward-visible `struct altera_tse_private` and `struct tse_buffer` definitions from `altera_tse.h` in including translation units.

## Risks and edge cases
Prototype drift between this header, `altera_msgdma.c`, and the `altera_dmaops` function-pointer signature would break builds or runtime backend selection.

## Test signals
Compile the composite Altera TSE driver and verify all MSGDMA callbacks are assigned in match data without warnings.
