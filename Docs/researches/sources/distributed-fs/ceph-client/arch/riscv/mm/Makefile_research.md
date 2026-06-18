<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/Makefile

## Purpose
This Makefile selects RISC-V architecture memory-management objects and build flags.

## Important APIs, Types, And Functions
It sets special flags for `init.o`, removes ftrace from early MM/cacheflush objects when needed, disables KCOV for `init.o`, disables KASAN instrumentation for early KASAN/MM files, and selects MMU, cacheflush, context, pmem, hugetlb, ptdump, debug virtual, DMA noncoherent, and nonstandard cache-op objects.

## Control Flow
Kbuild conditionals wire objects based on MMU, HUGETLB, PTDUMP, KASAN, DEBUG_VIRTUAL, RISCV_DMA_NONCOHERENT, and RISCV_NONSTANDARD_CACHE_OPS.

## State And Persistence
No runtime state is defined; build configuration controls which MM features are compiled.

## Dependencies And Integration Points
It integrates RISC-V MM code with kernel build instrumentation constraints and feature-specific object selection.

## Risks
Instrumenting early page-table code with ftrace/KASAN/KCOV can break boot. Missing conditional objects can remove required hooks for configured subsystems.

## Test Signals
Build matrix coverage across relocatable, ftrace, KASAN, MMU/no-MMU, hugetlb, DMA noncoherent, and debug virtual configs is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/Makefile -->
