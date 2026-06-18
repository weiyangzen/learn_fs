# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/memory.h

## Purpose
This header supplies the SA-1100 physical memory base used by ARM memory layout setup.

## Important APIs, Types, and Functions
- Register/constant macro families: `FLUSH`(3), `MAX`(1), `SECTION`(1), `__AS`(1); examples: `__ASM_ARCH_MEMORY_H`, `MAX_PHYSMEM_BITS`, `SECTION_SIZE_BITS`, `FLUSH_BASE_PHYS`, `FLUSH_BASE`, `FLUSH_BASE_MINICACHE`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/sizes.h`.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (1061 bytes, 38 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
