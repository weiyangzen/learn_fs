# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/memory.h

Purpose: RiscPC machine memory layout definitions.

Important APIs/types/functions: provides platform memory offset/limits required by `NEED_MACH_MEMORY_H`, including the physical memory layout expected by the SA110 RiscPC port.

Control flow: no runtime flow.

State and persistence: constants affect early memory mapping and address translation.

Dependencies and integration points: used by ARM memory initialization and RiscPC machine setup.

Risks: wrong physical offset or memory constants prevent boot or corrupt memory mapping.

Test signals: early boot memory detection, memblock layout, and successful userspace memory stress.
