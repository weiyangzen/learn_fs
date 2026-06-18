<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/nosy.h

Purpose: provides PCILynx register, DMA PCL, FIFO, link, PHY, and interrupt bit definitions used by the `nosy` snoop-mode driver. It is a hardware binding header rather than a behavioral module.

Important APIs and control flow: defines register offsets such as `MISC_CONTROL`, `PCI_INT_STATUS`, `PCI_INT_ENABLE`, DMA channel windows, `FIFO_SIZES`, `LINK_ID`, `LINK_CONTROL`, `LINK_PHY`, `LINK_INT_STATUS`, and `LINK_INT_ENABLE`. Macro families such as `DMA_BREG()`, `DMA_SREG()`, `DMA_CHAN_CTRL(chan)`, and `DMA_WORD*_CMP_*()` encode repeated channel windows. PCL command bits identify receive/transmit/PCI-to-local-bus commands, branch conditions, endian control, interrupt generation, and buffer termination. Interrupt bits describe both PCI-level DMA/link interrupts and link-level bus-reset, PHY, FIFO, cycle, and error conditions.

State and persistence behavior: there is no software state in this file. The values are the persistent hardware ABI between `nosy.c` and TI PCILynx silicon.

Dependencies and integration points: included only by the nosy driver in this work item. It mirrors naming from the PCILynx specification and older Linux 1394 headers so that `nosy.c` can build PCL receive programs and configure link snoop mode without duplicating magic numbers.

Risks and test signals: incorrect bit definitions can corrupt MMIO programming or leave interrupts uncleared. The header lacks include guards, so it relies on current include patterns. Several macros assume five DMA channels and fixed register strides. Test signals include successful compile of `nosy.c`, correct interrupt ownership and clearing, DMA0 receive PCL execution, snoop mode activation through `LINK_CONTROL_SNOOP_ENABLE`, and no unexpected FIFO or DMA error interrupts during capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy.h -->
