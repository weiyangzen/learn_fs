# sources/distributed-fs/ceph-client/arch/mips/kernel/setup.c

## Purpose
Performs core MIPS architecture setup: CPU probing, command-line construction, memory/initrd/crashkernel setup, device tree initialization, resource registration, SMP possible-map setup, cache/page table initialization, bootloader RNG seed ingestion, debugfs root creation, and CPU finalize bug checks.

## Important APIs, Types, and Functions
- Globals `cpu_data`, `mips_machtype`, `arcs_cmdline`, `mips_io_port_base`, `__kaslr_offset`, `ARCH_PFN_OFFSET`, `kernelsp`, firmware args, and `mips_debugfs_dir`.
- `detect_memory_region()` probes mirrored memory size and adds memblock RAM.
- Initrd helpers parse `rd_start`/`rd_size`, sanitize addresses, optionally byte-swap Octeon initrd, and reserve memory.
- `bootmem_init()`, `early_parse_mem()`, `early_parse_memmap()`, `mips_reserve_vmcore()`, `mips_parse_crashkernel()`, and `request_crashkernel()` establish memory limits/reservations.
- `bootcmdline_init()` combines built-in, DT, and bootloader command lines according to Kconfig policy.
- `arch_mem_init()` orchestrates platform memory setup, early params, FDT reserved memory, bootmem, SWIOTLB/CMA, nosave reservation, and early memtest.
- `resource_init()`, `prefill_possible_map()`, `setup_rng_seed()`, `setup_arch()`, `debugfs_mips()`, coherency early params, and `arch_cpu_finalize_init()`.

## Control Flow
`setup_arch()` probes CPU/CM, initializes PROM, early consoles, CPU reports, optional early R4K bug checks, then calls `arch_mem_init()`. Memory init calls platform memory setup, makes memblock bottom-up, builds the command line, parses early params, ensures kernel sections are in memblock, reserves FDT memory, initializes bootmem/initrd limits, reserves vmcore/crashkernel/device tree/SWIOTLB/CMA/nosave memory, and runs early memtest. Setup then registers resources for each RAM range, runs platform SMP setup and possible CPU prefill, initializes caches and page tables, dumps memblock, and ingests a firmware RNG seed. Later init creates the MIPS debugfs root. CPU finalize records `udelay_val` and runs bug checks.

## State and Persistence
Boot-only state includes memblock maps/reservations, command-line buffers, initrd globals, crash resources, resource tree entries, CPU data, possible CPU map, debugfs root, DMA coherency default, and random seed ingestion. No filesystem persistence.

## Dependencies and Integration Points
Depends on platform hooks (`plat_mem_setup`, `plat_smp_setup`, `prom_init`, `plat_swiotlb_setup`), OF/FDT, memblock, initrd, crash dump/kexec, DMI, DMA/CMA, highmem/NUMA, CPU/cache/page-table code, firmware environment, and bug checks in `r4k-bugs64.c`.

## Risks
Command-line precedence is Kconfig-dependent and easy to duplicate if relocation/FDT paths leave stale buffers. Memblock highmem/lowmem limits must be set after `max_low_pfn` is known. Initrd address conversion must handle bootloader sign-extension mistakes. User `mem=` wipes previous RAM maps. Crashkernel allocation is constrained to 64M alignment below 512M by default. RNG seed must be zeroed after use. Resource registration assumes `UNCAC_BASE == IO_BASE`.

## Test Signals
Boot logs should show correct command line, memory map, initrd, crashkernel, CPU/cache info, and memblock reservations. `mem=`/`memmap=`/`rd_start`/`rd_size`/`coherentio`/`nocoherentio` should alter behavior as expected. Debugfs `mips` directory should exist with debugfs enabled. Kdump and initrd boot tests are key integration signals.
