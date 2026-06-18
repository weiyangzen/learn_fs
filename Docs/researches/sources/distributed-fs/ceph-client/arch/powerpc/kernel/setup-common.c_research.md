# sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup-common.c

Purpose: common PowerPC architecture setup shared by 32-bit and 64-bit builds. It owns machine descriptor selection, reboot/poweroff/halt glue, `/proc/cpuinfo`, initrd validation, SMP CPU-map construction, legacy I/O discovery, panic notifiers, cache-coherency checks, hardware info logging, and the main `setup_arch()` sequence.

Important APIs/types/functions: globals `ppc_md`, `machine_id`, `boot_cpuid`, cache block sizes, legacy IRQ globals, `machine_shutdown()`, `machine_restart()`, `machine_power_off()`, `machine_halt()`, `arch_get_random_seed_longs()`, `cpuinfo_op`, `check_for_initrd()`, SMP state (`threads_per_core`, `cpu_to_phys_id`), `smp_setup_cpu_maps()`, `probe_machine()`, `check_legacy_ioport()`, `setup_panic()`, `ppc_printk_progress()`, `print_system_info()`, `smp_setup_pacas()`, and `setup_arch()`.

Control flow: `setup_arch()` initializes KASAN, command line, device tree, cache info, RTAS, initrd, machine descriptor, panic notifiers, power-save hooks, serial/early console, CPU maps, xmon, SMT state, memory topology, PACAs/TLB data, hardware info, init mm, stacks, MCE, secondary CPU release, memory initialization, platform-specific setup, speculative-execution mitigations, paging, and MMU contexts. SMP CPU mapping parses CPU nodes and `ibm,ppc-interrupt-server#s`/`reg`, handles boot-core renumbering, pSeries LPAR capacity, SMT thread masks, and PACA allocation. Machine probing walks linker-provided `machdep_calls` records and selects the first compatible/probing platform.

State and persistence: establishes global architecture state for the lifetime of the kernel: machine callbacks, boot CPU IDs, cache sizes, CPU possible/present/physical maps, PACAs, panic notifiers, legacy IRQ routes, and hardware description strings. It also validates/initrd roots and may register platform devices such as `pcspkr`.

Dependencies and integration points: central integration with OF device tree, memblock, RTAS initialization, platform `ppc_md` callbacks, SMP/PACA, xmon, serial, panic/fadump, KASLR reporting, cache coherency, memory topology, MMU, livepatch, MCE, and security mitigation setup.

Risks: boot-order regressions are severe because many subsystems rely on earlier setup state. CPU thread mapping assumes a uniform thread count per CPU. Machine descriptor matching must not leave stale `ppc_md` entries. Panic notifiers run under hard IRQ-disabled/fatal contexts. Legacy I/O detection depends on device-tree heuristics. Cache-coherency mismatch intentionally BUGs because DMA would be unsafe.

Test signals: ppc32/ppc64 boot tests across pSeries, powernv, CHRP, BookE, and kdump; verify `/proc/cpuinfo`, CPU hotplug capacity, initrd detection, panic/fadump notifiers, serial console, legacy keyboard/floppy detection, machine descriptor logs, stack allocation, and mitigation setup ordering.
