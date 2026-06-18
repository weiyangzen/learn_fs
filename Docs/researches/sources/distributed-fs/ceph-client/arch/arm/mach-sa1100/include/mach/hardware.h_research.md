# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/hardware.h

## Purpose
This machine hardware header wires SA-1100 platform code to the core register map and machine-type predicates, including Assabet-specific helpers when that board is configured.

## Important APIs, Types, and Functions
- Register/constant macro families: `VIO`(2), `io`(2), `PIO`(1), `UNCACHEABLE`(1), `__AS`(1), `__MR`(1); examples: `__ASM_ARCH_HARDWARE_H`, `UNCACHEABLE_ADDR`, `VIO_BASE`, `VIO_SHIFT`, `PIO_START`, `io_p2v`, `io_v2p`, `__MREG`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `SA-1100.h`.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (1388 bytes, 57 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
