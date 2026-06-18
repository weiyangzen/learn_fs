# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdmahw.h

## Purpose
`altera_msgdmahw.h` defines the mSGDMA hardware ABI used by the Altera TSE MSGDMA backend: extended descriptors, CSR registers, response registers, control/status bits, and offset helpers.

## Important APIs, types, and constants
- `struct msgdma_extended_desc` models the descriptor port fields: read/write address low/high, length, burst/sequence, stride, and control.
- Descriptor control macros define SOP/EOP generation, parking, end-on-EOP/length, completion/early/error IRQs, and `GO`.
- `MSGDMA_DESC_CTL_TX_SINGLE` and `MSGDMA_DESC_CTL_RX_SINGLE` are precomposed common controls.
- `struct msgdma_csr` maps status, control, fill-level, response fill-level, and sequence registers.
- CSR status/control masks define busy, FIFO empty/full, stopped/resetting/error/early states, IRQ, reset, stop, stop-on-error/early, global interrupt, and stop-descriptor controls.
- `struct msgdma_response` and response bits expose bytes transferred, status, early termination, and error mask.
- `msgdma_*offs()` macros provide `offsetof()` values for MMIO access helpers.

## Control flow and integration
The header has no executable flow. `altera_msgdma.c` uses it to write descriptors, reset/control engines, inspect fill levels, and parse RX responses.

## State and persistence behavior
All described state is volatile hardware state accessed through MMIO. Descriptors are written to hardware descriptor FIFO/ports rather than persistent memory.

## Dependencies and integration points
It depends on standard bit/offset macros and the utility `GET_BIT_VALUE` macro from the broader driver include context. It is private to the Altera TSE MSGDMA backend.

## Risks and edge cases
Bit definitions and structure layout must match mSGDMA IP. Since offsets derive from C structures, accidental type/field changes alter register programming. Error and early-termination bits must be propagated correctly to the main RX path.

## Test signals
Build with MSGDMA backend, validate descriptor writes on TX/RX, reset and IRQ status behavior, fill-level accounting, response FIFO parsing, and hardware error response propagation.
