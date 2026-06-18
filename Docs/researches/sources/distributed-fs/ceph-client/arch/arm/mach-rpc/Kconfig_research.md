# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/Kconfig

Purpose: Kconfig entry for Acorn RiscPC support.

Important APIs/types/functions: `ARCH_RPC` depends on ARMv4 multi-platform constraints, GCC version range, little endian, ATAGS, and MMU. It selects Acorn architecture support, PC FDC possibility, SA110 CPU, FIQ, PATA platform, ISA DMA API, legacy timer tick, machine I/O and memory headers, and no generic ioport mapping.

Control flow: build-time gating only.

State and persistence: none locally.

Dependencies and integration points: enables the legacy RiscPC machine files, IOMD IRQ/DMA, ecard bus, and ATAGS boot path.

Risks: explicit compiler constraints and deprecated ARMv4 assumptions make this fragile in modern toolchains. Lack of DT support means boot path is legacy.

Test signals: GCC 6-8 build, ATAGS boot on RiscPC, and compile rejection under unsupported compiler/architecture combos.
