<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/Makefile

### Purpose
The Jazz Makefile declares the platform objects that are always linked for the Jazz machine family.

### Important APIs, Types, And Functions
`obj-y := irq.o jazzdma.o reset.o setup.o` pulls in interrupt/timer setup, virtual DMA mapping, keyboard-controller reset, and platform device registration.

### Control Flow
Kbuild includes this Makefile when the Jazz platform directory is selected by the architecture build. There is no runtime control flow in the file.

### State, Persistence, And Dependencies
The build graph state determines which platform initialization symbols are present in the final kernel. It depends on Kbuild and the Jazz Kconfig path.

### Integration Points
The listed objects provide `arch_init_irq`, `plat_time_init`, `plat_mem_setup`, `jazz_dma_ops`, and restart support used by generic MIPS boot and driver code.

### Risks
Because every object is unconditional for Jazz, unresolved symbols or incompatible config assumptions in any file break all Jazz builds.

### Test Signals
Run a Jazz defconfig build and inspect that all four objects link, platform initcalls run, and no optional driver dependency is accidentally required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/Makefile -->
