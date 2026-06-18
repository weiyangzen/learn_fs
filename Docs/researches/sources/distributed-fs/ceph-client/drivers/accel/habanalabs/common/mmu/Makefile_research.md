# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/Makefile

## Purpose
This Makefile fragment declares the common HabanaLabs MMU object files for the parent driver build.

## Important APIs, Types, And Functions
The only interface is the `HL_COMMON_MMU_FILES` variable. It lists `common/mmu/mmu.o`, `common/mmu/mmu_v1.o`, `common/mmu/mmu_v2.o`, and `common/mmu/mmu_v2_hr.o`.

## Control Flow
There is no runtime flow. Parent Kbuild logic includes the variable so generic MMU code and v1/v2/v2-HR backends are compiled and linked.

## State And Persistence
No runtime state exists. The persistent effect is build composition for MMU support used by the memory and direct-I/O paths.

## Dependencies And Integration Points
It integrates with parent HabanaLabs Makefiles and source files that call MMU APIs, especially `memory.c`, context initialization, and `hldio.c` VA translation.

## Risks
Removing or misnaming an object can cause link failures or missing ASIC MMU support. Adding unsupported objects can break Kbuild. Path prefixes must remain aligned with parent build expectations.

## Test Signals
Build configurations that require MMU v1, v2, and v2-HR support, and verify no duplicate or missing object linkage.
