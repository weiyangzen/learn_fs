# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdma.h

## Purpose
`altera_sgdma.h` declares the SGDMA backend functions used by the Altera TSE main driver.

## Important APIs
The prototypes cover reset, IRQ enable/disable/clear, TX submission/completion, RX descriptor queueing/status, optional status reporting declaration, initialization, uninitialization, and RX DMA start.

## Control flow and integration
`altera_tse_main.c` assigns these functions to a `struct altera_dmaops` instance for SGDMA hardware. The header provides the compile-time contract for `altera_sgdma.c`.

## State and persistence behavior
No state is stored here. Declared functions operate on `struct altera_tse_private`, `struct tse_buffer`, and SGDMA hardware state.

## Dependencies and integration points
It requires compatible definitions from `altera_tse.h` in users. It pairs with `altera_sgdmahw.h` for hardware layout details.

## Risks and edge cases
The header declares `sgdma_status()` but the implementation in this file set does not define it; if referenced elsewhere, that would be a link risk. Otherwise, signature drift would break the DMAops assignments.

## Test signals
Compile the composite Altera TSE driver and confirm SGDMA callbacks link correctly and match the `altera_dmaops` signatures.
