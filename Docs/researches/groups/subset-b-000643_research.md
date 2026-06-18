# subset-b-000643 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/hw_breakpoint.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/hw_breakpoint.c

Purpose: implements ARM hardware breakpoint/watchpoint support for perf, ptrace, debug exceptions, and optional CFI traps by programming CP14 debug registers. It discovers debug architecture level, BRP/WRP counts, monitor-mode availability, OS save/restore support, and maximum watchpoint length.

Important APIs/types/functions: exported architecture hooks include `hw_breakpoint_slots`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `arch_check_bp_in_kernelspace`, `arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `arch_get_debug_arch`, `arch_get_max_wp_len`, `hw_breakpoint_pmu_read`, and `hw_breakpoint_exceptions_notify`. Internal control is built around `read_wb_reg`, `write_wb_reg`, `encode_ctrl_reg`/`decode_ctrl_reg`, `watchpoint_handler`, `breakpoint_handler`, and `hw_breakpoint_pending`.

Control flow: `arch_hw_breakpoint_init` probes CPUID/DIDR, blacklists Scorpion CPUs, registers CPU hotplug reset, clears debug control/value registers, calculates capacities, installs fault hooks, and registers PM restore. Runtime debug aborts enter `hw_breakpoint_pending`, decode DSCR MOE, dispatch to breakpoint/watchpoint/CFI handlers, fire `perf_bp_event`, and use mismatch breakpoints for single-step restoration when the default overflow handler is active.

State and persistence: per-CPU `bp_on_reg[]` and `wp_on_reg[]` track installed perf events. `core_num_brps`, `core_num_wrps`, `debug_arch`, `has_ossr`, and `max_watchpoint_len` are init-time global capability state. CPU PM exit and hotplug reset hardware registers because debug state can be lost across low-power modes.

Dependencies and integration: depends on perf hw breakpoint core, undef hooks, fault-code hooks, CPU hotplug, CPU PM, CoreSight OS lock registers, ARM CP15/CP14 helpers, and optional CFI reporting. Ptrace consumes its generic-field conversions and resource info.

Risks: debug-register access can undef on broken firmware or powered-down debug blocks; alignment and watchpoint attribution are architecture-sensitive; older debug architectures only expose one reliable watchpoint; single-step support requires reserved mismatch BRPs and target-bound events. Test signals include boot logs reporting BRP/WRP counts, max watchpoint size, ptrace/perf breakpoint tests, watchpoint uaccess cases, CPU hotplug/PM resume tests, and unsupported CPU fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/hw_breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/hyp-stub.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/hyp-stub.S

Purpose: installs a minimal ARMv7 HYP-mode stub during early boot or zImage transitions so the kernel can leave CPUs in a known SVC/HYP relationship and service a tiny set of HVC requests.

Important APIs/types/functions: assembly entry points are `__hyp_stub_install`, `__hyp_stub_install_secondary`, `__hyp_set_vectors`, `__hyp_soft_restart`, and vector table `__hyp_stub_vectors`. Writable `__boot_cpu_mode` records the primary boot mode and mismatch bit for later `hyp_mode_check`.

Control flow: primary install stores CPSR mode, secondaries compare their mode against it, abort on mismatch, and only install vectors when currently in HYP mode. Installation programs HVBAR, clears HCR/HCPTR/HSTR traps, configures HSCTLR, mirrors MIDR/MPIDR into virtual registers, opens physical timer access, and optionally enables GICv3 system registers. Trap handling accepts vector updates for zImage, soft restart jumps, and returns `HVC_STUB_ERR` otherwise.

State and persistence: persistent state is the boot-mode word and EL2/HYP register configuration. The stub vectors persist until replaced by KVM or firmware paths.

Dependencies and integration: called from early head/resume paths with MMU/cache off; `setup.c` reads the boot-mode state through virtualization helpers; reboot and suspend paths can invoke soft restart through HVC.

Risks: CPU mode mismatches indicate broken firmware and disable virtualization assumptions; these routines are not ABI-compliant and require exact register/boot-state contracts. Test signals include boot logs from `hyp_mode_check`, secondary CPU bring-up under HYP, KVM availability, and soft restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/hyp-stub.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/insn.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/insn.c

Purpose: generates in-memory ARM or Thumb-2 branch opcodes for runtime text patching users such as jump labels and alternatives.

Important APIs/types/functions: `__arm_gen_branch` is the exported core helper; internal `__arm_gen_branch_thumb2` and `__arm_gen_branch_arm` encode BL/B ranges and PC biases. It relies on `__opcode_thumb32_compose` and opcode endianness conversion helpers from `asm/opcodes.h`.

Control flow: callers provide source PC, destination, link flag, and warning policy. The helper selects Thumb-2 or ARM encoding at build time, checks signed branch range, warns once when requested, and returns zero on impossible branches.

State and persistence: stateless; returned opcodes are later persisted by callers into executable kernel text.

Dependencies and integration: feeds `jump_label.c`, ftrace/static key patching, and text patching. Correct PC bias differs by ISA: Thumb-2 uses `pc + 4`, ARM uses `pc + 8`.

Risks: off-by-one range or wrong ISA encoding produces patched control-flow corruption. Test signals include static-key toggling, branch range tests, Thumb-2 and ARM builds, and objdump validation of generated opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/io.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/io.c

Purpose: provides ARM-specific generic MMIO helper implementations for atomic register modification and byte-wise copies/memsets between normal memory and I/O memory.

Important APIs/types/functions: exports `atomic_io_modify_relaxed`, `atomic_io_modify`, `_memcpy_fromio`, `_memcpy_toio`, and `_memset_io`. `__io_lock` is a global raw spinlock protecting shared register read-modify-write sequences.

Control flow: atomic modify helpers lock with IRQ save, read relaxed, mask/merge the value, write either relaxed or ordered, then unlock. Copy/memset helpers loop over bytes with `readb`/`writeb`.

State and persistence: no persistent data beyond the lock; writes persist in device registers or I/O memory.

Dependencies and integration: used by drivers and low-level subsystems needing shared MMIO bit updates. Depends on Linux I/O accessors and raw spinlocks.

Risks: the single global lock serializes unrelated MMIO updates; relaxed variant lacks ordering beyond the lock; byte loops are simple and potentially slow. Test signals include driver register race tests, lockdep/IRQ-safe execution, and device functional tests that rely on register bit preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/irq.c

Purpose: supplies ARM interrupt initialization, generic first-level IRQ dispatch, IRQ stack setup, `/proc/interrupts` architecture rows, and platform/cache controller initialization hooks.

Important APIs/types/functions: `handle_IRQ`, `init_IRQ`, `arch_show_interrupts`, `arch_probe_nr_irqs`, and optional `do_softirq_own_stack`. `irq_err_count` records bad IRQs; per-CPU `irq_stack_ptr` exists under `CONFIG_IRQSTACKS`.

Control flow: `init_IRQ` allocates IRQ stacks, selects DT irqchip init or machine descriptor `init_irq`, initializes L2 cache controller support when configured, and initializes UniPhier cache support. Runtime `handle_IRQ` validates IRQ numbers, maps to `irq_desc`, and calls `handle_irq_desc` or `ack_bad_irq`.

State and persistence: per-CPU IRQ stack pointers persist after boot; `irq_err_count` is reported. Machine descriptor choices determine boot-time IRQ topology.

Dependencies and integration: integrates with irqchip, machine descriptors, FIQ/IPI reporting, softirq stacks, outer cache/L2X0, DT, sparse IRQ, and reboot code include dependencies.

Risks: invalid IRQ decoding must not crash; missing IRQ stack allocation degrades safety; machine descriptor vs DT selection must match platform firmware. Test signals include boot IRQ init logs, `/proc/interrupts`, bad IRQ accounting, SMP IPI rows, and IRQ stack/softirq stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/isa.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/isa.c

Purpose: exposes legacy ISA memory and I/O port base information through sysctl for ARM platforms that emulate or support ISA-style userspace port access.

Important APIs/types/functions: `register_isa_ports` stores `membase`, `portbase`, and `portshift`, then registers the `bus/isa` sysctl table. The table exposes read-only integer proc entries.

Control flow: platform code calls `register_isa_ports` during initialization; sysctl handlers serve the stored values.

State and persistence: static globals keep base/shift values for the system lifetime; `isa_sysctl_header` tracks the registration.

Dependencies and integration: depends on sysctl, proc integer handlers, and platform-specific ISA setup.

Risks: wrong values break glibc/userspace emulation of `iopl`, `inb`, and `outb`; values are read-only after registration. Test signals include presence and correctness of `/proc/sys/bus/isa/*` entries and userspace port I/O compatibility tests on affected boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/iwmmxt.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/iwmmxt.S

Purpose: implements lazy context management for Intel/XScale iWMMXt/Concan coprocessor state, including undefined-instruction enablement, task switch gating, signal/ptrace save-restore, and owner release.

Important APIs/types/functions: entry points include `iwmmxt_undef_handler`, `iwmmxt_task_enable`, `iwmmxt_task_disable`, `iwmmxt_task_copy`, `iwmmxt_task_restore`, `iwmmxt_task_switch`, and `iwmmxt_task_release`. Internal helpers `concan_save`, `concan_dump`, and `concan_load` manipulate WR and control registers using macros from `iwmmxt.h`.

Control flow: an undef trap enables CP0/CP1 access, backs PC up to retry the faulting instruction, saves the previous owner when needed, records the current task as `concan_owner`, and loads its saved state. Disable/copy/restore paths run with interrupts masked to keep ownership coherent. Task switch toggles coprocessor access to force lazy reloads.

State and persistence: global `concan_owner` points to the owning task save area; each thread stores iWMMXt state under `TI_IWMMXT_STATE`/fpstate.

Dependencies and integration: used by ptrace, signal handling, thread notifiers, undefined instruction handling, and ARM coprocessor access control.

Risks: ownership races corrupt user vector state; alignment and interrupt masking are critical; unsupported toolchains need raw instruction macros. Test signals include iWMMXt userspace context-switch tests, signal save/restore, ptrace register access, suspend save, and preemption stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/iwmmxt.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/iwmmxt.h -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/iwmmxt.h

Purpose: provides assembler macros and register number aliases for loading/storing iWMMXt data/control registers from assembly code.

Important APIs/types/functions: macros `wldrd`, `wldrw`, `wstrd`, and `wstrw` emit raw iWMMXt memory transfer instructions. Clang-specific `tmrc` and `tmcr` wrappers map to coprocessor 1 moves for `wCon`.

Control flow: no runtime control flow; included by `iwmmxt.S` to abstract instruction encoding.

State and persistence: no storage of its own.

Dependencies and integration: tightly coupled to iWMMXt save-area offsets and assembler capabilities. The `.irp` aliases make macro operands usable by symbolic register names such as `wR0` and `wCSSF`.

Risks: wrong encoding silently corrupts coprocessor state; macro/toolchain differences are architecture-specific. Test signals are successful ARM/Clang assembly builds and runtime iWMMXt save/restore correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/iwmmxt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/jump_label.c

Purpose: implements ARM static key/jump label patching by replacing NOPs with generated branches or restoring NOPs.

Important APIs/types/functions: `arch_jump_label_transform` is the runtime entry; `__arch_jump_label_transform` handles both early and live patching. It uses `arm_gen_branch`, `arm_gen_nop`, `__patch_text_early`, and `patch_text`.

Control flow: for each `jump_entry`, the requested type selects branch-to-target or NOP. Early static transformations write directly; live transformations use synchronized text patching.

State and persistence: modified kernel text is persistent until the static key changes again. No local state is kept.

Dependencies and integration: depends on jump label core metadata, instruction generation, and ARM text patching.

Risks: branch range and Thumb/ARM encoding must be correct; live patching must synchronize I-cache and CPUs. Test signals include static key selftests, boot-time static key initialization, and live enable/disable under SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/kgdb.c

Purpose: supplies ARM architecture support for KGDB register access, breakpoints, exception handoff, and sleeping-thread register reconstruction.

Important APIs/types/functions: `dbg_reg_def`, `dbg_get_reg`, `dbg_set_reg`, `sleeping_thread_to_gdb_regs`, `kgdb_arch_set_pc`, `kgdb_arch_handle_exception`, `kgdb_arch_init`, `kgdb_arch_exit`, `kgdb_arch_set_breakpoint`, `kgdb_arch_remove_breakpoint`, and `arch_kgdb_ops`. Undef hooks catch normal and compiled break instructions in ARM and Thumb modes.

Control flow: init registers a die notifier and undef hooks. Break traps call `kgdb_handle_exception`; continue/detach commands optionally update PC and compiled breakpoints skip the trapping instruction. Software breakpoint install saves the original instruction with nofault copy and patches text with `__patch_text`.

State and persistence: `compiled_break` remembers whether KGDB should advance PC. Breakpoint objects hold saved instructions; text remains patched until removed.

Dependencies and integration: integrates with kgdb core, die notifiers, undef instruction dispatcher, text patching, and task thread contexts.

Risks: breakpoint instruction size must match patching width; wrong PC adjustment loops forever; register offsets define the remote ABI. Test signals include kgdb attach, software breakpoint set/remove, Thumb and ARM break traps, sleeping task backtraces, and resume after compiled breakpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/machine_kexec.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/machine_kexec.c

Purpose: performs ARM-specific validation, crash shutdown, secondary CPU stopping, and final transition into a kexec or crashdump kernel.

Important APIs/types/functions: `machine_kexec_prepare`, `machine_kexec_cleanup`, `crash_smp_send_stop`, `machine_crash_shutdown`, and `machine_kexec`. It consumes `relocate_new_kernel` and writes `struct kexec_relocate_data` into the control page.

Control flow: prepare computes default `r2` ATAGS/DTB pointer, rejects unsafe SMP systems lacking CPU hotplug, validates segment memory, and detects DTB magic. Crash stop sends async calls to other CPUs, waits up to one second, saves CPU notes, masks interrupts, and proceeds. `machine_kexec` asserts only one CPU is online, copies relocation code with `fncpy`, fills relocation data, converts entry to identity mapping, and calls `soft_restart`.

State and persistence: `waiting_for_crash_ipi` tracks non-panic CPUs; `image->arch.kernel_r2` persists into the next kernel boot contract.

Dependencies and integration: depends on kexec core, memblock, OF FDT headers, SMP hotplug operations, cache flushes, identity mapping, and reboot/soft restart.

Risks: executing kexec with live secondary CPUs can corrupt memory; invalid segment memory or wrong DTB pointer breaks next-kernel boot. Test signals include kexec load/execute, crashkernel boot, SMP stop timeout logs, and DTB handoff validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/machine_kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/module-plts.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/module-plts.c

Purpose: sizes, allocates, and populates ARM module PLT entries used when module branch relocations cannot reach their target directly, with fixed entries for dynamic ftrace when enabled.

Important APIs/types/functions: `module_frob_arch_sections`, `get_module_plt`, and `in_module_plt`. Helpers include `prealloc_fixed`, `cmp_rel`, `is_zero_addend_relocation`, `duplicate_rel`, and `count_plts`.

Control flow: section frobbing locates `.plt`, `.init.plt`, and symtab, marks unwind sections executable when needed for range, sorts executable relocations, counts potential PLTs split between core/init, and converts PLT sections to allocated NOBITS executable sections. At relocation time, `get_module_plt` reuses fixed or last duplicate entries or appends a new literal/ldr pair.

State and persistence: per-module `mod->arch.core/init.plt`, counts, and cached entry pointers track PLT allocation. PLT code/literals persist in module memory until unload/init-free.

Dependencies and integration: used by `module.c` relocation range fallback, ftrace, module loader layout, ARM/Thumb opcode helpers, sort, and RCU module text lookup.

Risks: undercounting PLTs triggers `BUG_ON`; duplicate suppression assumes sorted relocations and zero-addend recognition; PLT distance is itself constrained by module layout. Test signals include loading large/out-of-range modules, ftrace modules, init text release, and `in_module_plt` stack/unwind checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/module-plts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/module.c

Purpose: implements ARM ELF module relocation handling, section classification, unwind table registration, physical/virtual patching, and SMP-on-UP module fixups.

Important APIs/types/functions: `module_init_section`, `module_exit_section`, `apply_relocate`, `module_finalize`, `module_arch_cleanup`, and `module_arch_freeing_init`. It handles relocation types including ABS32, PC24/CALL/JUMP24, PREL31, MOVW/MOVT ARM and Thumb variants, V4BX, REL32, and optional group relocations.

Control flow: `apply_relocate` validates symbol and target bounds, decodes each relocation, applies symbol/addend adjustments, routes long branches through `get_module_plt` when enabled, range-checks, and writes back opcode-endian-adjusted instructions. Finalization registers unwind tables for `.ARM.exidx*`, fixes `.pv_table`, and validates or patches `.alt.smp.init`.

State and persistence: relocation writes mutate module text/data; unwind tables are linked into `mod->arch.unwind_list`, with init table separately tracked for later freeing.

Dependencies and integration: module loader, ARM ELF psABI, PLT helper, unwind core, opcode conversion, SMP alternatives, and phys/virt patching.

Risks: relocation arithmetic and PC bias are easy to get wrong; unsupported ARM/Thumb interworking is rejected; bad bounds can corrupt module memory. Test signals include module load/unload across ARM and Thumb-2 configs, unwind from modules, out-of-range branch PLTs, and SMP-on-UP module behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/opcodes.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/opcodes.c

Purpose: provides canonical NOP encoding generation and instruction set helpers for runtime ARM text patching.

Important APIs/types/functions: `__arm_gen_nop` returns a memory-order NOP appropriate to ARM or Thumb-2 builds, using `__opcode_to_mem_arm` or Thumb compose/conversion helpers.

Control flow: build-time configuration selects Thumb-2 32-bit `nop.w` composition or ARM `mov r0, r0` style NOP.

State and persistence: stateless; generated opcodes are persisted by patching callers.

Dependencies and integration: used by jump labels, alternatives, ftrace, and other text patching code through `asm/opcodes.h`.

Risks: width mismatch breaks instruction stream alignment, especially for Thumb-2 patch sites. Test signals include static key transitions, objdump of patched NOPs, and boot on both ARM/Thumb kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/opcodes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/patch.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/patch.c

Purpose: implements safe ARM kernel text patching for early boot and live SMP systems, including fixmap mapping and cache synchronization.

Important APIs/types/functions: `__patch_text`, `__patch_text_real`, `__patch_text_early`, `patch_text`, and `patch_text_array`. It maps target code through a fixmap slot when MMU protections require it.

Control flow: early patching writes directly and flushes I-cache. Live patching packages patch data, calls `stop_machine` or CPU-synchronized patching path, maps the page writable if needed, writes opcode(s), flushes D/I cache for the target range, and restores mapping.

State and persistence: kernel text is modified persistently. Temporary fixmap state is local to patch operations.

Dependencies and integration: used by jump labels, KGDB, ftrace, alternatives, module finalization, and branch generation helpers. Depends on cacheflush, fixmap, stop_machine/SMP coordination, and page attribute behavior.

Risks: patching executable text while other CPUs execute it requires exact synchronization; cache maintenance errors leave stale instructions. Test signals include live static key toggles under SMP, KGDB breakpoints, ftrace, module alternatives, and cache coherency stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/patch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/perf_callchain.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/perf_callchain.c

Purpose: collects user and kernel callchains for ARM perf samples.

Important APIs/types/functions: `perf_callchain_user` walks user frames using ARM EABI frame pointers; `perf_callchain_kernel` consumes stack frames through `walk_stackframe`. User-frame helpers read `{fp, sp, lr, pc}` structures with fault-safe access.

Control flow: kernel path seeds a `stackframe` from regs and records PCs via perf callback. User path records current PC, then follows user frame pointers until invalid, looping, or inaccessible frames stop traversal.

State and persistence: no persistent state; callchains are stored in perf sample contexts.

Dependencies and integration: depends on perf event callchain core, stack unwinder, user accessors, frame-pointer ABI, and `pt_regs`.

Risks: user stacks are untrusted and may fault or loop; frame-pointer omission limits fidelity; kernel unwinder config changes behavior. Test signals include `perf record -g`, user/kernel callgraph sanity, fault-injection against invalid user frame pointers, and unwinder selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/perf_callchain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/perf_regs.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/perf_regs.c

Purpose: maps ARM `pt_regs` to perf register sampling ABI and validates requested register masks.

Important APIs/types/functions: `perf_reg_value`, `perf_reg_validate`, and `perf_reg_abi`. The code indexes ARM general registers and CPSR according to perf's architecture register IDs.

Control flow: validation checks mask bits fit within supported registers. Sampling returns requested register values from `pt_regs`; ABI reports 32-bit ABI.

State and persistence: stateless.

Dependencies and integration: used by perf sampling, BPF/perf register consumers, and user ABI definitions.

Risks: incorrect mapping breaks profiling/debug tooling; masks must reject unsupported IDs. Test signals include perf register sampling tests and comparing sampled register dumps with ptrace/core dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/phys2virt.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/phys2virt.S

Purpose: patches physical-to-virtual and virtual-to-physical conversion instruction sequences based on the boot-time `PHYS_OFFSET - PAGE_OFFSET` delta.

Important APIs/types/functions: `__fixup_pv_table` runs early from head code, `fixup_pv_table` patches module tables, and `__fixup_a_pv_table` handles ARM/Thumb-2 and LPAE/non-LPAE encodings. Data symbols `__pv_phys_pfn_offset` and `__pv_offset` export the calculated offset.

Control flow: early fixup stores PFN offset and signed PV delta, verifies 2 MiB alignment, then iterates linker-provided table entries and rewrites immediate fields in patchable instruction sequences. Module finalization calls the public wrapper for `.pv_table`.

State and persistence: patched instructions and exported offset data persist for the kernel lifetime.

Dependencies and integration: depends on linker pv tables, head.S register contracts, ARM/Thumb instruction encodings, endian modes, LPAE, and module finalization.

Risks: unsupported alignment deadloops early; wrong immediate patching corrupts all address translation helpers. Test signals include boot on varied RAM offsets, LPAE/non-LPAE and BE8/LE builds, module loading with `.pv_table`, and virt/phys conversion self-checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/phys2virt.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/process.c

Purpose: implements ARM process/thread lifecycle glue, idle hooks, register dumps, fork context setup, TLS propagation, wait-channel unwinding, gate VMA naming, and sigpage/vDSO mapping.

Important APIs/types/functions: `arch_cpu_idle*`, `show_regs`, `exit_thread`, `flush_thread`, `copy_thread`, `__get_wchan`, `arch_vma_name`, `arch_setup_additional_pages`, and gate-area helpers. It exports `thread_notify_head`, current task storage, and stack protector guard when configured.

Control flow: fork copies or initializes `pt_regs`, seeds `cpu_context` to `ret_from_fork`, clears ptrace hardware breakpoints, and handles TLS. Flush clears debug/fp/TLS state and notifies listeners. Sigpage setup allocates a randomized signal trampoline page and maps it with optional vDSO after exec.

State and persistence: per-thread CPU context, TLS values, debug state, fpstate, sigpage mapping in `mm->context.sigpage`, and optional global `signal_page`.

Dependencies and integration: scheduler, ptrace/hw breakpoints, thread notifiers, VFP/iWMMXt via fpstate, signal code, vDSO, memory management, gate VMA, LED triggers, and stacktrace.

Risks: bad child register setup breaks fork/clone; stale debug/fp state leaks across exec; sigpage mapping failures affect signal return. Test signals include fork/clone/TLS tests, `/proc/<pid>/maps` sigpage/vectors, signal return, register dumps on oops, and idle/resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/psci_smp.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/psci_smp.c

Purpose: adapts PSCI firmware calls to the ARM `smp_operations` interface for secondary CPU boot and CPU hotplug power-off.

Important APIs/types/functions: `psci_smp_available`, `psci_smp_ops`, `psci_boot_secondary`, and hotplug helpers `psci_cpu_disable`, `psci_cpu_die`, `psci_cpu_kill`.

Control flow: boot calls `psci_ops.cpu_on` with the target MPIDR and identity-mapped secondary startup address. Disable rejects missing `cpu_off` or trusted OS residency. Die invokes `cpu_off` with a power-down state and panics if it returns. Kill polls `affinity_info` up to ten times.

State and persistence: no local persistent state; relies on global `psci_ops` and CPU logical map.

Dependencies and integration: selected by `setup_arch` when DT PSCI is available and platform SMP ops are absent. Integrates with ARM hotplug, secondary startup assembly, XIP address translation, and PSCI firmware.

Risks: wrong entry address or MPIDR prevents boot; firmware may deny CPU_OFF; affinity polling races with shutdown. Test signals include secondary boot, CPU online/offline cycles, PSCI DT probing, trusted OS denial paths, and hotplug logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/psci_smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/ptrace.c

Purpose: implements ARM ptrace user ABI, register regsets, software breakpoint trap hooks, hardware breakpoint ptrace access, VFP/iWMMXt register transfer, and syscall tracing entry/exit.

Important APIs/types/functions: register helpers `regs_query_register_offset/name`, `regs_within_kernel_stack`, `regs_get_kernel_stack_nth`; ptrace hooks `arch_ptrace`, `ptrace_disable`, `ptrace_break`; regset view `task_user_regset_view`; syscall hooks `syscall_trace_enter/exit`. HW breakpoint helpers convert virtual ptrace HBP register numbers to perf events.

Control flow: init registers ARM/Thumb undef hooks for breakpoint instructions. `arch_ptrace` dispatches classic requests and regset copies, validates user register updates with `valid_user_regs`, creates/modifies user HW breakpoints via perf, and handles thread-area/syscall controls. Syscall entry reports ptrace first, then seccomp, tracepoints, and audit; exit audits, tracepoints, and ptrace reports.

State and persistence: per-task `thread.debug.hbp[]`, fp/VFP/iWMMXt state, `abi_syscall`, and saved `pt_regs` are mutated. Breakpoint hooks persist globally.

Dependencies and integration: perf hw_breakpoint, undef hooks, regset core, audit, seccomp, tracepoints, VFP/iWMMXt, signal delivery, and syscall ABI.

Risks: ptrace exposes a stable ABI, so register layout and HBP numbering must not drift; invalid CPSR/user regs must be rejected; hardware breakpoint lifecycle must not leak across fork/exec. Test signals include `strace`, `gdb`, PTRACE regset tests, HW watchpoint tests, seccomp+ptrace ordering, and syscall tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/reboot.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/reboot.c

Purpose: provides ARM restart, halt, power-off, and low-level soft restart sequencing.

Important APIs/types/functions: `arm_pm_restart`, `pm_power_off`, `machine_restart`, `machine_halt`, `machine_power_off`, `soft_restart`, and restart-mode handling. The file coordinates cache/TLB shutdown and optional HYP soft restart path.

Control flow: machine restart stops secondary CPUs, shuts down devices, then calls configured restart hook or falls back to `soft_restart`. Soft restart prepares an identity-mapped execution path, disables MMU/cache state through processor hooks, and branches to the physical/idmapped restart address.

State and persistence: global function pointers and reboot mode carry platform policy. Restart is terminal, so persistent state mostly concerns logs and hardware side effects.

Dependencies and integration: machine descriptors may install restart hooks; kexec calls `soft_restart`; HYP stub may be used for restart; cache/TLB/proc hooks must match CPU type.

Risks: restart with active secondary CPUs or stale caches can hang; missing platform restart hook may only soft reset CPU state, not board power. Test signals include reboot/halt/poweroff, kexec transition, watchdog fallback, and SMP stop logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/reboot.h -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/reboot.h

Purpose: declares restart/shutdown helpers shared by ARM kernel files that need to stop or restart the machine.

Important APIs/types/functions: small header exposing reboot-related prototypes, notably soft restart integration used by stacktrace/reboot users.

Control flow: no runtime flow.

State and persistence: no state.

Dependencies and integration: included by reboot-adjacent ARM kernel files to avoid local extern declarations.

Risks: because it is tiny, main risk is prototype drift from implementation. Test signals are compile coverage of files including it and reboot/kexec runtime paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/reboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/relocate_kernel.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/relocate_kernel.S

Purpose: contains the relocation trampoline copied to the kexec control page to move the next kernel's segments into place and branch to its entry.

Important APIs/types/functions: `relocate_new_kernel` and `relocate_new_kernel_size` are consumed by `machine_kexec.c`. The code interprets `struct kexec_relocate_data` values placed after the copied code.

Control flow: after soft restart jumps to the idmapped control page, the trampoline walks the kexec indirection page list, copies or clears pages according to control flags, sets ARM boot registers including machine type and r2 DTB/ATAGS pointer, and branches to the new kernel start address.

State and persistence: operates on physical pages and kexec control data; it is terminal for the old kernel.

Dependencies and integration: exact data layout must match `asm/kexec-internal.h` and `machine_kexec`. Runs with minimal MMU/cache assumptions.

Risks: any copy/order bug destroys the next kernel image or old memory before completion; register boot ABI must be exact. Test signals include successful kexec on DT and legacy ATAGS systems, crashdump boots, and relocation with multiple segments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/relocate_kernel.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/return_address.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/return_address.c

Purpose: implements `return_address()` support for callers needing an ancestor return PC, using ARM stack unwinding.

Important APIs/types/functions: `return_address` seeds a `stackframe` from current frame pointer/SP/LR/label PC and walks frames until the requested level is reached.

Control flow: level zero returns the compiler return address directly; higher levels invoke `walk_stackframe` with a callback that counts frames and captures the requested PC.

State and persistence: stateless.

Dependencies and integration: used by tracing/debug facilities; depends on frame pointer or unwind support and stacktrace helpers.

Risks: unreliable when unwind metadata/frame pointers are unavailable or optimized; must avoid exposing invalid PCs. Test signals include ftrace/lockdep callers using return addresses and stacktrace selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/return_address.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/setup.c

Purpose: central ARM architecture boot setup: identifies CPU and machine, initializes processor/cache feature globals, parses memory, builds resources, initializes MMU/memblock/DT/PSCI/SMP, reserves crashkernel memory, and exposes `/proc/cpuinfo`.

Important APIs/types/functions: `setup_arch`, `setup_processor`, `cpu_init`, `smp_setup_processor_id`, `arm_add_memory`, `hyp_mode_check`, `arch_cpu_is_hotpluggable`, `cpuinfo_op`, and boot params such as `early_mem`. It exports global platform state including `processor_id`, `cacheid`, `elf_hwcap`, `elf_hwcap2`, `system_rev`, and `system_serial`.

Control flow: `setup_arch` selects FDT or ATAGS machine descriptor, initializes fixmap/ioremap, parses early params, initializes memory and paging, registers resources, restart handler, DT CPU maps, PSCI, SMP ops, MPIDR hash, crashkernel reservation, console screen info, and machine early init. `setup_processor` finds the proc info table, initializes CPU/TLB/cache/user vectors, hardware capabilities, cache policy, errata, and CPU mode stacks.

State and persistence: global CPU/machine/hwcap/cache state persists for the lifetime of the kernel and user ABI. Memblock/resource reservations define system RAM visibility and crashkernel areas.

Dependencies and integration: machine descriptors, procinfo assembly tables, DT/ATAGS, memblock, MMU, PSCI, SMP, Xen/EFI, cache/TLB subsystems, kexec, procfs, VFP/hwcap ABI, and reboot handlers.

Risks: boot ordering is fragile; incorrect memory trimming or machine selection prevents boot; hwcap mistakes create user ABI breakage; MPIDR hash must be collision-free for suspend/SMP. Test signals include boot logs, `/proc/cpuinfo`, DT/ATAGS boot variants, `mem=` and crashkernel parameters, SMP bring-up, PSCI selection, and resource maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/signal.c

Purpose: implements ARM signal delivery and return ABI, including legacy and realtime frames, VFP/iWMMXt auxiliary contexts, syscall restart handling, randomized sigreturn page content, and return-to-user pending work.

Important APIs/types/functions: `sys_sigreturn`, `sys_rt_sigreturn`, `do_work_pending`, `get_signal_page`, and optional `do_rseq_syscall`. Internal helpers preserve/restore iWMMXt and VFP contexts, build `sigcontext`, choose signal stack, install return trampolines, and set handler registers.

Control flow: `do_work_pending` schedules, handles signals/uprobes/resume work, and may request syscall restart. `do_signal` converts restart errors, obtains a signal, adjusts syscall return behavior, and calls `handle_signal`. Frame setup writes user frames, signal masks, aux contexts, retcode, handler PC/LR/SP/CPSR, and realtime arguments. Return syscalls validate stack alignment/access, restore context and altstack, or SIGSEGV on bad frames.

State and persistence: mutates user stack frames, `pt_regs`, current blocked mask, restart block, VFP/iWMMXt hardware state, and `signal_return_offset`.

Dependencies and integration: signal core, uaccess, VFP/iWMMXt, rseq, uprobes, syscall restart ABI, process sigpage mapping, cache flushes, and static siginfo layout assertions.

Risks: signal frame ABI is user-visible and security-sensitive; invalid user frames must not restore privileged CPSR; trampoline cache flush and Thumb/ARM/FDPIC selection must be correct. Test signals include LTP signal tests, altstack, VFP/iWMMXt signal state, syscall restart, Thumb handlers, FDPIC, and malformed sigreturn fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/signal.h -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/signal.h

Purpose: shares ARM signal-frame layout definitions between signal delivery code and process setup code.

Important APIs/types/functions: defines structures for signal frames, realtime frames, and auxiliary VFP/iWMMXt blocks plus magic/size constants consumed by `signal.c`.

Control flow: no runtime flow; layout is used by copy-to/from-user paths.

State and persistence: describes persistent user-stack ABI content during signal delivery.

Dependencies and integration: tied to UAPI signal context, VFP/iWMMXt save formats, sigreturn trampoline code, and `process.c` sigpage mapping.

Risks: any layout change can break existing userspace signal return. Test signals include ABI size/offset compile assertions and userspace signal-frame compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/sigreturn_codes.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/sigreturn_codes.S

Purpose: defines the small ARM/Thumb/FDPIC signal return trampoline instruction sequences copied to user stacks or the sigpage.

Important APIs/types/functions: exports `sigreturn_codes`, an array consumed by `signal.c` and `get_signal_page`. Variants cover plain `sigreturn`, `rt_sigreturn`, ARM/Thumb mode, and FDPIC descriptor loading.

Control flow: user signal handlers return through these sequences, which load the appropriate syscall number and invoke SWI/SVC to enter `sys_sigreturn` or `sys_rt_sigreturn`.

State and persistence: code is copied into the randomized sigpage and sometimes user stack frames, then executed by userspace.

Dependencies and integration: must match syscall numbers, Thumb/ARM instruction encoding, FDPIC handler setup, and signal frame construction.

Risks: incorrect opcode ordering or cache visibility breaks every signal return path. Test signals include signal return on ARM and Thumb tasks, realtime signals, FDPIC handlers, and sigpage execution checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/sigreturn_codes.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/sleep.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/sleep.S

Purpose: implements low-level CPU suspend and resume assembly, preserving register state, indexing per-CPU save slots by MPIDR hash, restoring MMU state, and re-entering virtual kernel execution.

Important APIs/types/functions: `__cpu_suspend`, `cpu_resume`, `cpu_resume_arm`, `cpu_resume_mmu`, optional `cpu_resume_no_hyp`, and data object `sleep_save_sp`. Macro `compute_mpidr_hash` mirrors the C MPIDR hash algorithm.

Control flow: suspend saves callee registers, optionally switches to overflow stack, allocates CPU-specific save space, stores suspend function/argument, hashes MPIDR to select a save pointer slot, calls `__cpu_suspend_save`, then calls the platform finisher. Resume installs HYP stub if needed, enters SVC, hashes MPIDR, loads saved physical PGD/SP/resume function, enables MMU, calls `cpu_init`, unpoisons KASAN stack, and returns zero.

State and persistence: save slots under `sleep_save_sp` hold physical pointers to CPU context blocks across low-power states.

Dependencies and integration: C companion `suspend.c`, CPU proc sleep hooks, MPIDR hash from setup, idmap page tables, HYP stub, KASAN/vmap stack, and cache/TLB maintenance.

Risks: MPIDR hash mismatch resumes on wrong stack; MMU/idmap assumptions are strict; cache cleaning must make save data visible with MMU off. Test signals include suspend/resume on SMP, vmap stack/KASAN configs, HYP boot modes, and CPU hotplug/resume loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smccc-call.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/smccc-call.S

Purpose: provides assembly wrappers for ARM SMCCC SMC/HVC calls and optional quirk handling.

Important APIs/types/functions: exports `__arm_smccc_smc` and `__arm_smccc_hvc`, loading argument registers, issuing `smc` or `hvc`, and storing result registers into the caller-provided result structure.

Control flow: wrappers preserve callee-saved state, place up to eight SMCCC arguments in r0-r7, execute the conduit instruction, optionally apply Qualcomm A6 quirk register handling when configured, store r0-r3 results, and return.

State and persistence: no local persistent state; firmware calls may change secure/EL2 state outside Linux.

Dependencies and integration: PSCI, firmware mitigation calls, spectre hardening, and generic SMCCC core depend on these wrappers. ABI must match `linux/arm-smccc.h`.

Risks: register clobber or quirk mishandling corrupts firmware calls; conduit choice must match firmware. Test signals include PSCI boot/hotplug, SMCCC feature discovery, firmware spectre mitigation, and quirk platform tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smccc-call.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/smp.c

Purpose: implements ARM SMP operations glue: secondary CPU boot, CPU hotplug shutdown, per-CPU info, IPI routing/handling, CPU stop/panic behavior, cpufreq loop calibration updates, and NMI-style backtraces.

Important APIs/types/functions: `smp_set_ops`, `__cpu_up`, `smp_init_cpus`, `platform_can_secondary_boot`, hotplug hooks `__cpu_disable`, `arch_cpu_idle_dead`, `arch_cpuhp_cleanup_dead_cpu`, `secondary_start_kernel`, `smp_prepare_*`, IPI senders/handlers, `set_smp_ipi_range`, `smp_send_stop`, `panic_smp_self_stop`, and `arch_trigger_cpumask_backtrace`.

Control flow: boot CPU selects `smp_ops`; `__cpu_up` fills `secondary_data`, calls platform boot, and waits for `cpu_running`. Secondaries switch MMU context, initialize CPU stacks/proc state, run platform secondary init, set up IPIs, calibrate delay, publish online state, and enter idle. Hotplug disables platform CPU, migrates IRQs, flushes caches/TLBs, reports death, and calls platform die. IPI handler dispatches wakeup, timer, reschedule, call function, stop, irq_work, completion, and backtrace.

State and persistence: global `secondary_data`, `smp_ops`, `ipi_desc[]`, `ipi_irq_base`, per-CPU completions, per-CPU `cpu_data`, and cpufreq loop references.

Dependencies and integration: platform/PSCI SMP ops, scheduler, IRQ core, clock events, cpufreq, topology, MMU/TLB/cache, panic, tracepoints, and NMI backtrace.

Risks: secondary boot ordering and cache synchronization are fragile; IPIs must stay within secure-firmware usable SGIs; hotplug must not return to invalid stacks. Test signals include SMP boot, CPU hotplug, IPI statistics, panic stop, cpufreq calibration, and backtrace IPIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smp_scu.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/smp_scu.c

Purpose: controls the ARM Snoop Control Unit used by older MPCore/Cortex-A SMP systems for coherency and CPU count discovery.

Important APIs/types/functions: helpers include `scu_enable`, `scu_get_core_count`, `scu_power_mode`, and DT mapping helpers when configured.

Control flow: enable maps or receives SCU base, invalidates SCU tags/filters as required, sets the enable bit, and returns core count from SCU config. Power-mode helper adjusts per-CPU SCU power state.

State and persistence: SCU MMIO registers persist hardware coherency and power settings.

Dependencies and integration: platform SMP prepare code, device tree address mapping, cache coherency, and secondary CPU boot.

Risks: enabling SCU at the wrong time or with wrong base breaks coherency; power-mode writes are platform-sensitive. Test signals include SMP boot on SCU systems, cache coherency stress, and CPU hotplug/power mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smp_scu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smp_tlb.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/smp_tlb.c

Purpose: provides SMP-aware TLB and branch predictor flush operations, broadcasting flushes to relevant CPUs and applying Cortex-A15/Brahma-B15 erratum 798181 workarounds.

Important APIs/types/functions: `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_kernel_page`, `flush_tlb_range`, `flush_tlb_kernel_range`, `flush_bp_all`, and optional `erratum_a15_798181_init`. IPI helpers call local flush functions.

Control flow: each flush checks `tlb_ops_need_broadcast`; broadcast paths call `on_each_cpu` or `on_each_cpu_mask` with local IPI helpers, while non-broadcast paths use local flushes. User-address page/range flushes temporarily enable uaccess where required. Erratum handling may issue extra local invalidation and synchronous DMB broadcasts to affected CPUs or mm masks.

State and persistence: optional global function pointer `erratum_a15_798181_handler` encodes selected workaround level.

Dependencies and integration: MM/TLB core, SMP call functions, uaccess PAN helpers, CPU ID/revision registers, `mm_cpumask`, and setup-time erratum init.

Risks: missing a CPU in mask leaves stale translations; over-broadcast hurts performance; erratum detection must match CPU revision. Test signals include mmap/munmap stress on SMP, kernel mapping changes, A15 erratum platforms, and branch predictor flush users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smp_tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smp_twd.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/smp_twd.c

Purpose: implements the ARM local TWD timer as a per-CPU clock event device for SMP systems.

Important APIs/types/functions: timer mode callbacks `twd_shutdown`, `twd_set_oneshot`, `twd_set_periodic`, `twd_set_next_event`; interrupt handler `twd_handler`; registration paths `twd_local_timer_common_register` and OF match declarations.

Control flow: registration maps the timer, parses PPI IRQ, allocates per-CPU clockevent devices, requests percpu IRQ, installs CPU hotplug callbacks, obtains/calibrates clock rate, and sets up the boot CPU immediately or through `late_time_init`. Per-CPU setup initializes the clockevent device, registers it, and enables the PPI. Clock-rate notifier updates all CPUs after rate changes.

State and persistence: `twd_base`, `twd_clk`, `twd_timer_rate`, `twd_evt`, `twd_ppi`, feature flags, and per-CPU setup flags.

Dependencies and integration: clockevents, percpu IRQs, cpuhp, OF IRQ/address/clock APIs, jiffies calibration, and local timer hardware.

Risks: absent/incorrect clock leads to calibration dependence; rate changes must update all per-CPU devices; hotplug must disable PPIs. Test signals include timer interrupts on all CPUs, CPU hotplug, cpufreq/clock-rate changes, NOHZ/oneshot mode, and DT binding probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/smp_twd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/spectre.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/spectre.c

Purpose: reports ARM Spectre v1/v2 mitigation status through CPU vulnerability sysfs files and tracks cumulative v2 mitigation state.

Important APIs/types/functions: `cpu_show_spectre_v1`, `spectre_v2_update_state`, and `cpu_show_spectre_v2`. It checks unprivileged eBPF enablement when reporting v2 status.

Control flow: mitigation code elsewhere calls `spectre_v2_update_state` with a state and method bit. Sysfs show functions format v1 as user pointer sanitization and v2 as not affected, vulnerable, vulnerable due to unprivileged eBPF, or a mitigation method string.

State and persistence: static `spectre_v2_state` keeps the highest observed vulnerability/mitigation state; `spectre_v2_methods` ORs all mitigation methods.

Dependencies and integration: CPU vulnerability sysfs, BPF sysctl, and architecture spectre mitigation code.

Risks: status strings are user-visible security reporting; state aggregation can over/understate mixed CPU systems. Test signals include `/sys/devices/system/cpu/vulnerabilities/spectre_v*`, toggling unprivileged BPF, and CPU errata mitigation initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/spectre.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/stacktrace.c

Purpose: implements ARM stack frame unwinding and generic stack trace walking for current, saved, and register-based contexts.

Important APIs/types/functions: `unwind_frame`, `walk_stackframe`, and `arch_stack_walk`. Internal `frame_pointer_check` validates frame-pointer bounds and handles stack switches through `call_with_stack`.

Control flow: frame-pointer unwinding validates FP/SP boundaries, handles exception frames by returning saved PC from `pt_regs`, restores FP/SP/PC according to GCC or Clang prologue layout, resolves kretprobe trampolines, and marks entry text as exception frames. `arch_stack_walk` seeds frames from regs, current task, or non-current uniprocessor saved context, then invokes the consumer callback.

State and persistence: no persistent state; stackframe structure carries transient unwind state and optional kretprobe cursor.

Dependencies and integration: used by stacktrace core, perf, oops dumps, `process.c`, kprobes/kretprobes, and exception entry text markers.

Risks: unwinding arbitrary stacks is fragile, especially non-current SMP tasks; false exception frames can access invalid stack data; compiler prologue differences matter. Test signals include stacktrace selftests, oops backtraces, kretprobe traces, IRQ stack traces, and Clang/GCC builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/suspend.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/suspend.c

Purpose: provides the C half of ARM CPU suspend/resume, coordinating idmap requirements, graph tracing, MMU context restoration, CPU bug checks, and physical save-slot allocation.

Important APIs/types/functions: `cpu_suspend`, `__cpu_suspend_save`, and early init `cpu_suspend_alloc_sp`. It calls low-level `__cpu_suspend` and resumes through `cpu_resume_mmu`/`cpu_do_resume`.

Control flow: `cpu_suspend` verifies idmap page tables on MMU systems, temporarily enables uaccess when TTBR0 PAN requires it, pauses function graph tracing, calls assembly suspend with the logical MPIDR, then on successful resume switches back to active mm, flushes branch predictor/TLB, and reruns CPU bug checks. Save helper stores physical idmap PGD, virtual SP, physical resume function, invokes CPU-specific suspend save, and cleans cache/outer cache for context and save pointer. Early allocation creates an MPIDR-hash-sized physical pointer array.

State and persistence: `sleep_save_sp.save_ptr_stash` and physical counterpart persist across suspend; saved context blocks survive low-power entry.

Dependencies and integration: `sleep.S`, idmap page tables, CPU proc suspend hooks, cache/outer cache ops, MPIDR hash, KASAN/vmap stack interactions, and bugs/errata checks.

Risks: missing cache clean loses resume context; idmap absence blocks suspend; tracing must be paused around non-returning finishers. Test signals include suspend/resume, CPU idle deep states, SMP resume, TTBR0 PAN configs, and repeated suspend loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/suspend.c -->
