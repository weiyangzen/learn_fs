# sources/distributed-fs/ceph-client/arch/arc/mm/init.c

Purpose: performs ARC memory discovery, memblock setup, zone limits, initrd/reserved-memory handling, and highmem PFN validation.

Important APIs/functions: `arc_get_mem_sz()`, early parameter `setup_mem_sz()`, `early_init_dt_add_memory_arch()`, `arch_zone_limits_init()`, `setup_arch_memory()`, `arch_mm_preinit()`, and highmem `pfn_valid()`.

Control flow: DT memory parsing records the first lowmem bank at `CONFIG_LINUX_RAM_BASE`; additional banks become highmem when configured. `setup_arch_memory()` initializes `init_mm`, low PFN bounds, reserves kernel/initrd/FDT memory, scans reserved memory, dumps memblock state, computes highmem PFNs, sets `arch_pfn_offset`, and calls `kmap_init()`. `arch_mm_preinit()` frees highmem reservation for normal use and validates page-table page sizing.

State and persistence: owns `swapper_pg_dir`, `low_mem_sz`, highmem bounds, `high_mem_start/high_mem_sz`, and exported `arch_pfn_offset`. Memblock reservations determine early allocator state.

Dependencies and integration: depends on DT memory callbacks, memblock, initrd, reserved-memory scanning, ARC section symbols, highmem kmap setup, and generic zone setup.

Risks: DT base must match `CONFIG_LINUX_RAM_BASE` for lowmem. Highmem without PAE has noncontiguous physical address assumptions; `pfn_valid()` masks holes. Incorrect memblock reservations can overwrite kernel/initrd/FDT or allocate `mem_map` in unreachable highmem.

Test signals: boot with DT memory, `mem=` override, initrd boot, highmem and PAE variants, `/proc/iomem`/zone sizing, and sparse/hole PFN validation.
