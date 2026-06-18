# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu.c

Purpose: Reports RISC-V CPU identity, ISA, MMU, vendor, and cache information through cpuinfo and procfs-style interfaces.

Important APIs/types/functions: Handles CPU feature string formatting, `cpuinfo` population, `show_cpuinfo()`, ISA extension printing, vendor/arch/implementation IDs, and cache block size reporting.

Control flow: During boot, architecture code records per-hart ISA and identity data. When userspace reads `/proc/cpuinfo`, this file iterates online CPUs, formats base ISA and extension strings, prints vendor and MMU information, and exposes cache block parameters when available.

State and persistence: Reads persistent in-kernel per-CPU identity state, global ISA bitmaps, hardware probe data, and DT/ACPI-derived properties. It does not own long-lived mutable state itself.

Dependencies and integration points: Depends on `cpufeature.c`, DT/ACPI CPU descriptions, SBI/CSR identity reads, cache block globals, seq_file, and procfs CPU reporting.

Risks and test signals: Output is userspace-visible and relied on by diagnostics. Heterogeneous harts, vendor extensions, and deprecated ISA strings can produce misleading output. Test `/proc/cpuinfo` on DT and ACPI systems, heterogeneous simulated harts, vendor extension builds, and compat userspace parsing.
