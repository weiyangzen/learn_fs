# sources/distributed-fs/ceph-client/arch/arm/kernel/setup.c

Purpose: central ARM architecture boot setup: identifies CPU and machine, initializes processor/cache feature globals, parses memory, builds resources, initializes MMU/memblock/DT/PSCI/SMP, reserves crashkernel memory, and exposes `/proc/cpuinfo`.

Important APIs/types/functions: `setup_arch`, `setup_processor`, `cpu_init`, `smp_setup_processor_id`, `arm_add_memory`, `hyp_mode_check`, `arch_cpu_is_hotpluggable`, `cpuinfo_op`, and boot params such as `early_mem`. It exports global platform state including `processor_id`, `cacheid`, `elf_hwcap`, `elf_hwcap2`, `system_rev`, and `system_serial`.

Control flow: `setup_arch` selects FDT or ATAGS machine descriptor, initializes fixmap/ioremap, parses early params, initializes memory and paging, registers resources, restart handler, DT CPU maps, PSCI, SMP ops, MPIDR hash, crashkernel reservation, console screen info, and machine early init. `setup_processor` finds the proc info table, initializes CPU/TLB/cache/user vectors, hardware capabilities, cache policy, errata, and CPU mode stacks.

State and persistence: global CPU/machine/hwcap/cache state persists for the lifetime of the kernel and user ABI. Memblock/resource reservations define system RAM visibility and crashkernel areas.

Dependencies and integration: machine descriptors, procinfo assembly tables, DT/ATAGS, memblock, MMU, PSCI, SMP, Xen/EFI, cache/TLB subsystems, kexec, procfs, VFP/hwcap ABI, and reboot handlers.

Risks: boot ordering is fragile; incorrect memory trimming or machine selection prevents boot; hwcap mistakes create user ABI breakage; MPIDR hash must be collision-free for suspend/SMP. Test signals include boot logs, `/proc/cpuinfo`, DT/ATAGS boot variants, `mem=` and crashkernel parameters, SMP bring-up, PSCI selection, and resource maps.
