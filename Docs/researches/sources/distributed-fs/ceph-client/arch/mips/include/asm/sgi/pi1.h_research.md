# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/pi1.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/pi1.h

### Purpose
`sgi/pi1.h` defines the SGI PI1 parallel port register layout and control/status/DMA/interrupt/timing bit fields.

### Important APIs, Types, And Functions
The key type is `struct pi1_regs`. Macros include `PI1_CTRL_*`, `PI1_STAT_*`, `PI1_DMACTRL_*`, `PI1_INTSTAT_*`, `PI1_INTMASK_*`, and default timer constants `PI1_TIME1` through `PI1_TIME4`.

### Control Flow
Parallel-port drivers read/write 8-bit registers in the struct, configure direction and IRQ enable, start/abort DMA/FIFO operations, inspect status/interrupt bits, and program timing registers.

### State, Persistence, Dependencies, And Integration
State is PI1 MMIO register contents and FIFO/DMA state; no filesystem persistence. It is embedded in `struct sgioc_regs` and integrates with SGI parallel-port and IOC interrupt handling.

### Risks
Interrupt mask polarity is reset-high/enabled-low. DMA control has write-only side effects such as abort and FIFO clear. Register padding must preserve 8-bit-on-32-bit-boundary layout.

### Test Signals
Test parport probe, IRQ handling, read/write direction switching, DMA/FIFO modes, and timer defaults on SGI IOC systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/pi1.h -->
