# sources/distributed-fs/ceph-client/arch/arm64/kernel/setup.c

Purpose: this is the main ARM64 architecture setup file. It records boot CPU identity, validates and maps the FDT, initializes early memory and firmware paths, builds CPU MPIDR mapping helpers, registers memory resources, and installs panic/boot sanity hooks.

Important APIs and state: globals include `__fdt_pointer`, `mmu_enabled_at_boot`, `boot_args[4]`, `mpidr_hash`, `__cpu_logical_map`, `standard_resources`, and kernel code/data resources. Public functions include `smp_setup_processor_id()`, `arch_match_cpu_phys_id()`, `cpu_logical_map()`, `setup_arch()`, and `arch_cpu_is_hotpluggable()`.

Control flow: `setup_arch()` initializes `init_mm`, command line, KASLR, fixmap/ioremap, FDT scanning, jump labels, early params, dynamic SCS, DAIF state, idmap teardown, Xen/EFI, memblock, paging, ACPI/DT, bootmem, KASAN, standard resources, PSCI, RSI, CPU ops, SMP CPU enumeration, MPIDR hash, SW TTBR0 PAN state, and boot-argument warnings. `setup_machine_fdt()` remaps the FDT, reserves it, scans it, remaps read-only, and records machine description. Resource setup registers System RAM/reserved regions and later splits reserved ranges.

Dependencies and integration: central integration point for firmware discovery (FDT/ACPI/EFI/PSCI/RSI/Xen), memory management, SMP, CPU feature/static-key setup, dynamic SCS, KASAN, panic notifiers, and boot protocol validation.

Risks: ordering is critical: FDT and early params precede memory and CPU feature decisions; DAIF unmasking occurs only after early console readiness; idmap removal prevents speculative TTBR0 use. Broken bootloaders are warned for nonzero x1-x3 and can panic if booted non-EFI with MMU/caches enabled.

Test signals: boot logs for CPU ID, machine model, KASLR offset, boot-arg warnings, PSCI/ACPI selection, resource layout in `/proc/iomem`, CPU hotplug eligibility, and panic notifier output. Device-tree alignment/size errors halt very early.
