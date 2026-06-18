# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm.c

## Purpose
`svm.c` is the AMD SVM backend implementation for x86 KVM. It wires AMD-V hardware into the generic `kvm_x86_ops` interface: module setup, per-CPU SVM enablement, per-vCPU VMCB allocation and initialization, intercept recalculation, VM entry/exit orchestration, exception/interrupt injection, nested SVM, AVIC/APICv, SEV/SEV-ES/SNP constraints, Hyper-V-on-SVM cooperation, TSC scaling, MSR/CR/DR virtualization, SMM transitions, and feature advertisement.

The file is not Ceph-specific; it is copied Linux kernel virtualization code in the `ceph-client` source tree. Its behavioral center is the VMCB (`struct vmcb`) and the `struct vcpu_svm` state defined in `svm.h`.

## Important APIs, Types, and Functions
Key global knobs and state:

- Module parameters: `npt`, `nested`, `nrips`, `vls`, `vgif`, `lbrv`, `tsc_scaling`, `pause_filter_*`, `intercept_smi`, `vnmi`, `dump_invalid_vmcb`, `enable_device_posted_irqs`, and `enable_mediated_pmu`.
- `npt_enabled`, `nrips`, `vgif`, `vnmi`, `lbrv`, and `intercept_smi` are exported within the SVM backend and used by nested, SEV, AVIC, and Hyper-V paths.
- Per-CPU `svm_data` tracks ASID generation, host save area, SEV VMCB mappings, and Zen SRSO mitigation state.
- `iopm_base` is the global I/O permission bitmap physical address; each vCPU has its own MSRPM.

Hardware and module lifecycle:

- `kvm_is_svm_supported()` and `svm_check_processor_compat()` validate AMD/Hygon SVM availability and reject running KVM as an SEV guest.
- `svm_hardware_setup()` validates NX, configures TSC scaling, pause filtering, nested SVM exposure, NPT, MMIO masks, SEV, Hyper-V enlightenments, AVIC, vGIF, vNMI, vVMLOAD/VMSAVE, and CPU caps, then initializes per-CPU save areas.
- `svm_enable_virtualization_cpu()` takes the SVM virtualization reference, initializes ASID ranges, writes `MSR_VM_HSAVE_PA`, initializes OSVW/erratum state, TSC ratio, and PMU virtualization.
- `svm_disable_virtualization_cpu()` and `svm_hardware_unsetup()` restore host state and free per-CPU/global SVM allocations.
- `svm_init()` registers `svm_init_ops` with the common x86 KVM vendor layer and calls `kvm_init()`.

Per-VM/vCPU lifecycle:

- `svm_vm_init()` initializes SEV VM state, pause-exit disabling, AVIC VM state, and SRSO tracking.
- `svm_vm_destroy()` tears down AVIC, SEV, and SRSO tracking.
- `svm_vcpu_create()` allocates `vmcb01`, initializes SEV and AVIC vCPU state, allocates MSRPM, and switches the vCPU to VMCB01.
- `svm_vcpu_free()` leaves/free nested state, frees SEV vCPU state, VMCB01, and MSRPM.
- `init_vmcb()` programs the reset-time VMCB intercepts, control fields, segment defaults, NPT controls, pause filtering, AVIC, SEV, Hyper-V enlightenments, vNMI/vGIF/vLS, and requests intercept recalculation.
- `svm_vcpu_reset()` and `__svm_vcpu_reset()` reset VMCB and SVM-specific vCPU state such as OSVW, TSC ratio, NMI masks, and spec control shadows.

Core run/exit path:

- `svm_vcpu_run()` prepares VMCB state, handles immediate exits, assigns ASIDs via `pre_svm_run()`, syncs LAPIC/CR8 and CR2, prepares debug registers, handles SPEC_CTRL and DEBUGCTL switching, calls `svm_vcpu_enter_exit()`, restores host state, marks VMCB clean, completes partially injected interrupts, and returns a fastpath result.
- `svm_vcpu_enter_exit()` is the noinstr wrapper that transitions lockdep/guest-state accounting, enables host RFLAGS.IF while GIF is cleared, and calls assembly `__svm_vcpu_run()` or `__svm_sev_es_vcpu_run()`.
- `svm_handle_exit()` syncs CR state, performs nested-exit handling, handles VMRUN failures, honors fastpath exits, and dispatches through `svm_invoke_exit_handler()`.
- `svm_invoke_exit_handler()` indexes `svm_exit_handlers[]`, uses retpoline special cases for common exits, rejects malformed 64-bit failure exits, and prepares unexpected-exit userspace exits after optional VMCB dump.

Exit handlers and emulation:

- `svm_exit_handlers[]` maps SVM exit codes to handlers for CR/DR access, exceptions, IRQ/NMI/SMI/VINTR, PIO/MSR, task switch, shutdown, nested SVM instructions, GIF instructions, INVLPGA/INVPCID, HLT/PAUSE/monitor/mwait, RSM, bus lock, AVIC exits, NPF, and SEV VMGEXIT.
- `pf_interception()` and `npf_interception()` hand page faults to generic KVM MMU logic; NPF also handles fast MMIO, SNP private/RMP flags, and RMP-fault repair.
- `cr_interception()`, `cr_trap()`, `dr_interception()`, `msr_interception()`, `svm_get_msr()`, and `svm_set_msr()` implement register/MSR virtualization with SEV-ES access restrictions.
- `io_interception()`, `pause_interception()`, `invpcid_interception()`, `vmmcall_interception()`, and `task_switch_interception()` provide instruction-specific handling.
- `svm_check_intercept()` lets the x86 emulator ask whether an instruction should cause a nested SVM intercept, translating emulator intercept classes into SVM exit codes and staged semantics.

Interrupts, exceptions, and windows:

- `svm_inject_exception()`, `svm_inject_irq()`, `svm_inject_nmi()`, `svm_cancel_injection()`, and `svm_complete_interrupts()` manage `event_inj`, `exit_int_info`, soft interrupt RIP metadata, and reinjection after incomplete vectoring.
- `svm_update_soft_interrupt_rip()` handles AMD NextRIP shortcomings for INTn/soft exceptions and stores state needed to re-inject correctly.
- `svm_interrupt_blocked()`, `svm_nmi_blocked()`, `svm_smi_blocked()`, and their `*_allowed()` wrappers implement GIF, interrupt shadow, vNMI, nested intercept, SMM, and pending nested-run constraints.
- `svm_enable_irq_window()`, `svm_enable_nmi_window()`, and `svm_enable_smi_window()` request intercepts or single-stepping to detect delivery windows; AVIC IRQ-window inhibit is used when required.
- `svm_complete_interrupt_delivery()` and `svm_deliver_interrupt()` integrate with LAPIC/APICv, including memory ordering around vIRR and doorbell ringing.

State mutation helpers:

- `svm_set_efer()`, `svm_set_cr0()`, `svm_set_cr4()`, `svm_set_segment()`, `svm_set_rflags()`, `svm_load_mmu_pgd()`, `svm_write_tsc_offset()`, and `svm_write_tsc_multiplier()` keep generic KVM state and VMCB state synchronized while marking VMCB clean bits dirty.
- `svm_recalc_instruction_intercepts()`, `svm_recalc_msr_intercepts()`, `svm_recalc_lbr_msr_intercepts()`, and `svm_recalc_pmu_msr_intercepts()` derive intercept bitmaps from guest CPUID, SVM features, PMU mediation, SEV-ES, nested mode, userspace MSR filters, and mitigations.
- `svm_set_intercept_for_msr()` updates MSRPM read/write permissions and marks nested Hyper-V enlightenments/MSR merge state dirty.
- `new_asid()`, `svm_flush_tlb_asid()`, `svm_flush_tlb_current()`, `svm_flush_tlb_all()`, `svm_flush_tlb_gva()`, and `svm_flush_tlb_guest()` implement ASID and TLB invalidation, including Hyper-V enlightened NPT flushing.

Security and feature-specific paths:

- SEV/SEV-ES/SNP paths restrict instruction emulation, CR/MSR access, guest state visibility, VMCB initialization, VMSA handling, NPF/RMP faults, and SIPI delivery.
- `svm_check_emulate_instruction()` is a high-risk gate: plain SEV can emulate only with decode-assist bytes, SEV-ES generally cannot emulate, and AMD Erratum 1096 is handled specially.
- `svm_init_erratum_383()`, `is_erratum_383()`, and `svm_handle_mce()` handle AMD TLB multi-match erratum recovery/triple fault.
- `svm_srso_vm_init()` and `svm_srso_vm_destroy()` manage Zen SRSO BP_SPEC_REDUCE state while VMs exist.
- SPEC_CTRL, VIRT_SPEC_CTRL, DEBUGCTL, LBR virtualization, SRSO, RSB filling, and CPU buffer clearing are coordinated with the assembly path and CPU feature checks.

## Control Flow
Initialization starts at `svm_init()`: validate SVM support, register x86 vendor operations, then expose `/dev/kvm` only after common KVM init succeeds. `svm_hardware_setup()` runs before operational use and decides which runtime ops remain valid, e.g. clearing vNMI callbacks when unsupported or disabling AVIC callbacks when AVIC setup fails.

For each vCPU, `svm_vcpu_create()` allocates the VMCB/MSRPM and `svm_vcpu_reset()` calls `init_vmcb()`. `init_vmcb()` seeds the intercepts: CR/DR, exceptions, IO/MSR, SVM instructions, CPUID, RSM, PAUSE, shutdown, HLT/MWAIT, SMI, AVIC, NPT, vGIF/vNMI/vLS, and SEV. Recalculation later prunes or adds intercepts based on CPUID and runtime state.

The vCPU run loop is:

1. Generic KVM calls `svm_vcpu_pre_run()` and `svm_vcpu_run()`.
2. `svm_vcpu_run()` writes cached guest GPRs and control fields into the VMCB, assigns/flushes ASID, syncs CR8, prepares nested RIPs, TSC/Hyper-V state, debug state, mitigations, and interrupt timers.
3. `clgi()` masks host physical interrupts at the SVM GIF level, then `svm_vcpu_enter_exit()` calls assembly VMRUN.
4. On VMEXIT, guest GPRs and hardware-switched state are saved, host state/mitigations restored, `stgi()` reenables GIF, APIC/CR8 and nested metadata are synced, VMCB clean bits are reset, and partially injected events are requeued.
5. `svm_exit_handlers_fastpath()` may handle common WRMSR/HLT/INVD exits directly; otherwise generic KVM calls `svm_handle_exit()`.
6. `svm_handle_exit()` first gives nested SVM a chance to convert exits into L1-visible nested VMEXITs, then dispatches host-handled exits.

Nested SVM influences many paths. Intercepts are configured on VMCB01 and propagated to VMCB02 through nested helpers. During L2 execution, exits may be consumed by L0, reflected to L1, or handled specially before normal dispatch. SMM transitions save/restore nested host state through L1's HSAVE area and re-enter L2 after RSM when valid.

## State and Persistence Behavior
Persistent kernel objects include per-VM `struct kvm_svm`, per-vCPU `struct vcpu_svm`, per-CPU `struct svm_cpu_data`, VMCB pages, MSRPM/IOPM pages, AVIC tables, and SEV state. This file does not write filesystem data; persistence is in kernel memory, CPU MSRs, and guest-visible virtual CPU state.

VMCB clean-bit discipline is central. Helpers mark individual VMCB areas dirty after updates; `svm_vcpu_run()` marks all clean after VMRUN returns, except always-dirty interrupt/CR2 fields. Moving a VMCB to another physical CPU marks all dirty and resets ASID generation because clean bits and ASIDs are CPU-local.

Nested state persists in `svm->nested`: VMCB02, cached VMCB12 control/save fields, nested MSRPM, HSAVE/VM_CR MSRs, current VMCB GPA, last bus-lock RIP, and recalculation flags. SEV-ES state persists GHCB mappings, VMSA pointers, scratch areas, SNP PSC progress, registered GHCB GPA, and reset-hold tracking.

Interrupt state persists across exits in `event_inj`, `exit_int_info`, `nmi_masked`, `awaiting_iret_completion`, `nmi_singlestep`, `nmi_l1_to_l2`, and soft interrupt RIP snapshots. These fields are deliberately replayed after incomplete vectoring.

Host state is saved in per-CPU SVM host save areas via VMSAVE/VMLOAD. TSC ratio and TSC_AUX are switched by MSR writes/user-return MSR infrastructure. Debug and speculation-control state is manually switched when hardware does not virtualize it.

## Dependencies and Integration Points
Internal KVM dependencies:

- Generic x86 KVM APIs in `x86.h`, `kvm_cache_regs.h`, `cpuid.h`, `mmu.h`, `smm.h`, `pmu.h`, and `irq.h`.
- Nested SVM helpers declared in `svm.h` and implemented in neighboring files.
- AVIC functions declared in `svm.h`.
- SEV helpers declared in `svm.h` and implemented in `sev.c`.
- Hyper-V-on-KVM helpers from `hyperv.h`, `kvm_onhyperv.h`, and `svm_onhyperv.h`.
- Tracepoints from `arch/x86/kvm/trace.h`.

Hardware/architecture dependencies:

- AMD SVM instructions `clgi`, `stgi`, `invlpga`, `vmsave`, `vmload`, and VMRUN assembly.
- AMD MSRs including `MSR_VM_HSAVE_PA`, `MSR_AMD64_TSC_RATIO`, OSVW, VM_CR, HSAVE_PA, DE_CFG, SYSCFG, and SPEC_CTRL-family MSRs.
- CPU features such as SVM, NPT, NRIPS, vGIF, vNMI, LBRV, TSCRATEMSR, V_SPEC_CTRL, FLUSHBYASID, PAUSEFILTER, PFTHRESHOLD, ERAPS, SEV/SEV-ES/SNP, and Hyper-V nested features.

Top-level integration happens through `struct kvm_x86_ops svm_x86_ops`, which binds this file to common KVM. `svm_x86_ops` is the contract for hardware setup, vCPU lifecycle, run/exit, intercept checks, MSR/CR/segment state, MMU/TLB operations, APICv, nested ops, SMM, SEV ioctls, and guest memory callbacks.

## Risks and Edge Cases
High-risk areas:

- VMCB clean-bit bugs can cause stale hardware state because SVM avoids rewriting clean fields.
- ASID generation and TLB flushing are CPU-local and interact with nested transitions; missed invalidation can corrupt address translation.
- SEV/SEV-ES/SNP restrict visibility into guest state; emulating or decoding without valid bytes can corrupt guests or spin indefinitely.
- Interrupt/event injection is subtle because AMD reports incomplete vectoring through `exit_int_info`, while NextRIP can be absent or cleared.
- Nested SVM intercept precedence must preserve L1-visible behavior while still enforcing L0 safety; several paths explicitly warn or contain FIXME notes.
- SMM plus nested SVM depends on 64-bit SMRAM fields and L1 HSAVE mappings; bad guest state must fail rather than corrupt VMCB01.
- SPEC_CTRL/DEBUGCTL/LBR switching is security-sensitive and depends on matching C and assembly behavior.
- Hyper-V enlightened TLB paths must fall back correctly if hypercalls fail and must not skip required local ASID flushes.
- Module parameters can disable or expose features; unsupported hardware must prune ops and CPU caps consistently.

## Test Signals
Useful validation signals include:

- KVM selftests for SVM/nested SVM, state save/restore, SMM, interrupts, CR/MSR access, PMU, APICv/AVIC, Hyper-V enlightened TLB, SEV/SEV-ES/SNP, and dirty-log/MMU interactions.
- Runtime tracepoints: `kvm_entry`, `kvm_exit`, `kvm_nested_vmenter`, `kvm_nested_vmexit`, `kvm_inj_virq`, `kvm_inj_exception`, `kvm_page_fault`, `kvm_msr`, `kvm_cr`, `kvm_invlpga`, `kvm_skinit`, `kvm_ple_window_update`, `kvm_avic_*`, `kvm_vmgexit_*`, and `kvm_rmp_fault`.
- Kernel logs from `svm_hardware_setup()` feature announcements, `dump_invalid_vmcb`, erratum warnings, unsupported PMU/NX messages, and unexpected VMEXIT dumps.
- Functional smoke tests: create/destroy AMD KVM VMs, run CPUID/MSR/PIO/HLT workloads, nested AMD guests, migration/state restore, APIC interrupt storms, SMM/RSM, and SEV guest boot where supported.
