# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/hardware.h

Purpose: central RiscPC physical/virtual hardware address map.

Important APIs/types/functions: defines I/O base/window constants for IOMD, IOC, EASI, MEMC, podule slots, network slot, and related platform address conversion values.

Control flow: no functions; address constants drive MMIO mappings and resource declarations.

State and persistence: constants define how kernel code sees fixed RiscPC hardware windows.

Dependencies and integration points: included by DMA, ecard, IRQ, I/O, and machine setup code, plus mach headers.

Risks: incorrect addresses break virtually every platform driver. These constants must match `io-acorn.S` and machine map descriptors.

Test signals: early boot I/O access, ecard resource ranges, IOMD IRQ/DMA operation, and `/proc/iomem`.
