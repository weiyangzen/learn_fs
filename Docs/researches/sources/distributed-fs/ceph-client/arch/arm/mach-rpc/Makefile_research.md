# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/Makefile

Purpose: object list for Acorn RiscPC machine support.

Important APIs/types/functions: builds `dma.o`, `ecard.o`, `ecard-loader.o`, `fiq.o`, `floppydma.o`, `io-acorn.o`, `irq.o`, `riscpc.o`, and `time.o`.

Control flow: make-time object inclusion only.

State and persistence: none.

Dependencies and integration points: links the platform's DMA, expansion-card bus, FIQ handlers, I/O helpers, interrupt controller, machine descriptor, and timer setup.

Risks: all objects are mandatory, so missing legacy interfaces break the platform build.

Test signals: full `ARCH_RPC` build and link symbol coverage for FIQ/DMA/ecard helpers.
