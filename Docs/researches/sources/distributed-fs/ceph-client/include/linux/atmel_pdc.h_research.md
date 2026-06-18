# sources/distributed-fs/ceph-client/include/linux/atmel_pdc.h

## Purpose
Defines common Atmel Peripheral Data Controller register offsets and transfer-control bits.

## Important APIs, Types, And Functions
Offsets cover receive/transmit current and next pointer/counter registers (`ATMEL_PDC_RPR`, `RCR`, `TPR`, `TCR`, `RNPR`, `RNCR`, `TNPR`, `TNCR`), transfer control/status (`ATMEL_PDC_PTCR`, `ATMEL_PDC_PTSR`), enable/disable bits for RX/TX, and `ATMEL_PDC_SCND_BUF_OFF` for first-to-second buffer spacing.

## Control Flow, State, And Persistence
The header is declarative. Drivers program pointer/counter pairs, enable transfer with `RXTEN`/`TXTEN`, disable with `RXTDIS`/`TXTDIS`, and inspect status. Runtime state is the peripheral's PDC register set.

## Dependencies And Integration Points
No direct includes beyond constants. Integrated by Atmel peripheral drivers that share the PDC layout, including SSC and serial-like devices.

## Risks And Test Signals
Wrong pointer/counter programming can DMA from/to invalid memory. Tests should cover RX/TX enable-disable sequences, next-buffer handoff, zero-count behavior, interrupt completion in consuming drivers, and consistency with peripheral-specific PDC offsets.
