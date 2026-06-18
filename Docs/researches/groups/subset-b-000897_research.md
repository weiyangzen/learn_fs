# subset-b-000897 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm.h

## Purpose
`svm.h` is the central private header for the AMD SVM KVM backend. It defines SVM-specific VM/vCPU/per-CPU state, VMCB clean-bit and intercept helpers, MSRPM bit helpers, SEV/SEV-ES/SNP state abstractions and stubs, nested SVM contracts, AVIC contracts, Hyper-V/SEV assembly entry declarations, and GHCB accessor helpers.

The header is the shared state contract that lets `svm.c`, nested SVM, AVIC, SEV, and Hyper-V support manipulate the same VMCB-backed machine state consistently.

## Important APIs, Types, and Functions
Core constants and globals:

- `IOPM_SIZE` and `MSRPM_SIZE` define AMD I/O and MSR permissions map sizes.
- External feature knobs include `npt_enabled`, `nrips`, `vgif`, `intercept_smi`, `vnmi`, and `lbrv`.
- `VMCB_*` clean-bit enum defines dirty tracking fields for intercepts, permission maps, ASID, interrupts, NPT, CRs, DRs, descriptor tables, segments, CR2, LBR, AVIC, CET, and software state.
- `VMCB_ALL_CLEAN_MASK` and `VMCB_ALWAYS_DIRTY_MASK` encode what hardware can treat as clean and what KVM always writes before VMRUN.

Major types:

- `struct kvm_sev_info` holds per-VM SEV/SEV-ES/SNP state: activation flags, ASID, firmware handle, policy, locked pages, registered regions, AP jump table, VMSA features, GHCB version, encryption-context ownership/mirrors, cgroup accounting, migration flag, SNP context, guest-request bounce buffers, run CPU mask, and certificate support.
- `struct kvm_svm` embeds `struct kvm` and adds AVIC VM identifiers/tables plus optional SEV info.
- `struct kvm_vmcb_info` packages a VMCB pointer, physical address, last CPU, and ASID generation.
- `struct vmcb_save_area_cached` and `struct vmcb_ctrl_area_cached` snapshot guest-visible VMCB state and controls for nested virtualization.
- `struct svm_nested_state` stores VMCB02, nested MSRs, VMCB12 GPA tracking, nested MSRPM, cached VMCB12 control/save state, initialization and MSRPM recalc flags, and last nested bus-lock RIP.
- `struct vcpu_sev_es_state` tracks per-vCPU SEV-ES/SNP GHCB/VMSA state, scratch areas, PSC state, registered GHCB GPA, and AP reset/VMSA ownership flags.
- `struct vcpu_svm` embeds `struct kvm_vcpu` first and adds VMCB pointers, ASID, high SYSENTER halves for Intel-compatible migration, TSC_AUX, DE_CFG, NextRIP, SPEC_CTRL shadows, TSC ratio, MSRPM, NMI/soft interrupt state, nested state, AVIC state, SEV-ES state, loaded-state flags, and software GIF.
- `struct svm_cpu_data` tracks per-CPU ASID allocation, SRSO state, host save area, and SEV VMCB lookup table.

Inline helpers:

- `to_kvm_svm()`, `to_kvm_sev_info()`, and `to_svm()` convert generic KVM structures to SVM-specific containers.
- `is_sev_guest()`, `is_sev_es_guest()`, and `is_sev_snp_guest()` become real checks under `CONFIG_KVM_AMD_SEV` and constant false otherwise.
- `vmcb_mark_all_dirty()`, `vmcb_mark_all_clean()`, `vmcb_mark_dirty()`, and `vmcb12_is_dirty()` centralize VMCB clean-bit manipulation.
- `vmcb_set_intercept()`, `vmcb_clr_intercept()`, `svm_set_intercept()`, `svm_clr_intercept()`, `set_exception_intercept()`, and `clr_exception_intercept()` update intercept bitmaps and mark nested intercept state dirty.
- `nested_vgif_enabled()`, `get_vgif_vmcb()`, `enable_gif()`, `disable_gif()`, and `gif_set()` abstract GIF state across hardware vGIF and software fallback.
- `nested_npt_enabled()`, `nested_vnmi_enabled()`, `is_vnmi_enabled()`, and `nested_svm_virtualize_tpr()` expose nested feature predicates.
- `svm_msrpm_bit_nr()` and generated helpers `svm_test/clear/set_msr_bitmap_read/write()` map MSR numbers into AMD MSRPM bits.
- GHCB helpers generated by `DEFINE_KVM_GHCB_ACCESSORS()` read GHCB fields and validity bits safely.

Declared cross-file APIs include:

- Main SVM APIs such as `svm_set_efer()`, `svm_set_cr0()`, `svm_set_cr4()`, `svm_set_gif()`, `svm_invoke_exit_handler()`, `svm_complete_interrupt_delivery()`, and MSRPM allocation/free helpers.
- Nested APIs such as `enter_svm_guest_mode()`, `svm_leave_nested()`, `svm_allocate_nested()`, `nested_svm_vmrun()`, `nested_svm_vmexit()`, cached VMCB copy/sync functions, TSC ratio update, and `svm_nested_ops`.
- AVIC APIs for VM/vCPU init, posted interrupts, doorbells, APICv inhibit reasons, and virtual APIC mode refresh.
- SEV APIs or stubs for VMCB init, vCPU lifecycle, memory encryption ioctls, RMP faults, guest memory hooks, VMSA decrypt/free, and CPU capability setup.
- Assembly APIs `__svm_vcpu_run()` and `__svm_sev_es_vcpu_run()`.

## Control Flow
The header itself has no standalone runtime loop, but it shapes all SVM control flow:

- `struct vcpu_svm` begins with `struct kvm_vcpu`, enabling `to_svm()` and allowing `svm.c` to treat generic KVM callbacks as SVM state.
- Intercept changes always target VMCB01 and call `svm_mark_intercepts_dirty()`. If L2 is active, that helper triggers `nested_vmcb02_recalc_intercepts()` so nested execution sees the merged L0/L1 intercept policy.
- GIF helpers choose between a real VMCB vGIF bit and `svm->guest_gif` software state depending on host support and nested-vGIF availability.
- SEV helper definitions compile to real state accesses when enabled and benign stubs when disabled, letting common SVM code call SEV hooks unconditionally.
- MSRPM helpers encode the AMD three-range MSR bitmap layout and return intercepted for out-of-range MSRs, which is fail-safe.

## State and Persistence Behavior
`svm.h` declares the persistent in-memory state layout for the backend. Per-VM AVIC and SEV fields live for the VM lifetime. Per-vCPU VMCB, MSRPM, nested, interrupt, AVIC, and SEV-ES state live for the vCPU lifetime. Per-CPU ASID and host save state live while hardware virtualization is initialized.

VMCB clean state persists in `vmcb->control.clean` and is mutated through helpers. Nested cached VMCB12 state persists in `svm_nested_state` but comments note the save cache is not kept live while L2 runs; it is valid within nested VMRUN preparation.

SEV state includes external firmware resources, ASID allocation, pinned page accounting, migration coordination, and SNP request buffers protected by mutexes. GHCB validity state is tracked in a bitmap; accessors make invalid fields read as zero through `*_if_valid()`.

## Dependencies and Integration Points
This header depends on Linux KVM host types, AMD SVM architectural definitions, SEV common definitions, CPUID helpers, and cached register helpers. It is included by SVM implementation files and neighboring AVIC/nested/SEV/Hyper-V units.

The header bridges generic KVM and AMD-specific code by declaring `svm_x86_ops`, `svm_nested_ops`, SEV callbacks, AVIC callbacks, and assembly entry points. It also encodes compile-time optionality for `CONFIG_KVM_AMD_SEV`, `CONFIG_HYPERV`, and `CONFIG_KVM_HYPERV`.

## Risks and Edge Cases
Important risks:

- Changing `struct vcpu_svm` layout can break assembly offsets in `vmenter.S`; generated asm-offsets must match.
- VMCB clean-bit enum changes require updating `VMCB_ALL_CLEAN_MASK`.
- Intercept helpers must update VMCB01 and nested VMCB02 consistently, or L2 intercept behavior diverges from L1/L0 policy.
- MSRPM bit mapping must remain fail-safe for unsupported ranges; clearing an invalid MSR bitmap bit would incorrectly pass through unknown MSRs.
- SEV stubs must preserve call-site assumptions when `CONFIG_KVM_AMD_SEV` is disabled.
- GHCB accessor validity is critical because SEV-ES guests expose only selected fields through shared GHCB memory.

## Test Signals
Build-time signals include `BUILD_BUG_ON()` checks in dependent files, generated asm-offset compatibility, and config matrix builds with and without `CONFIG_KVM_AMD_SEV`, `CONFIG_HYPERV`, and `CONFIG_KVM_SMM`.

Runtime signals include successful vCPU creation, nested SVM intercept consistency, SEV/SEV-ES boot paths, AVIC IRQ delivery, MSR bitmap pass-through/interception tests, and VMCB dirty-bit correctness observed through KVM selftests and tracepoints.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_onhyperv.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_onhyperv.c

## Purpose
`svm_onhyperv.c` adds AMD SVM-specific optimizations for running KVM as an L1 hypervisor on top of Microsoft Hyper-V. It enables Hyper-V nested enlightenments for NPT TLB flushing and direct TLB flush hypercalls when the Hyper-V host advertises them.

## Important APIs, Types, and Functions
Main functions:

- `svm_hv_enable_l2_tlb_flush(struct kvm_vcpu *vcpu)` obtains a Hyper-V partition assist page, stores it in the current VMCB's `hv_vmcb_enlightenments`, assigns `hv_vm_id` from the KVM pointer, enables `nested_flush_hypercall` when not already set, and marks Hyper-V nested enlightenments dirty.
- `svm_hv_hardware_setup()` checks `ms_hyperv.nested_features` and mutates `svm_x86_ops` to use Hyper-V remote TLB flush functions and an SVM L2 TLB flush enabling callback.

Key data dependencies:

- `struct hv_vmcb_enlightenments` stored in VMCB control reserved software space.
- `ms_hyperv.nested_features` bits `HV_X64_NESTED_ENLIGHTENED_TLB` and `HV_X64_NESTED_DIRECT_FLUSH`.
- Per-CPU Hyper-V VP assist pages, where `nested_control.features.directhypercall` is enabled.

## Control Flow
During SVM hardware setup, `svm.c` calls `svm_hv_hardware_setup()`. If NPT is enabled and Hyper-V advertises enlightened NPT TLB support, the function installs `hv_flush_remote_tlbs` and `hv_flush_remote_tlbs_range` into `svm_x86_ops`. If Direct TLB Flush is available, it sets the direct hypercall feature on each online CPU's VP assist page and assigns `svm_x86_ops.enable_l2_tlb_flush` to `svm_hv_enable_l2_tlb_flush()`.

When a vCPU later needs L2 TLB flush support, `svm_hv_enable_l2_tlb_flush()` populates the VMCB enlightenment fields and marks the nested-enlightenment clean bit dirty so hardware/Hyper-V sees the update.

## State and Persistence Behavior
No file-backed persistence exists. State persists in:

- VMCB `hv_enlightenments` fields: partition assist page, Hyper-V VM ID, and nested flush control.
- Per-CPU Hyper-V VP assist pages where direct hypercall support is enabled.
- Function pointers inside `svm_x86_ops`, which persist for the module lifetime after hardware setup.

If `hv_get_partition_assist_page()` returns `INVALID_PAGE`, enabling L2 TLB flush fails with `-ENOMEM` and no VMCB enlightenment is installed.

## Dependencies and Integration Points
This file depends on:

- Generic KVM host state and SVM structures from `svm.h`.
- SVM VMCB dirty helpers from `svm_ops.h`/`svm.h`.
- Hyper-V feature data from `<asm/mshyperv.h>`.
- Generic Hyper-V-on-KVM helpers from `hyperv.h` and `kvm_onhyperv.h`.
- SVM Hyper-V inline helpers from `svm_onhyperv.h`.

It integrates with `svm_hardware_setup()` and `svm_flush_tlb_current()/all()` behavior through `svm_x86_ops` and VMCB enlightenment fields.

## Risks and Edge Cases
Risks:

- Enlightened TLB flushing is valid only with NPT; installing it without NPT would skip required shadow-MMU behavior, so the code gates on `npt_enabled`.
- Direct hypercall setup iterates only online CPUs during hardware setup; CPU hotplug behavior must be handled by Hyper-V/common code or later setup paths.
- `hv_vm_id` uses the `struct kvm *` pointer cast to integer; it is process-local identity, not a stable persistent ID.
- VMCB dirty marking is required when toggling nested flush hypercall support; missed dirty bits could leave Hyper-V using stale enlightenments.

## Test Signals
Signals include hardware setup logs announcing enlightened NPT TLB or Direct TLB Flush, KVM Hyper-V selftests for nested TLB flushes, tracepoints `kvm_hv_flush_tlb` and `kvm_hv_flush_tlb_ex`, and guest correctness under nested KVM-on-Hyper-V workloads that exercise L2 MMU invalidations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_onhyperv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_onhyperv.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_onhyperv.h

## Purpose
`svm_onhyperv.h` provides the inline SVM-side interface for Hyper-V nested virtualization enlightenments. It lets SVM code initialize VMCB Hyper-V fields, detect enlightened TLB support, dirty the VMCB enlightenment area after MSRPM changes, and update the Hyper-V VP ID. It also compiles to no-op stubs when Hyper-V support is disabled.

## Important APIs, Types, and Functions
When `CONFIG_HYPERV` is enabled:

- `svm_hv_hardware_setup()` is declared for setup-time function pointer installation.
- `svm_hv_is_enlightened_tlb_enabled(struct kvm_vcpu *vcpu)` checks Hyper-V nested enlightened TLB support and the current VMCB's `enlightened_npt_tlb` control bit.
- `svm_hv_init_vmcb(struct vmcb *vmcb)` validates that the Hyper-V enlightenment area fits in the VMCB reserved software area, enables enlightened NPT TLB if NPT and host support are present, and enables nested MSR bitmap enlightenment if advertised.
- `svm_hv_vmcb_dirty_nested_enlightenments(struct kvm_vcpu *vcpu)` marks `HV_VMCB_NESTED_ENLIGHTENMENTS` dirty when the MSR bitmap enlightenment bit is active.
- `svm_hv_update_vp_id(struct vmcb *vmcb, struct kvm_vcpu *vcpu)` writes the current Hyper-V VP index into VMCB enlightenments and marks the field dirty when it changes.

When Hyper-V support is disabled, all helpers return false or do nothing, keeping SVM call sites unconditional.

## Control Flow
`init_vmcb()` calls `svm_hv_init_vmcb()` while initializing a VMCB. `svm_set_intercept_for_msr()` calls `svm_hv_vmcb_dirty_nested_enlightenments()` after changing MSRPM bits. `svm_vcpu_run()` calls `svm_hv_update_vp_id()` before VMRUN to keep Hyper-V's VP identity synchronized. TLB flush paths query `svm_hv_is_enlightened_tlb_enabled()` to decide whether Hyper-V-specific NPT flushes are required.

## State and Persistence Behavior
State is stored inside `vmcb->control.hv_enlightenments`, which overlays the VMCB reserved software area. The header uses a `BUILD_BUG_ON()` to guarantee layout compatibility. The key persisted fields are enlightened NPT TLB enablement, MSR bitmap enlightenment, Hyper-V VP ID, partition assist page, VM ID, and nested flush hypercall control.

No filesystem state is used.

## Dependencies and Integration Points
The header depends on `<asm/mshyperv.h>`, `kvm_onhyperv.h`, and `svm/hyperv.h` under Hyper-V builds. It also assumes SVM structures and helpers are visible from including files. It integrates with `svm.c`, `svm_onhyperv.c`, and generic Hyper-V KVM support.

## Risks and Edge Cases
Risks:

- The VMCB reserved software layout must continue to match `struct hv_vmcb_enlightenments`; the build-time check catches size drift but not semantic drift.
- Dirtying nested enlightenments only when `msr_bitmap` is active avoids needless work but means the control bit must be initialized before MSRPM changes matter to Hyper-V.
- VP ID changes must be synchronized before entry; stale VP IDs can misroute enlightened operations.
- Stub behavior must remain equivalent to no Hyper-V support; call sites rely on unconditional helper calls being cheap and safe.

## Test Signals
Build matrix coverage with `CONFIG_HYPERV` on/off is important. Runtime signals include Hyper-V nested feature logs, correct VMCB enlightenment dirtying when MSR intercepts change, tracepoints for Hyper-V TLB/IPI operations, and nested guest behavior under KVM-on-Hyper-V.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_onhyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_ops.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_ops.h

## Purpose
`svm_ops.h` wraps privileged AMD SVM instructions in inline C helpers with exception-table recovery. It provides safe call sites for `CLGI`, `STGI`, `INVLPGA`, and `VMSAVE`, all of which may fault if SVM state or hardware execution context is unexpectedly invalid.

## Important APIs, Types, and Functions
Macros:

- `svm_asm(insn, clobber...)` emits a zero-operand SVM instruction with an exception-table entry that branches to `kvm_spurious_fault()` on fault.
- `svm_asm1(insn, op1, clobber...)` emits a one-operand SVM instruction with the same fault handling.
- `svm_asm2(insn, op1, op2, clobber...)` emits a two-operand SVM instruction with the same fault handling.

Inline functions:

- `clgi()` clears the global interrupt flag for SVM, masking physical interrupts at the SVM GIF level around VMRUN-sensitive host code.
- `stgi()` sets GIF after returning from guest execution.
- `invlpga(unsigned long addr, u32 asid)` invalidates a guest virtual address for a given SVM ASID.
- `vmsave(unsigned long pa)` saves hardware-managed guest/host state to a VMCB/HSAVE physical address.

## Control Flow
Callers invoke these wrappers as ordinary functions. The wrapper emits the SVM instruction and immediately returns on success. If the instruction faults, the exception-table target calls `kvm_spurious_fault()` and then returns. `svm.c` uses these wrappers during CPU enable/disable, guest entry/exit preparation, TLB invalidation, and host-state save paths.

## State and Persistence Behavior
The header does not own state. It mutates CPU/SVM hardware state:

- `clgi()`/`stgi()` modify GIF.
- `invlpga()` invalidates TLB entries for an ASID.
- `vmsave()` writes CPU state into the physical save area identified by `pa`.

The physical address type is `unsigned long` because AMD SVM instructions consume address-size-sensitive portions of `rAX`, even though the conceptual operand is a physical address.

## Dependencies and Integration Points
The header depends on compiler asm-goto support, kernel exception tables, and `kvm_spurious_fault()` from `x86.h`. It is included by `svm.c` and `svm_onhyperv.c` so C code can use SVM instructions without duplicating inline assembly.

## Risks and Edge Cases
Risks:

- Operand constraints must match AMD instruction requirements; `invlpga` uses `ECX` for ASID and `EAX/RAX` for address, and `vmsave` uses `EAX/RAX`.
- Fault recovery treats faults as spurious; if a real path can fault because SVM is disabled or an address is invalid, the caller may continue after logging rather than receiving a normal error.
- `clgi()`/`stgi()` ordering around guest entry is security- and correctness-sensitive; interrupts and lockdep state are coordinated in `svm_vcpu_enter_exit()`.

## Test Signals
Build tests catch asm syntax and exception-table generation. Runtime validation includes successful VM entry/exit, absence of `kvm_spurious_fault()` reports, correct interrupt masking/unmasking around VMRUN, and working INVLPGA-based guest TLB invalidation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/vmenter.S -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/vmenter.S

## Purpose
`vmenter.S` contains the low-level AMD SVM guest-entry assembly routines. It performs register save/restore, VMLOAD/VMSAVE/VMRUN sequencing, SPEC_CTRL switching, CPU-buffer/RSB/RET mitigations, and special SEV-ES entry behavior. It is placed in `.noinstr.text` because it runs in a fragile IRQ/guest-state transition context where instrumentation would be unsafe.

## Important APIs, Types, and Functions
Exported symbols:

- `__svm_vcpu_run(struct vcpu_svm *svm, bool spec_ctrl_intercepted)` runs a normal SVM vCPU.
- `__svm_sev_es_vcpu_run(struct vcpu_svm *svm, bool spec_ctrl_intercepted, struct sev_es_save_area *hostsa)` runs an SEV-ES vCPU on x86_64 when `CONFIG_KVM_AMD_SEV` is enabled.

Important macros:

- `RESTORE_GUEST_SPEC_CTRL` and `RESTORE_GUEST_SPEC_CTRL_BODY` restore guest `MSR_IA32_SPEC_CTRL` immediately before VMRUN when hardware does not virtualize it.
- `RESTORE_HOST_SPEC_CTRL` and `RESTORE_HOST_SPEC_CTRL_BODY` read guest SPEC_CTRL if it was not intercepted and restore the host's per-CPU SPEC_CTRL value after VMEXIT.
- `SVM_CLEAR_CPU_BUFFERS` emits CPU-buffer clearing when `X86_FEATURE_CLEAR_CPU_BUF_VM` is active.
- `FILL_RETURN_BUFFER`, `UNTRAIN_RET_VM`, and `RET` integrate x86 speculation mitigations.
- Offset macros such as `VCPU_RCX`, `SVM_vmcb01_pa`, and `SVM_current_vmcb` use generated asm offsets to access `struct vcpu_svm` and nested fields.

## Control Flow
Normal SVM path:

1. Save host callee-saved registers on the stack.
2. Push `spec_ctrl_intercepted`, per-CPU host save area physical address, and `svm` for post-exit recovery.
3. Put `svm` in the canonical argument register and restore guest SPEC_CTRL if required.
4. `vmload` VMCB01 to load hardware-managed guest state shared by VMCB01/VMCB02.
5. Load the current VMCB physical address, then load guest GPRs from `svm->vcpu.arch.regs` except RAX/RSP, which hardware switches through the VMCB.
6. Clear CPU buffers if required.
7. Execute `vmrun`.
8. On exit, recover `svm`, save guest GPRs back to `vcpu.arch.regs`, `vmsave` VMCB01, and `vmload` the host save area to restore host GSBASE and related state.
9. Fill the return buffer, restore host SPEC_CTRL, untrain returns, zero guest GPR values from registers, pop saved host registers, and return.

Fault labels around VMLOAD/VMRUN/VMSAVE/host VMLOAD check `virt_rebooting`; if a virtualization instruction faults during reboot, execution resumes after the instruction, otherwise `ud2` terminates the path. Exception-table entries route faults to these labels.

SEV-ES path:

1. Save nonvolatile host GPRs and needed volatile arguments into the SEV-ES host save area because SEV-ES hardware restores most GPRs on VMEXIT but does not save all host values on VMRUN.
2. Restore guest SPEC_CTRL if required.
3. Load current VMCB physical address.
4. Clear CPU buffers and execute `vmrun`.
5. On exit, fill RSB, restore host SPEC_CTRL, untrain returns, end frame, and return.

The SEV-ES path does not manually load/save guest GPRs because encrypted guest state is protected and hardware/VMSA mechanisms own it.

## State and Persistence Behavior
The assembly routine mutates:

- Guest general-purpose registers in `vcpu->arch.regs` for normal SVM.
- VMCB01 save state through `vmload`/`vmsave`.
- Current VMCB execution state through `vmrun`.
- Per-CPU host save area state through `vmload` after VMEXIT.
- `svm->spec_ctrl` if guest SPEC_CTRL was not intercepted.
- SEV-ES host save area GPR slots.

It deliberately clears most host registers after VMEXIT to avoid speculative use of guest-controlled values. It does not allocate memory or persist filesystem data.

## Dependencies and Integration Points
This file depends on generated offsets from `asm-offsets.h` and `kvm-asm-offsets.h`, SVM structure layout from `svm.h`, x86 speculation mitigation macros, x86 exception tables, and the C wrapper `svm_vcpu_enter_exit()`. The C code is responsible for entering the correct IRQ/GIF/guest-state context before calling these symbols and for interpreting VMCB exit information afterward.

## Risks and Edge Cases
Risks:

- Structure offset drift between C and assembly can corrupt guest/host registers; generated offsets and build checks are critical.
- No indirect branches or returns may occur between guest SPEC_CTRL restore and VMRUN; the comments explicitly call out RSB-underflow risk.
- Host SPEC_CTRL restore must read guest SPEC_CTRL only if the MSR was not intercepted; otherwise `svm->spec_ctrl` already contains the last known value.
- Guest register zeroing after VMEXIT is defensive against speculation and must not clobber values before they are saved.
- Fault recovery around SVM instructions is only acceptable for reboot paths; unexpected faults intentionally hit `ud2`.
- SEV-ES has different GPR ownership rules; applying normal SVM register save/restore would violate protected-state semantics.

## Test Signals
Test signals include successful VM entry/exit under normal SVM and SEV-ES, no objtool/noinstr warnings, no exception-table failures outside reboot, correct guest GPR preservation across exits, SPEC_CTRL correctness under guest writes and intercept-pass-through modes, and mitigation-sensitive tests for RSB/RET/CLEAR_CPU_BUF behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/vmenter.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/trace.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/trace.h

## Purpose
`trace.h` defines the x86 KVM tracepoint API for VM entry/exit, hypercalls, port I/O, MMIO, CPUID, interrupt/APIC delivery, nested virtualization, instruction emulation, TSC/timekeeping, SMM, posted interrupts/APICv/AVIC, Hyper-V features, SEV VMGEXIT, and SNP RMP faults. It is shared by VMX, SVM, Hyper-V, Xen, MMU, LAPIC, and SEV code.

For the SVM subset, this file is the observability surface used by `svm.c` for entry/exit, page faults, CR/MSR access, interrupt injection, nested SVM VMRUN/VMEXIT, INVLPGA/SKINIT, PLE window updates, AVIC events, Hyper-V TLB flushes, VMGEXIT, and RMP faults.

## Important APIs, Types, and Functions
Trace infrastructure:

- `TRACE_SYSTEM kvm` groups all events under KVM.
- `tracing_kvm_rip_read(vcpu)` returns RIP unless guest state is protected, in which case it reports zero to avoid reading inaccessible SEV-protected state.
- `KVM_ISA_VMX` and `KVM_ISA_SVM` distinguish exit reason formatting.
- `kvm_print_exit_reason(exit_reason, isa)` formats VMX and SVM exit reasons differently.
- `TRACE_EVENT_KVM_EXIT(name)` generates VM-exit-style tracepoints using the active `kvm_x86_ops.get_exit_info()` callback.

Major event families:

- Entry/exit: `kvm_entry`, `kvm_exit`, `kvm_nested_vmexit`.
- Hypercalls: `kvm_hypercall`, `kvm_hv_hypercall`, `kvm_hv_hypercall_done`, `kvm_xen_hypercall`.
- I/O and emulation: `kvm_pio`, `kvm_fast_mmio`, `kvm_cpuid`, `kvm_msr`, `kvm_cr`, `kvm_emulate_insn`, `vcpu_match_mmio`.
- IRQ/APIC: `kvm_ioapic_set_irq`, `kvm_ioapic_delayed_eoi_inj`, `kvm_msi_set_irq`, `kvm_apic`, `kvm_apic_ipi`, `kvm_apic_accept_irq`, `kvm_eoi`, `kvm_pv_eoi`, `kvm_inj_virq`, `kvm_inj_exception`, `kvm_pi_irte_update`.
- Nested virtualization: `kvm_nested_vmenter`, `kvm_nested_intercepts`, `kvm_nested_vmexit_inject`, `kvm_nested_intr_vmexit`, `kvm_nested_vmenter_failed`.
- SVM-specific or SVM-relevant: `kvm_invlpga`, `kvm_skinit`, `kvm_ple_window_update`, `kvm_avic_incomplete_ipi`, `kvm_avic_unaccelerated_access`, `kvm_avic_ga_log`, `kvm_avic_kick_vcpu_slowpath`, `kvm_avic_doorbell`, `kvm_vmgexit_enter`, `kvm_vmgexit_exit`, `kvm_vmgexit_msr_protocol_enter`, `kvm_vmgexit_msr_protocol_exit`, `kvm_rmp_fault`.
- Timekeeping: `kvm_write_tsc_offset`, `kvm_update_master_clock`, `kvm_track_tsc`, `kvm_pvclock_update`, `kvm_wait_lapic_expire`.
- SMM and APICv: `kvm_smm_transition`, `kvm_apicv_inhibit_changed`, `kvm_apicv_accept_irq`.
- Hyper-V synthetic interrupt/timer/TLB/IPI/debug: `kvm_hv_notify_acked_sint`, `kvm_hv_synic_set_irq`, `kvm_hv_synic_send_eoi`, `kvm_hv_synic_set_msr`, `kvm_hv_stimer_*`, `kvm_hv_timer_state`, `kvm_hv_flush_tlb`, `kvm_hv_flush_tlb_ex`, `kvm_hv_send_ipi`, `kvm_hv_send_ipi_ex`, `kvm_pv_tlb_flush`, `kvm_hv_syndbg_set_msr`, and `kvm_hv_syndbg_get_msr`.

Convenience wrappers:

- `trace_kvm_apic_read/write`, `trace_kvm_msr_read/write/read_ex/write_ex`, `trace_kvm_cr_read/write`, and `trace_kvm_emulate_insn_start/failed` normalize common read/write trace uses.

## Control Flow
This file is compile-time tracepoint definition, not executable control logic by itself. Callers invoke generated `trace_kvm_*()` functions at runtime. `TP_fast_assign` blocks capture fields from caller arguments into per-event records, and `TP_printk` defines human-readable formatting.

For entry/exit events, control flows through generic x86 KVM callbacks: `kvm_entry` uses `kvm_x86_call(get_entry_info)` and `kvm_exit`/`kvm_nested_vmexit` use `kvm_x86_call(get_exit_info)`. On SVM, those callbacks are supplied by `svm_get_entry_info()` and `svm_get_exit_info()` in `svm.c`, which read VMCB `event_inj`, `exit_code`, `exit_info_*`, and interrupt info fields.

The header ends by setting `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE`, then includes `<trace/define_trace.h>` outside include guards as required by Linux tracepoint generation.

## State and Persistence Behavior
Tracepoints do not own persistent VM state. They snapshot runtime state into the kernel tracing ring buffer when enabled. Fields include vCPU ID, RIP, exit reason, interrupt info, error code, requests bitmap, GPA/GVA, MSR/CR values, APIC vectors, nested VMCB/VMCS identifiers, TSC offsets, Hyper-V masks, GHCB data, and RMP fault metadata.

Protected guest state behavior is explicit: `tracing_kvm_rip_read()` avoids reading RIP for protected guests and emits zero, preventing tracepoints from depending on inaccessible SEV-ES/SNP register state.

## Dependencies and Integration Points
The header depends on Linux tracepoint macros and x86 architecture headers for VMX/SVM exit symbols, clocksource IDs, and pvclock structures. It also references KVM structures such as `struct kvm_vcpu`, `struct kvm_lapic`, `struct ghcb`, and `struct pvclock_vcpu_time_info`.

Integration points with this subset:

- `svm.c` emits `trace_kvm_entry`, `trace_kvm_exit`, `trace_kvm_page_fault`, `trace_kvm_fast_mmio`, `trace_kvm_cr_read/write`, `trace_kvm_invlpga`, `trace_kvm_skinit`, `trace_kvm_inj_virq`, `trace_kvm_apicv_accept_irq`, and `trace_kvm_ple_window_update`.
- Nested SVM code uses nested VMRUN/VMEXIT/intercept events.
- AVIC code uses the `kvm_avic_*` events.
- SEV code uses VMGEXIT and RMP fault tracepoints.
- Hyper-V paths use TLB, IPI, SynIC, timer, and synthetic debug tracepoints.

## Risks and Edge Cases
Risks:

- Tracepoints must not access protected guest state directly; the RIP helper mitigates that for entry/exit and page-fault style events.
- Tracepoint field widths must match architecture values; truncating exit codes, addresses, or masks would mislead debugging.
- Events called from hot paths must keep assignment logic cheap when tracing is disabled and safe when enabled.
- Format strings and symbolic tables must stay aligned with SVM/VMX architectural constants.
- `TRACE_EVENT_KVM_EXIT` depends on runtime x86 ops; backends must provide valid `get_exit_info()` and `get_entry_info()` semantics.

## Test Signals
Validation signals include successful kernel tracepoint generation, ability to enable events under `/sys/kernel/tracing/events/kvm/`, correct SVM exit reason formatting with `SVM_EXIT_REASONS`, and useful traces under workloads that exercise VM entry/exit, NPF, nested SVM, AVIC, Hyper-V TLB/IPI, VMGEXIT, and SNP RMP faults.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/trace.h -->
