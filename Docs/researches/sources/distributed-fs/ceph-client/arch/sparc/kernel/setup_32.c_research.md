# sources/distributed-fs/ceph-client/arch/sparc/kernel/setup_32.c

Purpose: performs SPARC32 early boot and architecture setup: PROM sync hook, command-line boot switches, CPU model detection, runtime instruction patching, memory base discovery, root/initrd setup, MMU/paging handoff, STOP-A handling, CPU topology registration, and UP delay calibration finalization.

Important APIs/functions: key entry points are `sparc32_start_kernel()`, `setup_arch()`, `sun_do_break()`, `topology_init()`, and `arch_cpu_finalize_init()`. Helpers include `prom_sync_me()`, `process_switch()`, `boot_flags_init()`, `per_cpu_patch()`, and `leon_patch()`. Globals include `cmdline_memory_size`, `boot_cpu_id`, `reboot_command`, `sparc_cpu_model`, `sparc_ttable`, and `stop_a_enabled`.

Control flow: `sparc32_start_kernel()` initializes PROM, identifies CPU model from `cputypval`, applies LEON patching, and enters `start_kernel()`. `setup_arch()` installs trap table pointer, obtains boot args, parses early params and SPARC switches, registers early PROM console, logs architecture, initializes IDPROM/MMU, computes `phys_base`/`pfn_base` from PROM banks, sets root and ramdisk state, registers PROM sync hook, optionally syncs KADB trap table, applies per-CPU instruction patches, initializes paging, and sets possible CPU map. `topology_init()` counts physical CPUs via PROM and registers online CPUs.

State and persistence: initializes runtime boot globals, physical memory base values, root device flags, early console state, trap table pointer, CPU model, and CPU topology. No durable storage is written.

Dependencies and integration points: depends on PROM services, trap table symbols, LEON/sun4m/sun4d CPU model patch sections, MMU load/paging init, IDPROM, generic root/initrd variables, KADB debug vector, sysctl-shared `stop_a_enabled`, and CPU registration.

Risks: early code runs before normal kernel services. CPU model misclassification selects wrong instruction patches. `mem=` parsing overrides PROM memory size. PROM sync temporarily swaps TBR and is marked broken. Topology registration allocates memory during init and reports errors only through return value.

Test signals: boot on sun4m/sun4d/sun4u/LEON, `mem=` command-line behavior, early PROM console, KADB boot path, PROM `sync` command, STOP-A shell entry, `/proc/cpuinfo` physical CPU count, and instruction patch correctness for LEON/non-LEON systems.
