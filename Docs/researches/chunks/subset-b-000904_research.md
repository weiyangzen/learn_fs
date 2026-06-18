# sources/distributed-fs/ceph-client/arch/x86/kvm/x86.c lines 1-9624

## Scope

This chunk covers the first 9,624 lines of KVM's x86 architecture core. It spans module-global capability state, MSR exposure and emulation, exception injection, control/debug register handling, pvclock/TSC synchronization, paravirtual MSRs, vCPU/device/VM ioctls, MSR filtering, MMIO/PIO access helpers, and the beginning of the x86 instruction-emulation path. The file continues past this chunk, so run-loop completion, later emulation writeback, vCPU/VM lifecycle, APICv, memory-slot, async-page, and module init/exit behavior must be reconciled with later chunk reports.

## Purpose

The code in this range is the common x86 KVM layer that sits between generic KVM UAPI/core code and vendor-specific VMX/SVM implementations. It validates x86 architectural state requested by userspace or guests, stores that state in `struct kvm_arch` and `struct kvm_vcpu_arch`, delegates hardware-specific operations through `kvm_x86_ops` static calls, and translates guest-visible events into KVM requests, exits, or emulation outcomes.

It also defines much of the userspace ABI surface for x86 KVM: capability reporting, global device ioctls, VM ioctls, vCPU ioctls, MSR lists, one-reg access, nested-state routing, Hyper-V/Xen capability plumbing, pvclock control, and optional exits for MSR faults, hypercalls, emulation failures, bus locks, and PMU control.

## Important State, Types, And Globals

- `struct kvm_caps kvm_caps` and `struct kvm_host_values kvm_host` hold recomputed vendor-module capabilities and host XCR/XSS/MSR data. The comment explicitly requires recomputation on vendor module load, avoiding stale values across VMX/SVM reloads.
- `struct kvm_x86_ops kvm_x86_ops` plus generated `DEFINE_STATIC_CALL_NULL(kvm_x86_*)` entries are the main integration seam to VMX/SVM code. Common code uses `kvm_x86_call()` for hardware-specific validation, register access, MSR handling, TLB flushes, ioctls, nested ops, and memory-encryption hooks.
- Module parameters in this chunk shape behavior: `ignore_msrs`, `report_ignored_msrs`, `min_timer_period_us`, `tsc_tolerance_ppm`, `enable_vmware_backdoor`, `force_emulation_prefix`, `pi_inject_timer`, `enable_pmu`, `eager_page_split`, and `mitigate_smt_rsb`.
- MSR exposure is split into `msrs_to_save_base`, `msrs_to_save_pmu`, `emulated_msrs_all`, and `msr_based_features_all_except_vmx`, then probed into runtime arrays by `kvm_init_msr_lists()`. This distinction drives `KVM_GET_MSR_INDEX_LIST`, `KVM_GET_MSR_FEATURE_INDEX_LIST`, and host-initiated MSR save/restore ABI.
- Per-CPU `struct kvm_user_return_msrs user_return_msrs` lets KVM temporarily load guest values for selected MSRs consumed on user return, then restores host values via a `user_return_notifier`.
- `struct pvclock_gtod_data`, per-CPU `cpu_tsc_khz`, `kvm_guest_has_master_clock`, and per-VM `pvclock_sc`/`tsc_write_lock` coordinate host clock snapshots and guest pvclock monotonicity.
- `struct kvm_x86_msr_filter`, `struct msr_bitmap_range`, and compat filter structs implement userspace-controlled MSR filtering under SRCU/RCU replacement.
- `struct read_write_emulator_ops` and `static const struct x86_emulate_ops emulate_ops` connect the generic x86 emulator to KVM-specific GVA translation, MMIO/PIO exits, register access, MSR access, segmentation, control registers, PMU reads, CPUID, SMM, NMI masking, and failure reporting.

## Key APIs And Functions

- MSR access and filtering:
  - `kvm_do_msr_access()` centralizes unsupported-MSR handling, zeroes read data on failure, honors advertised MSRs for host-initiated zero/read cases, and applies `ignore_msrs`/`report_ignored_msrs`.
  - `__kvm_set_msr()`, `__kvm_get_msr()`, `kvm_msr_write()`, `kvm_msr_read()`, `kvm_emulate_msr_read()`, and `kvm_emulate_msr_write()` divide host-initiated accesses from guest-emulated accesses and apply MSR filters for guest paths.
  - `kvm_set_msr_common()` and `kvm_get_msr_common()` implement common MSR semantics: EFER, PAT/MTRRs, APIC/x2APIC, TSC/TSC_ADJUST, pvclock, async PF, steal time, PV EOI, PMU MSRs, Hyper-V/Xen MSRs, machine-check banks, CET/XFD/XSS, power/misc platform MSRs, OSVW, and legacy compatibility MSRs.
  - `msr_io()` and `__msr_io()` support batched userspace `KVM_GET_MSRS`/`KVM_SET_MSRS`, temporarily loading guest FPU state for XSTATE-managed MSRs.
- Exception/event control:
  - `exception_class()`, `exception_type()`, `kvm_multiple_exception()`, `kvm_queue_exception*()`, `kvm_requeue_exception()`, `kvm_inject_page_fault()`, and `kvm_inject_emulated_page_fault()` implement x86 exception queuing, double-fault/triple-fault synthesis, nested exception-VMEXIT conversion, payload delivery, and MMU invalidation for emulated page faults.
  - `kvm_inject_nmi()`, vCPU event get/set helpers, and `kvm_prepare_event_vectoring_exit()` bridge event state between KVM internals and userspace migration/debug ABI.
- Register and CPU state:
  - `kvm_set_cr0()`, `kvm_set_cr3()`, `kvm_set_cr4()`, `kvm_set_cr8()`, `kvm_get_cr8()`, and post-set helpers validate architectural dependencies, update MMU roles, reload PDPTRs, and request TLB flushes.
  - `__kvm_set_xcr()`, `kvm_emulate_xsetbv()`, XFD/XSS paths, `kvm_load_xfeatures()`, and PKRU helpers maintain guest extended-state eligibility and dynamic CPUID dirtiness.
  - `kvm_set_dr()`, `kvm_get_dr()`, `kvm_update_dr7()`, and debugreg ioctls enforce fixed/reserved bits and guest-debug overrides.
- Timekeeping:
  - `kvm_get_time_scale()`, `kvm_set_tsc_khz()`, `kvm_synchronize_tsc()`, `__kvm_synchronize_tsc()`, `kvm_track_tsc_matching()`, `kvm_update_masterclock()`, `kvm_guest_time_update()`, `get_kvmclock()`, and `kvm_get_wall_clock_epoch()` implement TSC scaling, TSC offset synchronization across vCPU generations, masterclock enablement, pvclock writes, wall-clock epoch writes, and suspend/CPU-frequency reactions.
- UAPI dispatch:
  - `kvm_vm_ioctl_check_extension()` reports x86 KVM capability values, often depending on `kvm_caps`, compile options, in-kernel irqchip mode, host bugs/mitigations, PMU enablement, TDP, and protected-state availability.
  - `kvm_arch_dev_ioctl()` serves global x86 ioctls such as MSR index lists, supported/emulated CPUID, MCE capabilities, MSR feature reads, Hyper-V CPUID, and device attributes.
  - `kvm_arch_vcpu_ioctl()` handles LAPIC state, interrupt/NMI/SMI injection, CPUID set/get, MSR batches, one-reg state, MCE setup/injection, vCPU event state, debug regs, XSAVE/XCRS, TSC controls, pvclock paused flag, vCPU enable-cap, nested state, Xen vCPU attributes, SREGS2, and vCPU memory-encryption ioctls.
  - `kvm_arch_vm_ioctl()` handles VM-level TSS/identity-map/MMU-page controls, irqchip/PIT/PIC/IOAPIC state, boot CPU ID, Xen HVM config, VM clock, default TSC frequency, memory encryption, Hyper-V eventfd, PMU event filtering, and MSR filters.
- Emulator integration:
  - `kvm_read_guest_virt*()`, `kvm_write_guest_virt*()`, `kvm_mmu_gva_to_gpa_*()`, and `translate_nested_gpa()` bridge emulator virtual addresses to guest physical accesses through the active walk MMU.
  - `vcpu_mmio_read()`, `vcpu_mmio_write()`, `emulator_read_write_onepage()`, and `emulator_read_write()` distinguish RAM, in-kernel MMIO, and userspace MMIO fragments, including split-page accesses and read re-emulation.
  - PIO helpers build `KVM_EXIT_IO` exits and complete prior userspace reads.
  - `emulator_cmpxchg_emulated()` attempts atomic userspace cmpxchg on backed memory, avoids split-lock hazards, dirty-logs writes, and falls back to write emulation.
  - `alloc_emulate_ctxt()`, `init_emulate_ctxt()`, `x86_decode_emulated_instruction()`, and `x86_emulate_instruction()` set up decode mode, handle code breakpoints, forced emulation prefix, VMware backdoor checks, retry-on-write-protected-shadow-page logic, emulation-failure exits, PIO/MMIO exits, and nested intercept checks. The function continues beyond the chunk after assigning `complete_emulated_mmio`.

## Control Flow

MSR control flow generally enters from guest instruction emulation, vCPU ioctls, or device ioctls. Guest paths call `kvm_emulate_msr_read/write()`, first applying `kvm_msr_allowed()` against any VM filter, then using `kvm_do_msr_access()` with `host_initiated=false`. Userspace paths use `do_get_msr()`/`do_set_msr()` through `msr_io()` or one-reg helpers with `host_initiated=true`; immutable feature MSRs are blocked after CPUID is frozen unless writing the current value. Common MSRs are handled locally, while vendor-specific MSRs fall through to `kvm_x86_ops.set_msr/get_msr`.

Exception control flow queues events in `vcpu->arch.exception` or `exception_vmexit`, requests `KVM_REQ_EVENT`, and lets later entry/run code inject or exit. Multiple fault combinations synthesize #DF or request triple fault. Page faults carry payloads via CR2 or nested VMEXIT state; emulated page faults also invalidate stale MMU translations when a present translation fault could otherwise loop.

CR0/CR4/CR3 changes validate architectural invariants before calling vendor callbacks and then update KVM MMU context. Changes to paging, WP, PAE, PCID, PGE, SMEP, and LA57 determine whether KVM resets the MMU, unloads roots, reloads PDPTRs, or requests guest/current TLB flushes. CR3 handling preserves PCID no-flush semantics while invalidating the relevant current or previous roots for shadow MMU.

Timekeeping control flow is lock-heavy. TSC writes and TSC offset device attributes take `kvm->arch.tsc_write_lock`, update per-VM generation fields, write the vendor TSC offset/multiplier, and request masterclock or clock updates when synchronization changes. `kvm_guest_time_update()` snapshots the pvclock seqcount, disables IRQs while reading host TSC/frequency, applies catchup if needed, and writes pvclock data through `gfn_to_pfn_cache` objects for KVM, Hyper-V, and Xen clock pages.

Ioctl dispatch control flow loads the vCPU for vCPU ioctls, validates protected-state restrictions, copies userspace structs, invokes internal helpers under `srcu` or VM mutexes where needed, and copies results back. VM capability enablement is usually guarded by `kvm->lock` and rejected after vCPU or irqchip creation for modes that must be chosen before topology becomes visible.

Emulation control flow starts with vendor `check_emulate_instruction()`, optional decode, code-breakpoint handling, retry decisions for shadow-page write-protection failures, and then `x86_emulate_insn()`. Memory callbacks first try guest RAM if MMIO is not known, then in-kernel buses, then queue userspace exits. PIO and MMIO reads stop emulation until userspace supplies data; writes may continue and exit later.

## State And Persistence Behavior

Most state is persistent only for the lifetime of a VM/vCPU in kernel memory. Guest-visible state is stored under `vcpu->arch` and `kvm->arch`: exceptions, interrupts, NMI/SMI state, CRs, DRs, EFER, PAT, MTRRs, xcr0/xss/xfd, FPU/XSTATE, APF caches, steal-time config, pvclock GPA caches, TSC offsets/generations, MCE banks, LAPIC state, Xen/Hyper-V state, disabled quirks, MSR filters, irqchip mode, and memory-encryption context routing.

Userspace persistence for migration is implemented through ioctls in this chunk: MSR batches, CPUID, debug regs, vCPU events, XSAVE/XCRS, SREGS2, LAPIC, nested state, MCE state, VM clock, irqchip/PIT state, and one-reg SSP. Several ABI compatibility paths are explicit, e.g. conflating pending/injected exception payloads when `KVM_CAP_EXCEPTION_PAYLOAD` is not enabled, returning legacy MSR values for old guests, allowing advertised-but-unsupported host-initiated zero MSR writes, and preserving legacy TSC synchronization tolerance.

Guest memory writes occur through `kvm_write_guest()`, `kvm_vcpu_write_guest()`, gfn caches, and user access helpers. The code marks dirty pages for pvclock, steal time, cmpxchg, and page-track writes so migration and dirty logging observe guest-visible side effects. MSR filters are RCU-replaced and freed after `synchronize_srcu()`, making them persistent VM policy until changed.

## Dependencies And Integration Points

This chunk depends heavily on adjacent KVM x86 modules:

- MMU: `kvm_mmu_reset_context()`, `kvm_mmu_new_pgd()`, `kvm_mmu_free_roots()`, `kvm_mmu_sync_roots()`, `kvm_mmu_gva_to_gpa_*`, page tracking, TDP flags, and shadow-page retry helpers.
- LAPIC/IOAPIC/PIT/PIC/IRQ routing: APIC base/x2APIC MSRs, TPR/CR8, TSC deadline, interrupt injection, irqchip creation, MMIO fast paths, and timer migration.
- PMU: PMU MSR validation, RDPMC, PMU capability reporting, event filters, refresh, and fastpath emulation.
- Hyper-V and Xen: Hyper-V MSRs, CPUID, SynIC, enlightened VMCS/direct TLB flush, TSC pages, eventfd, Xen HVM/vCPU attributes, Xen pvclock/runstate/event-channel support.
- SMM/MCE/FPU/XSTATE: SMI/SMM event migration, SMBASE/SMM guards, MCE bank injection, guest FPU state load/copy, CET shadow-stack MSRs, XFD, XSS, PKRU.
- Host kernel subsystems: user-return notifiers, SRCU/RCU, seqcounts, raw spinlocks, cpufreq/timekeeper notifiers, sched info, perf/Intel PT capability checks, mitigation flags, memory encryption hooks, `copy_{to,from}_user`, and `user_access_begin`.

## Risks And Edge Cases

- MSR ABI compatibility is fragile. `ignore_msrs`, user-space MSR exits, advertised-but-unsupported MSRs, immutable feature MSR blocking, and host-versus-guest initiated checks must stay consistent or migration and guest behavior can regress.
- Timekeeping has high concurrency risk. Masterclock toggling, TSC generation matching, unstable/backwards TSC detection, CPU migration, suspend, cpufreq, TSC scaling, and Xen/Hyper-V clock overlays all share state guarded by seqcounts and `tsc_write_lock`; ordering bugs can break guest monotonicity.
- Exception migration is subtle. The file intentionally handles payload compatibility quirks and nested VMEXIT exceptions; saving the wrong exception or prematurely delivering payloads can lose #DB/#PF data or create spurious exits.
- CR0/CR4/CR3 validation must match x86 architectural ordering. Missing checks around LME/LMA, PAE/PDPTRs, PCID, CET/WP, LA57, and TLB flush scope can cause guest-visible faults, stale translations, or incorrect nested behavior.
- Emulator memory handling preserves historical ABI by treating failed host user memory access as MMIO in some cases. That compatibility can hide true memory errors and makes changes to MMIO/RAM fallback risky.
- Atomic cmpxchg emulation uses host userspace HVA operations and dirty logging. Split-lock detection, page crossing, error HVA, and page tracking must remain aligned with host security and migration semantics.
- Protected/confidential guest state intentionally rejects or no-ops several state ioctls. Later chunks must verify lifecycle and run-loop code preserve these restrictions consistently.
- Capability enablement often depends on call ordering before vCPU/irqchip creation. Userspace-visible behavior can break if locks or creation checks change.

## Test Signals

Useful validation signals for this chunk include:

- KVM selftests for x86 MSR behavior: get/set MSR lists, unknown MSR exits, MSR filters, feature MSRs after CPUID freeze, TSC/TSC_ADJUST, XFD/XSS/CET MSRs, PMU MSRs, and Hyper-V/Xen MSRs when configured.
- Selftests for exception payloads, vCPU events migration, debug registers, single-step/hardware breakpoints, nested exception VMEXIT routing, and triple-fault event delivery.
- TSC/pvclock tests covering `KVM_SET_CLOCK`, `KVM_GET_CLOCK`, TSC scaling, `KVM_SET_TSC_KHZ`, vCPU migration between CPUs, suspend/resume notifier behavior, steal time, async PF, and Xen/Hyper-V pvclock pages.
- Ioctl ABI tests for protected-state rejection, one-reg SSP exposure, XSAVE/XSAVE2/XCRS, SREGS2, LAPIC state, MCE setup/injection, irqchip/PIT creation, split irqchip, disable-exits, x2APIC API flags, PMU capability disablement, and VM type support.
- Emulator tests for MMIO/PIO exits and completion, forced-emulation prefix, VMware backdoor gating, UD/GP behavior, APIC MMIO, cross-page accesses, cmpxchg dirty logging, and retry after write-protected shadow-page faults.
- Kernel runtime signals: `trace_kvm_*` events for MSR, MMIO, PIO, pvclock, TSC tracking, and emulation failures; `vcpu->stat` counters for exits, TLB flushes, page faults, MMIO exits, instruction emulation, and emulation failures.

## Cross-Chunk Handoff

At line 9624, `x86_emulate_instruction()` is still in progress after setting `vcpu->arch.complete_userspace_io = complete_emulated_mmio` for MMIO exits. Later chunks must cover the rest of emulation completion/writeback, run-loop request processing, vCPU lifecycle, VM memory-slot/lifecycle operations, APICv inhibition, async page completion, memory failure handling, vendor initialization, and module init/exit to produce the final per-file research document.
