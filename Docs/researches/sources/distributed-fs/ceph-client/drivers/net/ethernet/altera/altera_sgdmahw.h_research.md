# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdmahw.h

## Purpose
`altera_sgdmahw.h` defines the legacy SGDMA hardware descriptor and CSR ABI for the Altera TSE SGDMA backend.

## Important APIs, types, and constants
- `struct sgdma_descrip` is the packed DMA descriptor with read/write addresses, next descriptor, byte counts, burst fields, transfer status, and control ownership/EOP/fixed-address bits.
- Status bits identify generic, length, CRC, truncation, PHY, collision, and EOP states.
- Control bits define EOP, read-fixed, write-fixed, and hardware ownership.
- `struct sgdma_csr` maps status, control, and next-descriptor registers with reserved padding.
- CSR status/control macros define error, EOP, descriptor/chain completion, busy, interrupt enables, start, stop-on-error, max-descriptor interrupt, reset, clear-owned-by-hardware, polling mode, and clear-interrupt.
- `sgdma_csroffs()` and `sgdma_descroffs()` provide offsets for register/descriptor field access helpers.

## Control flow and integration
The header has no executable flow. `altera_sgdma.c` uses these definitions to program descriptor memory, start/clear/reset controllers, test busy/EOP state, and parse RX status.

## State and persistence behavior
The described state lives in DMA-visible descriptor memory and volatile SGDMA MMIO registers. Hardware owns descriptors while `SGDMA_CONTROL_HW_OWNED` is set.

## Dependencies and integration points
It depends on bit and offset macros from kernel headers. It is private to the Altera TSE SGDMA backend but must match the SGDMA IP core configured in hardware.

## Risks and edge cases
The packed descriptor layout is a hardware ABI. Changing field sizes/order or control bits can corrupt DMA. The status/control register comments are the authoritative semantic map for the backend; mistakes cause missed interrupts, stuck busy state, or dropped RX/TX.

## Test signals
Validate descriptor programming with SGDMA hardware or simulation, reset/start/interrupt-clear behavior, RX error bit propagation, EOP handling, and ownership-bit transitions during TX/RX.
