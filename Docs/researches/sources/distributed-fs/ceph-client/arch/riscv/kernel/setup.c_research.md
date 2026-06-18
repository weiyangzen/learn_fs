<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/setup.c

Purpose: Performs RISC-V architecture setup: memory/resource reservation, DTB parsing, spinlock/static-key policy, command line setup, boot CPU state, initrd/elfcore handling, and late init-memory release.

Important APIs/types/functions: Key functions include `add_resource()`, `add_kernel_resources()`, `init_resources()`, `reserve_memblock_reserved_regions()`, `parse_dtb()`, `riscv_spinlock_init()`, `setup_arch()`, `arch_cpu_is_hotpluggable()`, `free_initmem()`, and kernel-offset panic notifier registration.

Control flow: `setup_arch()` parses firmware tables, initializes CPU features and SBI, sets boot command line, reserves kernel/initrd/crashkernel resources, initializes paging/memblock resources, sets up SMP and signal environment, and finalizes architecture knobs. Resource helpers create standard kernel resource regions and reserve memblock areas in iomem.

State and persistence: Establishes `boot_cpu_hartid`, kernel image/code/data/rodata/bss resources, standard resource arrays, qspinlock static key, command-line memory state, and boot-time notifier registrations.

Dependencies and integration points: Integrates firmware DT/ACPI, memblock, resource tree, paging, SBI, SMP, CPU feature discovery, signal frame sizing, initrd, crash dump metadata, and generic setup.

Risks: Resource overlaps or missed memblock reservations can expose kernel memory as RAM. Spinlock static-key selection must match CPU extension support. DTB parsing errors are early-boot fatal.

Test signals: Boot with DT and ACPI, initrd, crashkernel/elfcorehdr, KASLR offset dumps on panic, qspinlock config combinations, NUMA/memblock layouts, and hotplug-capability checks.

Source read size: 410 lines, 10394 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/setup.c -->
