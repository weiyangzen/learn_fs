# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_tsi148.h

## Purpose
Provides the TSI148 chip contract used by `vme_tsi148.c`: PCI IDs, resource counts, private driver state, DMA descriptor layout, and a comprehensive register/bitfield map for PCI config, local control/status, global CSR, CR/CSR, inbound/outbound windows, DMA engines, interrupts, VME status, errors, RMW, and location monitors.

## Important APIs, Types, and Constants
Key constants include `TSI148_MAX_MASTER`, `TSI148_MAX_SLAVE`, `TSI148_MAX_DMA`, register base arrays such as `TSI148_LCSR_OT[]`, `TSI148_LCSR_IT[]`, `TSI148_LCSR_DMA[]`, `TSI148_LCSR_VIACK[]`, `TSI148_GCSR_MBOX[]`, and mask arrays for LM/VIRQ interrupt enable/status/clear. `struct tsi148_driver` stores MMIO base, wait queues, callback arrays, CR/CSR image, flush image, and serialization mutexes. `struct tsi148_dma_descriptor` is the hardware-consumed big-endian linked-list descriptor; `struct tsi148_dma_entry` wraps it with list and DMA handle state.

## Control Flow and State
The header has no executable code, but every MMIO operation in `vme_tsi148.c` depends on these offsets and masks. Register arrays allow indexed programming of eight outbound and inbound windows, two DMA channels, seven VIRQ acknowledge registers, four mailboxes, and four location monitor bits.

## Dependencies and Integration Points
Depends on Linux PCI ID definitions and VME resource declarations indirectly through the C file. It integrates the generic VME attributes with TSI148-specific encodings such as `OTAT`, `ITAT`, `DSAT`, `DDAT`, `INTEN`, `INTEO`, `INTS`, `INTC`, `VICR`, and `VEAT`.

## Risks and Test Signals
Any offset or endian mismatch can corrupt bridge programming. The DMA descriptor layout must remain 64-bit aligned and big-endian for hardware. Static arrays in a header create per-translation-unit objects, acceptable here because the header is only used locally but worth avoiding for broader inclusion. Test signals are register readback after window programming, DMA descriptor dumps matching the hardware manual, interrupt mask/clear behavior per source, and successful CR/CSR and geographic-address setup.
