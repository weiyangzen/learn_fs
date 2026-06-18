# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie_regs.h

Purpose: maps Pearl PCIe HDP, HHBM, interrupt, legacy INTx, and system-control register offsets and bit fields for the Pearl transport implementation.

Important APIs/types/functions: macros compute MMIO addresses for HDP control, host write descriptors, RX/TX interrupt control/status/enables, RX descriptor pointers/counts, TX host queue controls, DMA counters, HHBM queue/pool registers, MSI/INTx status/mask registers, and SYSCTL LHOST interrupt offset. Bit definitions include HHBM reset/read/write/done/64-bit flags, HDP interrupt causes such as EP RXDMA/TXDMA/TXEMPTY/HHBM underflow/IPC, PCIe MSI/INTx status bits, legacy INTx assertion bit, Pearl IPC IRQ word construction, LHOST IPC IRQ, and EP reset IRQ.

Control flow: `pearl_pcie.c` uses these macros for descriptor table setup, HHBM initialization, IRQ enable/disable/clear, TX descriptor doorbells, RX polling counters, INTx deassertion, and endpoint reset/IPC interrupts.

State and persistence: no host state; the macros address volatile device registers.

Dependencies and integration points: consumed only by Pearl PCIe code. Register offsets must match the Pearl hardware programming model.

Risks: any incorrect offset or bit definition can cause lost interrupts, corrupted DMA queues, failed reset, or host/endpoint deadlock. Several macros alias offsets for different register meanings, so call-site context matters.

Test signals: Pearl hardware smoke boot, IRQ counter changes in debugfs, TX/RX traffic with descriptor counter movement, HHBM underflow/error handling, legacy INTx deassertion, and endpoint reset on remove.
