# sources/distributed-fs/ceph-client/arch/x86/kernel/setup.c

## Purpose
Contains `setup_arch()`, the central x86 boot initialization sequence. It translates boot parameters into kernel state, reserves early memory, processes firmware setup data, initializes CPU/platform subsystems, builds resource maps, configures paging/memblock, and hands off to later architecture init.

## APIs, Types, And Functions
Important globals include `max_low_pfn_mapped`, `max_pfn_mapped`, `_brk_start/_brk_end`, `boot_params`, kernel code/data/bss resources, `boot_cpu_data`, `mmu_cr4_features`, bootloader IDs, `sysfb_primary_display`, `saved_video_mode`, and `command_line`. Public helpers include `extend_brk()`, `ima_free_kexec_buffer()`, `ima_get_kexec_buffer()`, `reserve_standard_io_resources()`, `x86_configure_nx()`, `setup_arch()`, `i386_reserve_resources()`, and `arch_cpu_is_hotpluggable()`.

## Control Flow
`setup_arch()` starts with 32/64-bit page-table and command-line setup, detects OLPC/FW state, installs early traps, initializes CPU/static calls/ioremap, parses boot parameters, runs OEM setup, reserves kernel/initrd/setup_data/BIOS/SNB memory, builds E820/memblock state, processes setup_data entries for E820 extensions, DTB, EFI, IMA, KHO, and RNG seeds, configures NX, parses early params, initializes EFI/DMI/hypervisor/ROM resources, trims BIOS/kernel ranges, computes PFNs, randomizes memory layout, allocates page-table buffers, reserves brk, initializes memory encryption, reserves EFI boot services, real-mode trampoline, direct mapping, log buffer, initrd, ACPI tables, NUMA, crashkernel, KASAN, APIC/IOAPIC/topology, PCI gap/resources, timers, MCE, jiffies, EFI quirks, and unwinder state.

## State And Persistence
Boot parameters are copied into stable globals. Memblock/E820 reservations persist into the resource tree and allocator setup. RNG setup_data is zeroed after ingestion. IMA/KHO buffers are reserved for later consumers. Kernel resources and sysctls persist after boot.

## Dependencies And Integration
Integrates with nearly every x86 boot subsystem: E820, memblock, EFI, ACPI, DMI, hypervisor detection, APIC/MPTABLE/IOAPIC, NUMA, KASLR, memory encryption, KASAN, MTRR/cache, initrd, IMA, kexec handover, sysfb, vgacon, PCI resources, thermal/MCE, timers, and sysctl registration for NMI/reboot/io-delay knobs.

## Risks And Test Signals
Boot ordering is the main risk: memory must be reserved before allocators reuse it, EFI/DMI/hypervisor detection must happen before dependent cache/MTRR work, and setup_data must be mapped/unmapped safely. Other risks include wrong E820 trimming, crashkernel reservation in hotpluggable memory, initrd relocation failure, RNG seed reuse, and APIC/ACPI ordering regressions. Test signals are boot logs across BIOS/EFI/Xen/TDX/SEV/32-bit, memblock debug, `/proc/iomem`, initrd boot, kexec/IMA/KHO paths, NUMA topology, crashkernel reservation, KASAN boot, and APIC/IOAPIC initialization.
