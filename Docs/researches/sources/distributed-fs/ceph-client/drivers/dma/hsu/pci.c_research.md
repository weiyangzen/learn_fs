# sources/distributed-fs/ceph-client/drivers/dma/hsu/pci.c

## Purpose
`pci.c` is PCI glue for the Intel HSU DMA core, responsible for BAR mapping, DMA mask setup, IRQ allocation, and interrupt dispatch.

## Important APIs, Types, And Functions
Key routines are `hsu_pci_probe()`, `hsu_pci_irq()`, and `hsu_pci_dma_remove()`. It recognizes Intel MFLD and MRFLD/Tangier IDs and uses `HSU_PCI_CHAN_OFFSET` to locate channel registers.

## Control Flow
Probe enables PCI, maps BAR 0, sets bus mastering/MWI, sets a 32-bit coherent DMA mask, allocates one IRQ vector, fills `hsu_dma_chip`, invokes `hsu_dma_probe()`, requests the IRQ, and disables it on MRFLD-style shared UART interrupt systems. IRQ handling reads DMAISR and delegates each set channel to core status and completion helpers.

## State And Persistence Behavior
Runtime state is the devm-managed chip object, BAR mapping, IRQ vector, and core `chip->hsu` pointer.

## Dependencies And Integration Points
It depends on PCI managed helpers, IRQ vectors, DMA mask APIs, and exported HSU core functions. It integrates with UART drivers that may own the shared interrupt.

## Risks And Test Signals
MRFLD disables its IRQ path intentionally, so UART-side servicing is required. Validate both PCI IDs, channel count from BAR length, interrupt completion on MFLD, and clean unload.
