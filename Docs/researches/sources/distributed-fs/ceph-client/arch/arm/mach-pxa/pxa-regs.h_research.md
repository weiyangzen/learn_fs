<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-regs.h

Purpose: core PXA virtual/physical IO translation and register access macros.

Important definitions: `UNCACHED_PHYS_0`, `io_v2p(x)`, `io_p2v(x)`, `__REG(x)`, `__REG2(x,y)`, and `__PREG(x)`. Comments document the legacy PXA internal register virtual map.

Control flow and integration: headers use `__REG` and `io_p2v` to define volatile MMIO register lvalues; mapping is established by `generic.c`.

State and persistence: no state, but macros define how all legacy direct register accesses resolve.

Dependencies: assumes ARM `IOMEM()` and `u32` availability.

Risks and test signals: wrong translation breaks essentially all PXA MMIO. Test early boot, timer, IRQ, GPIO, reset, and suspend paths that use direct register macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-regs.h -->
