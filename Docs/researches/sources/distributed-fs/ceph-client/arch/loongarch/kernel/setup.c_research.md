## sources/distributed-fs/ceph-client/arch/loongarch/kernel/setup.c

### Purpose
`setup.c` is the main LoongArch architecture boot setup file. It initializes firmware arguments, CPU and SMBIOS metadata, command-line policy, FDT/ACPI/EFI platform state, memory reservations, resources, legacy I/O windows, possible CPU maps, and the architecture-specific `setup_arch` sequence.

### Important APIs, Types, And Functions
Global state includes `fw_arg0..2`, per-CPU `kernelsp`, `cpu_data`, `b_info`, `init_command_line`, `wc_enabled`, and kernel resource descriptors. Major functions are `arch_cpu_finalize_init`, `setup_writecombine`, `early_parse_mem`, `platform_init`, `arch_mem_init`, `resource_init`, `arch_reserve_pio_range`, `reserve_memblock_reserved_regions`, `prefill_possible_map`, and `setup_arch`.

### Control Flow
`setup_arch` probes CPU/unwinder, initializes environment and EFI/FDT, seeds memblock and page tables, builds boot command line, parses early params, reserves initrd, initializes ACPI/FDT/NUMA/DMI/EFI runtime platform state, then performs memory init, resource registration, jump-label setup, SMP possible-map setup, and KASAN init. Early `mem=` parsing can either enforce a global limit or replace firmware RAM maps with explicit ranges.

### State, Persistence, And Dependencies
Boot-time state persists in global command lines, memblock reservations, resource tree entries, CPU data, board info, write-combine flag, EFI runtime state, flattened/unflattened DT, and NUMA maps. Dependencies span EFI, ACPI, FDT, DMI/SMBIOS, memblock, SWIOTLB, DMA/CMA, crash dump, kexec, SMP, alternatives, and KASAN.

### Integration Points
This is called from generic early boot. `mem.c`, `numa.c`, `smp.c`, `time.c`, `relocate.c`, and platform firmware parsers all feed data into it. Resource and PIO registration affect drivers and `/proc/iomem`; command-line decisions affect every early parameter.

### Risks
Boot order is critical: command-line parsing, memblock setup, platform reservation, and NUMA initialization must occur before page allocator setup. `mem=` can remove firmware-discovered memory and must preserve node assignment under NUMA. FDT is skipped when ACPI root pointer exists. Legacy ISA I/O registration assumes the range starts at logic PIO offset 0. SMBIOS parsing uses fixed offsets and must match table versions.

### Test Signals
Boot ACPI and FDT systems, built-in DTB fallback, command-line force/extend/bootloader modes, `mem=` forms, crashkernel/vmcore reservation, initrd reservation, writecombine parameter, NUMA, legacy ISA I/O, EFI runtime, and KASAN builds. Compare `/proc/iomem`, DMI logs, and CPU possible/present masks.
