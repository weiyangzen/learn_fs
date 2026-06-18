# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpuid_0x2_table.c

## Purpose
`cpuid_0x2_table.c` is the static descriptor table for legacy Intel CPUID leaf `0x2` cache and TLB descriptors. It lets older CPUs without deterministic cache leaf `0x4` translate one-byte descriptor values into cache sizes, cache levels, TLB types, and TLB entry counts.

## Important APIs, Types, and Functions
The only exported object is `const struct leaf_0x2_table cpuid_0x2_table[256]`. `CACHE_ENTRY()` initializes cache descriptor entries with `c_type` and KiB size. `TLB_ENTRY()` initializes TLB descriptor entries with `t_type` and entry count.

Entries include L1 instruction/data cache descriptors, L2 and L3 descriptors, instruction/data/STLB descriptors for 4K, 2M, 4M, and 1G page sizes, and descriptors used by the parser macros in the CPUID types header.

## Control Flow
There is no runtime logic in this file. `cacheinfo.c:intel_cacheinfo_0x2()` calls `cpuid_leaf_0x2()` and iterates descriptors with `for_each_cpuid_0x2_desc()`, which indexes this table and accumulates cache sizes by `CACHE_L1_INST`, `CACHE_L1_DATA`, `CACHE_L2`, and `CACHE_L3`. TLB detection code elsewhere uses the TLB entries for last-level TLB counts.

## State and Persistence
The table is immutable static data. It has no runtime state, side effects, or persistence beyond being compiled into the kernel image.

## Dependencies and Integration Points
It depends on `linux/sizes.h`, `asm/cpuid/types.h`, and local `cpu.h`. Its main integration point is Intel legacy cache/TLB discovery, especially `cacheinfo.c` and any CPUID descriptor iterator using `cpuid_0x2_table`.

## Risks
Incorrect descriptor mappings directly produce wrong cache or TLB reporting on legacy CPUs. Missing descriptors are treated as empty/default entries, so silent under-reporting is possible. Because this is legacy hardware data, broad test coverage is difficult.

## Test Signals
On CPUs or emulators exposing CPUID leaf `0x2` without leaf `0x4`, compare `/proc/cpuinfo`, cacheinfo sysfs, and TLB dmesg lines against vendor documentation. Unit-like validation can iterate known descriptors and verify table type/size/entry values.
