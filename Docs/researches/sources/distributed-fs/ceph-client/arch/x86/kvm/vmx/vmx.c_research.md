# Research: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmx.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000901`: lines 1-8866, `Docs/researches/chunks/subset-b-000901_research.md`
- `subset-b-000902`: lines 8867-8879, `Docs/researches/chunks/subset-b-000902_research.md`

## Chunk Research

### subset-b-000901: lines 1-8866

# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmx.c lines 1-8866

## Scope

This chunk covers nearly all of the Intel VMX backend for KVM. It starts at the module header and includes module parameters, VMX capability discovery, L1TF and buffer-clear mitigations, VMCS allocation and CPU-load logic, guest register/MSR/segment/control-register handling, VMCS initialization, interrupt and exception injection, VM-exit dispatch, APICv/posting support, PML dirty logging, vCPU run/exit entry glue, vCPU and VM lifecycle hooks, CPU capability exposure, nested-intercept checks, hardware setup, and the first part of `vmx_init()`.

The file lives under a `ceph-client` source snapshot, but this source is not Ceph distributed-filesystem code. It is the Linux `kvm_intel` implementation for Intel VT-x. Research should therefore align it with `arch/x86/kvm/vmx/` and KVM/x86 integration, not with Ceph client data paths.

The requested range ends at line 8866, inside the final `for_each_possible_cpu(cpu)` loop in `vmx_init()`. The loop body and error label continue just after the range; this chunk covers the setup decisions and entry into the loop, while any strict line-bounded reconciliation should treat the last few post-8866 lines as outside the requested chunk.

## Purpose

`vmx.c` implements the hardware-facing side of KVM on Intel VT-x. It translates generic KVM/x86 operations into VMX-specific VMCS fields, VM-entry/VM-exit controls, VMX instructions, EPT/VPID invalidations, posted interrupts, processor trace handling, and nested-VMX state transitions.

The file owns the core lifecycle for non-TDX VMX VMs and vCPUs: global module initialization, per-CPU VMX enable/disable, per-VM setup, vCPU VMCS allocation and initialization, guest entry, VM-exit handling, and teardown. It also mediates the feature surface exposed to guests by combining hardware VMX capabilities, module parameters, KVM policy, nested virtualization constraints, and guest CPUID.

Operationally, the file is the place where KVM decides which guest actions run directly in hardware, which actions are intercepted and emulated, which state is atomically swapped by VMX MSR-load/store areas, and which conditions require exits to userspace. It is a security-sensitive boundary between host kernel state and guest-controlled state.

## Important APIs, Types, And Functions

The principal externally visible entry points in this chunk are `vmx_init()`, `vmx_exit()`, `vmx_hardware_setup()`, `vmx_hardware_unsetup()`, `vmx_check_processor_compat()`, `vmx_enable_virtualization_cpu()`, `vmx_disable_virtualization_cpu()`, `vmx_vm_init()`, `vmx_vm_destroy()`, `vmx_vcpu_precreate()`, `vmx_vcpu_create()`, `vmx_vcpu_free()`, `vmx_vcpu_load()`, `vmx_vcpu_put()`, `vmx_vcpu_reset()`, `vmx_vcpu_run()`, `vmx_handle_exit()`, and `vmx_handle_exit_irqoff()`. These are wired into the VT runtime operation tables in `arch/x86/kvm/vmx/main.c` through `vt_x86_ops` and `vt_init_ops`.

Global configuration state includes module parameters such as `enable_vpid`, `enable_ept`, `enable_unrestricted_guest`, `enable_ept_ad_bits`, `enable_cet`, `emulate_invalid_guest_state`, `enable_apicv`, `enable_ipiv`, `nested`, `enable_pml`, `enable_preemption_timer`, `pt_mode`, PLE parameters, and L1TF mitigation state. `vmcs_config` records the VMCS control baseline derived from VMX MSRs. `vmx_capability` records EPT/VPID capability MSRs. `vmx_vpid_bitmap` allocates VPIDs. Per-CPU `current_vmcs` and `loaded_vmcss_on_cpu` track active VMCS ownership.

VMCS and CPU capability setup is centered on `setup_vmcs_config()`, `adjust_vmx_controls()`, `adjust_vmx_controls64()`, `vmx_check_entry_exit_pairs()`, `vmx_set_cpu_caps()`, `vmx_get_perf_capabilities()`, and `vmx_setup_me_spte_mask()`. These routines read VMX control MSRs, reject unsupported mandatory controls, sanitize inconsistent entry/exit pairs, apply errata workarounds, configure EPT and VPID capability policy, and publish guest-visible CPUID/perf/SGX/CET/PT capabilities.

VMCS allocation and loading use `alloc_vmcs_cpu()`, `free_vmcs()`, `alloc_loaded_vmcs()`, `free_loaded_vmcs()`, `loaded_vmcs_clear()`, `vmx_vcpu_load_vmcs()`, `vmx_switch_loaded_vmcs()`, `vmx_load_vmcs01()`, and `vmx_put_vmcs01()`. A `loaded_vmcs` wraps the VMCS page, optional MSR bitmap, optional shadow VMCS, launch state, CPU ownership, host-state cache, and control-shadow cache.

Guest architectural state helpers include `vmx_get_rflags()`, `vmx_set_rflags()`, `vmx_cache_reg()`, `vmx_get_segment()`, `vmx_set_segment()`, `vmx_get_idt()`, `vmx_set_idt()`, `vmx_get_gdt()`, `vmx_set_gdt()`, `vmx_get_cpl()`, `vmx_set_cr0()`, `vmx_set_cr4()`, `vmx_set_efer()`, `vmx_load_mmu_pgd()`, `vmx_flush_tlb_all()`, `vmx_flush_tlb_current()`, `vmx_flush_tlb_gva()`, and `vmx_flush_tlb_guest()`. These maintain consistency between KVM's cached vCPU state and VMCS guest fields.

MSR virtualization is handled by `vmx_get_msr()`, `vmx_set_msr()`, `vmx_get_feature_msr()`, `vmx_has_emulated_msr()`, `vmx_set_intercept_for_msr()`, `vmx_recalc_msr_intercepts()`, `vmx_recalc_pmu_msr_intercepts()`, `pt_update_intercept_for_msr()`, and the atomic-switch helpers `add_atomic_switch_msr()`, `clear_atomic_switch_msr()`, `vmx_add_auto_msr()`, `vmx_remove_auto_msr()`, `vmx_add_autostore_msr()`, and `vmx_remove_autostore_msr()`. User-return MSR state is tracked through `vmx_uret_msr` entries initialized by `vmx_setup_user_return_msrs()` and configured per vCPU by `vmx_setup_uret_msrs()`.

Interrupt and event injection uses `vmx_inject_exception()`, `vmx_inject_irq()`, `vmx_inject_nmi()`, `vmx_enable_irq_window()`, `vmx_enable_nmi_window()`, `vmx_get_nmi_mask()`, `vmx_set_nmi_mask()`, `vmx_interrupt_allowed()`, `vmx_nmi_allowed()`, `vmx_cancel_injection()`, `vmx_complete_interrupts()`, and `vmx_recover_nmi_blocking()`. Posted interrupt and APICv support is implemented by `vmx_deliver_interrupt()`, `vmx_deliver_posted_interrupt()`, `vmx_sync_pir_to_irr()`, `vmx_set_virtual_apic_mode()`, `vmx_set_apic_access_page_addr()`, `vmx_hwapic_isr_update()`, `vmx_load_eoi_exitmap()`, and `vmx_refresh_apicv_exec_ctrl()`.

The VM-exit path is built around `vmx_vcpu_run()`, `vmx_vcpu_enter_exit()`, `__vmx_vcpu_run()`, `vmx_exit_handlers_fastpath()`, `__vmx_handle_exit()`, `vmx_handle_exit()`, and the `kvm_vmx_exit_handlers[]` table. Important handlers include `handle_exception_nmi()`, `handle_external_interrupt()`, `handle_triple_fault()`, `handle_io()`, `handle_cr()`, `handle_dr()`, `handle_invlpg()`, `handle_apic_access()`, `handle_ept_violation()`, `handle_ept_misconfig()`, `handle_invalid_guest_state()`, `handle_pause()`, `handle_invpcid()`, `handle_pml_full()`, `handle_preemption_timer()`, `handle_notify()`, `handle_rdmsr_imm()`, and `handle_wrmsr_imm()`.

Nested VMX integration appears throughout this file. Local stubs such as `handle_vmx_instruction()` inject `#UD` until `nested_vmx_hardware_setup()` overwrites VMX-instruction handlers. Runtime paths call into `nested_vmx_reflect_vmexit()`, `nested_vmx_vmexit()`, `nested_vmx_enter_non_root_mode()`, `nested_get_vpid02()`, `nested_cpu_has*()` helpers, `nested_vmx_cr_fixed1_bits_update()`, and nested MSR/eVMCS filtering routines.

## Control Flow

Module initialization begins in `vmx_init()`. It verifies that the current CPU supports and has enabled VMX, optionally enables Hyper-V enlightened VMCS support, parses VMCS controls through `setup_vmcs_config()`, and then calls `kvm_x86_vendor_init(&vt_init_ops)`. The later `vmx_hardware_setup()` callback applies hardware-policy gates, disables unsupported module options, configures MMU/EPT masks, initializes guest CPU capabilities, wires nested VMX support, and installs posted-interrupt wakeup handling.

Per-CPU enablement flows through `vmx_enable_virtualization_cpu()` and `vmx_disable_virtualization_cpu()`. Enabling gets a VMX virtualization reference and checks Hyper-V VP assist availability when eVMCS is active. Disabling clears all loaded VMCSs on the current CPU, releases VMX, and resets eVMCS state.

VM creation calls `vmx_vm_init()`, which adjusts pause-loop exit policy, warns about L1TF exposure when relevant, and records PML dirty-log size. vCPU creation allocates a VPID, optional PML page, `vmcs01`, optional APIC-access private page, real-mode identity page table when EPT without unrestricted guest is used, optional `#VE` info page, and optional IPI virtualization PID-table entry. `vmx_vcpu_reset()` then initializes VMCS state, reset segments, descriptor tables, activity state, entry interruption state, CET state, APIC reload requests, VPID context, and FB_CLEAR policy.

When KVM schedules a vCPU, `vmx_vcpu_load()` loads the VMCS on the target CPU and prepares posted-interrupt state. If the VMCS moved CPUs, `vmx_vcpu_load_vmcs()` clears it from the prior CPU, links it into the new per-CPU VMCS list, loads it with `VMPTRLD`, requests a TLB flush, and updates host TR/GDTR/SYSENTER fields that are CPU-local. `vmx_prepare_switch_to_guest()` later loads guest user-return MSRs and writes host FS/GS/LDTR state into VMCS host fields.

Guest entry runs through `vmx_vcpu_run()`. It first handles invalid guest state by synthesizing a failed entry, writes dirty RIP/RSP state to the VMCS, refreshes host CR3/CR4, clears interrupt shadow for single-step debugging, switches Intel PT and PMU MSRs, programs the VMX preemption timer or forces an IPI-style exit, waits for LAPIC timer expiry, and calls `vmx_vcpu_enter_exit()`.

`vmx_vcpu_enter_exit()` is the `noinstr` wrapper around the assembly VM-entry/VM-exit routine. It enters guest-state accounting, applies the L1D flush mitigation, disables host CPU-buffer clearing for suitable guests, syncs CR2, invokes `__vmx_vcpu_run()`, snapshots CR2 and lazy-loaded registers on return, restores FB_CLEAR state, reads VM-exit reason and IDT-vectoring info, handles NMI exits in irq-off context, and exits guest-state accounting.

After VM-exit, `vmx_vcpu_run()` restores host debug/PT state, handles nested-run accounting, marks eVMCS fields clean, traces the exit, marks successful VMCS launch, refreshes guest PMU state, recovers NMI blocking, requeues interrupted event injection via `vmx_complete_interrupts()`, and attempts fastpath handling. Fastpaths cover selected WRMSR, preemption timer, HLT, and INVD exits.

The slow VM-exit path is `__vmx_handle_exit()`. It flushes PML logs for L1, rejects impossible nested pending-entry states, handles L2 exits by marking VMCS12-related pages dirty and reflecting exits to L1 when requested, enters instruction emulation for invalid L1 guest state, reports VM-entry failures, validates event-vectoring constraints, handles software NMI blocking, and dispatches through `kvm_vmx_exit_handlers[]`. Unrecognized exits dump VMCS state and report an unexpected-reason userspace exit.

Exception exits are handled by `handle_exception_nmi()`. It defers machine checks and NMIs to irq-off handling, queues `#NM` with XFD payload when appropriate, handles `#UD`, diagnoses unexpected `#VE`, handles VMware-backdoor `#GP`, detects simultaneous exception/vectoring hazards, routes page faults to `vmx_handle_page_fault()`, handles real-mode exceptions specially, reports guest debug exits for `#DB/#BP`, injects eligible `#AC`, and otherwise exits to userspace with `KVM_EXIT_EXCEPTION`.

EPT violation and misconfiguration exits split normal memory faults from MMIO and illegal GPA cases. `handle_ept_violation()` uses `GUEST_PHYSICAL_ADDRESS` and exit qualification, preserves NMI blocking for IRET-related exits, emulates if the guest GPA exceeds the allowed MAXPHYADDR, and otherwise delegates to `__vmx_handle_ept_violation()`. `handle_ept_misconfig()` fast-paths MMIO bus writes for L1 and otherwise invokes the MMU page-fault path with `PFERR_RSVD_MASK`.

Control-register exits use `handle_cr()` and nested-aware setters. CR0/CR4 writes in L2 combine L2-owned bits from the attempted value with L1-owned bits from VMCS12. Real-mode/protected-mode transitions call `enter_rmode()` and `enter_pmode()` when unrestricted guest is unavailable. Long-mode entry/exit updates EFER and VM-entry IA32e controls.

## State And Persistence Behavior

Persistent module-wide state is stored in `__read_mostly` feature flags and in global VMX capability structures. These values are initialized from module parameters and hardware MSRs, then may be further narrowed by `vmx_hardware_setup()`. They determine the behavior of every VM until module unload.

Per-CPU state includes `current_vmcs` and `loaded_vmcss_on_cpu`. A VMCS may be loaded on only one CPU at a time, and the code uses cross-CPU `smp_call_function_single()`, memory barriers, and per-CPU lists to safely clear and migrate VMCSs during vCPU migration or CPU hot-unplug.

Per-vCPU persistent state is split between `struct kvm_vcpu`, `struct vcpu_vmx`, VMCS fields, and auxiliary allocations. `vcpu_vmx` owns `vmcs01`, the current `loaded_vmcs`, VPID, PML page, optional `ve_info`, real-mode shadow segment state, nested VMX state, user-return MSR caches, MSR autoload/autostore arrays, Intel PT context, SPEC_CTRL state, APIC posted-interrupt descriptor, PLE window, preemption-timer deadline, and FB_CLEAR policy.

VMCS guest fields are the hardware-persistent execution image for registers, controls, descriptors, MSRs, EPTP, VPID, APICv state, PML state, posted interrupt descriptors, and entry/exit controls. Many getters lazily cache VMCS fields in KVM registers, and many setters clear `vmx->segment_cache` or mark KVM registers available/dirty to preserve consistency.

MSR state is handled in several tiers. Some MSRs are VMCS native fields, some are KVM-emulated fields, some are user-return MSRs loaded on return to userspace or before guest entry, and some are VM-entry/VM-exit autoload/autostore entries. This split is central to both performance and correctness: EFER, PERF_GLOBAL_CTRL, SPEC_CTRL, PT, SYSENTER, FS/GS bases, CET, SGX launch-control MSRs, TSX_CTRL, and PMU MSRs all have feature-specific state paths.

Dirty logging with PML persists guest-written GPAs in the hardware PML buffer page. `vmx_flush_pml_buffer()` drains entries on VM-exit and marks KVM pages dirty before resetting the VMCS PML index. This state is deliberately disabled for L2 and is toggled when dirty-logging memslots change.

Nested VMX state persists in `vmx->nested` and VMCS12-related mappings. While running L2, the loaded VMCS switches to `vmcs02`; guard helpers temporarily load `vmcs01` when L1 VMCS state must be modified. On every L2 exit, pages that hardware can update via HPA mappings are marked dirty so VMCS12 shadow state stays coherent with KVM dirty tracking.

There is no filesystem persistence. All state is in kernel memory, CPU MSRs, VMCS pages, KVM memory slots, and user-visible `kvm_run` exits.

## Dependencies And Integration Points

The file includes generic Linux kernel headers, x86 architecture headers, KVM host headers, VMX-specific headers, MMU headers, Hyper-V integration headers, SGX, PMU, LAPIC, nested VMX, SMM, posted interrupt, and tracing headers. It depends heavily on helpers and types from `vmx.h`, `vmcs.h`, `vmcs12.h`, `nested.h`, `x86.h`, `x86_ops.h`, `kvm_cache_regs.h`, `mmu.h`, `pmu.h`, `sgx.h`, `posted_intr.h`, and `vmx_onhyperv.h`.

The primary KVM integration point is `arch/x86/kvm/vmx/main.c`, whose `vt_x86_ops` dispatches generic x86 KVM operations to VMX or TDX-specific implementations. This file provides the non-TDX VMX side of that dispatch, while TDX-specific behavior lives in `tdx.c`.

Nested virtualization integration is split with `nested.c`. This file provides base stubs and common VMX state handling; `nested_vmx_hardware_setup()` patches the VMX-instruction exit handlers when nested VMX is enabled. Many runtime decisions consult VMCS12 controls through `nested_cpu_has*()` and reflect exits through nested VMX helpers.

MMU integration is deep. EPT configuration flows through `kvm_mmu_set_ept_masks()`, `kvm_configure_mmu()`, `construct_eptp()`, `vmx_load_mmu_pgd()`, `ept_sync_*()` and `vpid_sync_*()` invalidations, `kvm_mmu_page_fault()`, `__vmx_handle_ept_violation()`, and dirty-page APIs. Memory type policy is exposed through `vmx_get_mt_mask()`.

APIC and interrupt integration is through in-kernel LAPIC helpers, APICv controls, posted-interrupt descriptors, EOI exit bitmaps, `kvm_lapic_*()` routines, IOMMU/device posted-interrupt paths, and `kvm_set_posted_intr_wakeup_handler()`.

Security and CPU-mitigation integration includes L1TF VM-entry L1D flushing, MDS/TAA/VERW buffer-clear controls, SPEC_CTRL save/restore, bus-lock detection, split-lock `#AC` handling, SGX enclave emulation restrictions, CET gating, XFD `#NM` handling, and machine-check handling in irq-off context.

Intel PT and PMU integration uses perf guest MSR switching, LBR and PEBS capability filtering, PT MSR validation, `vt_init_ops.handle_intel_pt_intr`, mediated PMU controls, and KVM PMU state refresh on VM-exit.

Hyper-V integration includes enlightened VMCS selection, VP assist pages, direct nested TLB flush, enlightened MSR bitmap clean-field updates, Hyper-V root TDP tracking, and remote TLB flush hook substitution when running as a nested hypervisor on Hyper-V.

Userspace integration is through KVM ioctls and `struct kvm_run` exits. This file sets exits such as `KVM_EXIT_FAIL_ENTRY`, `KVM_EXIT_INTERNAL_ERROR`, `KVM_EXIT_SHUTDOWN`, `KVM_EXIT_DEBUG`, `KVM_EXIT_EXCEPTION`, `KVM_EXIT_SET_TPR`, `KVM_EXIT_NOTIFY`, and `KVM_EXIT_X86_BUS_LOCK`.

## Risks And Edge Cases

VMCS control setup is high risk because unsupported mandatory controls must fail early, optional controls must be masked correctly, and paired VM-entry/VM-exit controls must remain consistent. A bad control bit can cause VM-entry failure, silent feature exposure mismatch, or host state corruption.

Host/guest state transitions are fragile. FS/GS bases, LDTR, SYSENTER, CR3, CR4, EFER, SPEC_CTRL, PERF_GLOBAL_CTRL, PT MSRs, and CET state are all changed around VM-entry/VM-exit. Missing a save, restore, or dirty-bit update can leak host state to guests, corrupt host state after exit, or expose stale guest state.

Nested VMX creates many ownership hazards. Code that assumes `vmcs01` while L2 is active must use the guard helpers, and code that reads VMCS12 outside the vCPU mutex is explicitly avoided. Exit reflection, event requeueing, CR0/CR4 shadowing, VPID selection, and dirty marking of HPA-updated nested pages are all correctness-sensitive.

Invalid guest-state emulation is a narrow compatibility path. It tries to emulate through bad VMX guest state when unrestricted guest is unavailable, but cannot handle all pending exceptions or nested entry cases. The loop is bounded and exits to emulation failure if state cannot be made valid.

Event vectoring and interruptibility are subtle. `vmx_complete_interrupts()` must requeue interrupted injections with correct instruction length and error code, NMI blocking must be restored after IRET-related failures and errata cases, and soft-vNMI fallback can only infer unblocking through interrupt windows or timeout.

MSR bitmaps and pass-through policy are security sensitive. Allowing direct guest writes to SPEC_CTRL, XFD, PT, PMU, CET, x2APIC, or SYSENTER-class MSRs improves performance but requires matching CPUID, KVM filters, nested state, and host mitigation expectations. Incorrect MSR interception can either break guests or allow state corruption/leakage.

EPT and memory-type behavior must account for illegal guest physical addresses, MMIO cacheability, MKTME KeyID bits, EPT A/D bits, PML, non-coherent DMA, and self-snoop quirks. Misclassifying EPT violations versus misconfigurations can lead to wrong page faults, failed MMIO, or missed dirty logging.

APICv and posted interrupt behavior depends on exact synchronization. PIR-to-IRR transfer, ON-bit clearing, RVI/SVI updates, nested posted interrupts, wakeup vectors, and IPI virtualization PID-table entries all involve concurrency with running vCPUs and devices.

Mitigation code carries performance and security tradeoffs. L1D flushing is conditional and static-key controlled. FB_CLEAR disabling deliberately avoids unnecessary VERW buffer clearing only when host/guest capability state says it is safe. SPEC_CTRL restoration must cover both normal and legacy IBRS behavior.

Several paths deliberately avoid instruction skipping or use special skipping behavior because hardware VM-exit instruction lengths can be undefined or misleading, especially for EPT misconfig under Hyper-V and SGX enclave exits. Incorrect RIP advancement can corrupt guest execution.

This chunk ends before the literal end of `vmx_init()`. A final per-file report should reconcile the post-8866 initialization loop completion and error path with this chunk.

## Test Signals

Build and load tests should cover `kvm_intel` with combinations of `ept`, `vpid`, `unrestricted_guest`, `nested`, `enable_apicv`, `enable_ipiv`, `pml`, `preemption_timer`, `enable_cet`, `pt_mode`, and mitigation parameters. The module should reject unsupported VMX hardware cleanly and emit expected diagnostics for BIOS-disabled VMX or inconsistent VMCS configuration.

VMCS configuration tests should validate that `setup_vmcs_config()` accepts only supported control bits, applies entry/exit pair consistency, disables errata-affected PERF_GLOBAL_CTRL load/store on listed CPUs, and produces identical `vmcs_config` across all online CPUs.

Lifecycle tests should create and destroy VMs/vCPUs repeatedly under CPU hotplug and vCPU migration, checking that VMCSs are cleared on the owning CPU, VPIDs are allocated/freed, PML and `ve_info` pages are released, and Hyper-V eVMCS state resets correctly.

Guest state tests should exercise real mode, protected mode, long mode, VM86 fallback, unrestricted guest disabled, EPT without unrestricted guest, and invalid segment/control-register combinations. Expected signals include successful emulation through valid real-mode transitions, `KVM_EXIT_FAIL_ENTRY` for VM-entry failures, and emulation-failure exits for unhandleable invalid state.

MSR tests should cover EFER, PAT, SYSENTER, FS/GS bases, KERNEL_GS_BASE, SPEC_CTRL, TSX_CTRL, FEATURE_CONTROL, SGX launch-control hashes, DEBUGCTL, BNDCFGS, XFD/XFD_ERR, CET MSRs, PT MSRs, PMU MSRs, and emulated VMX MSRs. Tests should verify CPUID gating, host-initiated exceptions, nested restrictions, reserved-bit rejection, and MSR bitmap pass-through changes.

VM-exit handler tests should trigger exception/NMI, external interrupt, triple fault, I/O, CR/DR access, CPUID, RDMSR/WRMSR, HLT, INVD, INVLPG, RDPMC, VMCALL, APIC access/write/EOI, task switch, EPT violation, EPT misconfig, PAUSE, INVPCID, PML full, preemption timer, ENCLS, bus lock, notify VM-exit, and immediate MSR exits. Each should either resume the guest, reflect to nested L1, or populate `kvm_run` with the correct exit reason.

Nested VMX tests should run L1 hypervisors with and without eVMCS, verify VMX instruction handlers are replaced when `nested=1`, check VMCS12 MSR filtering and CR fixed bits after CPUID changes, exercise L2 EPT/VPID/posted-interrupt flows, and verify that L2 exits are reflected or handled by L0 according to VMCS12 controls.

Interrupt tests should cover IRQ/NMI injection, IRQ and NMI windows, event requeue after delivery failure, soft-vNMI fallback, NMI blocking after IRET faults, APICv virtual interrupt delivery, posted interrupts from running and non-running vCPUs, x2APIC MSR bitmap modes, EOI exit bitmaps, and nested posted interrupt vectors.

MMU tests should cover EPT on/off, VPID on/off, global and single-context invalidations, 4-level and 5-level EPT roots, EPT A/D bits, PML dirty logging, MMIO EPT misconfig fast paths, illegal MAXPHYADDR page faults, guest PAT ignore quirks, non-coherent DMA behavior, and MKTME/KeyID SPTE reserved-bit masking.

Security regression tests should cover L1TF mitigation mode transitions, L1D flush accounting, SPEC_CTRL save/restore when guest writes are passed through, VERW FB_CLEAR disabling/enabling, SGX enclave emulation denial, split-lock `#AC` policy, bus-lock userspace exits, and machine-check/NMI handling while interrupts are disabled.

Performance and fastpath signals should include WRMSR fastpath handling, preemption-timer LAPIC deadline handling, HLT and INVD fastpaths, PLE window growth/shrink traces, APIC EOI fast path, and absence of unnecessary VM-exits when features are intentionally passed through.

### subset-b-000902: lines 8867-8879

# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmx.c lines 8867-8879

## Scope

This chunk is the final success and failure tail of `vmx_init()`, the Intel VMX vendor module initializer for x86 KVM. The exact covered lines initialize per-CPU VMX lists and posted-interrupt state for every possible CPU, run the nested-VMX VMCS12 layout sanity check, return success, and define the only local unwind label for failure after common KVM vendor initialization.

The surrounding `vmx_init()` sequence is important context: it first verifies VMX support, initializes Hyper-V enlightened VMCS configuration, parses VMCS hardware capabilities, calls `kvm_x86_vendor_init(&vt_init_ops)`, and then sets up the L1D flush mitigation. Lines 8867-8879 execute only after those earlier global/vendor setup stages have succeeded.

## Purpose

The successful path prepares per-CPU VMX bookkeeping that later runtime paths assume is already initialized:

- `INIT_LIST_HEAD(&per_cpu(loaded_vmcss_on_cpu, cpu))` creates an empty list head for each possible CPU. This list tracks every VMCS currently loaded on that CPU.
- `pi_init_cpu(cpu)` initializes posted-interrupt wakeup list state and its per-CPU lock for the same CPU.
- `vmx_check_vmcs12_offsets()` asserts that KVM's nested-VMX `struct vmcs12` ABI layout still matches the fixed offsets exposed to L1 guests and userspace migration state.

The failure label handles errors from `vmx_setup_l1d_flush()` after `kvm_x86_vendor_init()` has already registered the vendor module and allocated common KVM resources. In that case, `kvm_x86_vendor_exit()` unwinds common x86 KVM state before `vmx_init()` returns the original error.

## Important APIs, Types, And Functions

`vmx_init()` is declared `int __init`, so this path runs during module/load initialization and its code may be discarded after init. It returns `0` on successful registration of VMX support or a negative errno on failure.

`for_each_possible_cpu(cpu)` iterates all CPUs that may ever be present, not just the CPUs online at module load time. That choice is deliberate because hotplugged CPUs need valid per-CPU list heads and posted-interrupt locks before VMX CPU-online paths or vCPU migration can use them.

`loaded_vmcss_on_cpu` is a `DEFINE_PER_CPU(struct list_head, loaded_vmcss_on_cpu)` in `vmx.c`. It backs several VMCS lifecycle paths:

- `vmx_vcpu_load_vmcs()` adds a vCPU's `loaded_vmcs->loaded_vmcss_on_cpu_link` to the destination CPU list after clearing it from any prior CPU.
- `vmx_emergency_disable_virtualization_cpu()` walks the local CPU list and clears all loaded VMCSs during emergency virtualization shutdown.
- `vmclear_local_loaded_vmcss()` walks the local CPU list during normal CPU virtualization disable and calls `__loaded_vmcs_clear()` for every entry.

`pi_init_cpu(int cpu)` is defined in `vmx/posted_intr.c`. It initializes `wakeup_vcpus_on_cpu` with `INIT_LIST_HEAD()` and initializes `wakeup_vcpus_on_cpu_lock` with `raw_spin_lock_init()`. That state is used by posted-interrupt scheduling paths such as `vmx_vcpu_pi_put()`, `vmx_vcpu_pi_load()`, and `pi_wakeup_handler()`.

`vmx_check_vmcs12_offsets()` is a static inline helper in `vmx/vmcs12.h`. It uses `ASSERT_STRUCT_OFFSET()` through `CHECK_OFFSET()` for fixed fields in `struct vmcs12`. The comments around the helper explain that VMCS12 field offsets must not change for save/restore compatibility, although appending fields or filling gaps is allowed.

`kvm_x86_vendor_exit()` is the common x86 KVM vendor teardown routine. In this error path it undoes the successful `kvm_x86_vendor_init()` call by unregistering perf callbacks, tearing down lapic/timer/notifier state, calling the vendor `hardware_unsetup` hook, destroying user-return MSR state, exiting MMU vendor support, destroying the x86 emulator cache, and clearing the active vendor ops pointer under `vendor_module_lock`.

## Control Flow

The relevant control flow is:

1. Earlier `vmx_init()` checks `kvm_is_vmx_supported()`, initializes eVMCS state, parses `vmcs_config` and `vmx_capability`, then calls `kvm_x86_vendor_init(&vt_init_ops)`.
2. After common vendor initialization succeeds, `vmx_setup_l1d_flush()` configures L1TF-related VM-entry flush behavior. This setup can allocate mitigation pages and can fail, typically with `-ENOMEM`.
3. If the L1D setup fails, control jumps to `err_l1d_flush`, calls `kvm_x86_vendor_exit()`, and returns `r`.
4. If L1D setup succeeds, `for_each_possible_cpu(cpu)` initializes VMCS and posted-interrupt per-CPU state for every possible CPU.
5. `vmx_check_vmcs12_offsets()` runs after per-CPU initialization. This is a sanity/ABI assertion stage, not a runtime capability probe.
6. `vmx_init()` returns `0`, completing VMX vendor module initialization.

There are no additional unwind labels after the per-CPU initialization loop. The operations in the loop are list-head and spinlock/list initialization and do not allocate memory or return errors.

## State And Persistence

The chunk mutates global/per-CPU kernel state that persists for the lifetime of the loaded VMX module:

- `loaded_vmcss_on_cpu[cpu]` starts as an empty linked list for each possible CPU. Runtime vCPU load, CPU hotplug, and emergency disable paths later add/remove `struct loaded_vmcs` entries.
- `wakeup_vcpus_on_cpu[cpu]` and `wakeup_vcpus_on_cpu_lock[cpu]` are initialized by `pi_init_cpu()` and persist as posted-interrupt scheduling infrastructure.
- `struct vmcs12` layout is not changed here, but `vmx_check_vmcs12_offsets()` enforces the persistent nested-state ABI contract compiled into KVM.

No file-backed persistence, userspace-visible object creation, or VM-specific allocation occurs in the covered lines. The persistence concern is kernel ABI/state continuity: initialized per-CPU state must remain valid until module exit, and VMCS12 layout must remain compatible with migration/save-restore users.

## Dependencies And Integration Points

This chunk depends on earlier initialization work in `vmx_init()`:

- `setup_vmcs_config(&vmcs_config, &vmx_capability)` must already have established VMX hardware capabilities.
- `kvm_x86_vendor_init(&vt_init_ops)` must already have installed the VMX vendor hooks into the common x86 KVM layer and run `vt_init_ops.hardware_setup`.
- `vmx_setup_l1d_flush()` must have completed because the per-CPU setup is reached only after mitigation state is ready.

The per-CPU VMCS list integrates with `struct loaded_vmcs` in `vmx/vmcs.h`, especially the `loaded_vmcss_on_cpu_link` member. The list is manipulated with interrupts disabled in migration paths where necessary, and `__loaded_vmcs_clear()` uses memory barriers to coordinate CPU ownership changes against `vmx_vcpu_load_vmcs()`.

The posted-interrupt initialization integrates with APICv and VT-d posted interrupt handling. Even if APICv is dynamically disabled for a VM, the initialized per-CPU wakeup lists and locks are still part of the always-compiled VMX posted-interrupt support and are used when conditions allow posted interrupts.

The VMCS12 offset check integrates with nested virtualization, `KVM_GET_NESTED_STATE`/`KVM_SET_NESTED_STATE` compatibility, and L1-visible `MSR_IA32_VMX_BASIC` revision/size semantics. It is a guardrail for developers changing `struct vmcs12`, not a dynamic hardware feature.

The error path integrates with common KVM x86 module lifecycle rules. Because `kvm_x86_vendor_init()` has a "point of no return" internally after some stages, this chunk avoids adding complex unwind below its own post-L1D setup point and delegates cleanup to `kvm_x86_vendor_exit()`.

## Risks And Edge Cases

The main correctness risk is CPU hotplug coverage. Using online CPUs instead of possible CPUs would leave list heads or posted-interrupt locks uninitialized for CPUs hot-added after module load. This chunk uses `for_each_possible_cpu()`, which matches the later per-CPU access patterns.

`loaded_vmcss_on_cpu` is critical for safe VMCS cleanup. If its list heads are not initialized before a vCPU can be loaded or before CPU teardown/emergency paths can walk them, list corruption or crashes are possible. The covered loop must therefore stay before any successful return from `vmx_init()`.

The posted-interrupt state has locking and IRQ-context constraints. `pi_init_cpu()` initializes a raw spinlock that later code takes with interrupts disabled and sometimes under scheduler interactions. Missing or late initialization would break wakeup-vector handling for blocking vCPUs with posted interrupts.

`vmx_check_vmcs12_offsets()` protects nested VMX ABI compatibility. A failed offset assertion is a build/development signal that a VMCS12 layout change would break save/restore compatibility. Removing or bypassing this check could allow subtle live migration or nested-state restore corruption.

The `err_l1d_flush` label only covers failures after common vendor init and before per-CPU no-fail initialization. If a new fallible operation is added after the per-CPU loop, it must be audited for any additional cleanup requirements. The current loop does not need cleanup because reinitializing empty list heads and locks during failed module init has no external allocation to release.

The L1D flush setup failure path is security-sensitive. If mitigation setup fails, the module must not continue with partially configured L1TF mitigation state. Returning through `kvm_x86_vendor_exit()` preserves the invariant that VMX is not registered when required mitigation resources could not be set up.

## Test Signals

Useful validation signals for this chunk include:

- Building KVM with VMX enabled, which catches `vmx_check_vmcs12_offsets()` layout assertions and declaration mismatches for `pi_init_cpu()`.
- Loading `kvm-intel` on VMX-capable hardware and verifying successful module init reaches the `return 0` path.
- Fault-injection or constrained-memory testing around `vmx_setup_l1d_flush()` to confirm failure returns unwind through `kvm_x86_vendor_exit()` and do not leave VMX registered.
- CPU hotplug tests with KVM loaded, exercising CPUs that were possible but not online at module load, to verify per-CPU VMCS and posted-interrupt state was initialized early enough.
- vCPU migration and CPU offline tests that force `vmx_vcpu_load_vmcs()`, `vmclear_local_loaded_vmcss()`, and `vmx_emergency_disable_virtualization_cpu()` to manipulate `loaded_vmcss_on_cpu`.
- APICv/posted-interrupt tests with blocking vCPUs and assigned/bypass interrupts, validating that `wakeup_vcpus_on_cpu` and its lock are usable on all possible CPUs.
- Nested VMX state migration tests, especially `KVM_GET_NESTED_STATE`/`KVM_SET_NESTED_STATE`, to detect any VMCS12 layout drift not already caught at build time.
