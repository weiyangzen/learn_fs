# subset-b-000684 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/emulate-nested.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/emulate-nested.c

## Purpose

This file implements the arm64 KVM nested-virtualization trap triage and nested exception injection path. It maps architectural system-register encodings to coarse-grained trap controls, fine-grained trap controls, optional fine-grained filters, and main sysreg table indexes, then uses that metadata at runtime to decide whether a trapped access is handled by KVM or forwarded into a guest hypervisor.

## Important APIs, Types, And Functions

Key types are `enum trap_behaviour`, `struct trap_bits`, `enum cgt_group_id`, `union trap_config`, and `struct encoding_to_trap_config`. The large `encoding_to_cgt[]` and `encoding_to_fgt[]` tables describe forwarding rules for EL1, EL2, debug, PMU, trace, timer, cache, TLB, pointer-authentication, GIC CPU-interface, and FGT2 registers/instructions. `populate_nv_trap_config()` builds `sr_forward_xa`; `populate_sysreg_config()` attaches normal sysreg descriptor indexes. Runtime entry points include `triage_sysreg_trap()`, `forward_smc_trap()`, `forward_debug_exception()`, `kvm_emulate_nested_eret()`, `kvm_inject_nested_sync()`, `kvm_inject_nested_irq()`, `kvm_inject_nested_sea()`, and `kvm_inject_nested_serror()`.

## Control Flow

Boot/init code inserts table entries into an xarray keyed by sysreg encoding, validates duplicate mappings, checks FGT reserved-bit masks, and destroys the xarray on configuration errors. At trap time `triage_sysreg_trap()` decodes ESR, loads the trap config, rejects unavailable features through `kvm->arch.fgu`, applies FGT read/write group selection and filters, evaluates coarse or complex conditions, and either injects a nested sync exception or returns the sysreg table index for local handling. Nested ERET and exception injection temporarily put/load vCPU state to cross virtual EL1/EL2 contexts.

## State And Persistence Behavior

The xarray is persistent global metadata after initialization. Per-vCPU decisions read and mutate virtual EL2 sysregs, PSTATE, PC, exception flags, `ESR_EL2`, `FAR_EL2`, and PMU nested transition state. Nested injection may change the active virtual context and must run with preemption disabled around put/load boundaries.

## Dependencies And Integration Points

The file depends on arm64 sysreg encodings, `asm/kvm_nested.h`, `asm/kvm_emulate.h`, PMU helpers, timer helpers, pointer-authentication helpers, `hyp/adjust_pc.h`, xarray allocation, tracepoints, and the sysreg descriptor table populated elsewhere. `handle_exit.c` calls nested ERET and SMC/debug forwarding; sysreg handlers call `triage_sysreg_trap()`.

## Risks And Test Signals

Risks are table drift versus the architecture, duplicate/ranged encodings, wrong FGT polarity for negative bits, mishandled host-EL0-only forwarding, and missing put/load transitions when changing virtual EL. Test signals include nested sysreg trap forwarding, non-nested local handling, FGT-disabled feature UNDEF injection, nested IRQ filtering by `HCR_EL2.{TGE,IMO}`, ERETAx authentication failure behavior, SEA EASE routing, and boot logs for CGT/FGT counts or mask inconsistencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/emulate-nested.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/fpsimd.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/fpsimd.c

## Purpose

This file coordinates host and guest FPSIMD/SVE register ownership around vCPU load, guest entry, guest exit, and vCPU put. It is the host-side companion to the hyp lazy-FP trap path.

## Important APIs, Types, And Functions

The exported hooks are `kvm_arch_vcpu_load_fp()`, `kvm_arch_vcpu_ctxflush_fp()`, `kvm_arch_vcpu_ctxsync_fp()`, and `kvm_arch_vcpu_put_fp()`. They use `fpsimd_save_and_flush_cpu_state()`, `guest_owns_fp_regs()`, `fpsimd_bind_state_to_cpu()`, `TIF_FOREIGN_FPSTATE`, `FP_STATE_FREE`, and `struct cpu_fp_state`.

## Control Flow

On vCPU load, host FP/SVE/SME state is saved and flushed, and hyp ownership is marked free. Just before non-preemptible guest entry, any foreign FP state observed after host kernel FP use clears ownership again. On guest exit, if the guest owns hardware FP registers, the vCPU FP or SVE backing state is bound to CPU context tracking. On vCPU put, local IRQs are disabled and guest-owned FP state is saved/flushed so later host FP use cannot consume stale guest data.

## State And Persistence Behavior

Persistent state lives in `vcpu->arch.ctxt.fp_regs`, `vcpu->arch.sve_state`, `sve_max_vl`, `fp_type`, `SVCR`, `FPMR`, host per-CPU `fp_owner`, and the current thread's `TIF_FOREIGN_FPSTATE`. The code intentionally leaves host userspace restoration to normal FPSIMD tracking.

## Dependencies And Integration Points

It integrates with scheduler FPSIMD state management, hyp `host_data_ptr(fp_owner)`, SVE/SME feature checks, and the hyp file `switch.h` that lazily restores guest FP after a trap.

## Risks And Test Signals

Risks include stale guest data exposure, incorrect SVE vector-length binding, SME state leakage, and calling paths with IRQ/preemption assumptions violated. Test signals are FP/SVE guest migration, host kernel NEON use between exits, SVE-enabled vCPU get/set state, and `WARN_ON_ONCE` triggers for SME `SVCR` or IRQ state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/fpsimd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/guest.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/guest.c

## Purpose

This file implements arm64 KVM userspace ABI helpers for vCPU register enumeration, one-register get/set, event injection/query, guest debug setup, vCPU attribute dispatch, target CPU reporting, and MTE tag copy.

## Important APIs, Types, And Functions

Key public APIs are `kvm_arm_num_regs()`, `kvm_arm_copy_reg_indices()`, `kvm_arm_get_reg()`, `kvm_arm_set_reg()`, `__kvm_arm_vcpu_get_events()`, `__kvm_arm_vcpu_set_events()`, `kvm_arch_vcpu_ioctl_set_guest_debug()`, `kvm_arm_vcpu_arch_{set,get,has}_attr()`, and `kvm_vm_ioctl_mte_copy_tags()`. Internal helpers validate core-reg offsets, SVE vector-length bitmaps, SVE register regions, and event commitment.

## Control Flow

Register ID handling first validates the arm64 namespace, then dispatches to core, firmware, SVE, or sysreg handlers. SVE register access requires a finalized SVE vCPU except for setting vector lengths before finalization. Event setting immediately commits external data aborts and may inject SError with or without ESR. MTE tag copying locks memslots, walks pages by GFN, rejects device memory, serializes dirty logging restrictions, and copies tags between user buffers and page memory.

## State And Persistence Behavior

The file reads and writes `vcpu->arch.ctxt`, FPSIMD fields, `sve_state`, `sve_max_vl`, event/exception flags, `guest_debug`, external debug state, PMU/timer/pvtime attributes, and MTE page tag state. User copies are direct ABI transfers; register setters mutate live saved vCPU state.

## Dependencies And Integration Points

It depends on sysreg table helpers, firmware register helpers, PMU/timer/pvtime devices, FPSIMD/SVE layout macros, debug tracepoints, RAS/SEA injection, MTE tag APIs, page and memslot helpers, and nested virtualization checks for EL2 PSTATE validity.

## Risks And Test Signals

Important risks are off-by-one register-list bounds, accepting invalid PSTATE modes, SVE access before finalization, missing nospec bounds on SVE offsets, dirty logging conflicts during tag writes, partial tag-copy return values, and stale exception state after userspace injection. Test signals include `KVM_GET_REG_LIST` order, SVE VLS validation, AArch32 narrowing on pstate writes, SError/SEA event round trips, guest debug exits, and MTE copy over multiple pages or hugetlb pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/guest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/handle_exit.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/handle_exit.c

## Purpose

This file is the host-side dispatcher for exceptions returned from arm64 guest execution. It translates hyp exit codes and ESR exception classes into KVM handling, userspace exits, nested reinjection, or fatal nVHE panic reporting.

## Important APIs, Types, And Functions

The main APIs are `handle_exit()`, `handle_exit_early()`, and `nvhe_hyp_panic_handler()`. Trap handlers include `handle_hvc()`, `handle_smc()`, `kvm_handle_fpasimd()`, `kvm_handle_wfx()`, `kvm_handle_guest_debug()`, `handle_sve()`, `kvm_handle_ptrauth()`, `kvm_handle_eret()`, `handle_svc()`, `kvm_handle_gcs()`, and `handle_other()`. `arm_exit_handlers[]` maps ESR ECs to these functions.

## Control Flow

`handle_exit_early()` consumes pending SError before preemption where required. `handle_exit()` strips the exception code and returns to the guest for IRQ/SError, invokes trap handling for sync traps, reports fail-entry for hyp shutdown or illegal return, and emits internal errors for unsupported classes. Trap handling checks conditional execution first, then dispatches by ESR EC. Nested guests often receive reinjected sync exceptions instead of local handling.

## State And Persistence Behavior

The code updates vCPU stats, PC, run exit reason, debug payloads, flags, nested exception state, and panic diagnostics. WFx may set `IN_WFIT`; SMC increments PC before SMCCC handling. Panic handling does not return and exposes hyp offsets for debugging.

## Dependencies And Integration Points

It integrates with SMCCC handling, nested helpers from `emulate-nested.c`, guest abort/sysreg handlers, GIC and timer paths, debug monitor state, RAS helpers, UBSAN/CFI reporting, and nVHE stacktrace dumping.

## Risks And Test Signals

Risks include wrong PC advancement for SMC/HVC/SError replay, forwarding traps into L1 incorrectly, losing debug FAR or single-step state, mishandling WFxT deadlines and offsets, and incomplete panic decoding. Test signals include SMCCC calls, nested HVC/SMC/ERET traps, WFE/WFI/ WFIT stats, guest debug exits, RAS SError injection, GCS UNDEF, and controlled hyp BUG/CFI/UBSAN panic reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/handle_exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/Makefile

## Purpose

This short Makefile wires common arm64 KVM hyp objects into the kernel build and propagates the hyp include directory to C and assembly subdirectories.

## Important APIs, Types, And Functions

It sets `incdir := $(src)/include`, adds `-I$(incdir)` through `subdir-asflags-y` and `subdir-ccflags-y`, and includes `vhe/`, `nvhe/`, and `pgtable.o` when `CONFIG_KVM` is enabled.

## Control Flow

There is no runtime control flow. Build-time control is Kconfig-gated through `obj-$(CONFIG_KVM)`.

## State And Persistence Behavior

The file persists build configuration only. It does not create runtime state.

## Dependencies And Integration Points

It is the parent build entry for VHE, nVHE, and shared hyp page-table code. The include path is required by headers such as `hyp/switch.h`, `hyp/fault.h`, and nVHE private headers.

## Risks And Test Signals

Risks are missing include paths or accidentally excluding VHE/nVHE objects. Test signals are successful `CONFIG_KVM=y/m` arm64 builds and expected object inclusion for shared `pgtable.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/aarch32.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/aarch32.c

## Purpose

This hyp file supports AArch32 guest instruction emulation by validating conditional execution and advancing Thumb/ARM PCs, including ITSTATE maintenance.

## Important APIs, Types, And Functions

The exported helpers are `kvm_condition_valid32()` and `kvm_skip_instr32()`. Internal data includes the `cc_map[16]` NZCV condition lookup table and `kvm_adjust_itstate()`.

## Control Flow

For trap classes that may be conditional, `kvm_condition_valid32()` gets the condition from ESR or Thumb IT state, evaluates it against CPSR NZCV, and tells higher-level exit code whether the trapped instruction should execute. `kvm_skip_instr32()` advances PC by 2 for 16-bit Thumb traps or 4 otherwise, then advances ITSTATE.

## State And Persistence Behavior

The file mutates `vcpu->arch.ctxt.regs.pc` and CPSR IT bits. It reads PSTATE/CPSR, trap class, trapped instruction length, and condition code.

## Dependencies And Integration Points

It is used by generic PC-adjust helpers in `hyp/adjust_pc.h` and host exit handling. It depends on arm64 KVM emulate helpers and AArch32 PSR definitions.

## Risks And Test Signals

Risks include wrong ITSTATE advancement, Thumb instruction length mistakes, and conditional traps incorrectly treated as executed. Test signals are AArch32 guests running CP15/CP14/SVC/FP trapped instructions inside IT blocks and condition-failed traps advancing without side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/aarch32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/entry.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/entry.S

## Purpose

This assembly file implements `__guest_enter()`, the low-level transition between hyp/host register context and guest register context, plus the common guest-exit save path.

## Important APIs, Types, And Functions

The exported symbol is `__guest_enter`. Important labels are `__guest_exit`, `__guest_exit_panic`, and `__guest_exit_restore_elr_and_panic`. It uses macros for callee-saved registers, `sp_el0`, loaded-vCPU tracking, MTE switching, pointer-authentication key switching, and exception-table SError recovery.

## Control Flow

Entry saves hyp callee-saved state and `sp_el0`, checks pending asynchronous exceptions, records the loaded vCPU, switches MTE/ptrauth state, restores guest registers, and executes `eret`. Exit stores guest registers back into `VCPU_CONTEXT`, restores hyp state, clears the loaded vCPU pointer, records RAS DISR state where supported, and returns an exception code possibly marked with pending SError.

## State And Persistence Behavior

It persists full guest GPR state, host hyp callee-saved state, guest/hyp `sp_el0`, ptrauth keys, MTE state, loaded-vCPU per-CPU state, and RAS DISR fault metadata.

## Dependencies And Integration Points

It is entered from hyp switch code and branches from vector code in `hyp-entry.S`. It integrates with `handle_exit.c`, ptrauth/MTE macros, RAS alternatives, and nVHE panic paths.

## Risks And Test Signals

Risks are register corruption, stale loaded-vCPU pointers, missing context-synchronization on deferred entry, ptrauth/MTE leakage, and SError window mishandling. Test signals include stress vCPU migration, async SError injection, ptrauth/MTE-enabled guests, and hyp panic paths that restore ELR before panicking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/exception.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/exception.c

## Purpose

This file emulates exception entry into AArch64 EL1/EL2 or AArch32 modes for pending KVM-injected exceptions and implements `__kvm_adjust_pc()`.

## Important APIs, Types, And Functions

Core helpers are `enter_exception64()`, `get_except32_cpsr()`, `enter_exception32()`, `kvm_inject_exception()`, and `__kvm_adjust_pc()`. It also has VHE/nVHE-specific sysreg read/write wrappers and banked AArch32 SPSR writers.

## Control Flow

When `PENDING_EXCEPTION` is set, `__kvm_adjust_pc()` calls `kvm_inject_exception()`, which selects AArch32 UND/IABT/DABT or AArch64 EL1/EL2 sync/IRQ/SError injection. Exception entry saves the old PC/PSTATE into the target ELR/SPSR, computes vector offset from source and target mode, updates PC to VBAR plus offset plus type, and constructs new PSTATE. Otherwise, `INCREMENT_PC` causes `kvm_skip_instr()`.

## State And Persistence Behavior

The code mutates PC, CPSR/PSTATE, ELR/SPSR registers, ESR/FAR-related exception state indirectly, AArch32 banked SPSRs/LRs, and vCPU flags. It preserves old state in architecture-defined return registers.

## Dependencies And Integration Points

It is called by host and hyp paths through `__kvm_adjust_pc`, and by nested exception injection before reloading a virtual EL2 context. It depends on VHE/nVHE sysreg access conventions, MTE/RAS feature checks, and AArch32 compatibility state.

## Risks And Test Signals

Risks are incorrect vector offsets, wrong PSTATE masking, writing the wrong SPSR under VHE, failing to clear pending flags, and AArch32 return-address errors. Test signals include injected undefined/data/prefetch aborts, EL2 nested sync/IRQ/SError, MTE TCO behavior, PAN/SSBS inheritance, and PC increment after emulated traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/exception.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/fpsimd.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/fpsimd.S

## Purpose

This assembly wrapper exposes hyp-callable FPSIMD and SVE save/restore entry points backed by arm64 FPSIMD macros.

## Important APIs, Types, And Functions

The symbols are `__fpsimd_save_state`, `__fpsimd_restore_state`, `__sve_restore_state`, and `__sve_save_state`. They expand to `fpsimd_save`, `fpsimd_restore`, `sve_load`, and `sve_save`.

## Control Flow

Each symbol is a straight-line wrapper: save/restore the requested vector state and return. SVE wrappers pass through their arguments to the macro implementation.

## State And Persistence Behavior

The file reads or writes architectural FP/SIMD/SVE registers and memory buffers provided by the caller. It has no static state.

## Dependencies And Integration Points

It is called from `hyp/include/hyp/switch.h` during lazy FP/SVE switching. It depends on `asm/fpsimdmacros.h` and correct caller-managed vector lengths.

## Risks And Test Signals

Risks are ABI mismatch with macro arguments, wrong active SVE VL before save/restore, and clobber assumptions around hyp calls. Test signals are FPSIMD-only and SVE guest state preservation across exits and host FP use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/fpsimd.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/hyp-constants.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/hyp-constants.c

## Purpose

This file emits compile-time constants for hyp assembly by including `asm-offsets.h` under the hyp build.

## Important APIs, Types, And Functions

It defines `KBUILD_MODNAME` as `"kvm_hyp"` and includes `../kernel/asm-offsets.c`. There are no callable functions.

## Control Flow

Only build-time constant generation occurs.

## State And Persistence Behavior

The output is generated assembler constants consumed by hyp assembly. There is no runtime state.

## Dependencies And Integration Points

It integrates arm64 KVM hyp assembly with kernel structure offsets such as vCPU context and CPU register layout.

## Risks And Test Signals

Risks are stale or missing offsets causing assembly context save/restore corruption. Test signals are successful offset generation and build failures when structure references are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/hyp-constants.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/hyp-entry.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/hyp-entry.S

## Purpose

This assembly file defines the EL2 exception vectors used while running guests and the hardened vector variants used for Spectre mitigations.

## Important APIs, Types, And Functions

Key symbols are `__kvm_hyp_vector` and `__bp_harden_hyp_vecs`. Important local handlers are `el1_sync`, `el1_trap`, `el1_irq`, `el1_error`, `el2_sync`, `el2_error`, and generated invalid vectors. Macros include `save_caller_saved_regs_vect`, `restore_caller_saved_regs_vect`, `valid_vect`, `invalid_vect`, `hyp_ventry`, and `generate_vectors`.

## Control Flow

EL1 sync traps decode ESR EC, fast-return known SMCCC workaround HVCs, or branch to `__guest_exit` with `ARM_EXCEPTION_TRAP`. IRQ/FIQ and SError exits also branch to `__guest_exit`. Unexpected EL2 exceptions call `kvm_unexpected_el2_exception()` and retry via adjusted ELR or panic path. Hardened vector tables add ESB, BTI, BHB mitigation, optional SMC workaround, and indirect branch patch slots.

## State And Persistence Behavior

The file manipulates stack-saved caller registers, ESR/ELR/SPSR, vCPU pointer recovery, and exception return state. It does not own persistent data, but its vector table contents are patched by alternatives.

## Dependencies And Integration Points

It connects CPU exception vector entry to `entry.S`, `switch.h`, Spectre mitigation infrastructure, SMCCC workaround IDs, and vector branch patching.

## Risks And Test Signals

Risks include broken vector alignment/preamble length, missed BTI/mitigation requirements, clobbered HVC registers, and invalid EL2 exception recovery loops. Test signals are HVC workaround fast paths, trap/IRQ/SError exits, Spectre vector patching, illegal exception return handling, and hyp panic on invalid vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/hyp-entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/adjust_pc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/adjust_pc.h

## Purpose

This header provides inline helpers for advancing guest or host PCs after emulated instructions.

## Important APIs, Types, And Functions

Functions are `kvm_skip_instr()`, `__kvm_skip_instr()`, and `kvm_skip_host_instr()`.

## Control Flow

`kvm_skip_instr()` dispatches to AArch32 skip logic or advances AArch64 PC by 4 and clears BTYPE, then clears single-step state. `__kvm_skip_instr()` synchronizes live EL2 ELR/SPSR into vCPU state, skips, and writes adjusted values back. `kvm_skip_host_instr()` advances host ELR by 4.

## State And Persistence Behavior

It mutates guest PC, CPSR/PSTATE, EL2 ELR/SPSR, BTYPE, and single-step bits.

## Dependencies And Integration Points

It is included by hyp exception, switch, and nested code. AArch32 support comes from `kvm_skip_instr32()`.

## Risks And Test Signals

Risks are incorrect instruction length, stale live sysreg state during hyp emulation, and leaving single-step/BTYPE active. Test signals include emulated sysregs, VGIC MMIO fast paths, AArch32 Thumb traps, and host instruction skip after nVHE host traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/adjust_pc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/debug-sr.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/debug-sr.h

## Purpose

This header implements common hyp debug-register save/restore helpers for switching between host and guest debug contexts.

## Important APIs, Types, And Functions

Macros `save_debug()` and `restore_debug()` unroll breakpoint/watchpoint register transfers. Helpers include `__vcpu_debug_regs()`, `__debug_save_state()`, `__debug_restore_state()`, `__debug_switch_to_guest_common()`, and `__debug_switch_to_host_common()`.

## Control Flow

Switch helpers first check whether debug registers are in use. They select either guest-owned or external host-owned debug state based on `debug_owner`, save current host or guest debug registers, and restore the target context.

## State And Persistence Behavior

The code persists BCR/BVR/WCR/WVR arrays and `MDCCINT_EL1` in `kvm_guest_debug_arch` and `kvm_cpu_context`. It uses host per-CPU `debug_brps` and `debug_wrps` counts.

## Dependencies And Integration Points

It is shared by VHE/nVHE debug switching code and userspace debug setup in `guest.c`.

## Risks And Test Signals

Risks are wrong owner selection, register count mismatches, and leaked host debug configuration into guests. Test signals include guest hardware break/watchpoints, host single-step debugging while running guests, and debug-owner transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/debug-sr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/fault.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/fault.h

## Purpose

This header gathers guest fault metadata at hyp, including reconstructing HPFAR when hardware did not provide a valid value.

## Important APIs, Types, And Functions

Helpers are `__fault_safe_to_translate()`, `__translate_far_to_hpfar()`, `__hpfar_valid()`, and `__get_fault_info()`.

## Control Flow

`__get_fault_info()` reads FAR and decides whether HPFAR is architecturally valid. If not, it rejects unsafe external abort cases or performs an AT S1 translation of FAR, restores PAR, converts PAR to HPFAR, and marks HPFAR valid using the Non-secure bit.

## State And Persistence Behavior

It fills `struct kvm_vcpu_fault_info` with `far_el2` and `hpfar_el2`; it temporarily reads/writes `PAR_EL1`.

## Dependencies And Integration Points

It is used by `switch.h` memory-abort handlers before returning to host abort code. It depends on fault-status helpers, POE-aware AT selection, and erratum 834220 handling.

## Risks And Test Signals

Risks are unsafe translation after external abort, incorrect HPFAR validity for S1PTW faults, PAR corruption, and erratum misclassification. Test signals are guest stage-2 faults, permission/access-flag/address-size faults, S1PTW faults, SEA/SECC cases, and CPUs with erratum 834220.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/fault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/switch.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/switch.h

## Purpose

This header contains most inline hyp world-switch logic: trap activation/deactivation, FP/SVE lazy handling, fast sysreg/MMIO exits, fault population, exit fixup, and unexpected EL2 exception recovery.

## Important APIs, Types, And Functions

Important helpers include `__activate_cptr_traps_*()`, `__activate_traps_common()`, `___activate_traps()`, `___deactivate_traps()`, `kvm_hyp_handle_fpsimd()`, `kvm_hyp_handle_sysreg()`, `kvm_hyp_handle_dabt_low()`, `kvm_hyp_handle_exit()`, `synchronize_vcpu_pstate()`, `__fixup_guest_exit()`, and `__kvm_unexpected_el2_exception()`.

## Control Flow

Before guest entry, KVM programs CPTR/CPACR, PMU user traps, HCRX, FGT/ICH-FGT registers, MPAM traps, and optional vSError ESR. Hyp exit fixup records ESR, adjusts HVC ELR when SError is pending, gives fast handlers a chance to resolve FP/SVE, VGIC, timer counter, CPU erratum, or memory-fault cases, and otherwise returns to host. FP traps lazily disable traps, save protected-host FP if needed, restore guest FP/SVE, and re-enable the correct trap mask.

## State And Persistence Behavior

The header saves and restores host sysregs in `host_ctxt`, mutates live CPTR/CPACR/HCR/HCRX/FGT/MPAM/PMUSERENR/VSESR state, updates vCPU fault info, FP owner, SVE ZCR, PC/PSTATE, and vCPU flags.

## Dependencies And Integration Points

It integrates with VGIC v2/v3 CPU-interface emulation, timer offsets, nested virtualization, pKVM, PMU, SVE/FPSIMD assembly helpers, CPU errata, MPAM, HCRX/FGT features, and exception tables.

## Risks And Test Signals

Risks are wrong trap masks under VHE/nVHE/nested modes, lost host sysregs, unhandled CPU errata, stale SVE VL, incorrect vSError preservation, and returning to guest after incomplete fixup. Test signals include first FP/SVE access, nested trap layering, PMU user access, CNTxCT fast reads, VGIC CPUif traps, Cavium/Ampere errata, memory abort HPFAR population, and unexpected EL2 exception-table fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/switch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/sysreg-sr.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/sysreg-sr.h

## Purpose

This header defines inline system-register save/restore routines for host and guest CPU contexts during hyp world switch.

## Important APIs, Types, And Functions

Key helpers are `ctxt_to_vcpu()`, `ctxt_is_guest()`, `ctxt_mdscr_el1()`, `ctxt_midr_el1()`, `__sysreg_save_common_state()`, `__sysreg_save_user_state()`, `__sysreg_save_el1_state()`, `__sysreg_save_el2_return_state()`, matching restore functions, `to_hw_pstate()`, and AArch32 `__sysreg32_{save,restore}_state()`.

## Control Flow

Save functions snapshot common debug/POE, user TPIDR, EL1 translation/control/fault/timer/thread state, optional MTE/TCR2/PIE/POE/SCTLR2 state, return ELR/PSTATE, and RAS DISR/VDISR. Restore functions write VPIDR/VMPIDR and EL1 state, handle speculative AT workaround ordering, translate virtual EL2 PSTATE to hardware EL1 PSTATE, and restore RAS virtual-disrupt state.

## State And Persistence Behavior

The file moves state between live sysregs and `struct kvm_cpu_context::sys_regs`, plus banked AArch32 fields. Feature availability gates optional state fields.

## Dependencies And Integration Points

It is used by VHE/nVHE switch code and depends on KVM feature filtering, writable IMP ID regs, MTE, RAS, S1PIE/S1POE/TCR2/SCTLR2, and speculative AT erratum handling.

## Risks And Test Signals

Risks are restoring host and guest contexts in the wrong order, missing optional feature state, unsafe POR_EL0 timing affecting uaccess, and wrong virtual EL2 PSTATE translation. Test signals include guest sysreg persistence across exits, MTE/TCR2/POE/PIE guests, writable MIDR exposure, AArch32 banked register tests, and speculative-AT workaround platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/sysreg-sr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/arm-smccc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/arm-smccc.h

## Purpose

This nVHE header wraps SMCCC SMC calls so EL2 tracing records a hyp exit and re-entry around firmware calls.

## Important APIs, Types, And Functions

Macros are `hyp_smccc_1_1_smc(...)` and `hyp_smccc_1_2_smc(...)`.

## Control Flow

Each macro emits `trace_hyp_exit(NULL, HYP_REASON_SMC)`, performs the underlying SMCCC SMC call, then emits `trace_hyp_enter(NULL, HYP_REASON_SMC)`.

## State And Persistence Behavior

No persistent state is owned here, but tracing side effects may reserve and commit hyp trace entries.

## Dependencies And Integration Points

It depends on `linux/arm-smccc.h` and `asm/kvm_hypevents.h`, and is used by nVHE code paths making firmware calls.

## Risks And Test Signals

Risks are trace recursion or missing enter/exit balance around SMC. Test signals are nVHE trace streams showing SMC intervals and firmware calls preserving SMCCC results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/arm-smccc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/clock.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/clock.h

## Purpose

This header declares the nVHE tracing clock interface and compiles it to no-ops when EL2 tracing is disabled.

## Important APIs, Types, And Functions

APIs are `trace_clock_update()` and `trace_clock()`.

## Control Flow

With `CONFIG_NVHE_EL2_TRACING`, callers can update clock conversion parameters and read a nanosecond timestamp. Without tracing, update is empty and reads return 0.

## State And Persistence Behavior

The enabled implementation persists conversion parameters in `clock.c`; the disabled inline version has no state.

## Dependencies And Integration Points

It is consumed by nVHE trace infrastructure and host hypcalls that update EL2 trace clock data.

## Risks And Test Signals

Risks are accidentally relying on nonzero timestamps when tracing is disabled. Test signals are trace timestamps changing after `__tracing_update_clock()` and zero timestamps in non-tracing builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/define_events.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/define_events.h

## Purpose

This header materializes hyp event ID objects for each event declared in `asm/kvm_hypevents.h`.

## Important APIs, Types, And Functions

It redefines `HYP_EVENT()` to emit `struct hyp_event_id hyp_event_id_<name>` in a dedicated `.hyp.event_ids.<name>` section with `.enabled = ATOMIC_INIT(0)`.

## Control Flow

There is no runtime flow in the header itself. Inclusion expands the event list and creates linker-visible event descriptors.

## State And Persistence Behavior

Each event gets persistent hyp data containing at least an enabled atomic and later assigned IDs.

## Dependencies And Integration Points

It feeds `events.c` and nVHE tracing. The linker exposes `__hyp_event_ids_start/end`.

## Risks And Test Signals

Risks are section naming/linker ordering mismatches and event-list macro drift. Test signals are valid event ID ranges and successful enable/disable by event index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/define_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/early_alloc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/early_alloc.h

## Purpose

This header declares the simple early allocator used while initializing nVHE/pKVM page tables and memory before the normal hyp pool is ready.

## Important APIs, Types, And Functions

APIs are `hyp_early_alloc_init()`, `hyp_early_alloc_nr_used_pages()`, `hyp_early_alloc_page()`, `hyp_early_alloc_contig()`, and exported `hyp_early_alloc_mm_ops`.

## Control Flow

Initialization provides a virtual base and size; later page-table code obtains zeroed pages or contiguous page runs through the mm-ops callbacks.

## State And Persistence Behavior

Implementation stores a bump-pointer range (`base`, `cur`, `end`) and mm operation callbacks. There is no free path.

## Dependencies And Integration Points

It integrates with `struct kvm_pgtable_mm_ops` and nVHE setup/mapping code.

## Risks And Test Signals

Risks are exhausting the early range, requesting zero pages, and leaking allocations because the allocator is monotonic. Test signals include pKVM initialization page counts and failure when the supplied pool is too small.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/early_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/ffa.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/ffa.h

## Purpose

This header declares the nVHE FF-A proxy initialization and host-call handling interfaces.

## Important APIs, Types, And Functions

It defines FF-A function-number bounds `FFA_MIN_FUNC_NUM` and `FFA_MAX_FUNC_NUM`, and declares `hyp_ffa_init()` and `kvm_host_ffa_handler()`.

## Control Flow

The implementation initializes proxy pages, then host SMC handling can dispatch FF-A function IDs through `kvm_host_ffa_handler()`.

## State And Persistence Behavior

The header owns no state; implementation state includes proxy page mappings and FF-A mediation data.

## Dependencies And Integration Points

It integrates nVHE host SMC handling, pKVM memory sharing, and FF-A firmware calls.

## Risks And Test Signals

Risks are accepting out-of-range function IDs, bad proxy page ownership, and leaking secure-world shared memory state. Test signals are FF-A init failure/success, host FF-A SMC forwarding, and share/unshare paths with pKVM enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/ffa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/gfp.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/gfp.h

## Purpose

This header declares the nVHE hyp page-pool allocator used after early boot.

## Important APIs, Types, And Functions

`struct hyp_pool` contains a ticket spinlock, buddy free lists, range bounds, and max order. APIs include `hyp_alloc_pages()`, `hyp_split_page()`, `hyp_get_page()`, `hyp_put_page()`, and `hyp_pool_init()`.

## Control Flow

Callers initialize a pool over a PFN range with reserved pages, allocate pages by order, split compound pages, and adjust references. Freed used pages are constrained by allocator semantics and ownership rules.

## State And Persistence Behavior

State lives in the pool lock, free lists, page refcounts, page order metadata, and physical range fields.

## Dependencies And Integration Points

It uses `nvhe/memory.h` for `struct hyp_page` and `nvhe/spinlock.h` for EL2 locking. It backs pKVM VM pools, page tables, and memory-protection operations.

## Risks And Test Signals

Risks are lock misuse, double free/refcount corruption, out-of-range pages, and reserved page handling. Test signals include pKVM page allocation/free stress, lock assertions, and pool initialization with reserved bootstrap pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/gfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/mem_protect.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/mem_protect.h

## Purpose

This header declares pKVM/nVHE memory ownership, sharing, donation, reclaim, host stage-2, and guest stage-2 protection interfaces.

## Important APIs, Types, And Functions

It defines `struct host_mmu`, `enum pkvm_component_id`, exports `host_mmu`, and declares many `__pkvm_*` host/hyp/guest share, unshare, donate, reclaim, permission, young-bit, VM teardown, and memcache functions. `__load_host_stage2()` loads host stage-2 or disables `VTTBR_EL2`.

## Control Flow

Callers finalize protection, prepare host/guest stage-2 tables, perform ownership transitions under locking, handle host memory aborts, pin/unpin shared memory, reclaim page-table pages, and refill hyp memcaches. `__load_host_stage2()` selects protected host stage-2 once protected mode is initialized.

## State And Persistence Behavior

Persistent state includes host stage-2 page tables, host MMU lock, hyp vmemmap ownership states, guest PTE software ownership bits, memcaches, and pKVM component ownership.

## Dependencies And Integration Points

It integrates with pKVM VM structures, hyp allocator, spinlocks, FFA sharing, host S2 loading, and KVM page-table walkers.

## Risks And Test Signals

Risks are ownership leaks, wrong lock order, stale host S2 mappings, reclaiming live guest pages, and mismatched permissions. Test signals are pKVM protected boot, host share/unshare/donate workflows, guest page reclaim, host abort handling, and ownership selftests under `CONFIG_NVHE_EL2_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/mem_protect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/memory.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/memory.h

## Purpose

This header defines nVHE hyp memory metadata, address conversion helpers, ownership-state encoding, and `struct hyp_page` refcount helpers.

## Important APIs, Types, And Functions

Important pieces include `enum pkvm_page_state`, `struct hyp_page`, `hyp_phys_to_virt()`, `hyp_virt_to_phys()`, PFN/page conversion macros, `get_host_state()`, `set_host_state()`, `get_hyp_state()`, `set_hyp_state()`, `hyp_page_count()`, `hyp_page_ref_inc()`, `hyp_page_ref_dec()`, `hyp_page_ref_dec_and_test()`, and `hyp_set_page_refcounted()`.

## Control Flow

Most functions are direct conversions or metadata accessors. Hyp-state storage is XOR-compressed with `PKVM_PAGE_STATE_VMEMMAP_MASK` so the vmemmap layout can preserve compact ownership bits.

## State And Persistence Behavior

State lives in the global hyp vmemmap (`hyp_vmemmap`), per-page host/hyp ownership fields, pool pointer/order metadata, and 16-bit refcount.

## Dependencies And Integration Points

It is used by the hyp allocator, memory-protection code, early allocator mm ops, and pKVM ownership selftests.

## Risks And Test Signals

Risks include refcount overflow/underflow, bad phys/virt translation offset, corrupted compact ownership state, and misuse without pool locking. Test signals are page ownership transitions, allocator refcount assertions, pKVM vmemmap backing, and address conversion tests across the hyp VA range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/mm.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/mm.h

## Purpose

This header declares nVHE/pKVM hypervisor virtual-memory setup and mapping APIs.

## Important APIs, Types, And Functions

It exports `pkvm_pgtable` and `pkvm_pgd_lock`, and declares fixmap/fixblock helpers, `hyp_create_idmap()`, `hyp_map_vectors()`, `hyp_back_vmemmap()`, `pkvm_cpu_set_vector()`, mapping creation helpers, `__pkvm_create_private_mapping()`, `pkvm_create_stack()`, and `pkvm_alloc_private_va_range()`.

## Control Flow

Callers create the hyp ID map, map vectors, back the vmemmap, allocate private VA ranges, create protected mappings, and temporarily map physical pages through per-CPU fixmap/fixblock slots.

## State And Persistence Behavior

Persistent state includes the protected hyp page table, page-table lock, private VA allocator state in implementation, vector mapping, fixmap slots, and vmemmap backing.

## Dependencies And Integration Points

It integrates with nVHE setup, pKVM stack creation, host/hyp sharing, protected mappings, and spectre vector selection.

## Risks And Test Signals

Risks are missing lock coverage, VA range exhaustion, stale fixmap entries, executable vector mapping mistakes, and private mapping permission errors. Test signals are pKVM init, per-CPU stack mappings, vector remap selection, fixmap map/unmap pairing, and vmemmap access during allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/pkvm.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/pkvm.h

## Purpose

This header defines protected KVM hyp-side VM/vCPU containers and declares pKVM VM lifecycle and protected guest trap interfaces.

## Important APIs, Types, And Functions

`struct pkvm_hyp_vcpu` embeds a trusted hyp `struct kvm_vcpu`, an untrusted host-vCPU backpointer, and loaded-vCPU tracking. `struct pkvm_hyp_vm` embeds a trusted `struct kvm`, host backpointer, guest stage-2 page table, pool, lock, and flexible vCPU array. APIs include VM table init/reserve/unreserve/init, vCPU init/load/put, VM lookup/refcount helpers, teardown/reclaim functions, and protected trap handlers.

## Control Flow

Host hypcalls reserve a VM handle, initialize hyp VM/vCPU copies, load a hyp vCPU for execution, then put it back. Teardown transitions through start/finalize phases and can reclaim dying guest pages.

## State And Persistence Behavior

Persistent trusted state is maintained entirely at hyp for protected VMs and vCPUs, with backpointers to untrusted host objects. The VM table is protected by `vm_table_lock`.

## Dependencies And Integration Points

It integrates with pKVM memory protection, hyp allocator, host hypcall dispatch, protected sysreg/HVC handling, and KVM protected VM feature checks.

## Risks And Test Signals

Risks are stale host backpointers, handle lifetime bugs, loaded-vCPU pointer leaks, guest page reclaim races, and untrusted host state confusion. Test signals are protected VM creation/destruction, vCPU load/put nesting, invalid handle rejection, and protected HVC/sysreg trap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/pkvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/spinlock.h

## Purpose

This header implements a standalone nVHE EL2 ticket spinlock, independent of normal kernel locking.

## Important APIs, Types, And Functions

It defines `hyp_spinlock_t`, `DEFINE_HYP_SPINLOCK`, `hyp_spin_lock_init()`, `hyp_spin_lock()`, `hyp_spin_unlock()`, `hyp_spin_is_locked()`, and debug-only `hyp_assert_lock_held()`.

## Control Flow

Lock acquisition atomically increments the next ticket using LSE or LL/SC, then waits with `wfe` until owner matches. Unlock increments owner with release semantics. Debug assertion checks lock state only after protected mode initialization.

## State And Persistence Behavior

Lock state is a 32-bit ticket word split into `owner` and `next`. It is persistent wherever embedded in hyp structures.

## Dependencies And Integration Points

It is used by pKVM pools, VM tables, memory-protection locks, and MM locks where normal kernel primitives cannot run at EL2.

## Risks And Test Signals

Risks are memory ordering bugs, endianness field mistakes, ticket overflow under extreme contention, and assertions before all CPUs enter EL2. Test signals are allocator and memory-protection stress, LSE and LL/SC builds, and `CONFIG_NVHE_EL2_DEBUG` lock assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/trace.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/trace.h

## Purpose

This header defines the nVHE EL2 tracing interface, including remote event formatting, event emission helpers, and host-call entry points for trace control.

## Important APIs, Types, And Functions

It provides `__tracing_get_vcpu_pid()`, the `HYP_EVENT()` expansion for trace emitters, `tracing_reserve_entry()`, `tracing_commit_entry()`, and control APIs `__tracing_load()`, `__tracing_unload()`, `__tracing_enable()`, `__tracing_swap_reader()`, `__tracing_update_clock()`, `__tracing_reset()`, and `__tracing_enable_event()`.

## Control Flow

When tracing is enabled, each generated `trace_<event>()` checks the event atomic, reserves a remote entry, writes the event ID and assignment payload, and commits. Without tracing, emitters are inline no-ops and control APIs return `-ENODEV` or do nothing.

## State And Persistence Behavior

Enabled builds persist descriptor mappings, event IDs, per-event enabled atomics, ring-buffer state, and clock data. The helper derives PID from the running vCPU in host context.

## Dependencies And Integration Points

It integrates with `linux/trace_remote_event.h`, `asm/kvm_hyptrace.h`, `asm/kvm_hypevents.h`, and nVHE host hypcalls in `hyp-main.c`.

## Risks And Test Signals

Risks are tracing from unsafe contexts, failed reservations, stale vCPU PID, and host-controlled descriptor trust boundaries. Test signals are enable/disable event filtering, buffer swap/reset, clock updates, and trace output for hyp enter/exit events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/trap_handler.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/trap_handler.h

## Purpose

This header declares nVHE host trap-handling entry points for exceptions taken from the host into protected hyp.

## Important APIs, Types, And Functions

It declares `handle_trap()` and `handle_host_mem_abort()`.

## Control Flow

The implementation dispatches host traps, including memory aborts, based on the host CPU context and ESR/FAR state.

## State And Persistence Behavior

The header owns no state; implementations mutate host context, host stage-2 mappings, and injected host exceptions.

## Dependencies And Integration Points

It integrates with nVHE hyp-main trap dispatch and pKVM memory protection.

## Risks And Test Signals

Risks are misrouting host faults, failing to inject host exceptions, or corrupting host context. Test signals are protected-mode host memory aborts, host SMC/HVC traps, and pKVM permission faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/trap_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/Makefile

## Purpose

This Makefile builds the nVHE hypervisor object as isolated `.nvhe.o` files, links them with a hyp linker script, generates runtime relocation metadata, and prefixes symbols for final linking into `vmlinux`.

## Important APIs, Types, And Functions

Important variables are `asflags-y`, `ccflags-y`, `hyp-obj-y`, `hyp-obj`, `targets`, `LDFLAGS_kvm_nvhe.tmp.o`, and `LDFLAGS_kvm_nvhe.rel.o`. Build commands include `cc_o_c`, `as_o_S`, `cpp_lds_S`, `ld`, `hyprel`, and `hypcopy`.

## Control Flow

The build compiles sources to `.nvhe.o`, preprocesses `hyp.lds`, partially links objects into `kvm_nvhe.tmp.o`, runs `gen-hyprel` to create relocation assembly, links relocations into `kvm_nvhe.rel.o`, and uses objcopy to prefix symbols with `__kvm_nvhe_`.

## State And Persistence Behavior

The file creates build artifacts, not runtime state. It also removes ftrace, SCS, unwind, async unwind, and some profiling flags for isolated hyp code.

## Dependencies And Integration Points

It includes shared hyp objects, lib routines, SMCCC call code, optional tracing, optional hardened list debug, and optional UBSAN trap mode.

## Risks And Test Signals

Risks are relocation-generation failures, symbol collisions, forbidden instrumentation entering hyp code, missing shared objects, and unsupported LLVM SHT_REL profile sections. Test signals are successful `kvm_nvhe.o` generation, prefixed symbols, no ftrace/SCS instrumentation, and UBSAN/trace configuration builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/cache.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/cache.S

## Purpose

This assembly file provides position-independent nVHE cache maintenance helpers copied from arm64 MM code.

## Important APIs, Types, And Functions

Symbols are `__pi_dcache_clean_inval_poc` with alias `dcache_clean_inval_poc`, and `__pi_icache_inval_pou` with alias `icache_inval_pou`.

## Control Flow

The data-cache helper runs a clean+invalidate by line to PoC and returns. The I-cache helper returns after an ISB when DIC makes explicit invalidation unnecessary; otherwise it invalidates I-cache by line to PoU.

## State And Persistence Behavior

It affects CPU caches for caller-provided address ranges and has no persistent variables.

## Dependencies And Integration Points

It is used by nVHE mapping/setup code that needs cache coherency without normal kernel helpers.

## Risks And Test Signals

Risks are wrong range arguments, missing barriers, and incorrect DIC alternative behavior. Test signals are self-modifying/vector mapping paths and pKVM code/data mapping coherency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/cache.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/clock.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/clock.c

## Purpose

This file implements the nVHE tracing clock used to convert architectural counter cycles into nanoseconds at EL2.

## Important APIs, Types, And Functions

It defines `trace_clock_data`, helper `__clock_mult_uint128()`, and APIs `trace_clock_update()` and `trace_clock()`.

## Control Flow

`trace_clock_update()` validates multiplier/shift, writes the inactive bank of conversion parameters, computes overflow threshold, and publishes the new bank with release ordering. `trace_clock()` acquire-loads the active bank, subtracts epoch cycles from `CNTVCT`, uses fast 64-bit multiply when safe, falls back to 128-bit multiply on overflow risk, and adds epoch nanoseconds.

## State And Persistence Behavior

State is a double-buffered static clock structure containing two parameter banks and the current bank selector. Host-provided data is treated as untrusted but read locklessly.

## Dependencies And Integration Points

It depends on arch timer counter reads, division helpers, and nVHE tracing control paths that call `__tracing_update_clock()`.

## Risks And Test Signals

Risks are invalid host conversion parameters, torn bank reads, overflow, and non-monotonic timestamps after bad epochs. Test signals include clock update calls, tracing timestamps before/after bank swaps, large cycle deltas triggering 128-bit conversion, and disabled tracing builds via `clock.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/debug-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/debug-sr.c

## Purpose

This nVHE file extends common debug register switching with host SPE/TRBE trace-buffer save, drain, disable, and restore handling.

## Important APIs, Types, And Functions

Important helpers include `__debug_save_spe()`, `__debug_restore_spe()`, `__trace_do_switch()`, `__trace_drain_and_disable()`, and corresponding trace restore logic later in the file, plus public nVHE debug switch entry points.

## Control Flow

When switching away from the host, the code saves SPE buffer/control state if enabled, disables data generation, drains buffered data with `psb_csync()`/`dsb`, disables profiling buffers, switches TRFCR, drains TRBE if active, and handles CPU workaround 2064142 with an extra drain. Restore reverses buffer/control registers after synchronization.

## State And Persistence Behavior

State is stored in per-CPU `host_debug_state` fields such as `pmscr_el1`, `pmblimitr_el1`, and `trblimitr_el1`. It also touches live SPE/TRBE/TRFCR sysregs and host-data flags.

## Dependencies And Integration Points

It depends on common `hyp/debug-sr.h`, protected-mode flags, SPE/TRBE feature bits, trace barriers, and nVHE world-switch paths.

## Risks And Test Signals

Risks are host trace DMA after stage-2/trap changes, lost profiling data, missing workaround drain, and exposing host tracing buffers to protected guests. Test signals are SPE/TRBE enabled on host while running guests, protected-mode transitions, trace-buffer drain validation, and debug-register switch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/debug-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/early_alloc.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/early_alloc.c

## Purpose

This file implements the nVHE early bump allocator and page-table mm-ops used during hyp initialization.

## Important APIs, Types, And Functions

It defines `hyp_early_alloc_mm_ops`, `hyp_physvirt_offset`, static `base/end/cur`, and implements `hyp_early_alloc_nr_used_pages()`, `hyp_early_alloc_contig()`, `hyp_early_alloc_page()`, and `hyp_early_alloc_init()`.

## Control Flow

Initialization sets the allocation range and installs mm-op callbacks for zero-page allocation and phys/virt translation. Contiguous allocation rejects zero-page requests and insufficient space, returns the current pointer, advances by page count, and zeroes the allocation.

## State And Persistence Behavior

Allocator state is a monotonic range; allocations are never freed. `hyp_early_alloc_mm_ops` persists for page-table construction. `hyp_physvirt_offset` is read-only after init.

## Dependencies And Integration Points

It integrates with nVHE setup and KVM page-table code using `struct kvm_pgtable_mm_ops`.

## Risks And Test Signals

Risks are pool exhaustion, alignment assumptions inherited from callers, zeroing too much or too little, and using early mm-ops after the intended init phase. Test signals include used-page counts, pKVM init with small pools, and page-table mappings backed by early allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/early_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/events.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/events.c

## Purpose

This file implements enabling and disabling individual nVHE hyp trace events.

## Important APIs, Types, And Functions

The main API is `__tracing_enable_event(unsigned short id, bool enable)`. It uses event descriptors emitted by `nvhe/define_events.h`.

## Control Flow

The function indexes `__hyp_event_ids_start` by event ID, validates it is before `__hyp_event_ids_end`, maps the physical address of the event's `enabled` atomic through the hyp fixmap, writes the boolean value, and unmaps the fixmap.

## State And Persistence Behavior

It mutates the per-event `enabled` atomic in hyp event ID storage. The fixmap mapping is temporary and must be paired.

## Dependencies And Integration Points

It depends on `nvhe/mm.h` fixmap helpers, `nvhe/trace.h`, and event descriptors generated by `define_events.h`. Host trace-control hypcalls invoke it.

## Risks And Test Signals

Risks are out-of-range event IDs, stale fixmap mappings, and writing through incorrect physical addresses. Test signals include event enable/disable by ID, invalid ID returning `-EINVAL`, and trace emission only when the selected atomic is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/events.c -->
