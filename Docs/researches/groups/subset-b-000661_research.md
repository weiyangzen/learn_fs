# Research: subset-b-000661

Grouped research for ARM memory-management configuration, abort handlers, alignment emulation, and cache controller implementations under `sources/distributed-fs/ceph-client/arch/arm/mm`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mm/Kconfig

Purpose: declares the ARM processor, abort, cache, TLB, copy-page, endianness, branch-hardening, kuser-helper, VDSO, DMA memory, and outer-cache configuration symbols used by the ARM memory-management build. It is the Kconfig map from supported CPU cores to the low-level `arch/arm/mm` implementations selected into the kernel image.

Important APIs/types/functions: this is declarative Kconfig rather than executable code. Important symbols include CPU selections such as `CPU_ARM7TDMI`, `CPU_ARM920T`, `CPU_FEROCEON`, `CPU_V6`, `CPU_V7`, and `CPU_V7M`; implementation selectors such as `CPU_ABRT_*`, `CPU_CACHE_*`, `CPU_COPY_*`, `CPU_TLB_*`, `CPU_CP15_MMU`, and `CPU_CP15_MPU`; feature controls such as `ARM_LPAE`, `SWP_EMULATE`, `CPU_BIG_ENDIAN`, `CPU_HIGH_VECTOR`, `CPU_ICACHE_DISABLE`, `CPU_DCACHE_DISABLE`, `HARDEN_BRANCH_PREDICTOR`, `KUSER_HELPERS`, and `VDSO`; and outer-cache symbols `CACHE_B15_RAC`, `CACHE_FEROCEON_L2`, `CACHE_L2X0`, `CACHE_L2X0_PMU`, `CACHE_TAUROS2`, `CACHE_UNIPHIER`, and `CACHE_XSC3L2`.

Control flow: selecting a CPU core pulls in an architecture level, abort model, cache model, CP15/MMU/MPU support, page-copy routines, TLB routines, and feature dependencies. Later sections gate optional CPU features and outer cache controller drivers. The Makefile consumes these symbols to compile the matching assembly or C object, so this file is the first stage of low-level MM dispatch.

State and persistence: Kconfig choices persist in the kernel `.config` and shape the compiled binary. They do not create runtime state themselves, but they determine whether runtime global hooks such as `outer_cache`, fault hooks, proc entries, CPU hotplug callbacks, PMU registration, and cache maintenance routines exist.

Dependencies and integration points: integrates with platform `ARCH_*` and `SOC_*` selections, `MMU`, `SMP`, `PERF_EVENTS`, `PROC_FS`, `STRICT_KERNEL_RWX`, `AEABI`, `ARM_ARCH_TIMER`, `LD_IS_LLD`, and cache-controller device-tree support. The selected symbols drive `arch/arm/mm/Makefile`, processor support files, fault handling, cache/TLB flush vectors, DMA coherency, and security mitigations.

Risks: incorrect `select` chains can build an abort/cache/TLB implementation incompatible with the actual CPU, which is catastrophic because these routines run in exception and DMA paths. Some symbols encode hardware errata or security tradeoffs, so disabling defaults such as kuser helpers, branch hardening, or DMA bufferable mappings can break old userspace or expose hazards. Big-endian and no-MMU combinations have narrow hardware support. Optional cache controllers that should be mandatory for a board can produce a bootable but incoherent kernel if configured out.

Test signals: useful checks are `olddefconfig`/`savedefconfig` coverage for representative ARMv4, ARMv5, ARMv6, ARMv7, ARMv7-M, MMU, and no-MMU platforms; compile tests that ensure each selected `CPU_ABRT_*` and `CPU_CACHE_*` has a matching object; boot tests verifying cache/TLB/DMA coherency; Kconfig dependency tests for illegal endian/MMU combinations; and runtime smoke tests for proc alignment control, VDSO, SWP emulation, and outer cache registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mm/Makefile

Purpose: builds the ARM-specific memory-management objects according to the Kconfig CPU, MMU, debug, sanitizer, and outer-cache selections. It ties generic ARM MM files to the exact abort, cache, copy-page, TLB, processor, and outer-cache implementations selected for the target kernel.

Important APIs/types/functions: key build groups include always-built core objects `extable.o`, `fault.o`, `init.o`, `iomap.o`, `dma-mapping$(MMUEXT).o`, `cache.o`, and `tlb.o`; MMU-only objects `fault-armv.o`, `flush.o`, `idmap.o`, `ioremap.o`, `mmap.o`, `pgd.o`, `mmu.o`, and `pageattr.o`; no-MMU objects `nommu.o`, `pmsa-v7.o`, and `pmsa-v8.o`; abort objects `abort-*.o`; cache objects `cache-*.o`; TLB objects `tlb-*.o`; CPU processor objects `proc-*.o`; and outer cache objects such as `l2c-common.o`, `cache-l2x0.o`, and vendor-specific controllers.

Control flow: kbuild evaluates `obj-y` and `obj-$(CONFIG_...)` assignments, compiling and linking exactly the objects enabled by the configuration. It also disables KASAN for `mmu.o` and `physaddr.o` where instrumentation would interfere with low-level address translation paths.

State and persistence: the Makefile has no runtime state. Its persistent effect is the link composition of `arch/arm/mm`, including which entry points are available for processor dispatch tables and which outer-cache hooks can be initialized at boot.

Dependencies and integration points: consumes Kconfig symbols from this directory and broader kernel configuration. It integrates with kbuild, ARM processor support, fault handling, DMA mapping, KASAN, CFI, debug virtual address checks, module symbol export, and device-tree-driven outer cache initialization.

Risks: object selection must match Kconfig `select` chains exactly. A missing object for a selected CPU model will fail the build; a wrong object can compile but leave exception vectors, cache maintenance, or TLB routines incompatible with the CPU. Sanitizer overrides are important because instrumentation in early MM code can recurse through unmapped or not-yet-valid memory paths.

Test signals: run build coverage for representative `multi_v7_defconfig`, no-MMU, ARMv4/v5 legacy, LPAE, KASAN, CFI, and outer-cache configurations. Link-map inspection should show only the selected abort/cache/TLB/copy/proc objects. Runtime boot tests should exercise page faults, DMA mapping, module loading, CPU hotplug, and suspend/resume when corresponding objects are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev4.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev4.S

Purpose: implements the early data-abort entry helper for ARMv4-style CPUs using CP15 fault status/address registers and ARM instruction decoding to infer whether the abort came from a write.

Important APIs/types/functions: exports `v4_early_abort`. It reads FSR via `mrc p15, 0, r1, c5, c0, 0`, FAR via `mrc p15, 0, r0, c6, c0, 0`, reads the faulting ARM instruction at `r4`, disables user access with `uaccess_disable ip`, adjusts FSR write bits, and branches to `do_DataAbort`.

Control flow: the vector caller passes `pt_regs` in `r2`, fault PC in `r4`, and PSR in `r5`. The handler fetches fault metadata, reads the aborted instruction, clears FSR bits 10 and 11, tests instruction bit 20, sets the write indicator when needed, then tail-branches into the common data-abort handler.

State and persistence: no persistent state. It transiently updates `r0` and `r1` with FAR/FSR for `do_DataAbort` and must preserve the register contract documented in the comment.

Dependencies and integration points: selected by `CPU_ABRT_EV4` and linked through the ARM exception vector path. It depends on CP15 MMU registers, `asm/assembler.h`, and common fault handling in `do_DataAbort`.

Risks: it reads the aborted instruction from user space while handling an abort, so mismatched I-TLB/D-TLB state can produce nested aborts. The write/read inference is ARM-instruction-specific and lacks Thumb handling; it is only suitable for the CPU models selecting it.

Test signals: boot on FA526/StrongARM-style configurations, trigger read and write data aborts, verify fault status write classification, and test user instruction fetch fault nesting behavior under invalid mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev4.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev4t.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev4t.S

Purpose: implements early data-abort decoding for ARMv4T CPUs, adding Thumb instruction support to the ARMv4 abort model.

Important APIs/types/functions: exports `v4t_early_abort` and includes `abort-macro.S` for `do_thumb_abort`. It reads FSR/FAR from CP15, invokes Thumb-specific decode when `PSR_T_BIT` is set, otherwise reads the ARM instruction and infers write status from bit 20.

Control flow: after obtaining FSR and FAR, `do_thumb_abort` handles Thumb faults directly by decoding a 16-bit instruction and branching to `do_DataAbort`. If the aborted context is ARM state, execution falls through to ARM instruction fetch, FSR cleanup, write-bit adjustment, and the common abort handler.

State and persistence: no persistent state. Register outputs are FAR in `r0`, FSR in `r1`, and preserved context registers as required by the abort vector ABI.

Dependencies and integration points: selected by `CPU_ABRT_EV4T`, used by ARM920/922/925/1020-class configurations, and integrated with common `do_DataAbort`.

Risks: safe classification depends on correctly reading user Thumb/ARM instruction memory during abort handling. Thumb `LDRSB` needs special handling because its opcode bit convention differs from normal load/store write-bit semantics.

Test signals: test ARM and Thumb user-mode load/store aborts, especially `LDRSB`, write faults, and executable/non-executable mapping mismatches that could cause nested instruction reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev4t.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev5t.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev5t.S

Purpose: implements early data-abort decoding for ARMv5T CPUs, including Thumb handling and the ARM `LDRD` read-instruction exception to normal write-bit decoding.

Important APIs/types/functions: exports `v5t_early_abort` and uses macros `do_thumb_abort` and `teq_ldrd` from `abort-macro.S`. It reads FSR/FAR, handles Thumb, reads ARM instruction, disables user access, clears FSR bit 11, checks for `LDRD`, and otherwise derives write status from bit 20.

Control flow: Thumb-mode faults are resolved by the macro path. ARM-mode faults are decoded locally; if `teq_ldrd` matches, the handler does not mark the fault as a write. Other instructions use the load bit to set the write indicator before tail-branching to `do_DataAbort`.

State and persistence: no persistent state; it prepares `r0`/`r1` for the common abort path.

Dependencies and integration points: selected by `CPU_ABRT_EV5T` for XScale, XSC3, Mohawk, Feroceon, and related ARMv5-style CPUs. Relies on CP15 fault registers and the common data-abort path.

Risks: misclassifying `LDRD` as a write would incorrectly signal faults on read-only mappings. Instruction fetch from the faulting PC remains fragile if user mappings are inconsistent.

Test signals: trigger read/write aborts for ARM, Thumb, and `LDRD` instructions; verify `si_code`/fault permissions match read vs write; and run on ARMv5T hardware or emulator configurations selecting this object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev5t.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev5tj.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev5tj.S

Purpose: implements ARMv5TEJ/Jazelle-capable early data-abort decoding, preserving the ARMv5T behavior while avoiding instruction decode for Java state.

Important APIs/types/functions: exports `v5tj_early_abort`, uses `do_thumb_abort` and `teq_ldrd`, tests `PSR_J_BIT`, reads CP15 FSR/FAR, clears FSR bits 10 and 11, and branches to `do_DataAbort`.

Control flow: after FSR/FAR capture, Java state bypasses instruction decoding and goes straight to common data-abort handling. Non-Java Thumb state is handled by `do_thumb_abort`; ARM state reads the instruction, disables user access, special-cases `LDRD`, then derives the write indicator from bit 20.

State and persistence: no persistent state; all work is in exception registers.

Dependencies and integration points: selected by `CPU_ABRT_EV5TJ`, notably ARM926T-style configurations. It depends on the PSR Java and Thumb bits being accurate in the saved context.

Risks: Java/Jazelle state cannot be decoded like ARM/Thumb, so permission classification relies on hardware-provided status. As with other early abort handlers, user instruction reads during exception handling can fault again.

Test signals: exercise ARM926T data aborts from ARM, Thumb, and if applicable Jazelle state; verify `LDRD` read faults are not treated as writes; and boot-test configurations selecting `CPU_ABRT_EV5TJ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev5tj.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev6.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev6.S

Purpose: implements ARMv6 early data-abort entry handling, normally trusting hardware FSR/FAR data but applying an ARM1136 SWP erratum workaround when configured.

Important APIs/types/functions: exports `v6_early_abort`, reads CP15 FSR/FAR, optionally handles `CONFIG_ARM_ERRATA_326103`, checks processor ID, PSR Java/Thumb bits, decodes ARM instruction including BE8 byte reversal and `teq_ldrd`, disables user access, and branches to `do_DataAbort`.

Control flow: base flow is simple: capture FSR/FAR, disable user access, and dispatch. Under erratum 326103 on ARM1136, ARM-state aborted instructions are read to correct missing write indication for faulty `SWP` handling while preserving `LDRD` as a read.

State and persistence: no persistent state. The erratum path transiently changes FSR bit 11 before entering common abort handling.

Dependencies and integration points: selected by `CPU_ABRT_EV6`. It depends on CP15 registers, processor ID encoding, optional BE8 handling, and common `do_DataAbort`.

Risks: erratum-specific decode must not run on unaffected CPUs or non-ARM states. Incorrect BE8 reversal or `LDRD` handling would corrupt fault classification. The workaround reads faulting instruction memory during abort handling.

Test signals: ARMv6 data-abort tests with and without `CONFIG_ARM_ERRATA_326103`, ARM1136 SWP fault cases, BE8 instruction decoding, and regression tests for normal ARMv6 faults that should bypass the workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev6.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev7.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev7.S

Purpose: provides the ARMv7 early data-abort helper, relying on ARMv7 hardware fault status rather than software instruction decoding.

Important APIs/types/functions: exports `v7_early_abort`. It reads CP15 FSR and FAR into `r1` and `r0`, disables user access, and branches to `do_DataAbort`.

Control flow: the handler is straight-line: capture fault metadata, close user access in the exception context, and tail-call the common data-abort path.

State and persistence: no persistent state. It is an exception entry helper with strict register ABI.

Dependencies and integration points: selected by `CPU_ABRT_EV7` for ARMv7 and ARMv8 AArch32-style configurations. Integrated with ARM fault dispatch and `do_DataAbort`.

Risks: any change to the register ABI would break common fault handling. Unlike older handlers, it does not patch FSR from decoded instructions, so it assumes ARMv7 status bits are sufficient and correct for permission reporting.

Test signals: ARMv7 page fault and permission fault tests, user/kernel access-disable verification, and boot tests across SMP and LPAE-capable configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-lv4t.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/abort-lv4t.S

Purpose: implements late data-abort fixup for ARMv4T-class CPUs, where writeback may already have happened before the abort is reported. It decodes faulting ARM or Thumb load/store instructions and repairs base register/SP writeback before invoking common fault handling.

Important APIs/types/functions: exports `v4t_late_abort`. Internal labels handle ARM instruction classes such as `.data_arm_ldmstm`, `.data_arm_lateldrhpost`, `.data_arm_lateldrpreconst`, `.data_arm_lateldrpostreg`, `.data_unknown`, and Thumb classes `.data_thumb_reg`, `.data_thumb_pushpop`, and `.data_thumb_ldmstm`.

Control flow: the entry determines Thumb vs ARM state. With CP15 MMU, it reads FSR/FAR and clears write-related bits; without CP15 MMU it provides zero FSR/FAR. ARM state uses a jump table over instruction bits to classify LDR/STR/LDM/STM/halfword forms, computes offset or register count, and undoes writeback in `pt_regs` when required. Thumb state reads the 16-bit instruction, decodes high opcode bits, repairs SP or base register for push/pop and LDM/STM, and passes unknown instructions to `baddataabort`.

State and persistence: no global state. It mutates the saved register frame in `pt_regs` to undo architectural side effects before `do_DataAbort` sees the fault. Temporary `r9` is saved on the stack in paths needing it.

Dependencies and integration points: selected by `CPU_ABRT_LV4T` for ARM7/ARM720/ARM740-style late-abort CPUs. Integrates with `do_DataAbort`, `baddataabort`, CP15 if available, and the ARM exception vector ABI.

Risks: this is high-risk instruction decoding in exception context. Any unsupported addressing mode falls into bad-data-abort handling. Off-by-one register-count or U/P/W bit errors would corrupt user register state. It assumes specific ARM/Thumb encodings and is not portable to newer instruction sets beyond the selected CPUs.

Test signals: targeted assembly tests for post-index/pre-index LDR/STR, LDRH/STRH, LDM/STM writeback, Thumb push/pop, Thumb LDM/STM, and unknown instruction paths; verify base registers are restored exactly once; test no-MMU and CP15-MMU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-lv4t.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-macro.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/abort-macro.S

Purpose: provides shared assembly macros for early abort handlers that must classify Thumb `LDRSB` and ARM `LDRD` correctly despite nonstandard use of load/write indicator bits.

Important APIs/types/functions: defines `.macro do_thumb_abort, fsr, pc, psr, tmp` and `.macro teq_ldrd, tmp, insn`. `do_thumb_abort` reads the aborted Thumb instruction, masks opcode bits, recognizes `LDRSB`, adjusts the effective load bit, marks write faults in FSR, and branches to `do_DataAbort`. `teq_ldrd` tests the ARM `LDRD` encoding pattern.

Control flow: included abort handlers call `do_thumb_abort` before ARM-state instruction decode. If PSR is not Thumb, the macro falls through at `not_thumb`; otherwise it completes handling by branching to the common abort path. `teq_ldrd` sets condition flags for caller branches.

State and persistence: no runtime state; this is compile-time macro text. It operates on caller-supplied registers and condition flags.

Dependencies and integration points: included by ARMv4T, ARMv5T, ARMv5TJ, and ARMv6 abort handlers. Depends on `PSR_T_BIT`, `uaccess_disable`, and `do_DataAbort`.

Risks: macro register arguments must not conflict with caller live registers. Wrong decode masks would misclassify read faults as writes or vice versa, causing incorrect permission signals.

Test signals: assemble all including abort handlers, run Thumb `LDRSB` and ARM `LDRD` abort tests, and inspect generated code for correct fallthrough and branch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-macro.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-nommu.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/abort-nommu.S

Purpose: implements the data-abort entry helper for CPUs without a CP15 MMU fault status/address interface.

Important APIs/types/functions: exports `nommu_early_abort`. It clears `r0` and `r1` to represent absent FAR/FSR and branches to `do_DataAbort`.

Control flow: the exception vector enters the helper with `pt_regs`, PC, and PSR already available. Since no MMU fault registers exist, it supplies zero metadata and delegates all handling to the common data-abort path.

State and persistence: no persistent state.

Dependencies and integration points: selected by `CPU_ABRT_NOMMU` for no-MMU CPU models such as ARM9TDMI, ARM940T/946E, and ARMv7-M paths. Integrated with generic data abort dispatch.

Risks: downstream handlers must tolerate missing address/status data. Diagnostics and signal details are necessarily less specific than MMU-backed abort handling.

Test signals: no-MMU boot tests that trigger data aborts, verify no CP15 MMU accesses are emitted, and confirm common fault handling handles zero FAR/FSR without dereferencing invalid metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/abort-nommu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/alignment.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/alignment.c

Purpose: implements ARM alignment fault policy and emulation. It registers the alignment fault handler, exposes `/proc/cpu/alignment`, tracks alignment-fault statistics, decodes ARM/Thumb/Thumb-2 load-store instructions, and either emulates unaligned access, warns, signals userspace, or temporarily disables user alignment traps depending on policy and CPU capability.

Important APIs/types/functions: key state includes `ai_user`, `ai_sys`, `ai_sys_last_pc`, `ai_skipped`, `ai_half`, `ai_word`, `ai_dword`, `ai_multi`, `ai_usermode`, and `cr_no_alignment`. Important functions include `safe_usermode`, `alignment_proc_show`, `alignment_proc_write`, `do_alignment_ldrhstrh`, `do_alignment_ldrdstrd`, `do_alignment_ldrstr`, `do_alignment_ldmstm`, `thumb2arm`, `do_alignment_t32_to_handler`, `alignment_get_arm`, `alignment_get_thumb`, `do_alignment`, `noalign_setup`, and `alignment_init`.

Control flow: `alignment_init` creates the proc entry, applies ARMv6 unaligned-access policy, stores a control-register value with alignment checks disabled, and calls `hook_fault_code` for alignment status codes. On a fault, `do_alignment` fetches the faulting instruction from user or kernel memory, translates Thumb/Thumb-2 forms where needed, decides whether the fault is kernel or user mode, and dispatches to a handler for halfword, word, doubleword, or multiple-register access. Successful emulation updates the saved register frame and advances PC/IT state; faults call `do_bad_area`; unsupported instructions are logged and counted as skipped. User policy determines warn/fixup/signal/ignore behavior.

State and persistence: alignment counters and policy are global kernel state. `ai_usermode` is writable through a core parameter and proc file. The proc interface persists only while the kernel runs. Handler execution mutates `pt_regs` for emulated instructions and may update control register state to disable alignment traps until returning to user mode.

Dependencies and integration points: integrates with ARM CP15 control register helpers, fault dispatch in `fault.c`, procfs, uaccess helpers, instruction opcode conversion helpers, branch predictor hardening, signal delivery, and saved register/IT-state handling. It is selected by `CONFIG_ALIGNMENT_TRAP`.

Risks: instruction emulation must exactly match ARM addressing, writeback, endianness, and user-vs-kernel access semantics. Incorrect emulation can corrupt user registers or memory. Ignoring alignment faults is unsafe on ARMv6+ unaligned-access models because some instructions will refault indefinitely. The proc policy index is used to index `usermode_action`, so accepted values must remain bounded. Kernel-mode alignment faults can expose bugs in low-level code and should not be silently hidden.

Test signals: run userspace tests for unaligned LDR/STR/LDRH/STRH/LDRD/STRD/LDM/STM in ARM, Thumb, and Thumb-2 modes; verify proc counters and mode writes; test `alignment=` and `noalign` boot options; exercise signal mode and fixup mode; test BE and LE builds; and use fault-injection for inaccessible user addresses to confirm `do_bad_area` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/alignment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-b15-rac.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-b15-rac.c

Purpose: manages the Broadcom Brahma-B15/B53 read-ahead cache (RAC), wrapping ARMv7 whole-cache maintenance so operations that are not transparent to the RAC first disable and flush it.

Important APIs/types/functions: key state includes `b15_rac_base`, `rac_lock`, `rac_config0_reg`, `rac_flush_offset`, and `b15_rac_flags` with `RAC_ENABLED` and `RAC_SUSPENDED`. Important functions/macros include `__b15_rac_disable`, `__b15_rac_flush`, `b15_rac_disable_and_flush`, `__b15_rac_enable`, `BUILD_RAC_CACHE_OP`, `b15_flush_kern_cache_all`, `b15_rac_enable`, reboot notifier `b15_rac_reboot_notifier`, CPU hotplug callbacks `b15_rac_dying_cpu` and `b15_rac_dead_cpu`, syscore suspend/resume hooks, and `b15_rac_init`.

Control flow: `arch_initcall` locates the BIU control device-tree node, maps registers, chooses the B15 or B53 flush register from CPU compatibility, registers reboot/hotplug/syscore hooks, verifies RAC starts disabled, enables RAC for possible CPUs, and sets `RAC_ENABLED`. Wrapped cache operations disable and flush RAC under `rac_lock`, call the normal `v7_flush_*` operation, and restore RAC. Hotplug disables RAC before a CPU exits coherency and re-enables it after death; reboot and suspend force a suspended path.

State and persistence: MMIO register mapping and RAC enable bits are runtime global state. `rac_config0_reg` stores the last configuration across hotplug/suspend. Notifier and syscore registrations persist until shutdown.

Dependencies and integration points: depends on device-tree compatible `brcm,brcmstb-cpu-biu-ctrl` and CPU nodes `brcm,brahma-b15` or `brcm,brahma-b53`. It integrates with ARMv7 cache routines, CPU hotplug states, reboot notifier chain, syscore PM, and cache flush call patching through the exported `b15_flush_*` wrappers.

Risks: RAC must be disabled for set/way and all-cache operations that are not transparent; failure causes stale data or instruction fetches. Hotplug/reboot ordering is delicate because RAC spans CPUs and coherency domain exit. The implementation warns and refuses more than four CPUs even though B53 comments mention octo-core flush offset, so platform assumptions must match hardware support.

Test signals: boot on B15/B53 platforms, validate DT matching and register offset, run cache coherency and DMA tests with RAC enabled, exercise `flush_cache_all`, CPU hotplug offline/online, kexec/reboot, and suspend/resume, and confirm no RAC MMIO access occurs before successful mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-b15-rac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-fa.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-fa.S

Purpose: provides Faraday FA520/FA526/FA626 ARMv4-compatible cache maintenance routines for instruction/data cache flushing, coherency, and DMA cache handling.

Important APIs/types/functions: exports `fa_flush_icache_all`, `fa_flush_user_cache_all` aliasing `fa_flush_kern_cache_all`, `fa_flush_kern_cache_all`, `fa_flush_user_cache_range`, `fa_coherent_kern_range`, `fa_coherent_user_range`, `fa_flush_kern_dcache_area`, `fa_dma_flush_range`, `fa_dma_map_area`, and `fa_dma_unmap_area`; internal labels include `__flush_whole_cache`, `fa_dma_inv_range`, and `fa_dma_clean_range`. Constants define 16-byte cache lines, total D-cache size, and range threshold.

Control flow: whole-cache paths invalidate I-cache, clean/invalidate D-cache, invalidate BTB, drain write buffer, and flush prefetch. Range paths compare size against `CACHE_DLIMIT`, otherwise iterate by cache line. Coherency paths clean/invalidate D lines and invalidate I lines. DMA map chooses clean, invalidate, or flush based on DMA direction.

State and persistence: no global writable state. It directly changes CPU cache/BTB/write-buffer state through CP15 operations.

Dependencies and integration points: selected by `CPU_CACHE_FA`, used with FA526 processor support and `proc-macros.S` function pointer tables. Depends on CP15 cache op encodings and VM/DMA direction constants.

Risks: hard-coded cache size differs for Gemini vs other platforms; wrong value changes whole-cache threshold and coverage. DMA invalidation must clean partial lines to avoid discarding unrelated dirty data. Missing barriers or BTB invalidation can break self-modifying code and executable mappings.

Test signals: build FA526/Gemini and non-Gemini variants, run DMA map/unmap coherency tests for all directions, execute self-modifying/JIT code tests, and verify whole-cache threshold behavior for ranges around `CACHE_DLIMIT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-fa.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-feroceon-l2.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-feroceon-l2.c

Purpose: initializes and services the Marvell Feroceon L2 cache controller, including physical-address range maintenance, optional write-through override, prefetch disablement, and L2 enable sequencing.

Important APIs/types/functions: important helpers are `l2_get_va`, `l2_put_va`, `l2_clean_pa`, `l2_clean_pa_range`, `l2_clean_inv_pa`, `l2_inv_pa`, `l2_inv_pa_range`, `l2_inv_all`, `calc_range_end`, `feroceon_l2_inv_range`, `feroceon_l2_clean_range`, `feroceon_l2_flush_range`, `flush_and_disable_dcache`, `invalidate_and_disable_icache`, `disable_l2_prefetch`, `enable_l2`, `feroceon_l2_init`, and `feroceon_of_init`.

Control flow: initialization optionally reads DT for `marvell,kirkwood-cache`/`marvell,feroceon-cache`, applies write-through override, disables L2 prefetch, installs `outer_cache` range callbacks, and enables L2. Enabling L2 temporarily disables L1 D-cache and I-cache as required, invalidates L2, sets the extra-features L2 enable bit, then restores L1 caches.

State and persistence: `l2_wt_override` persists as runtime policy. The `outer_cache` function table is updated globally. CPU extra-feature register bits persist until reset or later firmware/kernel changes.

Dependencies and integration points: depends on Marvell Feroceon CP15 private registers, highmem temporary mappings for physical range ops, device tree, `outer_cache`, and ARM cache flush helpers.

Risks: hardware range operations require start and end within the same page because only the start address is translated. Range operations stall the pipeline, so `MAX_RANGE_SIZE` chunking is performance-critical. Enabling/disabling L1 caches during init is delicate and must run early with IRQ protection.

Test signals: boot on Feroceon/Kirkwood platforms, validate DT write-through bit behavior, run DMA/outer-cache range tests crossing page boundaries, test highmem mappings, and verify L2 enable/disable messages and coherency after suspend or bootloader state variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-feroceon-l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-l2x0-pmu.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-l2x0-pmu.c

Purpose: exposes L220/PL310 L2 cache controller performance counters as a Linux perf PMU using polling because the counters saturate rather than wrap.

Important APIs/types/functions: key state includes `l2x0_base`, `l2x0_pmu`, `pmu_cpu`, `l2x0_name`, `l2x0_pmu_poll_period`, `l2x0_pmu_hrtimer`, and `events[2]`. Important functions include counter MMIO helpers, `l2x0_pmu_event_read`, `l2x0_pmu_event_configure`, `l2x0_pmu_poll`, event start/stop/add/del/init callbacks, group validation, sysfs event attribute handling, `l2x0_pmu_reset`, CPU hotplug migration, `l2x0_pmu_suspend`, `l2x0_pmu_resume`, `l2x0_pmu_register`, and `l2x0_pmu_init`.

Control flow: `l2x0_pmu_register` is called by L2x0 cache initialization to stash MMIO base and choose PMU name from cache part. Later `device_initcall` allocates/registers a `struct pmu`, resets counters, starts CPU hotplug tracking, and registers with perf. Event add allocates one of two counters and starts the hrtimer if it is the first active event. The timer disables counters, reads and resets active events, re-enables counting, and forwards itself.

State and persistence: active perf events are stored in `events`; counter previous values are in each event's `hw.prev_count`; `pmu_cpu` tracks the CPU owning the pinned timer/context. PMU registration and sysfs attributes persist while the kernel runs.

Dependencies and integration points: depends on `CONFIG_PERF_EVENTS`, L2X0 MMIO register definitions, perf core, hrtimer, CPU hotplug, and `cache-l2x0.c` calling `l2x0_pmu_register`.

Risks: counters saturate at `0xffffffff`, so long poll periods lose event counts; the driver warns but cannot recover lost deltas. Only two counters are available, so event groups must be constrained. CPU hotplug migration must keep the pinned hrtimer and perf context on an online CPU. Sampling and task-attached events are rejected because this is a shared uncore-style PMU.

Test signals: perf list should show `l2c_220` or `l2c_310` events, PL310-only events should be hidden on L220, two-counter group constraints should be enforced, CPU hotplug should migrate `cpumask`, suspend/resume should stop and reload events, and stress tests should check saturation warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-l2x0-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-l2x0.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-l2x0.c

Purpose: implements the ARM L2x0 outer-cache controller framework for L2C-210, L2C-220, PL310/L2C-310, Marvell Aurora, Broadcom PL310 variants, and Tauros3. It initializes controllers from platform code or device tree, installs `outer_cache` callbacks, applies errata workarounds, saves registers for resume, and registers PMU support.

Important APIs/types/functions: key data includes `struct l2c_init_data`, global `l2x0_base`, `l2x0_data`, `l2x0_lock`, `l2x0_way_mask`, `l2x0_size`, `sync_reg_offset`, `l2x0_saved_regs`, `l2x0_bresp_disable`, and `l2x0_flz_disable`. Core functions include `l2c_wait_mask`, `l2c_write_sec`, `l2c_enable`, `l2c_disable`, `l2c_resume`, L2C-210/220 range operations, PL310 erratum handlers and config/save/enable/fixup paths, `__l2c_init`, `l2x0_init`, DT parsers `l2x0_of_parse` and `l2c310_of_parse`, Aurora/Broadcom/Tauros3 variant callbacks, and `l2x0_of_init`.

Control flow: platform or DT init maps the controller, chooses an `l2c_init_data`, saves current register state, parses DT properties if the controller is disabled, computes ways and size from AUX/cache ID, copies and patches `outer_cache` callbacks, applies errata or `nosync`, enables the controller if needed, saves final state for resume, logs configuration, and calls `l2x0_pmu_register`. Runtime cache maintenance callbacks perform line, way, or range operations with controller-specific locking and sync behavior. Suspend/resume uses saved registers and PMU suspend/resume.

State and persistence: MMIO base, selected controller data, way mask, size, sync offset, and saved register block are global runtime state. `outer_cache` becomes the global integration point for DMA and cache maintenance. DT-derived aux/prefetch/power/filter settings persist in saved registers and hardware until reset.

Dependencies and integration points: depends on ARM CP15 helpers, device tree, secure register write hooks (`outer_cache.write_sec`), optional platform configure hook, CPU hotplug for PL310 full-line-zero, PMU registration, and hardware headers for L2X0/Aurora/Tauros3. It is selected by `CACHE_L2X0`.

Risks: this file touches secure/non-secure registers and hardware errata. Wrong AUX mask/value handling can corrupt reserved bits or mis-size the cache. Range operations must respect cache-line alignment and controller background-operation constraints. Some systems require disabling outer sync for I/O coherency; enabling it can deadlock on affected platforms. Broadcom address remapping and Aurora page/range limits are SoC-specific and easy to regress.

Test signals: boot and DMA coherency tests on L210, L220, PL310, Aurora, Broadcom, and Tauros3 DTs; suspend/resume register restore checks; errata configuration tests for PL310 revisions; `arm,io-coherent` and `arm,outer-sync-disable` scenarios; CPU hotplug for Cortex-A9 full-line-zero; and perf PMU registration where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-l2x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-nop.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-nop.S

Purpose: provides no-op cache maintenance functions for CPUs or configurations where cache operations should be stubbed out, such as selected ARMv7-M/no-cache paths.

Important APIs/types/functions: exports typed stubs `nop_flush_icache_all`, `nop_flush_kern_cache_all`, `nop_flush_user_cache_all`, `nop_flush_user_cache_range`, `nop_coherent_kern_range`, `nop_coherent_user_range`, `nop_flush_kern_dcache_area`, `nop_dma_flush_range`, `nop_dma_map_area`, and `nop_dma_unmap_area`.

Control flow: every function immediately returns. `nop_coherent_user_range` returns zero in `r0` to match the success convention of user coherency routines.

State and persistence: no state and no hardware side effects.

Dependencies and integration points: selected by `CPU_CACHE_NOP` and used through processor/cache function tables generated with `proc-macros.S`.

Risks: only safe when hardware does not require cache maintenance or when another mechanism handles it. Accidentally selecting this for cached hardware would break DMA coherency, executable mapping coherency, and self-modifying code.

Test signals: verify selected configurations truly have no relevant cache, run DMA and instruction coherency smoke tests on no-cache systems, and inspect processor table wiring so no-op functions are not used by cached CPU models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-nop.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-tauros2.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-tauros2.c

Purpose: initializes Marvell Tauros2 L2 cache support on PJ1/PJ4 CPUs, enabling optional prefetch and burst features and registering outer-cache callbacks for pre-v7 operation modes.

Important APIs/types/functions: important functions include `tauros2_clean_pa`, `tauros2_clean_inv_pa`, `tauros2_inv_pa`, `tauros2_inv_range`, `tauros2_clean_range`, `tauros2_flush_range`, `tauros2_disable`, `tauros2_resume`, `read_extra_features`, `write_extra_features`, `cpuid_scheme`, `read_mmfr3`, `read_actlr`, `write_actlr`, `enable_extra_feature`, `tauros2_internal_init`, and `tauros2_init`. Feature bits include `CACHE_TAUROS2_PREFETCH_ON` and `CACHE_TAUROS2_LINEFILL_BURST8`.

Control flow: public init optionally reads DT compatible `marvell,tauros2-cache` and `marvell,tauros2-cache-features`, then calls internal init. It configures prefetch/burst bits. On ARMv5-like mode it enables L2 through the extra-features register and installs `outer_cache` range/disable/resume callbacks. On ARMv7 hierarchical-cache mode it enables L2 through ACTLR and relies on v7 cache maintenance instead of registering outer callbacks.

State and persistence: no C global state beyond `outer_cache` assignments. CP15 extra-feature and ACTLR bits persist until reset/suspend handling changes them.

Dependencies and integration points: depends on Marvell Tauros2 CP15 registers, CPU ID/MMFR3 detection, device tree, and global `outer_cache`. It is selected by `CACHE_TAUROS2`.

Risks: CPU mode detection is critical: registering outer callbacks on v7 hierarchical systems would duplicate maintenance, while failing to register them on ARMv5 mode would break DMA coherency. DT feature property absence intentionally disables extra features. CP15 register writes are CPU-specific.

Test signals: boot PJ1/PJ4 systems in ARMv5 and ARMv7 personalities, verify feature bits from DT, run DMA range operations on ARMv5 mode, confirm v7 mode uses hierarchical cache ops, and exercise suspend/resume when `outer_cache.resume` is installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-tauros2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-tauros3.h -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-tauros3.h

Purpose: defines Tauros3-specific L2 cache controller register offsets and control bits used by the L2x0 framework.

Important APIs/types/functions: constants include `TAUROS3_EVENT_CNT2_CFG`, `TAUROS3_EVENT_CNT2_VAL`, `TAUROS3_INV_ALL`, `TAUROS3_CLEAN_ALL`, `TAUROS3_AUX2_CTRL`, and `TAUROS3_AUX2_CTRL_LINEFILL_BURST8_EN`.

Control flow: no executable control flow. `cache-l2x0.c` includes this header to save and restore Tauros3 AUX2 and prefetch registers and to describe the Tauros3 variant as PL310-compatible with extensions.

State and persistence: no state. The constants describe MMIO register layout used to access persistent hardware state in the controller.

Dependencies and integration points: included by `cache-l2x0.c`. Integrates Marvell Tauros3 support into the generic L2x0 controller path.

Risks: wrong register offsets would make save/restore or maintenance target the wrong MMIO registers. The header documents that Tauros3 is PL310 r0p0-compatible but has r2p0-style prefetch control and an extra event counter, so generic PL310 assumptions may not cover all behavior.

Test signals: build Tauros3 configurations, verify `cache-l2x0.c` saves/restores AUX2 and prefetch registers, and compare register offsets with platform documentation or hardware bring-up logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-tauros3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-uniphier.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-uniphier.c

Purpose: implements the Socionext UniPhier outer/system cache controller, including multi-level cache discovery, queued range/all maintenance operations, active way setup, enable/disable, and global `outer_cache` callback registration.

Important APIs/types/functions: key type is `struct uniphier_cache_data` with control, revision, operation, and way-control MMIO bases plus way/line/range metadata and list node. Important functions include `__uniphier_cache_sync`, `__uniphier_cache_maint_common`, `__uniphier_cache_maint_all`, `__uniphier_cache_maint_range`, `__uniphier_cache_enable`, `__uniphier_cache_set_active_ways`, `uniphier_cache_inv_range`, `uniphier_cache_clean_range`, `uniphier_cache_flush_range`, `uniphier_cache_flush_all`, `uniphier_cache_disable`, `uniphier_cache_enable`, `uniphier_cache_sync`, `__uniphier_cache_init`, and `uniphier_cache_init`.

Control flow: initialization finds an L2 `socionext,uniphier-system-cache` node, recursively follows next-level cache nodes, validates cache properties, maps control/revision/operation registers, derives way masks and range limits, and appends each level to `uniphier_cache_list`. It registers `outer_cache` callbacks, invalidates all levels, enables each level, and programs active ways per possible CPU. Runtime range operations iterate all cache levels and submit queued operations; all operations sync afterward.

State and persistence: `uniphier_cache_list` persists discovered cache levels and MMIO mappings. Hardware control registers retain enabled state and active-way masks. Allocated `uniphier_cache_data` structures remain for the lifetime of the kernel.

Dependencies and integration points: depends on device tree cache properties (`cache-level`, `cache-unified`, `cache-line-size`, `cache-sets`, `cache-size`), MMIO mapping, Linux list infrastructure, `outer_cache`, and UniPhier hardware queue semantics.

Risks: operation registration relies on hardware arbitration and per-CPU status, so local IRQs are disabled for the command sequence but no global lock is used. `range_op_max_size` is reduced by line size; if not initialized correctly, chunking can underflow. L2 initialization failure is fatal, while later levels are optional, so error handling must preserve usable lower levels. SoC revisions have different active-way register offsets.

Test signals: boot UniPhier boards with single and multi-level caches, validate DT property errors, run DMA coherency tests across ranges larger than the queue max, exercise all-cache flush/invalidate paths, and test disable paths during shutdown or power management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-uniphier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4.S

Purpose: provides baseline ARMv4 cache maintenance routines for simple or no-cache ARMv4 systems, with optional CP15 whole-cache flush support.

Important APIs/types/functions: exports `v4_flush_icache_all`, `v4_flush_user_cache_all` aliasing `v4_flush_kern_cache_all`, `v4_flush_kern_cache_all`, `v4_flush_user_cache_range`, `v4_coherent_kern_range`, `v4_coherent_user_range`, `v4_flush_kern_dcache_area`, `v4_dma_flush_range`, `v4_dma_unmap_area`, and `v4_dma_map_area`.

Control flow: many operations are no-ops unless `CONFIG_CPU_CP15` is enabled. CP15 paths use `mcr p15, 0, r0, c7, c7, 0` to flush ID cache. DMA unmap flushes for non-`DMA_TO_DEVICE`, while DMA map does nothing.

State and persistence: no software state. Hardware cache state is invalidated/flushed through CP15 when present.

Dependencies and integration points: selected by `CPU_CACHE_V4`, used by ARM7TDMI/ARM740T/ARM9TDMI and similar configurations through cache function tables.

Risks: this is intentionally coarse. Whole-cache operations may be overkill for range requests but safe for simple legacy caches. Selecting it for CPUs requiring line-level writeback or Harvard coherency would be incorrect.

Test signals: build no-CP15 and CP15 variants, run DMA map/unmap smoke tests, verify self-modifying code behavior on systems with I/D cache, and ensure no unsupported CP15 instructions execute on no-CP15 cores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4wb.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4wb.S

Purpose: implements ARMv4 write-back data-cache maintenance for StrongARM SA110/SA1100-style processors, including whole-cache cleaning via the `FLUSH_BASE` alias trick and DMA coherency routines.

Important APIs/types/functions: exports `v4wb_flush_icache_all`, `v4wb_flush_user_cache_all`, `v4wb_flush_kern_cache_all`, `v4wb_flush_user_cache_range`, `v4wb_flush_kern_dcache_area`, `v4wb_coherent_kern_range`, `v4wb_coherent_user_range`, `v4wb_dma_flush_range`, `v4wb_dma_map_area`, and `v4wb_dma_unmap_area`; internal labels include `flush_base`, `__flush_whole_cache`, `v4wb_dma_inv_range`, and `v4wb_dma_clean_range`.

Control flow: whole-cache flush toggles `flush_base`, reads through a cache-sized region to force dirty eviction, optionally handles mini-cache, then drains the write buffer. Range flushing cleans and invalidates line by line unless the range exceeds `CACHE_DLIMIT`. Coherency paths clean/invalidate D lines, invalidate I-cache, and drain write buffer. DMA map chooses clean/invalidate/flush by direction; unmap is a no-op.

State and persistence: `flush_base` is a small writable data word tracking the alias base used for whole-cache flushes. Hardware cache and write-buffer state are modified directly by CP15 operations.

Dependencies and integration points: selected by `CPU_CACHE_V4WB`, used by SA110/SA1100 and v4 write-back configurations. Depends on `FLUSH_BASE`, optional `FLUSH_BASE_MINICACHE`, CP15 line operations, and DMA direction constants.

Risks: cache size is compile-time selected for SA110 vs SA1100; wrong selection causes incomplete or wasteful flushes. Partial-line DMA invalidation must clean endpoints to avoid losing dirty unrelated data. The whole-cache alias method depends on correct platform mapping of `FLUSH_BASE`.

Test signals: SA110 and SA1100 build/boot tests, DMA direction tests with unaligned buffers, mini-cache configurations if present, executable mapping coherency tests, and stress around ranges just below/above `CACHE_DLIMIT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4wb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4wt.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4wt.S

Purpose: implements ARMv4 write-through cache maintenance for CPUs such as ARM920T/922T/925T/1020-style configurations, assuming the write buffer is not enabled.

Important APIs/types/functions: exports `v4wt_flush_icache_all`, `v4wt_flush_user_cache_all`, `v4wt_flush_kern_cache_all`, `v4wt_flush_user_cache_range`, `v4wt_coherent_kern_range`, `v4wt_coherent_user_range`, `v4wt_flush_kern_dcache_area`, `v4wt_dma_flush_range`, `v4wt_dma_unmap_area`, and `v4wt_dma_map_area`; internal label `v4wt_dma_inv_range` performs line invalidation.

Control flow: whole-cache paths invalidate I-cache when executable and invalidate D-cache. Range paths either switch to whole-cache operation or iterate line by line invalidating D-cache and optionally I-cache. Coherency invalidates I-cache lines. DMA map is a no-op; unmap invalidates for non-`DMA_TO_DEVICE`; flush aliases to invalidate because data is write-through.

State and persistence: no software state. CP15 operations mutate cache state.

Dependencies and integration points: selected by `CPU_CACHE_V4WT`. Integrated through ARM cache function tables and DMA mapping code.

Risks: comments assume no write buffer, which is essential for treating flush as invalidate. If hardware has dirty buffered data, this implementation could lose coherency. Whole-cache threshold is marked as needing benchmarking.

Test signals: boot write-through v4 CPUs, DMA tests for all directions with unaligned buffers, executable mapping coherency tests, and validation that write-buffer assumptions hold for selected CPU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4wt.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v6.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v6.S

Purpose: provides ARMv6 VIPT cache maintenance, I-cache invalidation, D-cache cleaning/invalidation, executable coherency, and DMA map/unmap routines.

Important APIs/types/functions: exports `v6_flush_icache_all`, `v6_flush_kern_cache_all`, `v6_flush_user_cache_all`, `v6_flush_user_cache_range`, `v6_coherent_kern_range`, `v6_coherent_user_range`, `v6_flush_kern_dcache_area`, `v6_dma_flush_range`, `v6_dma_map_area`, and `v6_dma_unmap_area`; internal labels include `v6_dma_inv_range` and `v6_dma_clean_range`.

Control flow: full kernel cache flush cleans/invalidates D-cache then invalidates I-cache. User cache all/range are no-ops because VIPT assumptions avoid per-address flush for normal user mappings. Coherency cleans D lines to PoU, drains, invalidates I lines, and returns `-EFAULT` if user line operations fault. DMA map selects invalidate for `DMA_FROM_DEVICE` and clean otherwise; unmap invalidates unless direction is `DMA_TO_DEVICE`.

State and persistence: no C-level state. It modifies cache and write-buffer state via CP15 and barriers.

Dependencies and integration points: selected by `CPU_CACHE_V6`, uses ARMv6 CP15 cache operations, `USER()` fixup tables, `asm/unwind`, and DMA direction constants.

Risks: VIPT assumptions and fixed 32-byte line size must match selected hardware. DMA invalidation must clean partial first/last lines. User coherency paths must return `-EFAULT` on unmapped addresses rather than faulting in kernel mode.

Test signals: ARMv6 executable mapping/JIT tests, DMA coherency with aligned and unaligned buffers, user address fault tests for `coherent_user_range`, and SMP/UP variants where selected by Kconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v6.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v7.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v7.S

Purpose: implements ARMv7 cache maintenance using hierarchical cache discovery, set/way loops, point-of-unification operations, DMA maintenance, branch predictor invalidation, and erratum-aware barriers.

Important APIs/types/functions: exports `v7_invalidate_l1`, `v7_flush_icache_all`, `v7_flush_dcache_louis`, `v7_flush_dcache_all`, `v7_flush_kern_cache_all`, `v7_flush_kern_cache_louis`, `v7_flush_user_cache_all`, `v7_flush_user_cache_range`, `v7_coherent_kern_range`, `v7_coherent_user_range`, `v7_flush_kern_dcache_area`, `v7_dma_flush_range`, `v7_dma_map_area`, and `v7_dma_unmap_area`; internal DMA helpers are `v7_dma_inv_range` and `v7_dma_clean_range`. Optional `icache_size` supports `CONFIG_CPU_ICACHE_MISMATCH_WORKAROUND`.

Control flow: set/way routines read CLIDR/CSIDR, iterate cache levels, ways, and sets, and restore cache selector state. Kernel whole-cache flush cleans/invalidates D-cache then invalidates I-cache and BTB. Coherency cleans D lines to PoU, invalidates I lines, invalidates BTB, and returns `-EFAULT` if user line ops fault. DMA map/unmap dispatch based on DMA direction with endpoint cleaning for partial invalidation.

State and persistence: optional `icache_size` stores a workaround line size. Otherwise no software state. Hardware cache selector register and cache/BTB state are changed transiently; barriers ensure ordering.

Dependencies and integration points: selected by `CPU_CACHE_V7`, integrated with SMP alternatives (`ALT_SMP`/`ALT_UP`), preemption IRQ save around CSSR/CSIDR, errata configs `643719`, `764369`, `775420`, `814220`, and `proc-macros.S`.

Risks: set/way operations are sensitive to preemption because CSIDR describes the selected cache level. Errata barriers and LoUIS/LoUU handling are hardware-specific. User cache operations must not leave faults unhandled. Incorrect line-size detection breaks all range operations.

Test signals: ARMv7 SMP/UP boot tests, CPU hotplug, DMA coherency with unaligned buffers, self-modifying/JIT code, user fault injection in coherency paths, errata-specific builds, and systems with mismatched I-cache line sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v7m.S -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v7m.S

Purpose: implements ARMv7-M cache maintenance through memory-mapped System Control Block registers instead of CP15 instructions, covering whole-cache, coherency, and DMA operations.

Important APIs/types/functions: defines macros `v7m_cache_read`, `v7m_cacheop`, `read_ccsidr`, `read_clidr`, `write_csselr`, `dcisw`, `dccisw`, `dccimvac`, `dcimvac`, `dccmvau`, `dccmvac`, `icimvau`, `invalidate_icache`, and `invalidate_bp`. Exports `v7m_invalidate_l1`, `v7m_flush_icache_all`, `v7m_flush_dcache_all`, `v7m_flush_kern_cache_all`, `v7m_flush_user_cache_all`, `v7m_flush_user_cache_range`, `v7m_coherent_kern_range`, `v7m_coherent_user_range`, `v7m_flush_kern_dcache_area`, `v7m_dma_flush_range`, `v7m_dma_map_area`, and `v7m_dma_unmap_area`; internal helpers are `v7m_dma_inv_range` and `v7m_dma_clean_range`.

Control flow: whole-cache routines read CLIDR/CCSIDR through SCB registers, select cache levels, and loop set/way maintenance via memory-mapped operation registers. Coherency cleans D lines to PoU, invalidates I lines to PoU, invalidates branch predictor, and barriers. DMA map/unmap mirrors v7 semantics using SCB clean/invalidate registers.

State and persistence: no software state. It writes memory-mapped cache operation registers under `BASEADDR_V7M_SCB`, changing cache state and selector state.

Dependencies and integration points: selected by `CPU_CACHE_V7M`, depends on `asm/v7m.h` SCB register offsets, `proc-macros.S`, and ARMv7-M architecture mode. It is often paired with `CPU_CACHE_NOP` for cases where some operations are stubs.

Risks: memory-mapped cache operations can corrupt temporary registers used in macro expansion; the code explicitly handles this in partial-line invalidation. Unlike CP15 `USER()` handling, v7-M open-coded ops must avoid placing fault fixups on the wrong instruction. Register offsets must match the SCB implementation.

Test signals: Cortex-M cache-enabled boot tests, SCB register access validation, DMA coherency with unaligned endpoints, self-modifying code tests, and no-MMU/MPU configurations selecting ARMv7-M.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-v7m.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-xsc3l2.c -->
# sources/distributed-fs/ceph-client/arch/arm/mm/cache-xsc3l2.c

Purpose: implements XScale3 L2 cache maintenance and registration for systems where the XSC3 L2 cache is present and enabled.

Important APIs/types/functions: important helpers include `xsc3_l2_present`, `xsc3_l2_clean_mva`, `xsc3_l2_inv_mva`, `xsc3_l2_inv_all`, `l2_map_va`, `l2_unmap_va`, `xsc3_l2_inv_range`, `xsc3_l2_clean_range`, `xsc3_l2_flush_all`, `xsc3_l2_flush_range`, and initcall `xsc3_l2_init`. Constants define L2 enable bit `CR_L2`, 32-byte lines, and set/way sizing from L2 type.

Control flow: `core_initcall` checks CPU type and L2 presence. If CR_L2 is set, it invalidates all L2 and installs `outer_cache` range callbacks. Runtime range operations map physical addresses to virtual addresses when highmem is enabled because XScale3 cache ops use MVA, then perform clean/invalidate by line or set/way for all-cache sentinel ranges.

State and persistence: no global C state beyond `outer_cache` assignment. Highmem mappings are transient per operation. Hardware L2 state persists until cache operations or reset.

Dependencies and integration points: selected by `CACHE_XSC3L2`, depends on XScale3 CP15 private cache registers, `cpu_is_xsc3`, highmem `kmap_atomic_pfn`, and global `outer_cache`.

Risks: cache maintenance uses MVA rather than PA, requiring correct highmem temporary mappings and unmapping. The all-cache sentinel is `start == 0 && end == -1ul`; callers must use it intentionally. If L2 is present but CR_L2 is disabled, callbacks are not installed.

Test signals: boot XScale3 with L2 enabled and disabled, run highmem and lowmem DMA coherency tests, verify all-cache flush/invalidate sentinel behavior, and compare set/way loops against detected L2 type size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache-xsc3l2.c -->
