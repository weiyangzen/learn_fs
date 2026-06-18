<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/mem.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/mem.c

Purpose: Adds Loongson2EF physical memory ranges to memblock and configures optional CPU address windows.

Important APIs/types/functions: Exports globals `memsize` and `highmemsize`; `prom_init_memory()` adds low memory and optional high memory.

Control flow: Low memory starts at physical zero and spans `memsize << 20`. With address-window support, it computes a power-of-two size for total memory and maps CPU window 3 from 2G to DDR. On 64-bit builds high memory is added at `LOONGSON_HIGHMEM_START`.

State and persistence: Memblock regions define early boot memory layout and survive into the normal memory allocator.

Dependencies and integration: Consumes values initialized in `env.c`; called from `prom_init()`.

Risks: The address-window size calculation depends on `memsize + highmemsize`; non-power-of-two or zero values can misprogram windows. Highmem is ignored on non-64-bit builds.

Test signals: Memblock debug output should show low and high ranges; memory size reported by the kernel should match PMON arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/mem.c -->
