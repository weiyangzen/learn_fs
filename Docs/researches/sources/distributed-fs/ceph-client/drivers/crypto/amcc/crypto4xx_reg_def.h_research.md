# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_reg_def.h

## Purpose

`crypto4xx_reg_def.h` is the PPC4xx crypto-engine register and descriptor ABI header. It defines MMIO offsets, interrupt bits, PRNG registers, DMA/ring configuration values, gather/scatter descriptor formats, and packet descriptor formats.

## Important APIs, Types, And Functions

Important definitions include `CRYPTO4XX_*` register offsets, interrupt masks such as `CRYPTO4XX_INT_PDR_DONE` and `CRYPTO4XX_INT_ERROR`, PRNG status/control/result registers, `PPC4XX_*` initialization constants, and descriptor types `union ce_pe_dma_cfg`, `union ce_ring_size`, `union ce_ring_control`, `union ce_io_threshold`, `union ce_part_ring_size`, `struct ce_gd`, `struct ce_sd`, `union ce_pd_ctl`, `union ce_pd_ctl_len`, and `struct ce_pd`.

## Control Flow

There is no executable flow, but core initialization writes these register fields to reset and enable the processing engine, configure rings and byte ordering, seed PRNG, enable interrupts, and push descriptors. Completion flow interprets `ce_pd` control bits such as `PD_CTL_PE_DONE` and `PD_CTL_HOST_READY`.

## State And Persistence Behavior

The header models persistent hardware-visible state: ring base addresses, ring sizes, DMA byte ordering, interrupt state, PRNG seed/result registers, and packet/gather/scatter descriptor ownership bits. Structures are packed because hardware consumes their exact layout.

## Dependencies And Integration Points

It is included by both core and algorithm headers and binds software layout to the PPC4xx Security Subsystem specification. It integrates with DMA coherent memory allocated by the core file.

## Risks And Test Signals

Risks include bitfield layout dependency on compiler/endian behavior, typo-prone register offsets, conflated interrupt clear/mask offsets, and packet length/status field mistakes. Test on big-endian PPC hardware, use hardware register traces, run DMA descriptor selftests, and compare structure sizes/offsets against the datasheet.
