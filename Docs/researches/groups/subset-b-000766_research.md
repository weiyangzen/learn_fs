# subset-b-000766 research

Grouped research for PowerPC architecture headers under the Ceph client source tree. Each source file section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cmpxchg.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cmpxchg.h

Purpose: implements PowerPC architecture exchange and compare-exchange primitives for 8, 16, 32, and on PPC64, 64-bit operands. It backs the generic Linux `xchg`, `cmpxchg`, and `cmpxchg64` APIs with PowerPC load-reserve/store-conditional instruction sequences.

Important APIs/types/functions: `arch_xchg_local`, `arch_xchg_relaxed`, `arch_cmpxchg`, `arch_cmpxchg_local`, `arch_cmpxchg_relaxed`, `arch_cmpxchg_acquire`, and PPC64 `arch_cmpxchg64*` macros wrap `__xchg_*` and `__cmpxchg_*` helpers. `XCHG_GEN` and `CMPXCHG_GEN` synthesize byte/halfword fallback implementations when `CONFIG_PPC_HAS_LBARX_LHARX` is absent.

Control flow: each primitive loops around `lbarx/lharx/lwarx/ldarx` and `stbcx./sthcx./stwcx./stdcx.` until the conditional store succeeds. Compare-exchange first compares the reserved value with `old`, exits without storing on mismatch, and applies entry/exit or acquire barriers according to the exported variant. Small-width fallbacks align to a 32-bit word, compute endian-sensitive bit offsets, mask the target lane, and update the containing word atomically.

State and persistence: no persistent state is owned by the header; it mutates caller memory atomically and relies on reservation granule semantics. Memory-ordering state is expressed through `PPC_ATOMIC_ENTRY_BARRIER`, `PPC_ATOMIC_EXIT_BARRIER`, `PPC_ACQUIRE_BARRIER`, memory clobbers, and local/relaxed variants.

Dependencies and integration: depends on `asm/synch.h`, `linux/bug.h`, PowerPC endian layout, and generic cmpxchg-local fallback for 32-bit `cmpxchg64_local`. It is a foundational dependency for locking, atomics, reference counts, scheduler state, and concurrent driver code.

Risks and test signals: barrier placement, clobbers, type sizes, and byte-lane masking are correctness-critical. Wrong fallback bit offsets corrupt adjacent bytes on big- or little-endian builds. Test signals include PowerPC allmodconfig builds, LKMM litmus tests, lock/RCU stress, KCSAN, atomic selftests, boot on CPUs with and without byte/halfword reserve instructions, and 32-bit `cmpxchg64_local` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/code-patching-asm.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/code-patching-asm.h

Purpose: provides an assembler macro for declaring patchable instruction sites.

Important APIs/types/functions: `patch_site label name` emits a global symbol in `.rodata` whose value is a 32-bit relative offset from the table location to the patch label.

Control flow: assembly-only metadata emission. The macro pushes `.rodata`, aligns to four bytes, defines `name`, writes `label - .`, and returns to the previous section.

State and persistence: the generated relative offset persists in the kernel image and is consumed by runtime patching code. The header owns no mutable state.

Dependencies and integration: integrates with PowerPC code-patching and alternative/fixup paths that need compact, relocatable patch-site descriptors.

Risks and test signals: offset width and section placement must match the patching consumer. Bad alignment or a stale symbol name can make boot-time patching corrupt code. Test signals are assembler builds, objdump inspection of patch-site tables, boot-time code patching, ftrace/static-call style patch users, and module/vDSO relocation coverage where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/code-patching-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/compat.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/compat.h

Purpose: defines PowerPC 32-bit compatibility ABI types and layouts used by a 64-bit kernel servicing 32-bit tasks.

Important APIs/types/functions: exports `COMPAT_UTS_MACHINE`, `compat_ipc_pid_t`, `compat_nlink_t`, `struct compat_stat`, `struct compat_ipc64_perm`, `compat_semid64_ds`, `compat_msqid64_ds`, `compat_shmid64_ds`, and `is_compat_task()`.

Control flow: there is no runtime algorithm beyond `is_compat_task()` delegating to `is_32bit_task()`. The rest are ABI layout definitions for compat syscall marshaling.

State and persistence: no kernel-owned state. The structures persist as userspace ABI contracts for stat and SysV IPC data exchanged across syscall boundaries.

Dependencies and integration: includes generic compat definitions, Linux types, scheduler/task mode helpers, and endian-specific UTS machine strings (`ppc` or `ppcle`). It integrates with compat syscall handlers, ELF personality, and IPC/stat copy routines.

Risks and test signals: field order, width, padding, and time high/low halves are ABI-sensitive. Any layout change can break 32-bit userspace on 64-bit kernels. Test signals include 32-bit PowerPC userspace under a 64-bit kernel, LTP compat syscall tests, stat and SysV IPC tests, endian-specific builds, and ABI structure size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/context_tracking.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/context_tracking.h

Purpose: selects the assembly branch target used when returning through user scheduling paths with or without context tracking.

Important APIs/types/functions: defines `SCHEDULE_USER` as `bl schedule_user` under `CONFIG_CONTEXT_TRACKING_USER`, otherwise `bl schedule`.

Control flow: compile-time macro selection only. Assembly code includes this macro at call sites that need the correct scheduler entry.

State and persistence: no direct state, but the selected target controls whether context tracking/accounting state is updated around user transitions.

Dependencies and integration: integrates with low-level entry/exit assembly, scheduler code, and context-tracking/NOHZ full configurations.

Risks and test signals: choosing the wrong call target can break user/kernel context accounting or add unnecessary overhead. Test signals are builds with and without `CONFIG_CONTEXT_TRACKING_USER`, NOHZ full tests, syscall/interrupt return tracing, and scheduler context tracking selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/context_tracking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/copro.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/copro.h

Purpose: declares helpers for coprocessor address translation and fault handling on PowerPC systems that expose coprocessor-side memory access.

Important APIs/types/functions: `struct copro_slb` stores ESID/VSID pairs, `copro_handle_mm_fault()` handles a coprocessor fault against an `mm_struct`, and `copro_calculate_slb()` derives an SLB entry for an effective address.

Control flow: implemented elsewhere; callers pass an mm, effective address, DSISR-like status, and receive fault status or SLB values. The header defines the interface between coprocessor fault code and core MM.

State and persistence: no local state. It reads and updates process address-space state through `mm_struct` and fault handling, while SLB values are transient translation descriptors.

Dependencies and integration: depends on `linux/mm_types.h` and integrates with PowerPC MM, SLB management, and accelerator/coprocessor drivers.

Risks and test signals: incorrect SLB computation or fault result propagation can expose wrong address spaces, mishandle permissions, or livelock a coprocessor. Test signals include coprocessor driver fault tests, mmap/unmap stress while devices access memory, page fault accounting, and MMU context teardown races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/copro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm.h

Purpose: PowerPC compatibility include for Freescale Communication Processor Module definitions.

Important APIs/types/functions: re-exports `<soc/fsl/cpm.h>` without adding local declarations.

Control flow: include forwarding only.

State and persistence: no state; all CPM state contracts are in the SoC header and the CPM1/CPM2 architecture headers.

Dependencies and integration: lets older PowerPC code include `asm/cpm.h` while sharing the common Freescale SoC CPM definitions. Used by CPM serial, Ethernet, GPIO, and board support code.

Risks and test signals: risk is include-path drift or incompatible SoC header changes. Test signals are CPM1/CPM2 platform builds and drivers that include `asm/cpm.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm1.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm1.h

Purpose: describes MPC8xx CPM1 command fields, parameter-RAM layouts, channel register bits, interrupt vectors, GPIO/pin controls, and clock-routing APIs.

Important APIs/types/functions: declares `cpmp`, `cpm_setbrg()`, `cpm_load_patch()`, `cpm_reset()`, `cpm1_set_pin()`, `cpm1_clk_setup()`, `cpm1_gpiochip_add16()`, and `cpm1_gpiochip_add32()`. Key types include `smc_uart_t`, `smc_cent_t`, `sccp_t`, `scc_enet_t`, `scc_uart_t`, `scc_trans_t`, `iic_t`, `rt_pram_t`, and enums for CPM ports, clocks, directions, and targets.

Control flow: mostly declarative hardware layout. Runtime users build command words with `mk_cr_cmd()`, program parameter RAM offsets such as `PROFF_SCC1`, configure SMC/SCC modes and event masks, route BRG/CLK sources, and set pin modes. The RISC timer, CPM interrupt vectors, and GPIO helpers are configured by platform and driver code outside the header.

State and persistence: CPM registers and dual-port RAM are persistent device state accessed through `cpmp`. The structures mirror firmware/hardware parameter RAM, so field ordering is externally defined. GPIO, BRG, SCC/SMC, I2C, Ethernet, and timer settings persist until device reset.

Dependencies and integration: depends on `asm/8xx_immap.h`, `asm/ptrace.h`, and common CPM definitions. It integrates with 8xx serial, Ethernet, I2C, GPIO, timer, and interrupt-controller support.

Risks and test signals: register bit constants and parameter-RAM structures must exactly match MPC8xx manuals and board firmware quirks. Wrong offsets corrupt unrelated CPM channels. Test signals include MPC8xx boot, serial console, SCC Ethernet traffic, I2C/SPI transfers, GPIO export, CPM interrupt dispatch, and microcode patch loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm2.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm2.h

Purpose: defines CPM2 hardware command encoding, DPRAM/parameter-RAM offsets, SMC/SCC/FCC/IDMA/I2C structures, clock routing, pin assignments, and board-facing helpers for PowerQUICC II style devices.

Important APIs/types/functions: declares `cpmp`, `cpm2_reset()`, `__cpm2_setbrg()`, inline `cpm_setbrg()` and `cpm2_fastbrg()`, plus `cpm2_clk_setup()`, `cpm2_smc_clk_setup()`, and `cpm2_set_pin()`. It defines `smc_uart_t`, `sccp_t`, `scc_enet_t`, `scc_uart_t`, `scc_trans_t`, `fccp_t`, `fcc_enet_t`, `iic_t`, `idma_t`, `idma_bd_t`, `im_idma_t`, and clock target/direction enums.

Control flow: drivers compose CPM commands with `mk_cr_cmd(PG, SBC, MCN, OP)`, configure BRGs through `__cpm2_setbrg()`, select SMC/SCC/FCC clock sources with CMX macros, and initialize parameter RAM at `PROFF_*` offsets. Inline baud helpers choose 16x UART clocks or fast synchronous clocks by passing different base clock/divider arguments.

State and persistence: all meaningful state lives in CPM2 internal registers, DPRAM, parameter RAM, buffer descriptors, IDMA descriptors, and pin/clock mux registers. The header’s structures are persistent hardware ABI layouts rather than normal kernel-private objects.

Dependencies and integration: depends on `asm/immap_cpm2.h`, common CPM definitions, and Freescale SoC clock helpers. It integrates with CPM UART, FCC/SCC Ethernet, I2C, IDMA, board pinmux, and interrupt code.

Risks and test signals: large register maps are highly offset-sensitive. FCC clock macros rely on board definitions such as `F1_RXCLK`; invalid values produce unusable Ethernet clocks. Test signals include PowerQUICC II boot, serial console, FCC/SCC Ethernet, IDMA transfers, pinmux validation, and suspend/reset paths that reinitialize CPM state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpu_has_feature.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpu_has_feature.h

Purpose: provides fast PowerPC CPU feature tests for kernel code.

Important APIs/types/functions: `early_cpu_has_feature()` checks `CPU_FTRS_ALWAYS`, `CPU_FTRS_POSSIBLE`, and `cur_cpu_spec->cpu_features`. `cpu_has_feature()` either delegates to early checks or uses jump-label-backed `cpu_feature_keys`.

Control flow: constant feature masks are required in jump-label mode. Always-present features return true, impossible features return false, and possible runtime features index `cpu_feature_keys` with `ctzl(feature)`. Debug mode warns if jump-label checks run before initialization.

State and persistence: reads global `cur_cpu_spec`, static key state, and feature mask constants. It does not mutate state.

Dependencies and integration: depends on `asm/cputable.h`, `linux/jump_label.h`, and `static_key_feature_checks_initialized` from feature-fixup code. Used broadly for CPU errata, barrier selection, DCR access, FPU availability, SMT layout, and instruction alternatives.

Risks and test signals: multi-bit feature arguments are rejected because the static-key array is one bit per feature. Wrong possible/always masks can compile out required code or leave dead paths. Test signals include early boot before static-key init, jump-label enabled/disabled builds, feature-dependent alternatives, and CPU matrix boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpu_has_feature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpu_setup.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpu_setup.h

Purpose: declares CPU-family setup and restore entry points used by the CPU table and low-level bring-up code.

Important APIs/types/functions: setup functions include POWER7 through POWER10, e500 variants, 440/460/APM821xx, 603/604/750/7400/745x, PPC970, PA6T, e5500, and e6500. Restore functions exist for POWER7 through POWER10, PA6T, PPC970, e5500, and e6500.

Control flow: implemented in architecture code and referenced through `struct cpu_spec` setup/restore callbacks. Boot CPU setup initializes CPU-specific registers; secondary CPU and resume paths call restore variants.

State and persistence: the functions program CPU SPRs, cache/BHT/errata workarounds, and similar processor state outside this header.

Dependencies and integration: tightly coupled to `struct cpu_spec` declarations in `cputable.h`, early assembly bring-up, CPU hotplug, and suspend/resume.

Risks and test signals: declarations must match assembly/C implementations and CPU table entries. Missing restore support causes secondary CPU or resume misconfiguration. Test signals include per-family boot, SMP bring-up, CPU hotplug, suspend/resume, and build coverage for all configured CPU families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpu_setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpufeature.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpufeature.h

Purpose: exposes module-loader CPU feature numbers and a helper for testing user-visible CPU feature bits.

Important APIs/types/functions: defines `MAX_CPU_FEATURES`, `PPC_MODULE_FEATURE_VEC_CRYPTO`, `PPC_MODULE_FEATURE_P10`, `cpu_feature(x)`, and `cpu_have_feature()`.

Control flow: `cpu_have_feature()` selects `cur_cpu_spec->cpu_user_features` for feature numbers below 32 and `cpu_user_features2` for numbers 32 and above.

State and persistence: reads the current CPU specification’s user feature masks. No mutation or persistence.

Dependencies and integration: depends on `asm/cputable.h` and UAPI feature bits. Used by module CPU feature matching so modules can require vector crypto, POWER10 ISA features, or future user-visible capabilities.

Risks and test signals: feature numbers must remain synchronized with UAPI and module metadata. Off-by-32 errors can accept incompatible modules or reject valid ones. Test signals include module loading with feature requirements, POWER10/vector-crypto module tests, and compile checks when new `PPC_FEATURE2_*` bits are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpuidle.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpuidle.h

Purpose: declares PowerNV idle-state metadata and bit layouts for POWER stop/nap/sleep/winkle management.

Important APIs/types/functions: defines thread states (`PNV_THREAD_RUNNING`, `NAP`, `SLEEP`, `WINKLE`), packed core-idle lock/count/thread bits, PSSCR default value/mask macros, `struct pnv_idle_states_t`, `pnv_idle_states`, `nr_pnv_idle_states`, `pnv_cpu_offline()`, `validate_psscr_val_mask()`, and `report_invalid_psscr_val()`.

Control flow: runtime code validates firmware-provided PSSCR values, reports ESL/EC mismatches, and tracks per-thread core idle transitions with lock and winkle bitfields. Offline paths call `pnv_cpu_offline()`.

State and persistence: global idle-state arrays and core idle bitfields track CPU/core low-power state. PSSCR values persist as firmware-derived configuration used during idle entry.

Dependencies and integration: only active for `CONFIG_PPC_POWERNV`; depends on PSSCR bit definitions from processor headers and integrates with `kernel/idle_book3s.S`, cpuidle drivers, CPU offline, and firmware device-tree idle descriptions.

Risks and test signals: incorrect bitfield layout or PSSCR defaults can lose CPU state, wake at the wrong vector, or hang offline. Test signals include PowerNV cpuidle state enumeration, stop-state validation logs, CPU offline/online stress, suspend-like idle loops, and firmware variants with legacy RL-only PSSCR data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpuidle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputable.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputable.h

Purpose: defines the central PowerPC CPU specification structure, CPU feature bitmasks, per-family feature sets, possible/always feature masks, and CPU identification/fixup interfaces.

Important APIs/types/functions: `struct cpu_spec` records PVR match fields, feature masks, cache sizes, CPU setup/restore callbacks, platform names, and machine-check handlers. It declares `cur_cpu_spec`, `identify_cpu()`, `set_cur_cpu_spec()`, `identify_cpu_name()`, `do_feature_fixups()`, machine-check handlers, and `cpu_feature_keys_init()`. Feature macros include common bits such as `CPU_FTR_ALTIVEC`, `CPU_FTR_LWSYNC`, `CPU_FTR_DBELL`, POWER architecture levels, errata flags, and per-family `CPU_FTRS_*` bundles.

Control flow: early boot identifies a CPU by PVR, installs `cur_cpu_spec`, runs setup callbacks, then applies feature fixups based on selected CPU/MMU/firmware masks. Later code uses possible/always masks to optimize feature tests and alternatives.

State and persistence: `cur_cpu_spec` persists as the runtime CPU capability source. Feature masks determine emitted alternatives, userspace HWCAP, cache geometry, machine-check handling, and CPU hotplug restore behavior.

Dependencies and integration: includes UAPI CPU feature definitions and asm constants. It integrates with ELF aux vectors, module feature matching, feature-fixup sections, CPU setup declarations, machine-check handlers, debug/watchpoint limits, and jump-label feature checks.

Risks and test signals: feature mask mistakes can expose unsupported instructions, omit required errata workarounds, or patch wrong code paths. The `struct cpu_spec` size is consumed by assembly-generated offsets. Test signals include boot on each supported CPU family, HWCAP validation, module feature matching, machine-check recovery tests, `objdump`/mkdefs offset checks, and CPU hotplug/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputhreads.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputhreads.h

Purpose: defines topology helpers for mapping logical CPUs to hardware threads, cores, subcores, and TLB-sharing siblings.

Important APIs/types/functions: exports `threads_per_core`, `threads_per_subcore`, `threads_shift`, `threads_core_mask`, `cpu_nr_cores()`, `cpu_core_index_of_thread()`, `cpu_first_thread_of_core()`, sibling helpers, `get_tensr()`, `book3e_start_thread()`, `book3e_stop_thread()`, and `INVALID_THREAD_HWID`.

Control flow: helpers use power-of-two thread layout arithmetic. POWER9 big-core TLB sharing adjusts first/last sibling and step values when `CPU_FTR_ARCH_300` and eight threads per core are present. `get_tensr()` reads `SPRN_TENSR` on BookE SMT systems.

State and persistence: reads topology globals established during CPU discovery. No persistent state is modified by the inline helpers.

Dependencies and integration: depends on cpumasks and CPU feature tests. Used by SMP bring-up, IPI routing, TLB shootdown, CPU hotplug, BookE thread control, and scheduler/topology code.

Risks and test signals: the arithmetic assumes power-of-two thread counts and uniform numbering. Wrong sibling masks can send IPIs or TLB invalidations to the wrong CPUs. Test signals include SMT boot on Book3S/BookE, TLB shootdown stress, CPU hotplug, scheduler topology validation, and POWER9 big-core tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputhreads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputime.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputime.h

Purpose: implements PowerPC virtual CPU accounting hooks when native timebase accounting is enabled.

Important APIs/types/functions: `cputime_to_nsecs()`, `get_accounting()`, `raw_get_accounting()`, `account_cpu_user_entry()`, `account_cpu_user_exit()`, and `account_stolen_time()`.

Control flow: user entry/exit helpers read the timebase with `mftb()`, update unreconciled user/system start times, and avoid tracing. On SPLPAR, stolen-time accounting checks the lppaca dispatch trace index and calls `pseries_accumulate_stolen_time()` when it changed.

State and persistence: updates per-CPU/per-task `cpu_accounting_data`, stored in PACA on PPC64 and `thread_info` on PPC32. It reads lppaca DTL state for hypervisor stolen time.

Dependencies and integration: depends on `asm/time.h`, `asm/firmware.h`, `PACA`, SPLPAR firmware feature detection, and scheduler/accounting paths. Generic no-op stubs are emitted without native accounting.

Risks and test signals: these helpers run in sensitive entry/exit paths and cannot trace. Wrong start-time updates skew user/system/stolen accounting. Test signals include `CONFIG_VIRT_CPU_ACCOUNTING_NATIVE` builds, pseries SPLPAR workloads, `/proc/stat` accounting checks, context-switch stress, and tracing recursion checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/crash_reserve.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/crash_reserve.h

Purpose: supplies PowerPC crash-kernel reservation policy constants and hooks.

Important APIs/types/functions: defines `CRASH_ALIGN` as `PAGE_SIZE` and, with generic crashkernel reservation, `arch_add_crash_res_to_iomem()` returning false.

Control flow: no runtime control flow beyond the inline hook. Generic crashkernel code queries whether the crash reservation should be added to `/proc/iomem`.

State and persistence: no state. It constrains crashkernel memory reservation alignment and resource reporting.

Dependencies and integration: integrates with generic crashkernel reservation and kdump memory setup.

Risks and test signals: alignment must match PowerPC crash/purgatory expectations. Incorrect resource reporting can confuse kexec-tools. Test signals include `crashkernel=` reservation, `/proc/iomem` inspection, kdump boot, and builds with/without generic reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/crash_reserve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/crashdump-ppc64.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/crashdump-ppc64.h

Purpose: defines the PPC64 kdump backup source region used by purgatory trampoline code.

Important APIs/types/functions: `BACKUP_SRC_START`, `BACKUP_SRC_END`, and `BACKUP_SRC_SIZE` describe the first 64 KiB of system RAM.

Control flow: constants only; crash/purgatory code copies or preserves this region during kexec crash handling.

State and persistence: no live state in the header. The region describes persistent physical memory content needed across crash transition.

Dependencies and integration: documented assumptions are consumed by `arch/powerpc/purgatory/trampoline_64.S` and kdump tooling.

Risks and test signals: constants must remain less than `UINT32_MAX` and at least 8-byte aligned. Changing them breaks purgatory assumptions. Test signals include PPC64 kdump, purgatory build/relocation checks, and crash dump validation of low-memory backup data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/crashdump-ppc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/current.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/current.h

Purpose: provides the architecture implementation of the `current` task pointer.

Important APIs/types/functions: on PPC64, `get_current()` loads `paca->__current` from r13-relative PACA storage and `#define current get_current()`. On 32-bit, `current` is a global register variable in r2.

Control flow: PPC64 emits a single load from PACA offset; PPC32 uses compiler-reserved register state.

State and persistence: reads task pointer state maintained by context-switch code in PACA or r2. The header does not mutate it.

Dependencies and integration: depends on PACA layout offsets, `struct task_struct`, and compiler register allocation rules. Used by virtually all kernel code that references `current`.

Risks and test signals: wrong PACA offset or register convention breaks every task-context access. Test signals include early boot, context switching, preemption, modules compiled with this header, and mkdefs/offsetof consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dbdma.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dbdma.h

Purpose: defines Apple Descriptor-Based DMA controller registers, command descriptors, command encodings, and reset/stop macros for Power Macintosh hardware.

Important APIs/types/functions: `struct dbdma_regs`, `struct dbdma_cmd`, command values such as `OUTPUT_MORE`, `INPUT_LAST`, `DBDMA_STOP`, key/interrupt/branch/wait field macros, `DBDMA_ALIGN()`, `DBDMA_DO_STOP()`, and `DBDMA_DO_RESET()`.

Control flow: drivers build little-endian command rings and program controller registers. Stop/reset macros write control bits and busy-wait until `ACTIVE`, `FLUSH`, or `RUN` state clears.

State and persistence: DBDMA controller registers and command descriptors are hardware state. The structures encode persistent DMA programs shared with the device.

Dependencies and integration: depends on PowerPC I/O accessors such as `in_le32()` and `out_le32()`. Used by legacy Macintosh device drivers using DBDMA.

Risks and test signals: all fields are little-endian regardless of CPU endian. Busy waits can hang if hardware fails to clear status. Test signals include old PowerMac hardware or emulator boot, DBDMA device transfers, command ring alignment checks, and endian build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dbdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dbell.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dbell.h

Purpose: provides PowerPC doorbell/message-send constants and helpers for IPIs and message interrupts.

Important APIs/types/functions: defines doorbell message fields, `enum ppc_dbell`, `_ppc_msgsnd()`, `_ppc_msgclr()`, `ppc_msgsync()`, `ppc_msgsnd_sync()`, `ppc_msgsnd()`, `doorbell_global_ipi()`, `doorbell_core_ipi()`, `doorbell_try_core_ipi()`, and `doorbell_exception()`.

Control flow: Book3S builds use feature-fixup assembly to choose `msgsnd` versus `msgsndp` and `msgclr` versus `msgclrp` depending on HV mode. SMP IPI helpers set KVM host IPI state, issue a full sync, and send a tagged doorbell to PIR or thread-in-core target.

State and persistence: no persistent local state. It touches interrupt/message hardware state and KVM host IPI bookkeeping.

Dependencies and integration: depends on SMP topology helpers, opcode macros, feature fixups, and KVM PowerPC hooks. Used by platform IPI code and doorbell exception handling.

Risks and test signals: message type, target tag, and sync ordering are architecture-sensitive. Wrong topology choice can signal the wrong thread. Test signals include SMP IPI stress, KVM host/guest interrupt tests, Book3S HV and non-HV boots, and doorbell-capable BookE/embedded systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dbell.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr-native.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr-native.h

Purpose: implements native Device Control Register access for PowerPC 4xx-style systems.

Important APIs/types/functions: `dcr_host_native_t`, `dcr_map_native()`, `dcr_read_native()`, `dcr_write_native()`, `mfdcr()`, `mtdcr()`, indexed accessors `mfdcrx()` and `mtdcrx()`, table fallbacks `__mfdcr()` and `__mtdcr()`, indirect helpers `mfdcri()`, `mtdcri()`, and `dcri_clrset()`.

Control flow: constant DCR numbers below 1024 use direct `mfdcr/mtdcr` inline assembly. Dynamic DCRs use indexed DCR instructions when `CPU_FTR_INDEXED_DCR` is available, otherwise table fallback functions. Indirect DCR reads/writes serialize the address/data register pair with `dcr_ind_lock`.

State and persistence: DCR registers are hardware control state. The only kernel synchronization state is `dcr_ind_lock`.

Dependencies and integration: depends on CPU feature tests, spinlocks, and generated DCR register names from `dcr-regs.h`. Used by 4xx platform and device drivers.

Risks and test signals: fallback selection and indirect locking are critical; unsynchronized indirect access can corrupt another register transaction. Test signals include 4xx platform boot, DCR-mapped device probe, indexed/non-indexed DCR CPU variants, and lockdep/IRQ-disabled indirect access tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr-native.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr-regs.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr-regs.h

Purpose: collects common fixed and indirect DCR/SDR/CPR register numbers and bit definitions for IBM/AMCC 4xx processors.

Important APIs/types/functions: defines DCR address/data register pairs for CPR0 and SDR0, SDR fields for Ethernet/UART/reset, SRAM controller register offsets and bits, L2 cache controller offsets and fields, I2O/DMA registers, and memory queue bit positions.

Control flow: constants only. Drivers and platform code combine these offsets with DCR accessors from `dcr-native.h`.

State and persistence: no local state. Constants name persistent SoC control registers that affect clocks, reset, SRAM, L2 cache, Ethernet, and DMA behavior.

Dependencies and integration: integrates with DCR access macros and 4xx platform/device code. Many offsets intentionally exclude a base address that comes from the device tree.

Risks and test signals: wrong register numbers can reset or reconfigure unrelated hardware. Base-relative comments must be honored by callers. Test signals include 4xx board boot, Ethernet clock setup, SRAM/L2 cache init, I2O/DMA probe, and device-tree DCR resource validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr.h

Purpose: provides the public architecture DCR mapping/read/write facade when `CONFIG_PPC_DCR` is enabled.

Important APIs/types/functions: aliases `dcr_host_t` to `dcr_host_native_t`, maps `DCR_MAP_OK`, `dcr_map()`, `dcr_unmap()`, `dcr_read()`, and `dcr_write()` to native helpers, and declares `dcr_resource_start()` and `dcr_resource_len()` for device-tree resources.

Control flow: wrapper macros delegate to native DCR implementation. Device-tree helpers parse DCR resource ranges elsewhere.

State and persistence: no local state. It exposes hardware DCR register access and resource metadata.

Dependencies and integration: depends on `dcr-native.h` and `struct device_node`. Used by drivers that should not care whether DCR access is native or abstracted.

Risks and test signals: wrapper availability is config-gated; callers must not assume DCR APIs exist without `CONFIG_PPC_DCR`. Test signals include DCR device probe, device-tree DCR resource parsing, and builds with DCR disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/debug.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/debug.h

Purpose: declares PowerPC debugger hook function pointers and safe inline dispatch wrappers.

Important APIs/types/functions: optional hook pointers include `__debugger`, `__debugger_ipi`, `__debugger_bpt`, `__debugger_sstep`, `__debugger_iabr_match`, `__debugger_break_match`, and `__debugger_fault_handler`. `DEBUGGER_BOILERPLATE()` generates wrappers returning zero when hooks are absent.

Control flow: with debugger or kexec support, each wrapper tests the corresponding function pointer with `unlikely()` and calls it if installed. Without support, all wrappers are inline no-ops.

State and persistence: global hook pointers persist as debugger registration state. The header only reads them.

Dependencies and integration: includes hardware breakpoint definitions and integrates with exception handlers, KGDB/xmon-style debuggers, kexec crash paths, and breakpoint/fault handling.

Risks and test signals: hooks execute in exception contexts, so null checks and calling conventions are critical. Test signals include debugger breakpoint/single-step/IPI tests, kexec crash entry, builds without debugger support, and hardware breakpoint exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/delay.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/delay.h

Purpose: declares and defines PowerPC busy-wait delay helpers.

Important APIs/types/functions: exports `__delay()`, `udelay()`, `ndelay()`, `mulhwu_scale_factor()`, and loop-per-jiffy scaling inputs used by generic delay code.

Control flow: delay helpers convert requested microseconds or nanoseconds to timebase/loop counts using architecture scaling and call the low-level delay loop. Exact implementation details are in companion architecture code.

State and persistence: reads calibration state such as loops-per-jiffy/timebase conversion data. No persistent state is changed by the header.

Dependencies and integration: integrates with generic delay APIs, timebase calibration, device drivers that require short busy waits, and early boot code where timers may be unavailable.

Risks and test signals: overflow or scaling errors make delays too short or too long, breaking hardware sequencing. Test signals include timer calibration, driver probe timing, `udelay`/`ndelay` selftests where available, and 32/64-bit build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/device.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/device.h

Purpose: defines PowerPC per-device architecture data embedded in Linux device structures.

Important APIs/types/functions: `struct dev_archdata` carries `dma_offset`, optional PPC64 IOMMU table and PCI device-node data, optional EEH device pointer, fail-IOMMU flag, and SR-IOV data. `struct pdev_archdata` stores platform-device DMA mask and private PMU cleanup data.

Control flow: no algorithms. Bus and DMA/IOMMU setup code initialize these fields; DMA and PCI paths later consume them.

State and persistence: per-device state persists for the device lifetime and controls DMA address translation, IOMMU association, EEH recovery, PCI data, and SR-IOV metadata.

Dependencies and integration: integrates with `dma-direct.h`, PPC64 IOMMU, PCI/pci_dn, EEH, fail-IOMMU fault injection, SR-IOV, and platform-device registration.

Risks and test signals: stale or missing archdata causes bad DMA addresses, lost EEH association, or SR-IOV cleanup bugs. Test signals include DMA mapping tests, PCI hotplug, EEH recovery, IOMMU fault injection, SR-IOV enable/disable, and platform PMU unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/disassemble.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/disassemble.h

Purpose: provides small PowerPC instruction field extractors and DSISR synthesis for fault emulation paths.

Important APIs/types/functions: `get_op()`, `get_xop()`, `get_sprn()`, `get_dcrn()`, `get_tmrn()`, `get_rt()`, `get_rs()`, `get_ra()`, `get_rb()`, `get_rc()`, `get_ws()`, `get_d()`, `get_oc()`, `get_tx_or_sx()`, `IS_XFORM()`, `IS_DSFORM()`, and `make_dsisr()`.

Control flow: helpers shift and mask fixed instruction fields. `make_dsisr()` maps instruction bits into a DSISR-style value, with different bit routing for X-form versus D/DS-form instructions.

State and persistence: stateless computations over a 32-bit instruction word.

Dependencies and integration: depends only on Linux integer types. Used by exception, emulation, alignment, and data-storage interrupt handling code that needs to decode faulting instructions.

Risks and test signals: bit extraction must match the ISA exactly; DSISR synthesis errors break fault handling and emulation. Test signals include alignment/fault emulation tests, instruction decoder unit tests where available, KVM/emulation coverage, and randomized comparison against an authoritative decoder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/disassemble.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dma-direct.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dma-direct.h

Purpose: implements direct DMA address translation using per-device PowerPC DMA offsets.

Important APIs/types/functions: `phys_to_dma()` returns `paddr + dev->archdata.dma_offset`; `dma_to_phys()` returns `daddr - dev->archdata.dma_offset`.

Control flow: simple arithmetic conversion for direct-mapped DMA devices.

State and persistence: reads `dev->archdata.dma_offset`, which is set during device/bus setup and persists for the device lifetime.

Dependencies and integration: depends on `struct device` archdata from `device.h` and integrates with generic DMA-direct mapping.

Risks and test signals: a wrong offset causes devices to DMA to the wrong physical memory. Test signals include DMA API debug, device probe DMA masks, direct DMA transfers on offset and non-offset buses, and IOMMU-disabled boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dma-direct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dma.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dma.h

Purpose: provides legacy 8237-style ISA DMA register definitions and channel helpers for PowerPC platforms that emulate or expose PC-compatible DMA.

Important APIs/types/functions: constants define DMA controller ports, address/count/page registers, modes, and limits. Helpers include `claim_dma_lock()`, `release_dma_lock()`, `enable_dma()`, `disable_dma()`, `clear_dma_ff()`, `set_dma_mode()`, `set_dma_page()`, `set_dma_addr()`, `set_dma_count()`, `get_dma_residue()`, `request_dma()`, and `free_dma()`.

Control flow: callers claim `dma_spin_lock`, program mode/address/count/page registers with port I/O, enable the channel, and later query residue or disable/free. Address/count programming differs for 8-bit channels 0-3 and 16-bit channels 5-7.

State and persistence: hardware DMA controller registers persist transfer state. `dma_spin_lock` serializes register programming. `DMA_MODE_READ/WRITE` are externs on 32-bit and constants on 64-bit.

Dependencies and integration: depends on `asm/io.h`, spinlocks, and legacy ISA/floppy/sound style drivers. The header mainly keeps old generic DMA code buildable on PowerPC.

Risks and test signals: boundary, alignment, flip-flop, and count-minus-one rules are easy to violate. Port writes must happen with interrupts disabled while holding the lock. Test signals include floppy/ISA DMA operation, residue correctness, DMA API debug, and builds on 32-bit/64-bit PowerPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/drmem.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/drmem.h

Purpose: defines PowerPC dynamic reconfiguration memory logical memory block representation and iteration helpers.

Important APIs/types/functions: `struct drmem_lmb`, `struct drmem_lmb_info`, `drmem_info`, `drmem_lmb_next()`, `for_each_drmem_lmb*`, device-tree layout structs `of_drconf_cell_v1` and `of_drconf_cell_v2`, memory flags, reservation helpers, `drmem_lmb_memory_max()`, `walk_drmem_lmbs()`, `drmem_update_dt()`, pseries early walkers, and `invalidate_lmb_associativity_index()`.

Control flow: iterators walk LMB arrays and call `cond_resched()` every 16 entries to avoid monopolizing CPU during firmware-heavy DLPAR operations. Walk/update functions parse or rewrite dynamic-memory properties elsewhere.

State and persistence: `drmem_info` holds the runtime LMB table, LMB size, and flags. Reservation and associativity helpers mutate LMB flags/indices that drive memory hotplug and firmware/device-tree updates.

Dependencies and integration: depends on scheduler rescheduling, OF device-tree properties, and pseries DLPAR memory hotplug. Integrates with memory add/remove, NUMA associativity, and firmware dynamic memory properties.

Risks and test signals: device-tree v1/v2 layout handling and reservation flags are memory hotplug sensitive. Missing reschedules can stall large partitions. Test signals include pseries memory hotplug add/remove, dynamic-memory property updates, NUMA associativity changes, and large-LMB iteration latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/drmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dt_cpu_ftrs.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dt_cpu_ftrs.h

Purpose: declares the device-tree CPU feature discovery path that can supersede PVR-based CPU table discovery.

Important APIs/types/functions: `dt_cpu_ftrs_init()`, `dt_cpu_ftrs_scan()`, and `dt_cpu_ftrs_in_use()`, with false/no-op stubs when `CONFIG_PPC_DT_CPU_FTRS` is disabled.

Control flow: boot code initializes from the flattened device tree, scans `/cpus/features`, and later checks whether DT feature mode is active.

State and persistence: implementation maintains feature-discovery state elsewhere. The header exposes status through `dt_cpu_ftrs_in_use()`.

Dependencies and integration: includes UAPI cputable bits and integrates with early boot CPU feature setup, feature fixups, and firmware-provided CPU capability descriptions.

Risks and test signals: DT feature parsing must stay consistent with cputable feature masks. Test signals include pseries/PowerNV boots with `/cpus/features`, fallback to PVR discovery, feature fixup results, and HWCAP consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dt_cpu_ftrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dtl.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dtl.h

Purpose: defines the pseries hypervisor dispatch trace log entry format and DTL buffer management hooks.

Important APIs/types/functions: `struct dtl_entry`, `DISPATCH_LOG_BYTES`, `N_DISPATCH_LOG`, `DTL_LOG_*` masks, `dtl_cache`, `dtl_access_lock`, `register_dtl_buffer()`, and `alloc_dtl_buffers()`.

Control flow: implementation allocates per-CPU DTL buffers, registers them with firmware, and exposes log data under synchronization. The header only defines layouts and declarations.

State and persistence: per-CPU DTL buffers contain hypervisor-written dispatch/preempt/fault timing data in big-endian fields. `dtl_cache` and `dtl_access_lock` persist as allocation/synchronization state.

Dependencies and integration: depends on `asm/lppaca.h` and rwsem support. Used by pseries accounting, debugfs/proc reporting, and stolen-time analysis.

Risks and test signals: endian layout and buffer size must match firmware expectations. Test signals include pseries DTL registration, dispatch log reads, SPLPAR accounting, CPU hotplug buffer registration, and concurrency under `dtl_access_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dtl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/edac.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/edac.h

Purpose: provides the PowerPC EDAC atomic memory scrub primitive.

Important APIs/types/functions: `edac_atomic_scrub(void *va, u32 size)` iterates over 32-bit words and performs a load-reserve/store-conditional writeback of the same value followed by `isync`.

Control flow: for each word in the requested range, the helper loops on `lwarx/stwcx.` until the conditional store succeeds. This forces a read/write cycle without changing data.

State and persistence: mutates memory by writing the original value back, allowing ECC hardware to detect and correct errors. No separate kernel state is held.

Dependencies and integration: used by generic EDAC software scrubbing. Relies on PowerPC reservation semantics and memory clobbers for interrupt/DMA/SMP safety.

Risks and test signals: only full 32-bit words are scrubbed; callers must pass appropriate size/alignment. Reservation loops on faulty memory can be costly. Test signals include EDAC scrub tests, injected ECC correctable errors, SMP/DMA concurrent access, and alignment boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/eeh.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/eeh.h

Purpose: defines PowerPC Enhanced Error Handling state, platform operations, PE/device tracking, and MMIO read wrappers for PCI error isolation and recovery.

Important APIs/types/functions: `struct eeh_pe`, `struct eeh_dev`, `struct eeh_ops`, subsystem flags, PE/device state flags, traversal callbacks, `eeh_enabled()`, serialization helpers, PE tree functions, recovery/configuration APIs, `EEH_POSSIBLE_ERROR()`, `EEH_IO_ERROR_VALUE()`, and PPC64 `eeh_read*()`/string read wrappers.

Control flow: platform code registers `eeh_ops`; PCI probe creates EEH devices and PE hierarchy; MMIO reads returning all ones call `eeh_check_failure()`; events and recovery code freeze, reset, configure, restore, and resume PEs. Inline flag helpers gate EEH checks and serialize confirmation with `confirm_error_lock`.

State and persistence: global `eeh_subsystem_flags`, `eeh_ops`, freeze counters, timestamps, PE trees, per-device config snapshots, and error state persist across PCI device lifetimes and recovery cycles.

Dependencies and integration: depends on PCI, OF PCI device nodes, pseries/PowerNV platform EEH backends, IOMMU groups, debugfs, stacktrace, and UAPI EEH definitions. It integrates with PCI error handlers, hotplug, config-space access, and MMIO accessors.

Risks and test signals: false positives are possible because all-ones MMIO can be valid for some devices. PE hierarchy and config restore must be correct to avoid data loss or permanent removal. Test signals include PCI EEH injection, frozen PE recovery, hotplug remove during recovery, config-space restore, MMIO wrapper reads, and platform-specific pseries/PowerNV EEH tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/eeh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/eeh_event.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/eeh_event.h

Purpose: declares the EEH event queue item and event handling entry points.

Important APIs/types/functions: `struct eeh_event` holds a list node and affected `struct eeh_pe *`; functions include `eeh_event_init()`, `eeh_send_failure_event()`, `__eeh_send_failure_event()`, `eeh_remove_event()`, `eeh_handle_normal_event()`, and `eeh_handle_special_event()`.

Control flow: EEH detection enqueues PE failure events, worker/recovery code handles normal PE events or special global events, and events can be removed forcibly for teardown.

State and persistence: event queue entries persist until processed or removed. PE pointers tie queued work to EEH recovery state.

Dependencies and integration: depends on EEH PE definitions and Linux lists. Used by EEH recovery threads and PCI error handling.

Risks and test signals: stale PE pointers during hotplug or duplicate events can race recovery. Test signals include EEH injection storms, forced removal while queued, normal and special event handling, and recovery thread initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/eeh_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ehv_pic.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ehv_pic.h

Purpose: declares private structures and constants for the Embedded Hypervisor PIC interrupt controller.

Important APIs/types/functions: `NR_EHV_PIC_INTS`, polarity/sense macros, `struct ehv_pic` with irq domain, irq chip, and core interrupt flag, plus `ehv_pic_init()` and `ehv_pic_get_irq()`.

Control flow: initialization creates the irq domain/chip; interrupt dispatch calls `ehv_pic_get_irq()` to retrieve the active virtual interrupt.

State and persistence: `struct ehv_pic` instances hold controller mapping and Linux IRQ chip state. Hardware interrupt configuration persists in the EHV PIC.

Dependencies and integration: depends on Linux IRQ core and Freescale/ePAPR embedded hypervisor interrupt routing.

Risks and test signals: wrong sense/polarity mapping causes missed or repeated interrupts. Test signals include EHV PIC initialization, IRQ domain mapping, interrupt storm handling, and device-tree interrupt-spec parsing on embedded hypervisor systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ehv_pic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/elf.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/elf.h

Purpose: defines PowerPC ELF loading, core dump, aux vector, personality, HWCAP, vDSO, and relocation contracts.

Important APIs/types/functions: `elf_check_arch()`, `compat_elf_check_arch()`, `ELF_ET_DYN_BASE`, `ELF_CORE_EFLAGS`, `PPC_ELF_CORE_COPY_REGS`, `ppc_elf_core_copy_regs()`, `ELF_HWCAP`, `ELF_HWCAP2`, `ELF_PLATFORM`, `ELF_BASE_PLATFORM`, `SET_PERSONALITY`, `elf_read_implies_exec()`, `ARCH_DLINFO`, `COMPAT_ARCH_DLINFO`, `arch_setup_additional_pages()`, `relocate()`, and `struct func_desc`.

Control flow: ELF exec validates machine type, sets ABI/thread flags, chooses PIE base, emits aux vector cache/vDSO/min-sigstack entries, and copies registers for core dumps. PPC64 initializes r2 for ELFv1 TOC semantics and distinguishes ELFv2 via e_flags.

State and persistence: reads `cur_cpu_spec`, `current->mm->context.vdso`, task personality/thread flags, cache geometry globals, and base platform string. Core dump register data persists in ELF notes.

Dependencies and integration: depends on UAPI ELF definitions, page/task helpers, vDSO setup, signal frame sizing, CPU feature tables, and cache discovery.

Risks and test signals: ABI personality and aux vector mistakes break dynamic loaders and 32-bit compat. Core register copying must truncate correctly for 32-bit tasks. Test signals include native and compat ELF exec, PIE ASLR, glibc auxv checks, core dump inspection, ELFv1/ELFv2 binaries, vDSO mapping, and 32-bit toolchain executable-stack behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/elfnote.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/elfnote.h

Purpose: reserves PowerPC-specific ELF note type identifiers.

Important APIs/types/functions: `PPC_ELFNOTE_CAPABILITIES` identifies a PowerPC-named note containing a capabilities bitmap.

Control flow: constants only. Assembly note generation and tools consume the identifier.

State and persistence: ELF notes persist in the kernel image; this header owns no runtime state.

Dependencies and integration: integrates with `arch/powerpc/kernel/note.S` and boot/load tooling that inspects kernel capability notes.

Risks and test signals: note type collisions or format drift break external consumers. Test signals include readelf inspection of kernel notes and tooling that parses PowerPC capability notes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/elfnote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/emergency-restart.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/emergency-restart.h

Purpose: delegates PowerPC emergency restart support to the generic implementation.

Important APIs/types/functions: includes `<asm-generic/emergency-restart.h>` and defines no local API.

Control flow: generic emergency restart paths are used directly.

State and persistence: no local state.

Dependencies and integration: integrates generic restart handling into PowerPC builds.

Risks and test signals: risk is minimal and centered on generic include compatibility. Test signals include build coverage and emergency restart/reboot path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/emergency-restart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/emulated_ops.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/emulated_ops.h

Purpose: tracks and reports software-emulated PowerPC operations and alignment faults.

Important APIs/types/functions: `struct ppc_emulated_entry`, global `ppc_emulated`, `ppc_warn_emulated`, `ppc_warn_emulated_print()`, `PPC_WARN_EMULATED()`, and `PPC_WARN_ALIGNMENT()`.

Control flow: emulation sites call macros that emit perf software events and, when stats are enabled, atomically increment the relevant counter and optionally print a warning.

State and persistence: optional global counters persist per emulated operation category. `ppc_warn_emulated` controls warning output.

Dependencies and integration: depends on atomics and perf events. Used by instruction emulation, alignment handling, math emulation, VSX/Altivec/SPE emulation, and PPC64 emulated instruction paths.

Risks and test signals: missing counters hide performance/debug signals; excessive warnings can flood logs. Test signals include perf emulation/alignment event counts, `/proc` or debug stats where exposed, alignment fault tests, and builds with each optional emulation feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/emulated_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/epapr_hcalls.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/epapr_hcalls.h

Purpose: provides inline C wrappers for ePAPR hypercalls issued through the PowerPC `sc 1` hypercall entry.

Important APIs/types/functions: declares `epapr_paravirt_enabled`, `epapr_hypercall_start`, `epapr_paravirt_early_init()`, interrupt hypercalls (`ev_int_set_config`, `ev_int_get_config`, `ev_int_set_mask`, `ev_int_get_mask`, `ev_int_eoi`, `ev_int_iack`), byte channel hypercalls, `ev_doorbell_send()`, `ev_idle()`, generic `epapr_hypercall()`, and convenience `epapr_hypercall0*` through `epapr_hypercall4()`.

Control flow: wrappers bind arguments to fixed registers, set r11 to the hypercall token, branch to `epapr_hypercall_start`, read return registers, and copy outputs to caller buffers. Byte-channel helpers marshal four big-endian 32-bit words. Generic paravirt wrappers pass up to eight input/output registers when enabled, otherwise return `EV_UNIMPLEMENTED`.

State and persistence: no local state, but hypercalls mutate hypervisor state such as interrupt configuration, masks, byte-channel queues, doorbells, and virtual CPU idle state.

Dependencies and integration: depends on UAPI ePAPR tokens, byte order helpers, errno, and the paravirt early initialization path. Used by embedded hypervisor interrupt, console/byte-channel, idle, and paravirtualized platform code.

Risks and test signals: register constraints and clobber lists are correctness-critical. Missing memory clobbers can reorder guest memory shared with the hypervisor. Test signals include ePAPR guest boot, interrupt config/mask/EOI paths, byte-channel send/receive, idle hypercall behavior, paravirt-disabled fallback, and compiler build coverage for GCC/Clang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/epapr_hcalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exception-64e.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exception-64e.h

Purpose: defines Book3E 64-bit exception save-area offsets, TLB-miss prolog/epilog assembly macros, IVOR setup, and return-from-interrupt macros.

Important APIs/types/functions: PACA offsets such as `EX_R1` and `EX_TLB_*`, `START_EXCEPTION()`, `TLB_MISS_PROLOG`, `TLB_MISS_RESTORE()`, `TLB_MISS_EPILOG_SUCCESS`, error epilogs, `interrupt_base_book3e`, `SET_IVOR()`, `RFI_TO_KERNEL`, and `RFI_TO_USER`.

Control flow: TLB miss prolog saves scratch registers, CR, SRR0/SRR1, and PACA state into a reentrant PACA exception frame, advances the frame pointer for nested misses, and restores on success or error. IVOR setup writes exception vector offsets from `interrupt_base_book3e`.

State and persistence: uses PACA exception save areas and SPRG scratch registers. It manipulates SRR0/SRR1 and IVOR SPRs, all critical processor state.

Dependencies and integration: consumed by Book3E exception assembly, PACA layout, TLB miss handlers, and low-level interrupt return code.

Risks and test signals: reentrancy and SPRG usage are extremely sensitive; leaked user-readable SPRGs or wrong save offsets can corrupt nested exceptions. Test signals include Book3E boot, TLB miss stress, nested machine-check/critical interrupt scenarios, vector setup validation, and syscall/interrupt return tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exception-64e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exception-64s.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exception-64s.h

Purpose: defines Book3S 64-bit exception save offsets and assembly slots for speculation/security fixups around interrupt entry and return.

Important APIs/types/functions: PACA offsets `EX_R9` through `EX_CTR`, `MAX_MCE_DEPTH`, slot macros `STF_ENTRY_BARRIER_SLOT`, `STF_EXIT_BARRIER_SLOT`, `ENTRY_FLUSH_SLOT`, `SCV_ENTRY_FLUSH_SLOT`, `RFI_FLUSH_SLOT`, return macros `RFI_TO_*`, `HRFI_TO_*`, `RFSCV_TO_USER`, and C prototype `do_uaccess_flush()`.

Control flow: assembler entry/return paths expand to feature-fixup sections plus placeholder nops. Runtime feature fixups can replace those nops with barriers or cache flushes before entry to kernel or return to user/guest. Return macros execute `rfid/hrfid/rfscv` and branch to fallback flush code if patched behavior requires it.

State and persistence: PACA save areas hold interrupted register state. Feature-fixup tables and fallback labels persist in the kernel image and are patched/used based on CPU/firmware mitigations.

Dependencies and integration: depends on `feature-fixups.h`, low-level exception assembly, security mitigation code, membarrier sync-core semantics, uaccess flushing, and machine-check recursion handling.

Risks and test signals: slot sizes must match patch code and return instructions must remain context synchronizing. Mistakes can create security regressions or broken interrupt returns. Test signals include Book3S boot, syscall/SCV paths, Spectre/L1D mitigation toggles, KVM guest returns, machine-check recursion tests, and objdump verification of fixup sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exception-64s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exec.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exec.h

Purpose: declares the PowerPC stack alignment hook used during exec.

Important APIs/types/functions: `arch_align_stack(unsigned long sp)`.

Control flow: implementation adjusts the initial userspace stack pointer for architecture alignment and randomization policy.

State and persistence: no local state. The returned stack address persists as the new program’s initial stack.

Dependencies and integration: used by generic exec/binfmt code and interacts with ABI stack alignment and ASLR.

Risks and test signals: wrong alignment breaks ABI assumptions in userspace startup code. Test signals include exec of native and compat binaries, stack alignment checks, ASLR entropy tests, and dynamic loader startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/extable.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/extable.h

Purpose: defines PowerPC relative exception table entries and helpers for fault fixups.

Important APIs/types/functions: `ARCH_HAS_RELATIVE_EXTABLE`, `struct exception_table_entry`, `extable_fixup()`, and `EX_TABLE(_fault, _target)`.

Control flow: faulting instruction addresses and fixup targets are stored as relative offsets in `__ex_table`. On fault, `extable_fixup()` reconstructs the continuation address from the entry-local offset.

State and persistence: exception table entries persist in the kernel image. The header owns no mutable state.

Dependencies and integration: used by inline assembly, uaccess, copy routines, and exception handling code that recovers from expected faults.

Risks and test signals: relative offset encoding must match linker/runtime lookup assumptions. Bad entries cause recoverable faults to oops or continue at the wrong address. Test signals include uaccess fault injection, copy_from_user tests, exception table sorting/lookup, and module exception table handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fadump-internal.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fadump-internal.h

Purpose: defines internal Firmware-Assisted Dump configuration, crash-info headers, memory range tracking, and platform operations.

Important APIs/types/functions: constants such as `FADUMP_MAX_MEM_REGS`, `FADUMP_REGISTER`, crash-info magic/version, `fadump_str_to_u64()`, `struct fadump_crash_info_header`, `fadump_memory_range`, `fadump_mrange_info`, `fw_dump`, `fadump_ops`, helper declarations for CPU notes and ELF core header updates, and RTAS/OPAL device-tree scan hooks.

Control flow: common FADump code fills `fw_dump`, calls platform ops to initialize metadata, register/unregister/invalidate firmware dumps, process active dumps, and trigger crash capture. `fadump_str_to_u64()` builds stable 8-byte magic values.

State and persistence: `fw_dump` holds persistent dump reservation, boot memory ranges, CPU state destination, metadata, flags, and platform ops. Crash-info headers persist across crash/reboot so the capture kernel can identify and process prior crash data.

Dependencies and integration: integrates with memblock, pt_regs, cpumasks, seq_file reporting, pseries RTAS FADump, PowerNV OPAL FADump, CMA, and ELF core generation.

Risks and test signals: structure layout is cross-kernel persistent; new fields must append and bump versions. Memory range limits and reservation flags affect crash survivability. Test signals include FADump registration, crash trigger and capture boot, old/new header compatibility, OPAL/RTAS paths, reserved-memory contiguity, and ELF vmcore validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fadump-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fadump.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fadump.h

Purpose: exposes the public PowerPC Firmware-Assisted Dump interface and stubs when FADump is disabled.

Important APIs/types/functions: `crashing_cpu`, `is_fadump_memory_area()`, `setup_fadump()`, `is_fadump_active()`, `should_fadump_crash()`, `crash_fadump()`, `fadump_cleanup()`, `fadump_setup_param_area()`, `fadump_append_bootargs()`, `early_init_dt_scan_fw_dump()`, `fadump_reserve_mem()`, and `fadump_cma_init()`.

Control flow: enabled builds reserve memory, parse firmware dump device-tree data, set up parameter areas, append boot arguments for capture kernels, and trigger firmware-assisted crash dumps. Disabled builds compile no-op or false-returning inline stubs.

State and persistence: enabled FADump state includes reserved memory, active dump flags, crash CPU, bootargs, and optional CMA reservation state. The header itself stores no state.

Dependencies and integration: integrates with panic/crash paths, early device-tree scanning, memory reservation, CMA, and FADump internals.

Risks and test signals: stubs must preserve caller behavior when disabled. Enabled paths must not reserve overlapping memory or trigger unwanted dumps. Test signals include builds with `CONFIG_FA_DUMP`, `CONFIG_PRESERVE_FA_DUMP`, CMA combinations, `fadump=on/off`, crash capture boot, and cleanup after processed dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fadump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/feature-fixups.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/feature-fixups.h

Purpose: defines the PowerPC assembly metadata format and macros for CPU, MMU, firmware, and security-mitigation feature alternatives.

Important APIs/types/functions: `BEGIN_FTR_SECTION*`, `END_FTR_SECTION*`, `FTR_SECTION_ELSE`, `ALT_FTR_SECTION_END*`, MMU/FW variants, `ASM_FTR_IF*`, `ASM_MMU_FTR_IF*`, LWSYNC and barrier fixup section macros, BTB flush section macros, fixup boundary symbols, `apply_feature_fixups()`, `update_mmu_feature_fixups()`, and `setup_feature_keys()`.

Control flow: assembly wraps primary and alternate instruction sequences, emits relative offset table entries into feature-specific sections, and enforces alternate size constraints. Runtime fixup code scans those sections and patches instructions based on CPU/MMU/firmware masks. Security slots emit additional single-offset tables for entry/exit, uaccess, RFI, nospec, and BTB flush patching.

State and persistence: fixup tables persist in the kernel image and may be consumed during boot or runtime MMU feature updates. `static_key_feature_checks_initialized` and fallback symbols coordinate feature checks and mitigations.

Dependencies and integration: depends on assembler semantics, asm constants, Clang/GNU assembler differences, CPU/MMU/firmware feature masks, exception headers, barrier code, and jump-label feature keys.

Risks and test signals: relative offsets assume fixup tables follow code, and alternate code must not be larger than its patch slot. Incorrect table format can patch arbitrary code. Test signals include all PowerPC builds, objdump/fixup table inspection, boot-time alternatives, runtime MMU feature updates, Spectre/L1D mitigation toggles, Clang/GCC assembler coverage, and vDSO32 offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/feature-fixups.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/firmware.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/firmware.h

Purpose: defines firmware capability bits, possible/always masks for supported platforms, and firmware feature test/fixup interfaces.

Important APIs/types/functions: `FW_FEATURE_*` bits cover pseries RTAS/PAPR services, LPAR/SPLPAR, OPAL, PS3 LV1, dynamic memory, ultravisor, TCE features, watchdog, PLPKS, and more. It exports `powerpc_firmware_features`, `firmware_has_feature()`, FWNMI entry points, `fwnmi_active`, `ibm_nmi_interlock_token`, firmware fixup section boundaries, and `pseries_probe_fw_features()`.

Control flow: platform probe code populates `powerpc_firmware_features`; `firmware_has_feature()` returns true for always-present features or runtime-detected possible features. Feature-fixup code can patch firmware-dependent sections.

State and persistence: global firmware feature masks and FWNMI state persist after platform initialization. Firmware capabilities drive hypervisor calls, memory hotplug, dump, IOMMU, and interrupt behavior.

Dependencies and integration: depends on asm constants and platform config selections for pseries, PowerNV, PS3, and native hash MMU. Used throughout platform, memory, interrupt, dump, and virtualization code.

Risks and test signals: incorrect possible/always masks can call unavailable firmware services or skip required ones. Test signals include pseries/PowerNV/PS3 boot, RTAS/OPAL feature probing, firmware fixup patching, FWNMI handling, SPLPAR behavior, and dynamic memory features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fixmap.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fixmap.h

Purpose: defines PowerPC compile-time fixed virtual address slots and the architecture implementation of `__set_fixmap()`.

Important APIs/types/functions: `enum fixed_addresses`, early debug slots, highmem kmap slots, 8xx/83xx IMMR slots, boot-time bitmap slots, `FIXADDR_START`, `FIXMAP_PTE_SIZE`, `FIXMAP_PAGE_NOCACHE`, `FIXMAP_PAGE_IO`, `__set_fixmap()`, `__early_set_fixmap`, and `VIRT_IMMR_BASE`.

Control flow: `__set_fixmap()` validates the index at compile time or runtime, maps the physical address with `map_kernel_page()` when `flags` is nonzero, otherwise unmaps the fixed virtual address.

State and persistence: fixed mappings persist in kernel page tables until changed. Highmem and boot mappings use reserved ranges below `FIXADDR_TOP`.

Dependencies and integration: depends on page table APIs, generic fixmap, highmem, kmap sizing, and platform IMMR requirements for 8xx/83xx.

Risks and test signals: index arithmetic must avoid overlap with vmalloc and satisfy PPC64 size limits. Wrong IMMR alignment breaks early platform register access. Test signals include early ioremap/fixmap use, highmem kmap tests, 8xx/83xx boot, map/unmap assertions, and PPC64 `BUILD_BUG_ON` coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/floppy.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/floppy.h

Purpose: supplies PowerPC-specific glue for the legacy PC floppy driver, including virtual DMA fallback.

Important APIs/types/functions: port I/O macros, DMA/IRQ macros, `struct fd_dma_ops`, static virtual DMA state, `floppy_hardint()`, virtual DMA helpers, `fd_request_irq()`, `vdma_dma_setup()`, `hard_dma_setup()`, real/virtual ops tables, `fd_request_dma()`, FDC base constants, drive counts, and floppy type defaults.

Control flow: request paths choose virtual DMA when `can_use_virtual_dma` allows it, otherwise request real ISA DMA. Hard DMA maps buffers through `isa_bridge_pcidev`, programs DMA registers, and caches the last mapping. Virtual DMA services bytes from the floppy data port in the interrupt handler until DMA/ready status changes, then calls the generic floppy interrupt.

State and persistence: static variables track virtual DMA count, residue, address, mode, active flag, selected ops, and cached real DMA mapping. Hardware FDC/DMA state persists across transfers.

Dependencies and integration: depends on generic floppy driver symbols, ISA DMA helpers, PCI `isa_bridge_pcidev`, DMA mapping API, IRQ API, and PowerPC machine-dependent I/O.

Risks and test signals: static cached DMA mapping can go stale if device lifetime changes; virtual DMA interrupt loops must not overrun buffers. Test signals include floppy probe/read/write on PowerPC systems with and without real DMA, DMA mapping error paths, IRQ handling, and module unload/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fprobe.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fprobe.h

Purpose: adapts generic fprobe support to PowerPC address layout.

Important APIs/types/functions: includes `asm-generic/fprobe.h` and, on 64-bit, overrides `FPROBE_HEADER_MSB_PATTERN` to `PAGE_OFFSET & ~FPROBE_HEADER_MSB_MASK`.

Control flow: no runtime control flow. Compile-time constants influence fprobe header/address validation.

State and persistence: no state.

Dependencies and integration: integrates generic fprobe instrumentation with PowerPC kernel virtual address high bits.

Risks and test signals: wrong MSB pattern can reject valid fprobe targets or accept invalid ones. Test signals include fprobe/ftrace selftests on PPC64, kprobe/fprobe coexistence, and address validation for kernel text and modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fpu.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fpu.h

Purpose: exposes safe kernel FPU usage helpers for PowerPC.

Important APIs/types/functions: `kernel_fpu_available()`, `kernel_fpu_begin()`, and `kernel_fpu_end()`.

Control flow: availability checks that the CPU does not advertise `CPU_FTR_FPU_UNAVAILABLE`. Begin disables preemption and enables kernel FP state; end disables kernel FP and reenables preemption.

State and persistence: manipulates per-CPU/thread floating-point ownership and preemption state through `enable_kernel_fp()` and `disable_kernel_fp()`.

Dependencies and integration: depends on CPU feature checks, preemption control, and switch-to/FPU state management. Used by kernel code that needs floating-point operations without corrupting userspace FP state.

Risks and test signals: missing `kernel_fpu_end()` leaves preemption disabled or FP state exposed. Calling on CPUs without FPU support is invalid. Test signals include kernel FPU selftests/users, preempt debug, context-switch FP state preservation, and builds with `CPU_FTR_FPU_UNAVAILABLE` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fpu.h -->
