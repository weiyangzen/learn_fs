# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_regs.h

## Purpose
This header defines the CN23XX PF PCI config offsets, BAR0 CSR offsets, queue register address macros, mailbox registers, DMA counters, MSI-X table layout, interrupt masks, BAR1 index registers, DPI registers, and reset registers used by the LiquidIO PF implementation.

## Important APIs, Types, And Functions
Important macro families include `CN23XX_SLI_IQ_*` for input queues, `CN23XX_SLI_OQ_*` for output queues, `CN23XX_SLI_PKT_MAC_RINFO64()` for PF/VF ring mapping, `CN23XX_SLI_PKT_PF_VF_MBOX_SIG()` and `CN23XX_SLI_MAC_PF_MBOX_INT()` for mailbox signaling, `CN23XX_SLI_MAC_PF_INT_*()` for PF interrupt summary/enable registers, `CN23XX_PEM_BAR1_INDEX_REG()` for BAR1 windows, and `CN23XX_DPI_*`/`CN23XX_RST_*` for DMA and reset programming. Bit masks describe ring enable/reset, endian/snoop/ordering behavior, interrupt status, and input/output thresholds.

## Control Flow
The header has no runtime control flow, but its macros are the address-generation layer used by CN23XX PF setup, queue programming, mailbox processing, interrupt handling, and reset routines.

## State And Persistence
It defines hardware register layout. State exists only in hardware CSRs and PCI config space when the driver uses these macros.

## Dependencies And Integration Points
It depends on kernel `BIT`/`BIT_ULL` definitions supplied through including translation units. It is consumed by `cn23xx_pf_device.c` and indirectly by the PF header.

## Risks
Register macros encode large offsets and stride assumptions; any mismatch corrupts queue or mailbox programming. Endian-dependent `CN23XX_PKT_INPUT_CTL_MASK` changes gather-list byte-swap behavior. The macro `CN23XX_INTR_PCIE_DATA` references `CN23XX_INTR_PKT_DAT`, which appears to be a typo for `CN23XX_INTR_PKT_DATA`; it is not used in the read PF implementation, but would break compilation if referenced. `CN23XX_INTR_ERR` and `CN23XX_INTR_MASK` intentionally select only subsets of possible interrupt bits.

## Test Signals
Build any code path that references every macro family, especially `CN23XX_INTR_PCIE_DATA`. Runtime validation should compare programmed queue, mailbox, BAR1, and interrupt addresses against CN23XX hardware documentation and exercise little- and big-endian builds.
