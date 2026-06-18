# sources/distributed-fs/ceph-client/arch/mips/pci/msi-octeon.c

## Purpose
Implements Octeon architecture MSI allocation, teardown, interrupt masking, dispatch, and initialization.

## Important APIs, Types, And Functions
Public hooks are `arch_setup_msi_irq`, `arch_teardown_msi_irq`, and `octeon_msi_initialize`. State is tracked in `msi_free_irq_bitmask`, `msi_multiple_irq_bitmask`, `msi_irq_size`, `msi_rcv_reg`, and `mis_ena_reg`. IRQ chips are `octeon_irq_chip_msi_pcie` and `octeon_irq_chip_msi_pci`.

## Control Flow
Setup rejects MSI-X, reads MSI capability sizing, allocates aligned contiguous MSI bits under spinlock, writes the MSI message address based on `octeon_dma_bar_type`, updates QSIZE, attaches the descriptor, and writes the MSI message. Teardown computes the owned range using the multiple bitmap and clears allocation bits. Initialization selects PCIe or PCI CSR registers, installs irq chips for all MSI IRQs, and requests parent MSI interrupt lines. Runtime handlers ack the pending CSR bit and invoke `do_IRQ` for the logical MSI.

## State And Persistence
Global bitmaps persist allocation ownership for the boot lifetime. Hardware MSI enable/receive CSRs are programmed and updated under locks. No durable storage.

## Dependencies And Integration Points
Depends on Octeon PCI/PCIe BAR type globals, CVMX CSR definitions, Linux MSI core, IRQ chip APIs, and Octeon feature/host-mode probes.

## Risks And Edge Cases
Bitmap allocation has panic-on-exhaustion behavior for single IRQ failure. Multi-MSI range accounting must remain aligned. PCI mode lacks per-vector mask support. Incorrect BAR type produces invalid MSI addresses or panic. Register arrays for invalid lanes deliberately use addresses that fault if misused.

## Test Signals
MSI-capable PCI/PCIe device tests on Octeon, allocation/teardown stress, multi-MSI devices, interrupt delivery/disable tests, and boot logs for requested parent IRQs are key signals.
