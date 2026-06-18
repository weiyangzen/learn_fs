# sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup_64.c

Purpose: 64-bit PowerPC early setup for PACA/bootstrap CPU state, exception mode configuration, SMT selection, cache metadata, bolted-memory limits, interrupt/emergency stacks, per-CPU areas, secondary CPU release, and hardlockup defaults.

Important APIs/types/functions: globals `spinning_secondaries`, `ppc64_pft_size`, `ppc64_caches`, `spr_default_dscr`, `__per_cpu_offset`, `__percpu_first_chunk_is_paged`; `setup_tlb_core_data()`, `check_smt_enabled()`, `early_smt_enabled()`, `fixup_boot_paca()`, `configure_exceptions()`, `cpu_ready_for_interrupts()`, `record_spr_defaults()`, `early_setup()`, `early_setup_secondary()`, `panic_smp_self_stop()`, `smp_release_cpus()`, `initialize_cache_info()`, `ppc64_bolted_size()`, `irqstack_early_init()`, `exc_lvl_early_init()`, `emergency_stack_init()`, `setup_per_cpu_areas()`, `memory_block_size_bytes()`, and `disable_hardlockup_detector()`.

Control flow: `early_setup()` installs a temporary PACA before printk-safe code, enables machine checks when possible, discovers CPU features from device tree or PVR, parses early device tree memory/CPU IDs, allocates real PACAs, configures exception endian/AIL/SCV constraints, sets up KUP before feature fixups, initializes MMU and early ioremap, records DSCR, updates PACA kernel MSR, and enables dynamic ftrace for the boot CPU. Common `setup_arch()` later calls 64-bit stack/cache/SMT/percpu hooks. Secondary CPUs run `early_setup_secondary()` to initialize MMU/KUP/interrupt readiness. Stack allocation honors bolted/RMA limits so early interrupt/NMI/MCE handlers avoid faults, with pSeries MCE stacks limited below 4 GiB for RTAS argument placement.

State and persistence: initializes PACA fields, cache topology, SMT boot thread count, per-CPU offsets, emergency stack pointers, TLB core data, DSCR default, exception mode state, and secondary CPU spinloop release function pointer.

Dependencies and integration points: depends on firmware feature bits (PAPR/OPAL), pSeries and OPAL exception configuration, KVM PR/HV constraints, radix/hash MMU, memblock, NUMA early CPU nodes, CPU feature fixups, KUP, ftrace, hardlockup detector, and common setup.

Risks: PACA must be valid before stack protector/kcov/percpu code runs. Exception endian/AIL/SCV setup is constrained by hypervisor and KVM mode. Emergency stacks must be allocated where real-mode/bolted accesses cannot fault. Cache parsing includes POWER8 device-tree workarounds. Per-CPU first-chunk selection differs by MMU mode and can panic on allocation failure.

Test signals: ppc64 boot under pSeries LPAR, PowerNV/OPAL, KVM guest, radix/hash MMU, Book3E, SMT on/off command lines, kdump, secondary CPU bring-up, NMI/MCE path smoke tests, per-cpu allocator diagnostics, and hardlockup detector default behavior.
