# subset-b-000680 research

This grouped report covers the arm64 kernel files requested for `subset-b-000680`. Each section is source-tree aligned and bounded by the markers used by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/fpsimd.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/fpsimd.c

Purpose: Implements arm64 floating point, Advanced SIMD, SVE, SME, FPMR, kernel NEON, EFI FP, CPU PM, and hotplug state management. The file's central design is lazy ownership of vector registers: each task records the last CPU holding its state, and each CPU records the last bound `cpu_fp_state` in `fpsimd_last_state`.

Important APIs and state: exported entry points include `cpu_enable_fpsimd()`, `cpu_enable_sve()`, `cpu_enable_sme()`, `fpsimd_thread_switch()`, `fpsimd_restore_current_state()`, `fpsimd_flush_thread()`, `fpsimd_preserve_current_state()`, `kernel_neon_begin/end()`, SVE/SME prctl helpers, and trap handlers `do_sve_acc()`, `do_sme_acc()`, `do_fpsimd_acc()`, `do_fpsimd_exc()`. State lives in `task->thread` fields (`uw.fpsimd_state`, `sve_state`, `sme_state`, `svcr`, VL arrays, `fp_type`, `fpsimd_cpu`) plus per-CPU `fpsimd_last_state` and global `vl_info` / `vl_config`.

Control flow: context switch saves current user or kernel FP state, then marks the next task foreign unless the CPU already contains its valid state. Return-to-user loads only when `TIF_FOREIGN_FPSTATE` is set. SVE/SME traps allocate backing storage, migrate FPSIMD into vector state, set task flags, and disable user traps. Vector length changes allocate replacement buffers first, flush live state, preserve the effective FPSIMD subset, then replace buffers.

Dependencies and integration: integrates with cpufeature, syscall/prctl ABI, signal frame formats, KVM guest FP binding, EFI runtime calls, CPU PM notifiers, hotplug callbacks, KASAN/MTE-adjacent state, and arch exception entry. The code relies on precise preemption, IRQ, and softirq exclusion via `get_cpu_fpsimd_context()`.

Risks and test signals: high risk areas are lazy state corruption, SVE/SME VL mismatch, allocation failure on trap, PREEMPT_RT differences, nested kernel NEON, EFI hardirq/NMI use, and CPU suspend loss of registers. Test signals include SVE/SME prctl and ptrace ABI tests, context-switch stress with signal delivery, KVM FP tests, kernel crypto NEON tests, CPU hotplug/suspend, EFI runtime smoke tests, and fault injection around allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/fpsimd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/ftrace.c

Purpose: Provides arm64 dynamic ftrace text patching, callsite address adjustment, module PLT fallback, call-ops literal management, and function graph return rewriting.

Important APIs and state: main functions are `ftrace_call_adjust()`, `arch_ftrace_get_symaddr()`, `ftrace_make_call()`, `ftrace_make_nop()`, `ftrace_modify_call()`, `ftrace_init_nop()`, `arch_ftrace_update_code()`, `prepare_ftrace_return()`, `ftrace_graph_func()`, and graph caller enable/disable helpers. With dynamic call ops, each callsite stores an `ftrace_ops` literal near the patch site and updates it via `aarch64_insn_write_literal_u64()`.

Control flow: ftrace normalizes compiler patchable-entry locations, accounting for pre-function NOPs and optional BTI. Enabling tracing writes a per-site ops literal, finds a branch target reachable by `BL`, uses module ftrace PLTs if necessary, then validates and patches a NOP into a branch. Disabling reverses the branch to NOP. Graph tracing replaces the saved LR with `return_to_handler` after `function_graph_enter*()` accepts the call.

Dependencies and integration: depends on `asm/insn.h`, `asm/text-patching.h`, module PLT allocation, `entry-ftrace.S` symbols, BTI configuration, and ftrace core locking. Module integration uses `get_ftrace_plt()` for core and init text trampoline slots.

Risks and test signals: primary risks are wrong patch-site adjustment with BTI/call-ops, out-of-range module branch without PLT, stale ops literals, and validating against the wrong old instruction. Test with dynamic ftrace enable/disable, function graph tracer, direct trampolines, modules loaded far from core text, BTI kernels, and tracing selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/head.S

Purpose: Contains the low-level arm64 kernel image header, primary boot entry, secondary CPU entry, exception-level setup, MMU enabling, and handoff to C boot code.

Important symbols and routines: `primary_entry`, `record_mmu_state`, `preserve_boot_args`, `init_kernel_el`, `secondary_holding_pen`, `secondary_entry`, `secondary_startup`, `__enable_mmu`, `__primary_switch`, `__primary_switched`, and `__secondary_switched`. It emits the boot loader Image header and EFI PE header and uses the `init_cpu_task` macro to establish task, stack, frame record, shadow call stack, and per-CPU offset.

Control flow: the primary CPU records whether it entered with MMU/cache enabled, preserves x0-x3 boot args, creates an initial idmap via PI code, performs cache maintenance depending on entry state, initializes EL1/EL2 state, runs `__cpu_setup()`, enables the MMU, calls `__pi_early_map_kernel()` to map/relocate, then branches to `start_kernel()`. Secondary CPUs initialize EL state, verify VA support when needed, enable the MMU with idmap/swapper tables, set boot mode, install vectors, initialize task context, and enter `secondary_start_kernel()`.

Dependencies and integration: tightly coupled to linker symbols, page table layout, `arch/arm64/mm/proc.S`, hypervisor stub vectors, KASAN early init, KASLR PI mapping code, CPU boot mode flags, SMP holding pen, shadow call stack, pointer authentication, and EFI header generation.

Risks and test signals: risks include wrong endian/MMU state handling, insufficient cache maintenance before MMU-off execution, unsupported granule detection, EL2/VHE misconfiguration, broken early FDT preservation, and secondary CPU parking. Test signals are early boot across EL1/EL2/VHE/nVHE, big-endian builds, KASLR/relocatable kernels, 52-bit VA/LPA2 hardware, SMP bring-up, and bootloader Image header validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/hibernate-asm.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/hibernate-asm.S

Purpose: Provides the copied-to-safe-page hibernation resume exit routine that restores memory contents and returns through the saved CPU resume path.

Important symbol: `swsusp_arch_suspend_exit` in `.hibernate_exit.text`. It receives temporary page table addresses, the restored kernel's swapper table, `cpu_resume`, the restore page list, optional hyp stub vector address, and a zero page for break-before-make TTBR switching.

Control flow: the routine switches TTBR1 to a temporary copied linear map, iterates `restore_pblist`, copies each saved page back to its original address with the assembly `copy_page` macro, cleans each restored page to PoU, waits for cache maintenance, switches TTBR1 to the restored kernel tables, invalidates instruction cache, optionally HVCs into the restored EL2 stub, and returns to `cpu_resume`.

Dependencies and integration: called from `hibernate.c` after being copied by `create_safe_exec_page()`. It depends on hibernation PBE offsets, break-before-make TTBR macros, cache maintenance alternatives, EL2 stub vectors from `hyp-stub.S`, and the invariant that it cannot call PC-relative external routines while memory is being overwritten.

Risks and test signals: risks include self-overwrite, stale I-cache after restoring text, missing EL2 reinitialization, wrong PBE traversal, and TTBR switch ordering. Test with hibernate/resume under KASLR, nVHE, VHE, 4K/16K/64K pages, modules loaded, and CPU hotplug around suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/hibernate-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/hibernate.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/hibernate.c

Purpose: Implements arm64 architecture hibernation support, including image header invariants, nosave page filtering, temporary executable resume mapping, crashkernel preservation, MTE tag save/restore, and CPU selection for resume.

Important APIs and state: exports `arch_hibernation_header_save()` and `arch_hibernation_header_restore()`. Other entry points include `pfn_is_nosave()`, `swsusp_arch_suspend()`, `swsusp_arch_resume()`, and `hibernate_resume_nonboot_cpu_disable()`. Persistent image state is captured in `resume_hdr`, including `ttbr1_el1`, `reenter_kernel`, `__hyp_stub_vectors`, and `sleep_cpu_mpidr`; live local state includes `sleep_cpu` and optional MTE tag storage in `mte_pages`.

Control flow: suspend checks CPUs can be offlined, enters `__cpu_suspend_enter()`, prepares crash dump memory, saves MTE tags, records the suspend CPU, and calls `swsusp_save()`. On resume return, it cleans restored critical text, restores MTE tags, reprotects crash memory, clears `in_suspend`, exits CPU suspend, and restores mitigations. Resume builds a temporary linear map, allocates a zero page, optionally copies EL2 vectors, copies hibernate exit code to a safe executable page, installs temporary vectors, and jumps to `swsusp_arch_suspend_exit()`.

Dependencies and integration: integrated with generic swsusp, kexec crash resources, KVM/nVHE EL2 handling, trans_pgd temporary page tables, CPU hotplug, MTE, cache maintenance, and UTS version invariants.

Risks and test signals: key risks are resuming a different kernel, wrong CPU MPIDR, missing nosave/crash exclusions, losing MTE allocation failures, KASLR relocation mismatch, and EL2 vector handling. Test with hibernate image validation, crashkernel plus hibernate, MTE tagged memory, KASLR enabled/disabled, CPU hotplug, and nVHE KVM loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/hibernate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/hw_breakpoint.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/hw_breakpoint.c

Purpose: Implements arm64 hardware breakpoint/watchpoint support for perf, ptrace, kernel debugging, CPU suspend restore, and exception handling.

Important APIs and state: per-CPU `bp_on_reg[]`, `wp_on_reg[]`, and `stepping_kernel_bp` track register ownership and single-step state. Global `core_num_brps` / `core_num_wrps` cache register counts. Entry points include `hw_breakpoint_slots()`, `arch_install_hw_breakpoint()`, `arch_uninstall_hw_breakpoint()`, `hw_breakpoint_arch_parse()`, `arch_bp_generic_fields()`, `do_breakpoint()`, `do_watchpoint()`, `try_step_suspended_breakpoints()`, `hw_breakpoint_thread_switch()`, and `hw_breakpoint_reset()`.

Control flow: install/uninstall allocates a slot, enables/disables debug monitors for EL0 or EL1, writes address and control registers, and respects per-task disabled flags. Attribute parsing maps generic perf breakpoint types and lengths into arch encodings, aligns addresses, handles compat tasks, and rejects per-task kernel breakpoints. Exception handlers match trigger addresses, report perf events, disable matching registers, and single-step past the trapped instruction before restoring the registers.

Dependencies and integration: uses debug monitor sysregs, perf breakpoint core, task `debug_info`, ptrace compat state, CPU hotplug, CPU suspend debug restorer hooks, and kprobes restrictions (`NOKPROBE_SYMBOL`).

Risks and test signals: risks are slot leaks, stale per-CPU register programming after CPU PM, imprecise watchpoint address attribution, nested single-step conflicts, compat alignment mistakes, and kernel/user privilege confusion. Test with perf breakpoints/watchpoints, ptrace hardware debug, CPU hotplug/suspend, compat AArch32 watchpoints, overlapping watchpoints, and kernel breakpoint stepping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/hw_breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/hyp-stub.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/hyp-stub.S

Purpose: Supplies the minimal EL2 hypervisor stub vectors used before KVM installs its own hyp code and during EL2 finalization/resume.

Important symbols: `__hyp_stub_vectors`, `elx_sync`, `__finalise_el2`, `enter_vhe`, `__hyp_set_vectors`, `__hyp_reset_vectors`, and `finalise_el2`. The vector table handles selected HVC commands: set vectors, reset vectors, finalize EL2, read `ICH_VTR_EL2`, and soft restart.

Control flow: synchronous EL2/EL1 entries dispatch on x0 command. `__finalise_el2` checks MMU-off state and VHE capability/overrides, transfers EL1 system state to EL2, configures HCR for VHE, copies stack/percpu/FP/vector/MMU state, rewrites return state to EL2h, and enters `enter_vhe` in idmap text. `__hyp_set_vectors()` and `__hyp_reset_vectors()` are thin HVC wrappers.

Dependencies and integration: used by `head.S`, KVM hyp initialization, hibernation, kexec, and soft restart. It depends on EL2 setup macros, feature override storage, KVM ABI command constants, and idmapped execution for enabling VHE translations.

Risks and test signals: risks include finalizing EL2 with MMU still on, losing system register state when switching to VHE, wrong vector alignment, unexpected `kvm_call_hyp()` against the stub, and broken hibernate/kexec EL2 recovery. Test EL1 boot, EL2 nVHE boot, VHE finalization, KVM load/unload, kexec, hibernate, and protected/nVHE command-line overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/hyp-stub.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/idle.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/idle.c

Purpose: Provides the default low-level arm64 idle path around `wfi`.

Important APIs: `cpu_do_idle()` saves interrupt-priority masking context, executes `dsb(sy)` and `wfi`, then restores the context. `arch_cpu_idle()` delegates to `cpu_do_idle()`.

Control flow and state: no persistent state is stored in this file. The temporary `arm_cpuidle_irq_context` preserves interrupt controller priority masking state so a CPU using priority masking can still wake from interrupts.

Dependencies and integration: integrates with the generic idle loop, arm64 cpuidle helpers, IRQ flags, barrier semantics, cpufeature/sysreg support, and any platform cpuidle driver that falls back to the arch default idle handler.

Risks and test signals: risks are failing to unmask the wake signal in PMR-backed interrupt priority masking or missing the barrier before WFI. Test with idle loop stress, tickless idle, systems using GIC priority masking, suspend-to-idle, and interrupt wake latency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/image-vars.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/image-vars.h

Purpose: Defines linker-script symbols and aliases needed after section layout resolution for the arm64 kernel image, EFI stub, PI startup code, and nVHE KVM code.

Important macros and symbols: `PI_EXPORT_SYM()` publishes selected kernel symbols as `__pi_*` aliases and asserts they are not BSS. The file provides EFI aliases such as `__efistub_primary_entry`, `__efistub__text`, and `__efistub_caches_clean_inval_pou`, PI libc aliases, feature override aliases, page table aliases, and many `KVM_NVHE_ALIAS*` entries under `CONFIG_KVM`. It also defines `kimage_limit` to avoid LLD convergence issues.

Control flow and persistence: this is linker-time metadata, not runtime code. Its effects persist in the final vmlinux symbol table and govern what early PI/EFI/nVHE code can legally reference.

Dependencies and integration: included only by `vmlinux.lds.S` with `LINKER_SCRIPT` defined. It depends on linker symbols from the arm64 memory layout, EFI stub namespace rules, KVM nVHE namespace isolation, and LLD version behavior.

Risks and test signals: risks are exporting unsafe BSS symbols to PI code, missing aliases after symbol renames, broken nVHE linking, and LLD script regressions. Test with full arm64 links under GNU ld and LLD, EFI boot builds, KVM nVHE builds, relocation/KASLR builds, and link-time assertion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/image-vars.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/image.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/image.h

Purpose: Supplies linker-script macros for emitting little-endian arm64 Image header fields regardless of kernel endianness.

Important macros: `DATA_LE32()` endian-swaps 32-bit fields for big-endian builds. `DEFINE_IMAGE_LE64()` splits a 64-bit link-time value into little-endian lo/hi words. `__HEAD_FLAG*` encodes endianness, page size, and physical placement flags. `HEAD_SYMBOLS` emits `_kernel_size_le` and `_kernel_flags_le`.

Control flow and state: no runtime control flow. The macros determine header fields consumed by bootloaders and kexec image validation. Splitting values avoids unsuitable absolute 64-bit relocations in PIE/KASLR builds.

Dependencies and integration: included only from the linker script, depends on `<asm/image.h>`, `PAGE_SHIFT`, `_text`, `_end`, and arm64 boot protocol flag definitions. `head.S` references the generated symbols in the Image header.

Risks and test signals: risks are wrong endian encoding, wrong page-size flag, or relocation forms incompatible with PIE. Test with big-endian and little-endian builds, 4K/16K/64K page configurations, `file`/bootloader header inspection, and kexec image loader validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/image.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/io.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/io.c

Purpose: Implements optimized aligned MMIO copy helpers for 64-bit and 32-bit full-width writes.

Important APIs: `__iowrite64_copy_full()` and `__iowrite32_copy_full()` are exported. The `memcpy_toio_aligned()` macro batches copies in groups of eight, four, two, and one element and calls constant-sized aligned MMIO helper routines.

Control flow and state: functions copy a caller-provided count of 64-bit or 32-bit quantities to an I/O memory address, then issue `dgh()` to provide a data gathering hint barrier. No persistent state exists.

Dependencies and integration: integrates with generic Linux I/O helpers and drivers that need posted/write-combining-friendly bulk MMIO writes. Requires aligned source/destination expectations implied by the full-copy helper name.

Risks and test signals: risks include callers passing unaligned addresses, incorrect count units, or devices requiring stricter barriers. Test with driver MMIO copy users, sparse `__iomem` checks, KASAN/KMSAN where applicable, and device-level DMA/MMIO functional tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/irq.c

Purpose: Initializes arm64 IRQ infrastructure, per-CPU IRQ stacks, optional shadow call stacks, root IRQ/FIQ handlers, and softirq-on-own-stack support.

Important APIs and state: per-CPU `nmi_contexts`, `irq_stack_ptr`, and optional `irq_shadow_call_stack_ptr` hold interrupt execution context. `handle_arch_irq` and `handle_arch_fiq` are `__ro_after_init` function pointers initialized to panic defaults. APIs include `set_handle_irq()`, `set_handle_fiq()`, `init_IRQ()`, and `do_softirq_own_stack()`.

Control flow: `init_IRQ()` allocates IRQ stacks, allocates IRQ shadow call stacks when enabled, calls `irqchip_init()`, and adjusts DAIF/PMR state for priority masking. Root handlers can be installed only once; otherwise registration returns `-EBUSY`.

Dependencies and integration: depends on irqchip drivers, stacktrace/vmap stack helpers, shadow call stack allocation, softirq stack assembly helper `call_on_irq_stack()`, NUMA early CPU-to-node mapping, and GIC priority masking cpufeatures.

Risks and test signals: risks include missing IRQ stack allocation, double root handler registration, priority mask left blocking wakeups, and SCS stack exhaustion. Test with boot IRQ init, interrupt flood, softirq stress, FIQ handler registration where available, vmap stack debug, and priority masking configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/jump_label.c

Purpose: Implements arm64 static key jump label patching.

Important APIs: `arch_jump_label_transform_queue()` turns a jump-label site into either an unconditional branch to `jump_entry_target()` or a NOP. `arch_jump_label_transform_apply()` calls `kick_all_cpus_sync()` after queued nosync patches.

Control flow and state: each transformation computes the new instruction with `aarch64_insn_gen_branch_imm()` or `aarch64_insn_gen_nop()`, then patches text via `aarch64_insn_patch_text_nosync()`. No file-local persistent state exists.

Dependencies and integration: depends on generic jump label/static key core, arm64 instruction encoding, and text patching. It assumes branch range is representable for jump label sites generated by the build.

Risks and test signals: risks are invalid branch range, patching while CPUs execute stale code, or missing synchronization after queued changes. Test with static key selftests, dynamic enabling/disabling of tracepoints and paravirt/static branches, CPU hotplug during toggles, and lockdep/static key stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/kaslr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/kaslr.c

Purpose: Publishes whether runtime arm64 KASLR is enabled after early PI mapping has selected any offset.

Important APIs and state: `__kaslr_is_enabled` is `__ro_after_init`. `kaslr_init()` evaluates command-line disablement and `kaslr_offset()`. `parse_nokaslr()` exists only so early cpufeature parsing can own the real `nokaslr` handling.

Control flow: if `nokaslr` was parsed, log disabled. If the offset is less than `MIN_KIMG_ALIGN`, treat it as lacking a seed and disable. Otherwise log enabled and set `__kaslr_is_enabled = true`.

Dependencies and integration: depends on early PI KASLR seed handling in `pi/kaslr_early.c`, feature override command-line parsing, and memory layout helpers. Consumers use the exported state to decide whether the kernel image was randomized.

Risks and test signals: risks are false positives when physical placement contributes low offset bits, mismatched early/late command-line interpretation, or misleading logs. Test with `nokaslr`, missing seed, FDT seed, RNDR seed, and KASLR offset inspection in boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/kaslr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/kexec_image.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/kexec_image.c

Purpose: Implements the arm64 `Image` format loader for `kexec_file_load`.

Important APIs: static `image_probe()` validates the arm64 magic and buffer size. `image_load()` validates a nonzero image size, endian compatibility, page-size granule support, loads the kernel segment with `TEXT_OFFSET`, and delegates initrd/DTB/crash segments to `load_other_segments()`. `kexec_image_ops` exposes probe/load and optional PE signature verification.

Control flow: the loader repeatedly tries to place the kernel segment, then attempts to place dependent segments. If dependent placement fails, it removes the kernel segment, advances the minimum address, and retries. On success it adjusts the visible segment start/memsz by `text_offset` and sets `image->start`.

Dependencies and integration: depends on arm64 Image header definitions, cpufeature granule checks, kexec buffer placement, `machine_kexec_file.c` helpers, optional PE signature verification, and `kexec-tools` expectations for direct kernel entry.

Risks and test signals: risks are accepting incompatible endian/page-size images, mishandling text offset, exhausting placement holes, or leaking segments after retries. Test with signed/unsigned Image loads, all page sizes, mixed-endian capability, initrd/DTB placement pressure, and crash/non-crash kexec_file paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/kexec_image.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/kgdb.c

Purpose: Provides arm64 KGDB register mapping, breakpoint patching, exception handling, single-step control, and die notifier integration.

Important APIs and state: `dbg_reg_def[]` maps GDB remote registers to `pt_regs` offsets, with vector registers stubbed as zero. Entry points include `dbg_get_reg()`, `dbg_set_reg()`, `sleeping_thread_to_gdb_regs()`, `kgdb_arch_set_pc()`, `kgdb_arch_handle_exception()`, breakpoint handlers, `kgdb_arch_init/exit()`, and `kgdb_arch_set/remove_breakpoint()`. `compiled_break` tracks compiled breakpoint PC adjustment.

Control flow: continue/detach/kill packets update PC if supplied, clear single-step state, and disable kernel single-step. Step packets update PC, set `kgdb_cpu_doing_single_step`, and enable or rewind kernel single-step. Breakpoint handlers invoke `kgdb_handle_exception()` and return handled. Dynamic KGDB breakpoints read the saved instruction and patch an AArch64 break instruction via text patching.

Dependencies and integration: depends on debug monitors, die notifiers, `asm/text-patching.h`, KGDB core, `pt_regs`, and kernel single-step helpers. `NOKPROBE_SYMBOL` avoids recursive probing of handlers.

Risks and test signals: risks are incorrect register offsets, endian mismatch for pstate, failing to advance compiled breakpoints, single-step conflicts with other debug users, and text patch failures. Test with kgdb over serial, continue/step/detach, dynamic breakpoints, compiled `kgdb_breakpoint()`, SMP stop, and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/kuser32.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/kuser32.S

Purpose: Defines fixed-address AArch32 kuser helper code mapped for legacy 32-bit applications.

Important symbols: `__kuser_helper_start`, `__kuser_cmpxchg64`, `__kuser_memory_barrier`, `__kuser_cmpxchg`, `__kuser_get_tls`, `__kuser_helper_version`, and `__kuser_helper_end`. Instructions are emitted with `.inst` in ARM state.

Control flow: helpers implement 64-bit compare-exchange, memory barrier, 32-bit compare-exchange, and TLS read using ARM load-exclusive/store-exclusive or CP15 instructions. The version word encodes helper size in 32-byte units.

Dependencies and integration: used by AArch32 compatibility mapping code (`aarch32_setup_additional_pages()`) and documented fixed ABI addresses. It depends on compatibility mode, ARM instruction encoding, and the historical kernel user helpers ABI.

Risks and test signals: risks are changing instruction layout or helper size, breaking fixed offsets, or exposing helpers on systems without compat support. Test with AArch32 userland atomics/TLS, helper mapping inspection, compat signal/syscall tests, and ABI conformance to `kernel_user_helpers.rst`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/kuser32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/machine_kexec.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/machine_kexec.c

Purpose: Implements arm64 machine-level kexec and crash-kexec preparation, relocation mapping, CPU shutdown, and hibernation crashkernel interaction.

Important APIs and state: functions include `machine_kexec_prepare()`, `machine_kexec_post_load()`, `machine_kexec()`, `machine_crash_shutdown()`, `crash_prepare_suspend()`, `crash_post_resume()`, `crash_is_nosave()`, and `crash_free_reserved_phys_range()`. The code fills `kimage->arch` fields such as `ttbr0`, `ttbr1`, `t0sz`, `kern_reloc`, `el2_vectors`, `zero_page`, and `phys_offset`.

Control flow: post-load flushes in-place images or builds temporary page tables, copies nVHE EL2 vectors, copies relocation code, idmaps it, records physical offset, and flushes caches. `machine_kexec()` masks interrupts, asserts CPU state, then either uses identity-mapped `cpu_soft_restart()` for in-place images or installs temporary vectors/TTBR0 and jumps to relocation code.

Dependencies and integration: integrates with generic kexec, crash dump, SMP CPU stop, trans_pgd, idmap/TTBR helpers, nVHE hyp stub, hibernation nosave filtering, and cache maintenance.

Risks and test signals: risks include executing stale relocation code, kexec with online/stuck CPUs, wrong EL2 vectors, crash kernel stale CPUs, and hibernation preserving crash memory incorrectly. Test normal kexec, kexec_file, crash kdump, CPU hotplug, nVHE KVM, hibernate plus crashkernel, and in-place `IND_DONE` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/machine_kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/machine_kexec_file.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/machine_kexec_file.c

Purpose: Provides arm64 `kexec_file_load` support for loader registration, DTB/initrd placement, crash ELF headers, and cleanup.

Important APIs and state: `kexec_file_loaders[]` currently exposes `kexec_image_ops`. `arch_kimage_file_post_load_cleanup()` frees `image->arch.dtb` and ELF headers. `load_other_segments()` adds crash headers, optional initrd, and a generated DTB to the kimage.

Control flow: crash loads first prepare an ELF64 core header after excluding crashkernel ranges, add it as a top-down buffer, and optionally load dm-crypt keys. Initrd is placed above the kernel within a 1GB-aligned up-to-32GB window. A new FDT is allocated and packed, then placed top-down with 2MB alignment. On any failure, segment count is restored and temporary DTB memory is freed.

Dependencies and integration: depends on memblock ranges, crash dump helpers, libfdt, Open Firmware FDT setup, kexec buffer placement, vmalloc/kvfree, and `kexec_image.c` for the kernel image segment.

Risks and test signals: risks are segment rollback bugs, DTB/initrd placement outside boot protocol limits, crash memory exclusion mistakes, leaked ELF headers, or missing cleanup. Test `kexec_file_load` with and without initrd, crash kernels, dm-crypt key loading, small memory placement pressure, and cleanup after failed loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/machine_kexec_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/module-plts.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/module-plts.c

Purpose: Sizes, creates, and emits arm64 module PLT entries for out-of-range branches, ftrace trampolines, and ADRP erratum veneers.

Important APIs and state: `get_plt_entry()` builds an ADRP/ADD/BR sequence using x16. `module_emit_plt_entry()` emits or reuses branch PLTs. `module_emit_veneer_for_adrp()` handles ARM64 erratum 843419 when enabled. `module_frob_arch_sections()` finds `.plt`, `.init.plt`, ftrace trampoline sections, sorts branch relocations, counts required entries, and resizes sections.

Control flow: relocations are partitioned so branch relocations needing PLTs are grouped and sorted, enabling duplicate detection. `count_plts()` counts branch PLTs and optional ADRP veneers, adjusts alignment to avoid vulnerable ADRP offsets, and adds slack for skipped unsafe slots. Emit functions choose core/init PLT section based on relocation target, skip forbidden ADRP offsets, and enforce max-entry bounds.

Dependencies and integration: used by module loader and `module.c` relocation fallback. Integrates with ftrace, ARM64 erratum 843419 capability, ELF section metadata, instruction encoders, and module init/core memory layout.

Risks and test signals: risks are undercounting PLTs, duplicate detection errors, forbidden ADRP placement, module section alignment changes, and ftrace trampoline absence. Test with large modules placed far from core kernel, ftrace-enabled modules, erratum 843419 configs, init text relocations, and module load/unload stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/module-plts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/module.c

Purpose: Implements AArch64 module relocation application, alternative patching, dynamic SCS patching, and ftrace PLT initialization.

Important APIs and state: relocation helpers include `do_reloc()`, `reloc_data()`, `reloc_insn_movw()`, `reloc_insn_imm()`, and `reloc_insn_adrp()`. Public entry points are `apply_relocate_add()` and `module_finalize()`. `WRITE_PLACE()` writes directly for unformed modules and uses `aarch64_insn_copy()` for already formed text.

Control flow: `apply_relocate_add()` iterates ELF RELA entries, resolves `S + A`, switches on relocation type, patches data or instruction immediates, emits PLTs for out-of-range CALL/JUMP26, and emits veneers or ADR substitutions for vulnerable ADRP locations. `module_finalize()` applies `.altinstructions`, optionally patches `.init.eh_frame` for dynamic shadow call stack, and initializes ftrace PLTs.

Dependencies and integration: integrates with module loader, `module-plts.c`, alternative patching, shadow call stack PI patcher, ftrace, KASAN/module memory, and arm64 instruction encoding.

Risks and test signals: risks include relocation overflow, unsupported RELA types, incorrect signed vs unsigned handling, writing executable memory without text patching, missing PLTs, and malformed SCS frame data. Test by loading modules with broad relocation coverage, far branch targets, alternatives, dynamic SCS, ftrace, and negative tests for unsupported/overflow relocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/mpam.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/mpam.c

Purpose: Initializes arm64 MPAM requestor support and restores MPAM system registers after CPU power management events.

Important APIs and state: defines static key `mpam_enabled`, per-CPU `arm64_mpam_default` and `arm64_mpam_current`, and global `arm64_mpam_global_default`. The PM notifier `mpam_pm_notifier()` restores `MPAM1_EL1`, optional `MPAMSM_EL1`, and `MPAM0_EL1` on `CPU_PM_EXIT`. `arm64_mpam_register_cpus()` registers the CPU PM notifier and calls `mpam_register_requestor()`.

Control flow: at arch init, the code reads sanitized `MPAMIDR_EL1`, extracts maximum PARTID and PMG, and exits if MPAM is unsupported. On CPU PM exit, it writes the current per-CPU MPAM value back to relevant registers with enable bits and synchronization.

Dependencies and integration: depends on arm64 MPAM cpufeature detection, Linux MPAM core, CPU PM notifiers, jump labels/static keys, and SME support for streaming-mode MPAM register restoration.

Risks and test signals: risks are stale partition/PMG values after suspend, incorrect PARTID/PMG limits, missing SME register restore, and init ordering relative to MPAM MSC driver. Test with MPAM-enabled hardware or emulation, CPU suspend/resume, hotplug, resource control assignments, and SME-capable systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/mpam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/mte.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/mte.c

Purpose: Implements arm64 Memory Tagging Extension support for page tag initialization, kernel/user tag checking modes, thread switching, prctl controls, ptrace tag access, suspend/resume, and sysfs CPU preferences.

Important APIs and state: per-CPU `mte_tcf_preferred` controls preferred user tag check mode. `mte_async_or_asymm_mode` is a static key for KASAN HW tags. Entry points include `mte_sync_tags()`, `memcmp_pages()`, kernel enable helpers, `mte_check_tfsr_el1()`, `mte_thread_init_user()`, `mte_thread_switch()`, `mte_cpu_setup()`, suspend hooks, `set_mte_ctrl()`, `get_mte_ctrl()`, `mte_ptrace_copy_tags()`, and `mte_probe_user_range()`.

Control flow: page mapping calls clear tags once and mark pages/hugetlb folios tagged before publishing PTEs. Thread switch resolves requested TCF modes against per-CPU preference, updates `SCTLR_EL1` user fields and `GCR_EL1`, clears TCO state, and reports pending async faults when needed. `set_mte_ctrl()` converts prctl bits into thread state and updates current CPU immediately. Ptrace tag access validates ptrace permission, walks remote pages, requires `VM_MTE`, and copies tag granules to or from user iovecs.

Dependencies and integration: integrates with page table mapping, KASAN HW tags, scheduler context switch, prctl ABI, ptrace ABI, hugetlb, swap/KSM comparison, CPU sysfs devices, and suspend resume.

Risks and test signals: risks include publishing PTEs before tags are visible, merging tagged pages in KSM, async fault loss, wrong per-CPU preferred mode, ptrace permission bugs, tag copy partial-progress handling, and suspend losing MAIR/GCR/RGSR state. Test with MTE selftests, KASAN HW tags sync/async/asymm/store-only, ptrace tag copy, hugetlb MTE, KSM, CPU hotplug/suspend, and sysfs preference changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/mte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/paravirt.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/paravirt.c

Purpose: Enables arm64 paravirtualized stolen-time accounting through SMCCC hypervisor calls.

Important APIs and state: per-CPU `stolen_time_region` stores an RCU-protected mapped `pvclock_vcpu_stolen_time` pointer. `para_steal_clock()` returns stolen time in ns. `pv_time_init()` probes hypervisor support, registers CPU hotplug callbacks, updates the `pv_steal_clock` static call, and enables static keys. Early param `no-steal-acc` disables runqueue steal accounting.

Control flow: CPU online calls SMCCC `ARM_SMCCC_HV_PV_TIME_ST`, remaps the returned stolen-time structure, validates revision/attributes, and publishes it under RCU. CPU down removes the pointer, synchronizes RCU, and unmaps. Reads return zero until the CPU mapping exists.

Dependencies and integration: depends on SMCCC 1.1, PSCI/hypervisor PV time ABI, CPU hotplug, RCU, memremap, static calls, scheduler cputime accounting, and static keys in paravirt core.

Risks and test signals: risks are mapping invalid hypervisor addresses, stale RCU pointers on CPU down, revision/attribute mismatch, and enabling accounting despite user opt-out. Test on hypervisors with and without PV time, CPU hotplug, scheduler steal-time accounting, `no-steal-acc`, and malformed hypervisor return handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/paravirt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/patching.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/patching.c

Purpose: Provides safe arm64 instruction and executable text patching primitives used by ftrace, alternatives, jump labels, KGDB, BPF/JIT-style code fill, and module relocation.

Important APIs and state: `patch_lock` serializes fixmap writes. APIs include `aarch64_insn_read()`, `aarch64_insn_write()`, `aarch64_insn_write_literal_u64()`, `aarch64_insn_copy()`, `aarch64_insn_set()`, `aarch64_insn_patch_text_nosync()`, and `aarch64_insn_patch_text()`. Helpers map image or vmalloc text through `FIX_TEXT_POKE0`.

Control flow: writes acquire the raw spinlock with IRQs saved, map the target physical page through fixmap, copy or memset the new instruction data with nofault helpers, unmap, and flush instruction cache as needed. Multi-instruction synchronized patching uses `stop_machine_cpuslocked()` so one master CPU applies patches while others wait and execute `isb()`.

Dependencies and integration: depends on fixmap, cache maintenance, stop_machine, kernel nofault access, `core_kernel_text()`, `vmalloc_to_page()`, and executable section symbols including exit text before init discard.

Risks and test signals: risks are patching unaligned A64 instructions, missing cache synchronization, writing freed init/exit text after boot, vmalloc text without pages, and deadlocks under patch_lock. Test with ftrace, alternatives, jump labels, KGDB breakpoints, BPF/JIT fill users, CPU hotplug, and fault injection on nofault copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/patching.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pci.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pci.c

Purpose: Supplies arm64 platform-independent raw PCI config access wrappers and optional NUMA node lookup.

Important APIs: `raw_pci_read()` and `raw_pci_write()` find the `pci_bus` by domain and bus, then delegate to the bus operations. Under `CONFIG_NUMA`, `pcibus_to_node()` returns `dev_to_node(&bus->dev)` and is exported.

Control flow and state: no persistent state. Missing buses return `PCIBIOS_DEVICE_NOT_FOUND`; otherwise operation return codes come from host bridge ops.

Dependencies and integration: depends on the PCI core, host bridge config access callbacks, domain/bus enumeration, and NUMA device topology. It is used by generic PCI code paths expecting arch raw accessors.

Risks and test signals: risks are null bus ops from malformed host controllers, incorrect domain lookup, and NUMA node mismatch. Test with PCI ECAM and non-ECAM host bridges, multi-domain systems, hotplug, and NUMA topology checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/perf_callchain.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/perf_callchain.c

Purpose: Implements arm64 perf user and kernel callchain collection.

Important APIs: `perf_callchain_user()` and `perf_callchain_kernel()` call the architecture stack walkers with `callchain_trace()`, which stores PCs through `perf_callchain_store()`.

Control flow and state: if `perf_guest_state()` is active, both paths return without recording guest callchains. Otherwise user callchains use `arch_stack_walk_user()` with current regs, while kernel callchains use `arch_stack_walk()` for `current`.

Dependencies and integration: depends on perf callchain core, arm64 stacktrace unwinding, user access safety, and pointer authentication stripping behavior in stack walkers.

Risks and test signals: risks are missing guest support, bad unwinding across PAC-signed frames, user memory faults, and truncated callchains. Test with perf record/report in user and kernel mode, PAC-enabled kernels, frame-pointer unwinding, and guest execution samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/perf_callchain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/perf_regs.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/perf_regs.c

Purpose: Provides arm64 perf register sampling ABI support for native, compat, and SVE vector-granule registers.

Important APIs: `perf_reg_value()`, `perf_reg_validate()`, `perf_reg_abi()`, and `perf_get_regs_user()`. `perf_ext_regs_value()` currently supports `PERF_REG_ARM64_VG` when SVE exists.

Control flow: register reads validate the index, handle compat mode specially for SP/LR/PC ABI compatibility, return native SP/PC or general regs, and dispatch extended registers. Validation rejects empty masks and reserved bits, except VG when SVE is supported. ABI selection returns 32-bit for compat threads and 64-bit otherwise.

Dependencies and integration: depends on perf event ABI definitions, `pt_regs`, compat task state, SVE vector length state from `fpsimd.c`, and task stack helpers.

Risks and test signals: risks are ABI compatibility regressions for 32-bit tasks sampled by 64-bit tools, exposing unsupported extended regs, and wrong VG values after vector length changes. Test with perf register sampling for native and compat tasks, SVE-enabled systems, invalid masks, and unwinder consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/Makefile

Purpose: Builds the position-independent early arm64 startup objects that run before full kernel relocation and normal runtime services are available.

Important rules and state: `KBUILD_CFLAGS` removes ftrace, stack protector, SCS, LTO, fortify, branch profiling, latent entropy, and unwind table assumptions, then adds `-fpie`, `-ffreestanding`, hidden include, libfdt include path, and strict no-exports behavior. `CFLAGS_map_range.o += -mstrict-align` protects MMU-off execution. The `%.pi.o` rule prefixes symbols with `__pi_`, strips `.note.gnu.property`, and runs `relacheck`.

Control flow: object list always includes `idreg-override`, `map_kernel`, `map_range`, and selected libfdt objects. Relocatable, KASLR, and dynamic SCS patching add optional PI objects. Library source files are compiled from `lib/*.c` and object-copied so allocated sections become init sections when needed.

Dependencies and integration: consumed by `head.S` and linker aliases in `image-vars.h`. Depends on objcopy, a host `relacheck` tool, libfdt sources, and early startup constraints forbidding absolute addressing.

Risks and test signals: risks are compiler flags reintroducing instrumentation, relocations unsafe for early PI code, unaligned accesses with MMU off, and missing symbol prefixing. Test with `relacheck`, `readelf -r` on PI objects, KASLR/relocatable builds, LTO/SCS configurations, and early boot smoke.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/idreg-override.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/idreg-override.c

Purpose: Parses very early command-line CPU feature overrides into global `arm64_ftr_override` structures before normal kernel mapping and cpufeature finalization.

Important types and APIs: `struct ftr_set_desc` describes ID registers, fields, shifts, widths, and optional filters. Descriptors cover MMFR0/1/2, PFR0/1, ISAR1/2, SMFR0, and software features. `init_feature_override()` clears overrides, stores boot status, parses bootargs and built-in cmdline, and cleans override cache lines. It also provides PI `skip_spaces()`.

Control flow: parser tokenizes cmdline words, normalizes dashes to underscores, matches `<reg>.<field>=<hex digit>`, applies filters, updates override val/mask, and recursively expands aliases such as `arm64.nosve`, `arm64.nomte`, `kvm_arm.mode=protected`, `nokaslr`, and `rodata=off`. Filters cascade dependent feature disables, for example clearing ZFR0 when SVE is disabled or SMFR0 when SME is disabled.

Dependencies and integration: runs from PI early mapping code with FDT bootargs. Depends on libfdt, cpufeature override globals exported to PI by linker aliases, boot EL status, cache maintenance, and no absolute-address constraints.

Risks and test signals: risks are parsing only one override per token, alias length truncation, filters silently masking user requests, stale cache-visible overrides before cpufeature reads, and VHE/nVHE override conflicts. Test boot parameters for all aliases, CONFIG_CMDLINE_FORCE precedence, FDT bootargs, protected/nVHE KVM modes, SVE/SME/MTE/PAuth disabling, and cache coherency on MMU-off boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/idreg-override.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/kaslr_early.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/kaslr_early.c

Purpose: Computes the early virtual KASLR offset in position-independent startup code.

Important APIs: `kaslr_early_init()` returns a high-bit virtual displacement or zero. `get_kaslr_seed()` reads `/chosen/kaslr-seed` from the writable FDT, converts it from big-endian, and clears the property to avoid leaking the seed.

Control flow: if command-line overrides disabled KASLR, return zero. Otherwise use the FDT seed if present; if absent, try architectural RNDR via `__early_cpu_has_rndr()` and `__arm64_rndr()`. The result places the kernel in the middle half of the vmalloc-to-kimage range by multiplying the range by the seed and taking the high 64 bits.

Dependencies and integration: called by `pi/map_kernel.c` during early mapping. Depends on libfdt, arch random, feature override state from `idreg-override.c`, memory layout constants, and the FDT being temporarily mapped writable.

Risks and test signals: risks include not clearing the seed, weak/no entropy disabling KASLR, offset range collision with other virtual allocations, and command-line parsing mismatch. Test with FDT seed, RNDR seed, `nokaslr`, missing entropy, boot log KASLR status, and virtual address placement checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/kaslr_early.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/map_kernel.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/map_kernel.c

Purpose: Builds the early kernel virtual mapping, handles relocation/KASLR, feature override parsing, LPA2/idmap remapping, optional dynamic SCS patching, BTI/PAC text permissions, and final swapper page table installation.

Important APIs and state: `early_map_kernel()` is called from `head.S`. Helpers include `map_kernel()`, `map_segment()`, `unmap_segment()`, `remap_idmap_for_lpa2()`, `map_fdt()`, and `ng_mappings_allowed()`. It uses linker symbols for text/rodata/init/data ranges and PI globals such as `arm64_use_ng_mappings`.

Control flow: the FDT is mapped, BSS and initial page tables are cleared, feature overrides are parsed, VA bits/root level are adjusted for LVA/LPA2 hardware, KASLR seed is folded with physical low bits, LPA2 idmap descriptors are remapped if needed, then segments are mapped. A two-pass mapping is used for relocation or dynamic SCS: text is first writable, relocation/SCS patching runs, text is unmapped, TLBs are invalidated, and text is remapped with final executable permissions before copying the root table to `swapper_pg_dir`.

Dependencies and integration: depends on PI `map_range()`, relocation and SCS PI helpers, libfdt, cpufeature probes, TCR/TTBR manipulation, linker aliases, KASLR early seed, Cavium erratum handling for non-global mappings, and `head.S` handoff.

Risks and test signals: risks are wrong permissions during two-pass mapping, TLB conflicts when remapping text, FDT overlap with kernel image, LPA2 descriptor bit reinterpretation, dynamic SCS with PAC/BTI, and KASLR/KPTI non-global mapping errata. Test relocatable and non-relocatable boots, BTI/PAC/SCS combinations, `rodata=off`, LPA2/LVA hardware, KASLR seed, KPTI, and early page table dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/map_kernel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/map_range.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/map_range.c

Purpose: Provides the early PI page-table range mapper used for idmaps, kernel maps, FDT maps, and temporary LPA2 remaps before the normal mm subsystem is available.

Important APIs: `map_range()` recursively creates block/page mappings at the requested translation level, allocating lower-level tables from a caller-provided physical pointer. `create_init_idmap()` builds the initial idmap over text and data ranges and returns the end of used page-table memory.

Control flow: `map_range()` aligns start and physical address, advances to the relevant table entry, chooses block/page descriptor bits unless clearing mappings, recurses when alignment or level requires finer mappings, optionally uses contiguous PTE attributes, and writes descriptors directly. `create_init_idmap()` maps `_stext` to `__initdata_begin` RX and `__initdata_begin` to `_end` RW, applying a caller-supplied clear mask.

Dependencies and integration: called by `head.S` through PI aliases and by `pi/map_kernel.c`. It depends on arm64 page table descriptor definitions, early linker symbols, strict alignment flags, and MMU-off physical pointer assumptions.

Risks and test signals: risks are table allocation overrun, wrong contiguous-bit boundaries, clearing live mappings without TLB handling by caller, and descriptor bits invalid under LPA2 unless masked. Test early boot with all page sizes and levels, LPA2, KASLR relocation, FDT mapping, and page table debug instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/map_range.c -->
