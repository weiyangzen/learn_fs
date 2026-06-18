# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/cputype.h

## Purpose
Mirrored arm64 CPU identification header for tools code that needs the kernel's MIDR/MPIDR layout, CPU implementor IDs, part numbers, and erratum range helpers without including the live architecture tree.

## Important APIs, Types, and Functions
Defines MPIDR affinity extraction macros, MIDR field masks, `MIDR_CPU_MODEL()`, `MIDR_CPU_VAR_REV()`, implementor/part constants for Arm, Cavium, Broadcom, Qualcomm, NVIDIA, Fujitsu, HiSilicon, Apple, Ampere, and Microsoft cores, and C helpers around `struct midr_range` and `struct target_impl_cpu`. Inline helpers include `midr_is_cpu_model_range()`, `is_midr_in_range()`, `is_midr_in_range_list()`, `read_cpuid_id()`, `read_cpuid_mpidr()`, `read_cpuid_implementor()`, `read_cpuid_part_number()`, and `read_cpuid_cachetype()`.

## Control Flow, State, and Persistence
There is no mutable storage. Consumers mask a raw MIDR/MPIDR value, compare it against compile-time model/range constants, or read CPU system registers through `read_sysreg_s()`. Range-list traversal is sentinel-based and stops on a zero `.model` entry.

## Dependencies and Integration Points
Depends on arm64 `sysreg.h`, integer type macros, and system-register access helpers. It is used by tools and generated/perf-style code that need the same CPU model and erratum predicates as the kernel.

## Risks and Test Signals
Risk centers on drift from upstream arm64 CPU IDs or erratum masks; a wrong part number silently changes model matching. Test signals are successful tools builds, compile-time use of every range helper, and comparison against known MIDR values for supported cores including newer Cortex/Neoverse and vendor cores.
