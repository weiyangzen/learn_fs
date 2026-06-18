# subset-b-000773 research

This grouped report covers the requested PowerPC kernel CPU setup, DMA, ePAPR, crash dump, and EEH PCI error recovery files from the Ceph client source snapshot. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_ppc970.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_ppc970.S

## Purpose
`cpu_setup_ppc970.S` provides low-level PPC970/PPC970MP hypervisor-mode setup and restore routines used by the Book3S 64 CPU table. It programs HID registers before normal kernel execution, saves selected CPU state, and restores that state after low-level transitions where the MMU context may be unavailable.

## Important APIs, Types, And Functions
Exported assembly entry points are `__cpu_preinit_ppc970`, `__setup_cpu_ppc970`, `__setup_cpu_ppc970MP`, and `__restore_cpu_ppc970`. The file defines a small `cpu_state_storage` data area holding HID0, HID1, HID4, and HID5 snapshots. It relies on SPR constants including `SPRN_HID0`, `SPRN_HID1`, `SPRN_HID4`, `SPRN_HID5`, and `SPRN_HIOR`.

## Control Flow
All major routines first test MSR HV state and return or downgrade features when not running in hypervisor mode. Preinit clears HID4 real-mode cache-inhibited mode, large-page and DCBZ-related HID5 bits, enables HID1 fetch cacheability/prefetch, and clears HIOR. CPU setup selects PPC970 or PPC970MP idle/deep-nap HID0 behavior, writes HID0 with repeated reads/synchronization, attempts to set HID4 LPES1, saves HID state, and if the bit does not stick removes `CPU_FTR_HVMODE` from the active CPU spec. Restore clears unsafe HID4 state and HIOR, then writes the saved HID registers with the required sync/isync sequencing.

## State And Persistence
State is per-kernel in-memory assembly data, not persistent storage. The only durable side effect is hardware CPU SPR programming and mutation of the boot CPU's `cpu_spec` feature bits when HV mode is unavailable.

## Dependencies And Integration Points
The PPC970 entries in `cpu_specs_book3s_64.h` reference these routines through `cpu_setup` and `cpu_restore`. It depends on PowerPC assembly helpers, CPU feature structures, page/cache constants, and correct early boot relocation behavior.

## Risks
Incorrect SPR ordering can leave the CPU in an unsafe cache or interrupt-prefix state. The shared `cpu_state_storage` is minimal and assumes the saved boot setup is suitable for later restore. The `no_hv_mode` path mutates the active CPU spec through register `r4`, so calling convention changes would be dangerous.

## Test Signals
Signals are architecture boot tests on PPC970-class hardware or emulators, suspend/restore paths invoking `cpu_restore`, absence of early machine checks, and feature detection showing `CPU_FTR_HVMODE` only when HID4 LPES programming succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_ppc970.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs.h

## Purpose
`cpu_specs.h` is the compile-time selector for PowerPC CPU specification tables. It includes exactly the CPU descriptor header(s) needed by the configured kernel family so `cputable.c` can expose a single `cpu_specs[]` array to early CPU identification.

## Important APIs, Types, And Functions
The file declares no functions or types. Its important contract is conditional inclusion of `cpu_specs_47x.h`, `cpu_specs_44x.h`, `cpu_specs_8xx.h`, `cpu_specs_e500mc.h`, `cpu_specs_85xx.h`, `cpu_specs_book3s_32.h`, and `cpu_specs_book3s_64.h` based on `CONFIG_*` symbols.

## Control Flow
Control flow is preprocessor-only. Build configuration chooses mutually exclusive or additive CPU families; for example 47x wins over 44x, e500mc wins over 85xx, and Book3S 32/64 tables are included for their respective builds.

## State And Persistence
No runtime state exists here. The included file contributes `static struct cpu_spec cpu_specs[] __initdata`, which is consumed during boot and later discarded with other init data.

## Dependencies And Integration Points
It is included directly by `cputable.c`. The correctness of `identify_cpu()` depends on this include graph producing a non-empty `cpu_specs` array with a default or exact PVR match appropriate for the target architecture.

## Risks
Configuration overlap can produce duplicate `cpu_specs` definitions if new include branches are added carelessly. Missing a configured CPU family causes `BUILD_BUG_ON(!ARRAY_SIZE(cpu_specs))` or a boot-time `BUG()` if no PVR match exists.

## Test Signals
Build coverage across PowerPC subarchitectures is the main signal. Runtime boot logs should identify the expected CPU name/platform and avoid falling into a generic default unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_44x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_44x.h

## Purpose
`cpu_specs_44x.h` defines the PVR match table for 44x-family BookE PowerPC cores. It maps 440/460/APM821xx revisions to kernel CPU features, user-visible HWCAPs, MMU type, cache line sizes, setup routines, machine-check handlers, and platform strings.

## Important APIs, Types, And Functions
The file contributes `static struct cpu_spec cpu_specs[] __initdata`. Entries cover 440GR, 440EP, 440GRX, 440EPX, 440GP, 440GX, 440SP, 440SPe, 460EX, 460GT, 460SX, APM821XX, and a generic 44x fallback. It references setup helpers such as `__setup_cpu_440ep`, `__setup_cpu_440gx`, `__setup_cpu_440spe`, `__setup_cpu_460ex`, `__setup_cpu_460gt`, `__setup_cpu_460sx`, and machine-check handlers including `machine_check_4xx` and `machine_check_440A`.

## Control Flow
`identify_cpu()` scans this array in declaration order and picks the first `(pvr & pvr_mask) == pvr_value` match. The table intentionally places exact or revision-specific masks before broader defaults, including logical PVR variants for 440EP/440EPx.

## State And Persistence
The array is init-only metadata. Its selected entry is copied into the persistent `the_cpu_spec` object by `cputable.c`, after which the table can be discarded.

## Dependencies And Integration Points
It depends on 44x CPU feature macros, MMU feature macros, machine-check implementations, and CPU setup assembly/C helpers. The user-visible flags feed `AT_HWCAP`, and cache sizes feed cache maintenance code.

## Risks
PVR mask ordering is fragile: a broad match before a revision-specific entry would select the wrong setup routine or omit FPU exposure. The default entry can hide unsupported silicon by booting as generic 44x. Incorrect machine-check selection risks poor fault diagnosis.

## Test Signals
Booting each supported SoC should report the right CPU name and platform, expose FPU HWCAP only where listed, use 32-byte I/D cache lines, and survive 44x machine-check and cache/TLB invalidation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_44x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_47x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_47x.h

## Purpose
`cpu_specs_47x.h` defines CPU descriptors for 47x/476-class embedded PowerPC cores. It distinguishes key 476 variants and exposes the 47x MMU/cache model to the rest of the kernel.

## Important APIs, Types, And Functions
The header supplies `static struct cpu_spec cpu_specs[] __initdata`. Entries cover 476 DD2, 476fpe, 476 ISS, other 476 cores, and a generic 47x fallback. They use `CPU_FTRS_47X`, sometimes add `CPU_FTR_476_DD2`, expose BookE and FPU user features where applicable, set `MMU_FTR_TYPE_47x` with broadcast invalidation features, and use `machine_check_47x`.

## Control Flow
Selection is first-match PVR scanning. The DD2 exact `0xffffffff` match appears before broader 476 matches so the DD2 feature bit is preserved only for the known revision.

## State And Persistence
This is boot-time metadata copied into `cur_cpu_spec`; no direct runtime mutable state is kept in the table.

## Dependencies And Integration Points
The descriptors integrate with `cputable.c`, BookE MMU code, machine-check handling, user HWCAP generation, and TLB invalidation paths that depend on `MMU_FTR_USE_TLBIVAX_BCAST` and `MMU_FTR_LOCK_BCAST_INVAL`.

## Risks
The default generic 47x entry omits FPU and broadcast invalidation feature bits listed on specific entries, so unexpected PVRs may boot with conservative behavior. Mask mistakes can misclassify ISS or DD2 cores.

## Test Signals
Expected signals are correct CPU name on boot, FPU HWCAP on matching 476 variants, 128-byte D-cache line behavior, and stable SMP TLB invalidation on systems using broadcast invalidates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_47x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_85xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_85xx.h

## Purpose
`cpu_specs_85xx.h` describes classic Freescale e500/e500v2 85xx CPUs for BookE kernels that are not using the newer e500mc table. It maps PVRs to SPE/EFP capabilities, FSL embedded MMU features, setup routines, and machine-check behavior.

## Important APIs, Types, And Functions
It defines `COMMON_USER_BOOKE` and `static struct cpu_spec cpu_specs[] __initdata`. Entries include e500, e500v2, and a generic E500 fallback. Specific entries reference `__setup_cpu_e500v1`, `__setup_cpu_e500v2`, `machine_check_e500`, `cpu_down_flush_e500v2`, and set PMC counts.

## Control Flow
`identify_cpu()` scans exact high-16-bit PVR matches before the zero-mask default. e500v2 adds double-precision EFP compatibility, big physical address support, and a CPU-down flush hook relative to e500.

## State And Persistence
The table itself is discarded after init. The chosen feature and callback fields persist in `the_cpu_spec` and guide MMU, machine-check, perf, and CPU hotplug behavior.

## Dependencies And Integration Points
It integrates with FSL BookE MMU support, SPE/EFP user ABI exposure, e500 CPU setup assembly, and platform strings such as `ppc8540`/`ppc8548`.

## Risks
The generic fallback can boot unrecognized 85xx CPUs with incomplete setup callbacks or feature exposure. Incorrect user feature flags would affect userspace ABI detection for SPE/EFP code.

## Test Signals
Boot on e500/e500v2 should identify the exact name, expose the expected `PPC_FEATURE_HAS_SPE_COMP` and EFP flags, initialize four PMCs on matched entries, and survive CPU offline flush and machine-check tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_85xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_8xx.h

## Purpose
`cpu_specs_8xx.h` provides the CPU descriptor for classic 8xx PowerPC processors. It is the minimal cputable input for kernels targeting the 8xx MMU and cache model.

## Important APIs, Types, And Functions
The file defines `static struct cpu_spec cpu_specs[] __initdata` with one 8xx entry. The descriptor uses `PVR_8xx`, `CPU_FTRS_8XX`, `MMU_FTR_TYPE_8xx`, 16-byte I/D cache line sizes, `machine_check_8xx`, and platform string `ppc823`.

## Control Flow
There is a single high-16-bit PVR match. Unlike other tables, there is no explicit zero-mask default in this file, so unsupported PVRs should fail identification rather than silently booting as generic 8xx.

## State And Persistence
Only init-time metadata is defined here. The selected descriptor is copied to `cur_cpu_spec` and then drives runtime feature checks.

## Dependencies And Integration Points
It integrates with `cputable.c`, 8xx MMU initialization, cache maintenance, machine-check handling, and userspace HWCAP generation. The comment notes possible doze support if the 8xx code is present.

## Risks
The lack of a fallback is intentional but means any new 8xx PVR must be added explicitly. Cache-line size or MMU feature errors would affect low-level memory management and DMA/cache coherency assumptions.

## Test Signals
Successful 8xx boot should identify the CPU as `8xx`, expose 32-bit MMU HWCAPs, use 16-byte cache blocks, and route machine checks through `machine_check_8xx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_32.h

## Purpose
`cpu_specs_book3s_32.h` is the 32-bit Book3S/classic PowerPC CPU descriptor table. It covers 603/604/G2/e300, 740/750, and G4-class 7400/7410/745x/744x variants, mapping PVR revisions to feature workarounds, PMU types, setup routines, HWCAPs, and MMU feature flags.

## Important APIs, Types, And Functions
The file defines `COMMON_USER` and `static struct cpu_spec cpu_specs[] __initdata`. It references setup routines such as `__setup_cpu_603`, `__setup_cpu_604`, `__setup_cpu_750`, `__setup_cpu_750cx`, `__setup_cpu_750fx`, `__setup_cpu_7400`, `__setup_cpu_7410`, and `__setup_cpu_745x`. It also selects `machine_check_generic` or `machine_check_83xx`, IBM/G4 PMC types, high-BAT features, HPTE table support, Altivec compatibility, and variant-specific CPU feature macros like `CPU_FTRS_750FX2` or `CPU_FTRS_7450_20`.

## Control Flow
The array is ordered from exact revision matches to broad family matches and finally a generic PPC default for the 604 section. `identify_cpu()` performs linear first-match PVR selection, so comments about specific revisions are part of the functional contract.

## State And Persistence
The table is `__initdata`; selected fields persist in `the_cpu_spec`. User feature fields become visible to userspace through aux vectors, while MMU/cache fields influence low-level memory behavior.

## Dependencies And Integration Points
It integrates with classic 32-bit Book3S boot, feature fixups, PMU/perf, machine-check paths, cache maintenance, and processor-specific setup files. `CONFIG_PPC_BOOK3S_603`, `CONFIG_PPC_BOOK3S_604`, and `CONFIG_PPC_83xx` gate table portions.

## Risks
Ordering mistakes are high risk because many entries share high PVR bits but require revision-specific feature masks, especially 750FX/7450/7455/7447 families. The default generic PPC entry can mask missing support. Incorrect HWCAP Altivec or FPU exposure changes userspace ABI behavior.

## Test Signals
Test signals include boot identification for old 32-bit systems, correct `/proc/cpuinfo` platform, HWCAP FPU/Altivec flags, PMU counter availability, and regression tests for feature fixups and machine-check handling on emulated or real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_64.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_64.h

## Purpose
`cpu_specs_book3s_64.h` defines the 64-bit Book3S PVR table for PPC970, POWER5 through POWER11, Cell, and PA6T processors. It is the static fallback and compatibility-mode CPU description path used when CPU features are not built dynamically from device tree.

## Important APIs, Types, And Functions
The file defines common user feature macro groups for PPC64 and POWER generations, then supplies `static struct cpu_spec cpu_specs[] __initdata`. Important callbacks include PPC970 setup/restore, POWER7/8/9/10 setup and restore, PA6T setup/restore, and early machine-check handlers for POWER7-10. Entries set MMU feature groups, cache line sizes, PMC counts/types, platform strings, user `PPC_FEATURE*` and `PPC_FEATURE2*` flags, and POWER9 DD revision workaround feature sets.

## Control Flow
`identify_cpu()` scans in order. Exact architected compatibility PVR entries, raw PVR entries, and DD-specific POWER9 entries rely on specific-before-generic ordering. PPC970MP DD1.0 is matched exactly before the broader PPC970MP entry to avoid deep-nap setup.

## State And Persistence
The init-only table is copied into `the_cpu_spec`. The selected fields persist as the authoritative CPU feature, MMU feature, PMU, machine-check, setup, and restore contract for the booted kernel.

## Dependencies And Integration Points
This table integrates with `cpu_setup_ppc970.S`, POWER setup routines, machine-check real-mode handlers, MMU selection, perf, feature fixups, and user HWCAP export. It also preserves compatibility-mode PMU information when logical PVR values override real PVR values in `cputable.c`.

## Risks
Incorrect PVR matching can expose unsupported ISA facilities to userspace or miss processor errata bits. POWER9 revision masks are especially sensitive. Adding POWER generation support requires keeping user feature macros, setup/restore hooks, PMU state, and machine-check handlers consistent.

## Test Signals
Signals include booting under raw and architected PVR modes, correct platform strings for POWER generations, accurate HWCAP2 ISA bits, PMU availability, machine-check handler selection, and PPC970 HV-mode behavior through the referenced setup routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_book3s_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_e500mc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_e500mc.h

## Purpose
`cpu_specs_e500mc.h` describes e500mc, e5500, and e6500 BookE CPUs. It is the newer FSL embedded CPU table used instead of the classic 85xx e500 table when `CONFIG_PPC_E500MC` is enabled.

## Important APIs, Types, And Functions
It defines `COMMON_USER_BOOKE` differently for PPC32 and PPC64, then contributes `static struct cpu_spec cpu_specs[] __initdata`. Entries reference `__setup_cpu_e500mc`, `__setup_cpu_e5500`, `__setup_cpu_e6500`, 64-bit restore callbacks for e5500/e6500, `machine_check_e500mc`, and CPU-down flush hooks.

## Control Flow
PVR high-16-bit matches select e500mc, e5500, or e6500. The e500mc entry is present only for PPC32 builds, while e5500/e6500 support both 32-bit and 64-bit configurations with restore callbacks excluded on PPC32.

## State And Persistence
As with other CPU spec tables, this is init-only metadata copied into `cur_cpu_spec`. The selected descriptor controls persistent runtime feature checks, cache line sizing, PMU count, and CPU hotplug flush behavior.

## Dependencies And Integration Points
It integrates with FSL BookE MMU features including `MMU_FTR_BIG_PHYS` and `MMU_FTR_USE_TLBILX`, user HWCAPs for FPU/Altivec/ISEL, machine-check handling, and platform strings `ppce500mc`, `ppce5500`, and `ppce6500`.

## Risks
The file has no generic default, so unsupported PVRs fail identification. Conditional PPC32/PPC64 fields must stay aligned with available assembly helpers. Incorrect user features could mislead applications about FPU, Altivec, 64-bit, or BookE support.

## Test Signals
Boot tests should identify exact CPU names, expose ISEL and FPU/Altivec flags as appropriate, use 64-byte I/D cache lines, initialize four or six PMCs, and exercise CPU restore/down-flush paths on SMP or hotplug-capable systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_specs_e500mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cputable.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cputable.c

## Purpose
`cputable.c` owns PowerPC CPU identification from static PVR tables. It selects a `cpu_spec`, copies it into permanent storage, invokes processor setup when required, records the base platform string, and initializes static keys for CPU/MMU feature checks.

## Important APIs, Types, And Functions
Important globals are `the_cpu_spec`, exported `cur_cpu_spec`, and `powerpc_base_platform`. Key functions are `set_cur_cpu_spec()`, `setup_cpu_spec()`, `identify_cpu()`, `identify_cpu_name()`, `cpu_feature_keys_init()`, and `mmu_feature_keys_init()`. The file includes `cpu_specs.h`, which supplies the active `cpu_specs[]` table.

## Control Flow
`identify_cpu()` relocates the table pointer, linearly scans PVR masks, and calls `setup_cpu_spec()` for the first match. Setup copies the descriptor using `memcpy`, preserves PMU fields and PMAO bug bits when logical PVR overrides a real PVR-derived spec, enables 32-bit KUAP by default when configured, records the platform string on first call, and invokes `cpu_setup` for PPC64/BookE. Static-key init disables jump labels for features absent from `cur_cpu_spec`.

## State And Persistence
The selected CPU descriptor is copied into `the_cpu_spec` marked `__ro_after_init`; `cur_cpu_spec` points to it. `powerpc_base_platform` persists the platform string of the real PVR. Static key arrays persist for optimized feature tests.

## Dependencies And Integration Points
It depends on early relocation macros, `struct cpu_spec`, feature bit definitions, CPU setup callbacks, OF/platform setup, and jump label support. It is used by early boot, dynamic device-tree CPU features for naming, and runtime `cpu_has_feature()`/`mmu_has_feature()` fast paths.

## Risks
No matching PVR calls `BUG()`, so table omissions are fatal. Copying and relocation happen very early; KASAN and relocation comments explain why simple struct assignment is avoided. Static keys must be initialized after `cur_cpu_spec` is final or feature checks can be wrong.

## Test Signals
Boot logs should show correct CPU name/platform, feature fixups should match selected bits, jump-label feature checks should agree with `cur_cpu_spec`, and compatibility logical PVR boots should retain real PMU information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cputable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/crash_dump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/crash_dump.c

## Purpose
`crash_dump.c` implements PowerPC kdump support helpers. It reserves low memory for kdump trampolines, creates branch trampolines for non-static kernels, copies memory from the crashed kernel image, distinguishes kdump from firmware-assisted dump, and frees crashkernel pages while preserving RTAS memory.

## Important APIs, Types, And Functions
Key functions are `reserve_kdump_trampoline()`, `setup_kdump_trampoline()`, private `create_trampoline()`, `copy_oldmem_page()`, exported `is_kdump_kernel()`, and RTAS-specific `crash_free_reserved_phys_range()`. It uses `patch_instruction()`, `patch_branch()`, memblock APIs, `ioremap_cache()`, `copy_to_iter()`, `is_fadump_active()`, and RTAS device-tree properties.

## Control Flow
On non-static kernels, low memory is reserved and trampoline slots are populated every eight bytes. `create_trampoline()` emits a NOP followed by a branch that effectively reaches `addr + PHYSICAL_START`. `copy_oldmem_page()` uses direct mapping for normal memory and temporary cached ioremap for non-memory regions. `is_kdump_kernel()` returns true only for kexec crash dumps, not fadump. RTAS page freeing skips pages overlapping the RTAS reserved region.

## State And Persistence
State effects are boot-time memblock reservations, patched trampoline instructions in low memory, and page reservation accounting. There is no file-backed persistence.

## Dependencies And Integration Points
It integrates with kexec/kdump, `/proc/vmcore` oldmem reads, pSeries FWNMI trampoline addresses, fadump, RTAS, and crashkernel memory management.

## Risks
Branch range assumptions are delicate and tied to the trampoline layout. `copy_oldmem_page()` must avoid invalid direct mappings for non-RAM. Freeing crashkernel pages without RTAS overlap checks can corrupt firmware runtime services.

## Test Signals
Signals include successful kdump boot and vmcore reads, reserved low memory visibility, correct FWNMI trampoline behavior on pSeries, `is_kdump_kernel()` false under fadump, and no RTAS failures after shrinking crashkernel memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/crash_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dawr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dawr.c

## Purpose
`dawr.c` manages PowerPC Data Address Watchpoint Register programming and the POWER9 debugfs override that can force-enable DAWR despite platform restrictions. It bridges generic hardware breakpoint requests to DAWR/DAWRX SPRs or platform callbacks.

## Important APIs, Types, And Functions
Exported global `dawr_force_enable` controls forced use. `set_dawr()` programs a DAWR slot from `struct arch_hw_breakpoint`. Helpers include `disable_dawrs_cb()`, `dawr_write_file_bool()`, `dawr_enable_fops`, and init function `dawr_force_setup()`.

## Control Flow
`set_dawr()` builds DAWRX bits from breakpoint read/write/translate/privilege type and doubleword-biased length, then delegates to `ppc_md.set_dawr()` if present or writes DAWR0/DAWR1 SPR pairs directly. The debugfs write path first validates that an LPAR hypervisor permits DAWR writes unless force-enable is already set, then updates the boolean and clears all DAWRs on all CPUs when disabling. Init auto-enables DAWR for CPUs with `CPU_FTR_DAWR`; POWER9 without that feature gets `dawr_enable_dangerous`.

## State And Persistence
Runtime state is the global boolean and per-CPU DAWR SPR contents. Debugfs changes are not persistent across reboot.

## Dependencies And Integration Points
It integrates with perf/hw-breakpoint code, platform machine descriptors, hypervisor calls, firmware feature detection, debugfs, CPU feature detection, and `nr_wp_slots()`.

## Risks
Forcing DAWR on restricted POWER9 systems can expose hardware errata or hypervisor denial behavior. Length encoding must handle zero or invalid lengths defensively through callers. Clearing DAWRs across CPUs is asynchronous with running debug users.

## Test Signals
Signals include hardware breakpoint tests, debugfs toggling on POWER9 LPARs, expected `-ENODEV` when the hypervisor rejects DAWR writes, and all watchpoint slots cleared after disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dawr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dbell.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dbell.c

## Purpose
`dbell.c` implements the PowerPC doorbell exception handler. Doorbells are used primarily for inter-processor interrupts and host/KVM notification paths.

## Important APIs, Types, And Functions
The file defines `doorbell_exception` with `DEFINE_INTERRUPT_HANDLER_ASYNC`. In SMP builds it uses `set_irq_regs()`, tracing hooks, `ppc_msgsync()`, `should_hard_irq_enable()`, `do_hard_irq_enable()`, `kvmppc_clear_host_ipi()`, per-CPU `irq_stat.doorbell_irqs`, and `smp_ipi_demux_relaxed()`.

## Control Flow
On SMP, the handler installs the active pt_regs, emits entry tracing, performs message synchronization, conditionally enables hard IRQs according to interrupt state, clears any host KVM IPI for the current CPU, increments statistics, demultiplexes relaxed SMP IPIs, emits exit tracing, and restores prior IRQ regs. On non-SMP builds it only logs a warning.

## State And Persistence
State changes are per-CPU interrupt statistics and clearing pending host IPI state. There is no persistent storage.

## Dependencies And Integration Points
It integrates with the generic interrupt framework, SMP IPI demux, KVM PPC host code, tracepoints, and PowerPC message synchronization semantics.

## Risks
Ordering is important: `ppc_msgsync()` and `smp_ipi_demux_relaxed()` rely on barriers being satisfied. Enabling hard IRQs too early or failing to restore IRQ regs can corrupt nested interrupt handling. Non-SMP receipt indicates platform misconfiguration.

## Test Signals
SMP boot, IPI stress tests, KVM host IPI tests, tracepoint consistency, and increasing `doorbell_irqs` counters are the main signals. Non-SMP builds should compile and warn only if a doorbell arrives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dbell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dexcr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dexcr.c

## Purpose
`dexcr.c` implements per-task userspace controls for the PowerPC Dynamic Execution Control Register on ISA 3.1 processors. It supports querying and changing selected DEXCR aspects through prctl and records on-exec state in the task thread.

## Important APIs, Types, And Functions
Key functions are `init_task_dexcr()`, `prctl_to_aspect()`, `get_dexcr_prctl()`, and `set_dexcr_prctl()`. Editable aspects are `DEXCR_PR_IBRTPD`, `DEXCR_PR_SRAPD`, and `DEXCR_PR_NPHIE`; `DEXCR_PR_SBHE` is queryable but not user-editable here.

## Control Flow
Early init stores the boot task's current DEXCR into `current->thread.dexcr_onexec` when `CPU_FTR_ARCH_31` is present. `prctl_to_aspect()` maps Linux `PR_PPC_DEXCR_*` selectors to bit masks. Get reports whether an aspect is editable, currently set in SPRN_DEXCR, and set in the task's on-exec mask. Set validates aspect editability, mutually exclusive set/clear controls, on-exec controls, and the `NPHIE` privilege rule, then updates both the hardware DEXCR and `task->thread.dexcr_onexec`.

## State And Persistence
State lives in the current CPU's DEXCR SPR and in `task_struct.thread.dexcr_onexec`, which persists across exec policy transitions for the task. It is not filesystem-persistent.

## Dependencies And Integration Points
It integrates with the PowerPC prctl implementation, task thread state, capability checks, CPU feature detection, and low-level DEXCR restore/exec code elsewhere.

## Risks
Allowing unprivileged clearing of `NPHIE` on exec is explicitly blocked to protect setuid hash-check behavior. Direct SPR writes affect the running thread immediately; scheduler save/restore must remain consistent. Unsupported selectors return `-ENODEV`.

## Test Signals
Prctl tests should cover get/set/clear, set-onexec/clear-onexec, invalid masks, non-editable `SBHE`, `CAP_SYS_ADMIN` enforcement for `NPHIE`, and no-op behavior on non-ISA-3.1 CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dexcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-iommu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-iommu.c

## Purpose
`dma-iommu.c` provides PowerPC DMA mapping operations for devices using the architecture IOMMU/TCE infrastructure, plus direct-DMA bypass decisions for platforms that pre-map RAM.

## Important APIs, Types, And Functions
Architecture hooks include `arch_dma_map_phys_direct()`, `arch_dma_unmap_phys_direct()`, `arch_dma_map_sg_direct()`, `arch_dma_unmap_sg_direct()`, `arch_dma_alloc_direct()`, and `arch_dma_free_direct()` when direct map support is configured. The IOMMU map ops are implemented by `dma_iommu_alloc_coherent()`, `dma_iommu_free_coherent()`, `dma_iommu_map_phys()`, `dma_iommu_unmap_phys()`, `dma_iommu_map_sg()`, `dma_iommu_unmap_sg()`, `dma_iommu_dma_supported()`, `dma_iommu_get_required_mask()`, and exported `dma_iommu_ops`.

## Control Flow
Direct bypass is allowed only when `dev->bus_dma_limit` and DMA offsets show the address/handle fits the direct aperture. IOMMU operations delegate to `iommu_alloc_coherent`, `iommu_map_phys`, `ppc_iommu_map_sg`, and matching unmap/free helpers using `get_iommu_table_base(dev)`. `dma_supported` enables `dma_ops_bypass` for PCI devices whose PHB supports bypass for the requested mask; otherwise it validates IOMMU table availability and table offset against the device mask.

## State And Persistence
Runtime state changes include `dev->dma_ops_bypass`. IOMMU mapping state is maintained in platform IOMMU tables, not in this file. No persistent storage exists.

## Dependencies And Integration Points
It integrates with Linux DMA API, PCI host bridge controller ops, PowerPC IOMMU table management, `dma_common_*` helpers, scatterlist iteration, and device masks.

## Risks
Off-by-one checks around `bus_dma_limit`, scatterlist end addresses, and table offset/mask validation can cause invalid DMA or unnecessary bounce/IOMMU use. Calling `to_pci_dev()` in bypass support assumes PCI devices.

## Test Signals
Signals include DMA API tests, PCI devices with 32-bit and 64-bit masks, IOMMU table absence errors, direct-bypass logging, coherent allocation/free, scatter-gather map/unmap, and stress with memory above 4GB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-mask.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-mask.c

## Purpose
`dma-mask.c` supplies the PowerPC architecture hook called when a device DMA mask changes. It lets platform-specific machine descriptors react to mask updates.

## Important APIs, Types, And Functions
The only function is exported `arch_dma_set_mask(struct device *dev, u64 dma_mask)`. It checks `ppc_md.dma_set_mask` and delegates when the platform provides one.

## Control Flow
There is no local policy beyond optional callback dispatch. If the machine descriptor lacks a `dma_set_mask` hook, the function returns without side effects.

## State And Persistence
This file owns no state. Any state mutation occurs inside platform-provided `ppc_md.dma_set_mask`, typically in device or host bridge DMA metadata.

## Dependencies And Integration Points
It integrates with the generic DMA mapping layer, `asm/machdep.h`, and machine descriptor callbacks for pSeries, PowerNV, or embedded platforms.

## Risks
The hook is intentionally thin, so platform bugs are not contained here. Callers should not expect a return status or fallback validation from this function.

## Test Signals
Changing PCI DMA masks should trigger the platform hook when present. Build coverage should verify the exported symbol and no-op behavior on platforms without the callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-mask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-swiotlb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-swiotlb.c

## Purpose
`dma-swiotlb.c` contains PowerPC-specific SWIOTLB enablement helpers. It detects systems with RAM above the 32-bit address boundary and finalizes whether the software bounce buffer remains active.

## Important APIs, Types, And Functions
Globals are `ppc_swiotlb_enable` and `ppc_swiotlb_flags`. Functions are `swiotlb_detect_4g()` and initcall `check_swiotlb_enabled()`.

## Control Flow
`swiotlb_detect_4g()` sets `ppc_swiotlb_enable` when the last byte of DRAM is above `0xffffffff`. During `subsys_initcall`, `check_swiotlb_enabled()` either prints SWIOTLB info when enabled or calls `swiotlb_exit()` to tear down unused bounce buffering.

## State And Persistence
The enable and flags globals persist for runtime DMA setup. SWIOTLB memory reservation/lifetime is managed by the generic SWIOTLB layer. There is no durable storage.

## Dependencies And Integration Points
It integrates with memblock DRAM discovery, generic SWIOTLB, platform DMA setup, and device mask decisions for systems with limited DMA addressing.

## Risks
Detection based only on DRAM end is conservative and does not model every device mask. Disabling SWIOTLB too early would break devices unable to DMA high memory; keeping it unnecessarily wastes memory.

## Test Signals
Boot systems with DRAM below and above 4GB, confirm SWIOTLB info or teardown behavior, run DMA on 32-bit-limited devices, and verify no bounce allocation failures under high-memory I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-swiotlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dt_cpu_ftrs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dt_cpu_ftrs.c

## Purpose
`dt_cpu_ftrs.c` builds a PowerPC CPU specification dynamically from device-tree CPU feature nodes. It is the firmware-described alternative to static PVR tables for modern POWER systems, enabling hardware facilities, MMU modes, PMU setup, machine-check handlers, user HWCAPs, and processor errata bits.

## Important APIs, Types, And Functions
Core types are `struct dt_cpu_feature` and `struct dt_cpu_feature_match`. Important globals include `hv_mode`, `system_registers`, `init_pmu_registers`, `dt_cpu_name`, `base_cpu_spec`, `using_dt_cpu_ftrs`, `enable_unknown`, `nr_dt_cpu_features`, and `dt_cpu_features`. Public functions are `dt_cpu_ftrs_in_use()`, `dt_cpu_ftrs_init()`, and `dt_cpu_ftrs_scan()`. Major helpers include `cpufeatures_setup_cpu()`, `feat_enable*()` variants, `cpufeatures_process_feature()`, `cpufeatures_cpu_quirks()`, `process_cpufeatures_node()`, and `cpufeatures_deps_enable()`.

## Control Flow
Early init verifies the FDT, finds an `ibm,powerpc-cpu-features` node with `isa`, honors `dt_cpu_ftrs=off`, initializes `base_cpu_spec`, and marks the feature path active. The scan callback allocates a memblock array for subnodes, sets ISA baseline bits, parses each feature's privilege/support/FSCR/HFSCR/HWCAP properties, immediately enables independent features, then recursively enables dependency-gated features. Known names dispatch through `dt_cpu_feature_match_table`; unknown features can be enabled by generic FSCR/HFSCR/HWCAP recipes unless `dt_cpu_ftrs=known` was specified. Finish applies PVR-specific quirks, captures LPCR/HFSCR/FSCR/PCR for CPU restore, sets display name, logs final features, and frees the memblock array.

## State And Persistence
The dynamic CPU spec persists through `cur_cpu_spec`. `system_registers` stores restore-time SPR values, and `init_pmu_registers` persists a callback for secondary CPU restore. The temporary parsed feature array is freed after scanning.

## Dependencies And Integration Points
It depends on libfdt/flat DT scanning, memblock, CPU/MMU feature macros, machine-check handlers, PMU SPRs, HFSCR/FSCR/PCR/LPCR programming, command-line parsing, and `set_cur_cpu_spec()`.

## Risks
Firmware property validation is strict but recursive dependencies can silently disable dependent features. Unknown feature enablement can expose HWCAPs based on firmware recipes without kernel-specific code. SPR programming differs between HV and guest modes. PVR quirks for POWER9 errata must remain synchronized with static tables.

## Test Signals
Test by booting POWER8-POWER11 systems with DT CPU features, toggling `dt_cpu_ftrs=off` and `dt_cpu_ftrs=known`, checking final feature logs and HWCAPs, validating radix/hash MMU selection, PMU operation, secondary CPU restore, machine-check handler selection, and POWER9 errata flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dt_cpu_ftrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/early_32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/early_32.c

## Purpose
`early_32.c` performs very early 32-bit PowerPC initialization before normal relocation assumptions are valid. It clears BSS when appropriate, identifies the CPU, applies feature fixups, and returns the relocated kernel virtual address.

## Important APIs, Types, And Functions
The file defines `notrace unsigned long __init early_init(unsigned long dt_ptr)`. It uses `reloc_offset()`, `PTRRELOC`, `kernstart_virt_addr`, `__bss_start`, `__bss_stop`, `identify_cpu()`, `mfspr(SPRN_PVR)`, and `apply_feature_fixups()`.

## Control Flow
The function computes the relocation offset, reads the relocated kernel start virtual address, zeroes BSS only if running at `KERNELBASE`, identifies the CPU from PVR with the relocation offset, applies feature-dependent code patching, and returns `kva + offset`.

## State And Persistence
State changes include BSS zeroing, initialization of `cur_cpu_spec`, and patched feature sections. These persist for the booted kernel; no external persistence is involved.

## Dependencies And Integration Points
It is part of 32-bit boot and must use relocation-safe accesses before the kernel is fully relocated. It integrates with cputable, feature fixups, and linker-provided section symbols.

## Risks
Using non-relocated static addresses here can corrupt memory during early boot. BSS clearing must not run in cases where the boot path already relies on BSS data. Feature fixups must happen after CPU identification.

## Test Signals
Successful 32-bit boot across Book3S/BookE variants, correct CPU identification, feature-patched code paths, and no early boot BSS/relocation faults are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/early_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh.c

## Purpose
`eeh.c` is the core Enhanced Error Handling implementation for PowerPC PCI. It detects frozen PCI processing elements after all-ones MMIO reads, logs platform error detail, manages global EEH state, exposes reset/control APIs, supports pass-through ownership, and provides proc/debugfs diagnostics.

## Important APIs, Types, And Functions
Important globals are exported `eeh_subsystem_flags`, `eeh_max_freezes`, `eeh_debugfs_no_recover`, `eeh_ops`, `confirm_error_lock`, and `eeh_stats`. Key functions include `eeh_setup()`, `eeh_show_enabled()`, `eeh_slot_error_detail()`, `eeh_dev_check_failure()`, exported `eeh_check_failure()`, `eeh_pci_enable()`, `pcibios_set_pcie_reset_state()`, `eeh_pe_reset_full()`, `eeh_save_bars()`, `eeh_init()`, `eeh_probe_device()`, `eeh_remove_device()`, exported `eeh_unfreeze_pe()`, `eeh_dev_open()`, `eeh_dev_release()`, `eeh_iommu_group_to_pe()`, `eeh_pe_set_option()`, `eeh_pe_get_state()`, `eeh_pe_reset()`, `eeh_pe_configure()`, and `eeh_pe_inject_err()`.

## Control Flow
MMIO failure detection resolves the token to a physical address, looks up an `eeh_dev` in the address cache, checks PHB failure first, skips passed-through PEs, serializes duplicate reports, queries platform state, escalates to frozen parents when needed, marks the PE isolated, and queues an async recovery event. Reset APIs freeze or thaw MMIO/DMA, block config access during reset, restore BARs/config, and clear PE state. Probe/remove bind or unbind PCI devices to `eeh_dev`, sysfs, and address-cache state. Debugfs can enable/disable EEH, force recovery, trigger checks, inject MMIO errors, and report whether a driver supports recovery.

## State And Persistence
State is in-memory: global flags/statistics, PE state bits, per-device saved config space, address-cache entries, pass-through counters, and debugfs/procfs settings. No state persists across reboot.

## Dependencies And Integration Points
It integrates with platform `struct eeh_ops`, PCI hotplug, IOMMU groups, RTAS/OPAL logging through platform callbacks, debugfs/procfs, PCI device notifiers, reboot notifiers, the EEH event thread, and the address cache.

## Risks
The detection path can run in interrupt context, so locking and allocation assumptions are sensitive. Duplicate all-ones reads can form loops, mitigated by `EEH_MAX_FAILS` logging. Config-space blocked PEs must avoid normal PCI access or can fence a PHB. Pass-through PEs must not be thawed unexpectedly.

## Test Signals
Test signals include EEH injection through debugfs, all-ones MMIO detection, proc stats increments, successful temporary and permanent error logs, pass-through open/release behavior, PHB fenced event handling, reset API behavior, and hotplug add/remove races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_cache.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_cache.c

## Purpose
`eeh_cache.c` implements the PCI I/O address cache used by EEH to map an MMIO or I/O token back to the owning `eeh_dev` quickly, including from interrupt context.

## Important APIs, Types, And Functions
The private `struct pci_io_addr_range` stores an RB-tree node, address range, `eeh_dev`, `pci_dev`, and resource flags. Public functions are `eeh_addr_cache_get_dev()`, `eeh_addr_cache_insert_dev()`, `eeh_addr_cache_rmv_dev()`, `eeh_addr_cache_init()`, and `eeh_cache_debugfs_init()`. Internal helpers handle RB lookup, insert, remove, and debug printing/showing.

## Control Flow
Lookup takes `piar_lock`, walks the RB tree by comparing the requested address with `addr_lo/addr_hi`, and returns the matching `eeh_dev`. Insert skips devices without EEH PEs, walks standard BAR and ROM resources, filters invalid or non-I/O/MEM resources, and inserts non-overlapping ranges. Removal walks the tree repeatedly, erasing all entries for a PCI device. Debugfs renders the tree under the same lock.

## State And Persistence
State is a global RB tree protected by a spinlock. Entries are allocated with `GFP_ATOMIC` and freed on device removal. The cache is runtime-only.

## Dependencies And Integration Points
It integrates with PCI resources, `pci_dev_to_eeh_dev()`, EEH probe/remove, `eeh_check_failure()`, debugfs, and PowerPC PCI bridge metadata.

## Risks
Overlapping BAR ranges are warned and return the existing entry, which can hide ambiguous ownership. Removal is intentionally O(n * resources). Entries hold raw pointers and depend on remove hooks running before devices disappear.

## Test Signals
Signals include address-cache debugfs output, successful lookup after MMIO all-ones reads, insertion/removal during PCI hotplug, no stale pointers after remove, and warnings for overlapping resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_driver.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_driver.c

## Purpose
`eeh_driver.c` orchestrates EEH recovery after events are dequeued. It notifies PCI drivers through `pci_error_handlers`, decides whether MMIO/DMA thaw or reset is required, performs hotplug fallback for EEH-unaware devices, handles permanent failure removal, and scans special platform-wide errors.

## Important APIs, Types, And Functions
Key public functions are `eeh_pe_reset_and_recover()`, `eeh_handle_normal_event()`, and `eeh_handle_special_event()`. Helpers include result priority/merge functions, `eeh_edev_actionable()`, driver module ref helpers, IRQ disable/enable, `eeh_pe_report()`, report callbacks for `error_detected`, `mmio_enabled`, `slot_reset`, `resume`, and permanent failure, virtual-function add/remove helpers, `eeh_reset_device()`, `eeh_pe_cleanup()`, and slot presence/attention helpers.

## Control Flow
Normal recovery locks PCI rescan/remove, finds the affected bus, verifies devices remain present, logs location and saved stack trace, clears stale no-handler flags, increments freeze counters, notifies drivers of frozen I/O, waits for PE state, collects temporary logs, then follows the aggregate driver result. No EEH-aware drivers triggers full hotplug reset. `CAN_RECOVER` tries MMIO and DMA thaw plus optional `mmio_enabled`. `NEED_RESET` performs reset without full hotplug, restores state, calls `slot_reset`, and resumes. Failure collects permanent logs, marks devices permanently failed, removes VFs or the bus, and marks PE removed. Special events loop through platform `next_error()`, purge duplicate events, handle frozen/fenced PEs as normal events, and remove dead PHBs/IOCs.

## State And Persistence
Runtime state includes PE recovery/isolation/removed/keep bits, device `in_error`, `EEH_DEV_NO_HANDLER`, `EEH_DEV_DISCONNECTED`, IRQ-disabled mode bits, removed VF lists, freeze counters, and PCI device error states. No persistent storage exists.

## Dependencies And Integration Points
It integrates with EEH core APIs, event thread, PCI error recovery callbacks, PCI hotplug, SR-IOV, IRQ core, RTAS/platform logging, rescan/remove locking, and hotplug slot attention LEDs.

## Risks
This file has high race risk around device removal, driver unload, and PE tree mutation; module refs and device locks mitigate that. Recovery result merging is conservative and can escalate. Blocking config access and restoring BARs must respect restricted PEs. Freeze-count policy can permanently remove noisy hardware.

## Test Signals
Signals include injected EEH recovery for aware and unaware drivers, `mmio_enabled`/`slot_reset`/`resume` callback ordering, hotplug remove/add fallback, VF removal/re-add, permanent failure behavior after `eeh_max_freezes`, dead PHB/IOC special events, and absence of rescan/remove lock deadlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_event.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_event.c

## Purpose
`eeh_event.c` decouples EEH error detection from recovery. It queues failure events that may be produced in interrupt context and processes them in the `eehd` kernel thread.

## Important APIs, Types, And Functions
State includes `eeh_eventlist_lock`, `eeh_eventlist_event`, and `eeh_eventlist`. Functions are private `eeh_event_handler()`, `eeh_event_init()`, `__eeh_send_failure_event()`, `eeh_send_failure_event()`, and `eeh_remove_event()`.

## Control Flow
The handler waits for completions, pops one event under the spinlock, calls `eeh_handle_normal_event(pe)` when the event has a PE or `eeh_handle_special_event()` otherwise, then frees the event. Send allocates with `GFP_ATOMIC`, optionally saves a stack trace, marks the PE recovering before queueing, appends to the list, and completes the event. The public send wrapper drops events when debugfs no-recover is enabled. Remove walks the queue and removes matching PE, PHB, or all events, with special handling to avoid dropping isolated events unless forced.

## State And Persistence
The event queue is in-memory only. PE recovery bits are set before queue insertion to protect PEs from being freed while pending.

## Dependencies And Integration Points
It integrates with the EEH core detector, EEH driver recovery functions, kthread/completion APIs, stack trace support, and debugfs no-recover flag from `eeh.c`.

## Risks
Allocation failure drops recovery and logs an error. Marking a PE recovering before event processing must be cleared by recovery paths. Event removal rules can lose or duplicate recovery if force usage is wrong.

## Test Signals
Signals include `eehd` thread startup, forced debugfs recovery, async recovery after interrupt-context detection, no-recover drops, duplicate event purging, and stack traces printed during normal recovery when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_pe.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_pe.c

## Purpose
`eeh_pe.c` manages EEH Processing Element topology and PE-local operations. It creates PHB roots, inserts/removes device/bus/VF PEs, traverses PE trees, tracks isolation/recovery state, restores PCI BAR/config data after reset, and resolves PE location/bus information.

## Important APIs, Types, And Functions
Important globals are `eeh_pe_aux_size` and `eeh_phb_pe`. Public functions include `eeh_set_pe_aux_size()`, `eeh_phb_pe_create()`, `eeh_wait_state()`, `eeh_phb_pe_get()`, `eeh_pe_next()`, `eeh_pe_traverse()`, `eeh_pe_dev_traverse()`, `eeh_pe_get()`, `eeh_pe_tree_insert()`, `eeh_pe_tree_remove()`, `eeh_pe_update_time_stamp()`, exported `eeh_pe_state_mark()`, exported `eeh_pe_mark_isolated()`, `eeh_pe_dev_mode_mark()`, `eeh_pe_state_clear()`, `eeh_pe_restore_bars()`, `eeh_pe_loc_get()`, `eeh_pe_loc_get_bus()`, `eeh_pe_bus_get()`, and `eeh_pe_bus_get_nolock()`.

## Control Flow
PHB PEs are allocated at host bridge discovery and form roots. Device insertion searches by PE address, reuses existing PEs, clears invalid ancestors during recovery hotplug, or allocates device/VF PEs under the requested parent or PHB. Removal detaches the `eeh_dev`, frees empty non-recovering PEs, or marks empty recovering PEs invalid for later cleanup. State marking/clearing walks the affected subtree and updates PCI channel state and config-blocking. BAR restore handles bridges and endpoint devices differently, using EEH config ops and link checks. `eeh_wait_state()` loops on firmware unavailable state with bounded waits.

## State And Persistence
PE tree state is runtime-only and includes parent/child lists, attached `eeh_dev` lists, state bits, freeze counters, timestamps, primary bus cache, and optional auxiliary data. Saved config space resides in `eeh_dev`.

## Dependencies And Integration Points
It integrates with platform `eeh_ops`, PCI controller/bridge metadata, PCI resource and config definitions, OF location-code properties, PCI rescan/remove locking, and EEH driver recovery cleanup.

## Risks
Tree mutation during recovery is delicate; invalid marking avoids freeing nodes while traversals are active. Config-space access on restricted PEs can fence a PHB. Bridge link power/link training loops can delay recovery. Bus lookup without locks must be used only when the caller already protects PCI topology.

## Test Signals
Signals include PE tree creation for PHBs and hotplug devices, VF PE insertion/removal, subtree traversal, repeated unavailable firmware state handling, BAR restore after reset, location-code output, and cleanup of invalid empty PEs after recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_pe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_sysfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_sysfs.c

## Purpose
`eeh_sysfs.c` exposes per-PCI-device EEH attributes through sysfs. It lets users inspect EEH mode, PE config address, platform and kernel PE state, manually unfreeze an isolated PE, and optionally notify resume for selected SR-IOV pSeries devices.

## Important APIs, Types, And Functions
Macro `EEH_SHOW_ATTR` creates read-only `eeh_mode` and `eeh_pe_config_addr`. Functions implement `eeh_pe_state_show()`, `eeh_pe_state_store()`, optional `eeh_notify_resume_show/store/add/remove()`, `eeh_sysfs_add_device()`, and `eeh_sysfs_remove_device()`.

## Control Flow
Add skips when EEH is disabled or attributes were already added, then creates mode, config address, PE state, and optional notify-resume files. `eeh_pe_state_show()` returns platform `get_state` and kernel PE state bits. Store ignores non-isolated PEs, otherwise unfreezes the PE and clears isolated state. Notify-resume files are added only for pSeries Open SR-IOV physical-function-related nodes and call `eeh_ops->notify_resume()`.

## State And Persistence
Sysfs files reflect runtime `eeh_dev` and `eeh_pe` state. `EEH_DEV_SYSFS` tracks file creation. Writes can mutate PE isolation state but are not persistent across reboot.

## Dependencies And Integration Points
It integrates with PCI device sysfs, EEH core state APIs, OF node properties, SR-IOV/pSeries platform behavior, and `eeh_probe_device()`/`eeh_remove_device()`.

## Risks
Manual unfreeze can interfere with recovery if used at the wrong time. Removal must tolerate already-removed parent kobjects. Optional notify-resume depends on platform callbacks and specific OF properties.

## Test Signals
Signals include sysfs attribute creation/removal during PCI probe/hotplug, correct state formatting, successful manual unfreeze of isolated PEs, no stale files after device removal, and notify-resume behavior on Open SR-IOV PFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/entry_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/entry_32.S

## Purpose
`entry_32.S` implements 32-bit PowerPC syscall entry/return, fork thread entry, fast exception return, normal interrupt return, KUEP segment locking, and BookE critical/debug/machine-check return paths. It is the low-level bridge between saved exception frames and C interrupt/syscall handlers.

## Important APIs, Types, And Functions
Important entry symbols include `prepare_transfer_to_handler`, `__kuep_lock`, local `__kuep_unlock`, `transfer_to_syscall`, `ret_from_syscall`, `syscall_exit_finish`, `ret_from_fork`, `ret_from_kernel_user_thread`, `start_kernel_thread`, `fast_exception_return`, `interrupt_return`, `ret_from_crit_exc`, `ret_from_debug_exc`, and `ret_from_mcheck_exc`. It calls C helpers such as `system_call_exception`, `syscall_exit_prepare`, `schedule_tail`, `interrupt_exit_user_prepare`, `interrupt_exit_kernel_prepare`, and `unrecoverable_exception`.

## Control Flow
Syscall entry saves GPRs and frame metadata, locks user execute permission when configured, calls the C syscall handler, runs syscall exit preparation, handles 44x I-cache flushing, unlocks KUEP, restores registers, and returns with `rfi`. Interrupt return chooses user or kernel exit preparation based on MSR_PR, clears reservations and stack markers, optionally restores nonvolatile registers, emulates delayed `stwu` stack stores for kernel returns, and executes `rfi`. BookE special returns restore xSRR/MMU state and return with `rfci`, `rfdi`, or `rfmci`. Napping/sleeping flags redirect interrupted low-power returns.

## State And Persistence
State is CPU register, SPR, stack frame, thread flag, and segment register state. It persists only as live execution context.

## Dependencies And Integration Points
It depends on exact `pt_regs`/thread-info offsets, KUEP/KUAP helpers, BookE SPR layouts, feature fixup sections, syscall and interrupt C code, stack unwinder marker conventions, and CPU-specific errata macros.

## Risks
Register restore order is extremely fragile. KUEP unlock/lock mistakes can expose user mappings in kernel or break user return. TLB misses between SRR writes and `rfi` are avoided by alignment; moving code can violate that. BookE special interrupt returns must restore the right SPR sets.

## Test Signals
Signals include syscall ABI tests, fork/kernel-thread startup, interrupt/preemption stress, KUEP/KUAP tests, stack unwinder reliability, 44x I-cache flush paths, BookE critical/debug/machine-check return testing, and membarrier sync-core assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/entry_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_hcalls.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_hcalls.S

## Purpose
`epapr_hcalls.S` provides the patchable ePAPR hypercall entry sequence and, on supported non-64-bit or Book3E-64 builds, an ePAPR idle loop that repeatedly invokes the hypervisor idle call until an interrupt returns execution to the caller.

## Important APIs, Types, And Functions
Exported symbols are `epapr_ev_idle`, `epapr_ev_idle_start`, and exported `epapr_hypercall_start`. The hypercall instruction slots begin as `li r3, -1` plus NOPs and are patched from device-tree `hcall-instructions`.

## Control Flow
`epapr_ev_idle()` sets the thread napping flag, enables external interrupts, loads the EV_IDLE token, executes the patched hypercall instruction sequence at `epapr_ev_idle_start`, and loops to guard against spurious hypervisor wakeups. `epapr_hypercall_start` is the generic callable hypercall sequence and returns after the patched instructions.

## State And Persistence
State changes include thread local flags and patched text instructions. The patched instructions persist for the running kernel only.

## Dependencies And Integration Points
It integrates with `epapr_paravirt.c` text patching, ePAPR hypercall ABI, PowerPC interrupt/idle handling, thread-info flags, and machine descriptor power-save hooks.

## Risks
The instruction patch area is limited to four instructions, matching parser validation. Idle relies on `_TLF_NAPPING` exception return behavior; incorrect flag handling can loop or return incorrectly. Spurious wakeups are intentionally ignored.

## Test Signals
Signals include successful patching from DT `hcall-instructions`, functional ePAPR hypercalls, idle entry/exit under interrupts, and no use of the placeholder `-1` return path after early paravirt init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_hcalls.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_paravirt.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_paravirt.c

## Purpose
`epapr_paravirt.c` enables ePAPR paravirtualization by reading hypercall instructions from the flattened device tree, patching the assembly hypercall stubs, and optionally installing an ePAPR idle handler.

## Important APIs, Types, And Functions
Globals are `epapr_paravirt_enabled` and private `epapr_has_idle`. Key functions are `early_init_dt_scan_epapr()`, `epapr_paravirt_early_init()`, and postcore initcall `epapr_idle_init()`. It patches `epapr_hypercall_start` and, for supported builds, `epapr_ev_idle_start`.

## Control Flow
Early DT scanning looks for a node with `hcall-instructions`, validates the property length is a multiple of four bytes and at most four instructions, converts big-endian instruction words to `ppc_inst_t`, patches the hypercall and idle stubs, records `has-idle` when present, and marks paravirt enabled. Later, `epapr_idle_init()` installs `ppc_md.power_save = epapr_ev_idle` only when the idle property was present and the build supports that assembly path.

## State And Persistence
State is runtime-only: patched kernel text plus boolean feature flags. There is no persistent storage.

## Dependencies And Integration Points
It depends on flat OF scanning, instruction patching, ePAPR assembly symbols, `ppc_md` machine descriptor, cache/text patching helpers, and build-time 32-bit/Book3E-64 conditions.

## Risks
Invalid instruction length aborts the scan with an error return but leaves no hypercall support. Patching must happen early enough before callers use `epapr_hypercall_start`. Installing idle on unsupported builds is intentionally compiled out.

## Test Signals
Signals include DT-based patching visible in disassembly or behavior, `epapr_paravirt_enabled` true only with valid instructions, ePAPR hypercall success, idle hook installation when `has-idle` is present, and safe no-op behavior without the property.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_paravirt.c -->
