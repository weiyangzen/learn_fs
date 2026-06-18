# Research: subset-b-000896

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/avic.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/avic.c

## Purpose
`avic.c` implements AMD SVM AVIC/x2AVIC support for KVM: hardware-accelerated local APIC register virtualization, IPI delivery, posted interrupt integration with AMD IOMMU, and runtime APICv activation/deactivation. It owns the per-VM AVIC logical/physical ID tables, VM IDs used in IOMMU GA log tags, x2APIC MSR pass-through policy, and vCPU load/put transitions that publish the host physical CPU to AVIC hardware.

## Important APIs, types, and functions
- Module parameters: `avic`, `enable_ipiv`, and unsafe `force_avic` control feature enablement. `avic_param_set()` accepts `auto`; `avic_want_avic_enabled()` turns auto into the Zen4+/x2AVIC default.
- VM lifecycle: `avic_vm_init()`, `avic_alloc_physical_id_table()`, and `avic_vm_destroy()` allocate/free the logical ID table, physical ID table, assign a nonzero `avic_vm_id`, and maintain `svm_vm_data_hash`.
- vCPU lifecycle and VMCB setup: `avic_init_vcpu()`, `avic_init_backing_page()`, `avic_init_vmcb()`, `avic_activate_vmcb()`, and `avic_deactivate_vmcb()` program VMCB AVIC fields, APIC access page requirements, APICv inhibit state, CR8 intercepts, and x2APIC MSR intercepts.
- Interrupt delivery: `avic_incomplete_ipi_interception()`, `avic_ring_doorbell()`, `avic_kick_target_vcpus_fast()`, `avic_kick_target_vcpus()`, and physical/logical kick helpers emulate or complete IPIs that hardware cannot deliver.
- APIC register synchronization: `avic_unaccelerated_access_interception()`, `avic_unaccel_trap_write()`, `avic_handle_ldr_update()`, `avic_handle_dfr_update()`, and `avic_apicv_post_state_restore()` keep the AVIC logical table aligned with guest APIC state.
- IOMMU posted interrupts: `avic_pi_update_irte()`, `avic_update_iommu_vcpu_affinity()`, `__avic_vcpu_load()`, `__avic_vcpu_put()`, `avic_vcpu_blocking()`, and `avic_vcpu_unblocking()` update AMD IOMMU IRTE state and per-vCPU AVIC physical entries.
- Hardware registration: `avic_hardware_setup()` and `avic_hardware_unsetup()` enable AVIC/x2AVIC and register/unregister the AMD IOMMU GA log notifier.

## Control flow
Initialization starts at hardware setup, which validates NPT, AVIC CPUID, SNP-host constraints, x2AVIC support, and erratum-driven `enable_ipiv` policy before registering `avic_ga_log_notifier()`. VM initialization allocates logical and physical APIC ID tables and inserts the VM into the VM-ID hash. vCPU initialization creates a valid AVIC backing page entry indexed by vCPU ID unless the ID exceeds the hardware maximum, in which case it inhibits APICv immediately.

On VMCB initialization or APICv refresh, KVM toggles VMCB control bits, CR8 intercepts, and x2APIC MSR interception according to `kvm_vcpu_apicv_active()` and current APIC mode. Running vCPUs go through `avic_vcpu_load()` and `avic_vcpu_put()`; these publish or clear `AVIC_PHYSICAL_ID_ENTRY_IS_RUNNING`, record host APIC IDs, and update IOMMU posted-interrupt affinity under `ir_list_lock`. Blocking vCPUs clear `IsRunning` and set synthetic GA-log behavior so external interrupts wake them through the GA log path.

IPI VM exits enter `avic_incomplete_ipi_interception()`. Invalid target or unsupported interrupt type exits are emulated through the local APIC. Target-not-running exits rely on hardware-populated IRR bits and only wake affected vCPUs. Fast path matching avoids scanning all vCPUs when destination APIC IDs map directly; slow path uses `kvm_apic_match_dest()`.

## State and persistence behavior
Persistent VM state includes `avic_vm_id`, `avic_logical_id_table`, and `avic_physical_id_table`. Per-vCPU state includes cached physical ID entry, saved LDR/DFR values, `x2avic_msrs_intercepted`, and the per-vCPU `ir_list` of IRQ bypass entries. The VM-ID hash is global and protected by `svm_vm_data_hash_lock`; per-vCPU IRTE metadata is protected by `ir_list_lock`. The backing page address is derived from the local APIC register page and tagged through `__sme_set()`.

AVIC physical table entries are updated on scheduling and blocking transitions, not just on APICv enablement. Logical table entries are invalidated and rewritten as LDR/DFR changes are trapped. Hardware state in VMCB control fields is marked dirty via `vmcb_mark_dirty()` where needed.

## Dependencies and integration points
This file integrates with KVM LAPIC/APICv (`lapic.h`, `kvm_apic_*`, `kvm_set_apicv_inhibit()`), AMD SVM VMCB management (`svm.h`, intercept helpers), AMD IOMMU IRQ remapping (`irq_set_vcpu_affinity()`, `amd_iommu_*`, GA log notifier), IRQ bypass/irqfd, CPU feature probing, SEV-ES/SNP constraints, and KVM request handling (`KVM_REQ_TLB_FLUSH_CURRENT`, `KVM_REQ_APICV_UPDATE`). It also emits AVIC tracepoints for GA log, doorbell, incomplete IPI, and slow-path wake decisions.

## Risks and edge cases
- Correctness depends on vCPU ID/APIC ID identity; oversized IDs inhibit APICv, and x2AVIC sizing must match table allocation.
- Doorbell signaling can race with migration; the code intentionally tolerates stale CPU signaling because a migrated vCPU will process interrupts on next VMRUN.
- IOMMU IRTE metadata must be synchronized with schedule-in/out and blocking transitions; missed `ir_list_lock` ordering could leave stale pCPU or GA-log state.
- Family 17h IPI virtualization is disabled for erratum 1235, showing sensitivity to memory ordering around `IsRunning`.
- Nested virtualization inhibits APICv, and nested MSR bitmap ownership can prevent x2APIC intercept updates from being applied.
- SNP hosts without `HvInUseWrAllowed` disable AVIC to avoid unsafe host/guest hypervisor-in-use writes.

## Test signals
Useful tests include KVM selftests for APICv/AVIC inhibit reasons, xAPIC and x2APIC IPI delivery, blocking vCPU wakeups, irqfd/posted interrupt affinity migration, nested virtualization APICv disablement, CPU hotplug or vCPU migration stress, and boot-time parameter combinations (`avic=auto`, disabled NPT, forced AVIC, SNP host). Tracepoints `kvm_avic_*` and IOMMU posted interrupt behavior provide runtime evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/avic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/hyperv.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/hyperv.c

## Purpose
`hyperv.c` provides the SVM-specific implementation for injecting a Hyper-V enlightened synthetic VM exit after an L2 TLB flush hypercall. It is small but important glue between KVM's Hyper-V emulation and SVM nested virtualization.

## Important APIs, types, and functions
- `svm_hv_inject_synthetic_vmexit_post_tlb_flush(struct kvm_vcpu *vcpu)` is the sole exported function in this file.
- It uses `to_svm()` to access the SVM vCPU, writes VMCB exit fields, asserts `HV_SVM_EXITCODE_ENL == SVM_EXIT_SW`, and calls `nested_svm_vmexit()`.

## Control flow
The function is called after L0 handles an enlightened L2 TLB flush hypercall that should be reported to L1 as a Hyper-V synthetic exit. It writes the software-defined exit code into `exit_code`, sets `exit_info_1` to `HV_SVM_ENL_EXITCODE_TRAP_AFTER_FLUSH`, clears `exit_info_2`, and immediately routes through the generic nested SVM VM-exit path.

## State and persistence behavior
It mutates only the active VMCB control exit fields for the vCPU and relies on `nested_svm_vmexit()` to persist the result back into vmcb12, leave guest mode, and restore L1 state. No independent allocation or long-lived state is kept here.

## Dependencies and integration points
The file depends on `hyperv.h` for Hyper-V/SVM constants and on nested SVM support for `nested_svm_vmexit()`. Its caller is selected through Hyper-V nested operations and the SVM nested ops table. It is compiled only when the corresponding Hyper-V support is enabled through the declarations in `hyperv.h`.

## Risks and edge cases
The function assumes the vCPU is currently in nested guest mode and that `svm->vmcb` refers to the L2-running VMCB. Calling it outside that context would synthesize an exit into the wrong state. The build-time assertion protects against mismatch between the Hyper-V software exit encoding and AMD's reserved software exit code.

## Test signals
Signals are Hyper-V-on-KVM nested tests that issue L2 TLB flush hypercalls with enlightened VMCB enabled, then verify L1 observes `HV_SVM_EXITCODE_ENL` and `HV_SVM_ENL_EXITCODE_TRAP_AFTER_FLUSH`. Nested migration tests should confirm no persistent state beyond vmcb12 exit fields is needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/hyperv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/hyperv.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/hyperv.h

## Purpose
`hyperv.h` defines SVM-specific inline helpers for Hyper-V nested enlightenment state. It bridges the enlightened VMCB fields in SVM's nested control cache to KVM's generic Hyper-V vCPU state and provides feature checks for direct L2 TLB flush hypercalls.

## Important APIs, types, and functions
- `nested_svm_hv_update_vm_vp_ids()` copies `partition_assist_page`, `hv_vm_id`, and `hv_vp_id` from `svm->nested.ctl.hv_enlightenments` into `hv_vcpu->nested`.
- `nested_svm_l2_tlb_flush_enabled()` checks the enlightened VMCB control bit and the Hyper-V VP assist direct-hypercall feature.
- `nested_svm_is_l2_tlb_flush_hcall()` combines guest CPUID exposure, the nested flush enablement check, and `kvm_hv_is_tlb_flush_hcall()`.
- `svm_hv_inject_synthetic_vmexit_post_tlb_flush()` is declared when `CONFIG_KVM_HYPERV` is enabled and stubbed otherwise.

## Control flow
Nested SVM copies enlightened VMCB control fields into its cache and then calls `nested_svm_hv_update_vm_vp_ids()` during nested guest entry. When L2 executes a VMMCALL, nested SVM's special-exit path consults `nested_svm_is_l2_tlb_flush_hcall()` so L0 can handle direct flush hypercalls instead of forwarding them to L1 as generic VMMCALL exits. If L0 must notify L1 after the flush, the implementation in `hyperv.c` injects a synthetic exit.

## State and persistence behavior
The helper persists Hyper-V nested VM/VP identifiers and the partition assist page GPA in `struct kvm_vcpu_hv`. It does not allocate memory. Its output remains tied to the currently cached vmcb12 control state and must be refreshed when L1 changes enlightened VMCB fields.

## Dependencies and integration points
The header depends on `asm/mshyperv.h`, KVM's generic x86 Hyper-V support (`../hyperv.h`), and SVM internals (`svm.h`). It is called from `nested.c` during guest entry and special-exit classification. The `#ifdef CONFIG_KVM_HYPERV` stubs keep the nested SVM code buildable without Hyper-V support.

## Risks and edge cases
The helpers must tolerate `to_hv_vcpu(vcpu)` returning NULL. TLB flush acceleration is allowed only when both L1's enlightened VMCB and L2's VP assist page opt in; missing either condition falls back to ordinary nested exit handling. Stale VM/VP IDs are possible if callers fail to refresh after vmcb12 changes.

## Test signals
Relevant tests exercise nested Hyper-V enlightened VMCB with and without VP assist direct hypercalls, verify fallback behavior when `CONFIG_KVM_HYPERV` is absent, and validate VM/VP ID propagation across VMRUN, migration, and clean-field optimizations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/hyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/nested.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/nested.c

## Purpose
`nested.c` implements nested AMD SVM virtualization for KVM. It emulates L1's VMRUN/VMEXIT model, validates and caches vmcb12, synthesizes vmcb02 by merging L0 and L1 controls, manages nested NPT/MMU state, routes exits between L0 and L1, and implements KVM's nested state migration ioctls for SVM.

## Important APIs, types, and functions
- Entry and exit: `nested_svm_vmrun()`, `enter_svm_guest_mode()`, `nested_svm_vmexit()`, `svm_leave_nested()`, and `nested_svm_exit_handled()` are the central nested transition APIs.
- VMCB validation/cache: `nested_svm_copy_vmcb12_to_cache()`, `__nested_copy_vmcb_control_to_cache()`, `nested_copy_vmcb_save_to_cache()`, `nested_svm_check_cached_vmcb12()`, `nested_vmcb_check_controls()`, and `nested_vmcb_check_save()` sanitize and validate L1-provided state.
- vmcb02 synthesis: `nested_vmcb02_prepare_control()`, `nested_vmcb02_prepare_save()`, `nested_vmcb02_recalc_intercepts()`, `nested_svm_merge_msrpm()`, and `nested_vmcb02_compute_g_pat()` combine vmcb01 and vmcb12.
- MMU/NPT: `nested_svm_init_mmu_context()`, `nested_svm_uninit_mmu_context()`, `nested_svm_load_cr3()`, and `nested_svm_inject_npf_exit()` switch KVM to nested NPT walking and reflect nested page faults to L1.
- Event and exit routing: `nested_svm_exit_special()`, `svm_check_nested_events()`, `nested_svm_inject_exception_vmexit()`, `nested_svm_intercept()`, and MSR/IO bitmap helpers decide whether L0 handles an exit or L1 receives it.
- State persistence/migration: `svm_get_nested_state()`, `svm_set_nested_state()`, `svm_get_nested_state_pages()`, and `svm_nested_ops` expose nested state to KVM core/userspace.
- Allocation: `svm_allocate_nested()` and `svm_free_nested()` allocate a SNP-safe vmcb02 page and nested MSRPM.

## Control flow
`nested_svm_vmrun()` checks SVM permissions, hsave setup, SMM restrictions, VP assist validity, vmcb12 GPA validity, then maps vmcb12 and copies control/save state into cached structures. Validation failures write `SVM_EXIT_ERR` into vmcb12 and skip the emulated VMRUN instruction. On success, KVM advances RIP, saves L1 state in vmcb01, marks `nested_run_pending`, and enters guest mode.

Guest entry switches `svm->vmcb` to vmcb02, requests TLB/MMU synchronization, enters KVM guest mode, optionally initializes nested NPT MMU, calculates nested TSC offset/scaling, merges intercepts and MSRPM, copies L2 save state into vmcb02, loads CR3, sets GIF, refreshes APICv if needed, and updates Hyper-V VM/VP IDs.

While L2 runs, exits first pass through special handling. Exits that L0 must own, such as host-intercepted exceptions, NPF, NMI/interrupt handling, or Hyper-V L2 TLB flush hypercalls, are retained by L0. Otherwise `nested_svm_intercept()` checks L1's intercept bitmaps or IO/MSR permission maps. If L1 owns the exit, `nested_svm_vmexit()` writes vmcb02 state and pending injected events back to vmcb12, leaves guest mode, restores vmcb01/L1 CPU state, resets nested MMU/TSC/LBR state, drops L2 pending events, clears nested-run state, and refreshes APICv.

Userspace migration enters through `svm_get_nested_state()` and `svm_set_nested_state()`. Restore validates user-provided control/save areas, leaves any existing nested mode, sets GIF and pending-run flags, rebuilds vmcb02, reloads CR3/MMU state, forces MSRPM recalculation, and requests nested-state pages before running.

## State and persistence behavior
The SVM nested state lives under `svm->nested`: vmcb02 pointer/physical address, nested MSRPM, cached control/save areas, vmcb12 GPA, last vmcb12 GPA, forced MSRPM recalculation flag, last bus-lock RIP, Hyper-V enlightenments, and nested NPT CR3. vmcb01 stores L1 state while L2 runs. vmcb02 stores merged execution state. vmcb12 is guest memory owned by L1 and is updated on nested exits.

State is persisted to userspace through `struct kvm_nested_state` plus a full-sized SVM VMCB image. Clean-bit optimizations are honored for repeated vmcb12 entries, but freeing vmcb02 invalidates `last_vmcb12_gpa` to avoid stale clean-field assumptions.

## Dependencies and integration points
This file integrates deeply with KVM x86 core guest-mode helpers, MMU/NPT (`kvm_init_shadow_npt_mmu`, `kvm_mmu_new_pgd`), SVM VMCB/intercept helpers, LAPIC/APICv, Hyper-V nested enlightenment helpers, SMM support, CPU feature gating, tracepoints, and KVM migration ABI. It also coordinates with PMU/LBR, TSC scaling, virtual GIF/NMI, bus-lock detection, and async page fault handling.

## Risks and edge cases
- vmcb12 validation is security-critical because L1 controls physical addresses, intercepts, event injection fields, and save state.
- MSRPM merging intentionally optimizes only offsets where L0 may allow pass-through; incorrect offsets can either over-intercept or expose host-owned MSRs.
- Nested NPT CR3/PDPTR handling differs depending on NPT and PAE; migration restore can otherwise load stale PDPTRs.
- Event reinjection and `nested_run_pending` block ordering must prevent exceptions, NMI, SMI, INIT, and IRQ exits from being reflected at architecturally invalid times.
- Hyper-V clean fields can skip MSR bitmap recalculation; the force flag must be set when vmcb12 identity changes.
- APICv must be inhibited while nested and restored promptly on VMEXIT.

## Test signals
Test signals include KVM selftests for nested SVM VMRUN failures, nested state get/set migration, nested NPT page faults, MSR/IO bitmap interception, event injection/interrupt-window behavior, Hyper-V enlightened TLB flush, LBR/TSC scaling, APICv inhibit restoration, and SMM/INIT/NMI edge cases. Tracepoints `kvm_nested_*` and nested VMEXIT injection logs are useful runtime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/nested.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/pmu.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/pmu.c

## Purpose
`pmu.c` implements AMD-specific KVM PMU operations for SVM. It maps AMD performance counter/control MSRs to KVM PMCs, handles RDPMC, programs event selectors and counters, derives guest-visible PMU capability from CPUID, and supports mediated PMU save/restore for AMD PerfMonV2 global control/status MSRs.

## Important APIs, types, and functions
- `enum pmu_type` distinguishes counter MSRs from event-select MSRs.
- `amd_pmu_get_pmc()`, `get_gp_pmc_amd()`, `amd_rdpmc_ecx_to_pmc()`, and `amd_msr_idx_to_pmc()` translate RDPMC indexes and AMD MSR numbers to `struct kvm_pmc`.
- `amd_is_valid_msr()` gates legacy K7, Family 15h core, and PerfMonV2 global PMU MSRs.
- `amd_pmu_get_msr()` and `amd_pmu_set_msr()` read/write PMC counters and event selectors, mask reserved bits, build `eventsel_hw` with guest-only behavior, and request counter reprogramming.
- `amd_pmu_refresh()` computes PMU version, number of counters, global reserved masks, counter bitmasks, reserved event bits, and fixed-counter absence from guest CPUID and host caps.
- `amd_pmu_init()` initializes the per-vCPU GP counter array.
- `amd_mediated_pmu_load()` and `amd_mediated_pmu_put()` switch AMD PerfMonV2 global status/control between host and guest.
- `amd_pmu_ops` exports the SVM PMU callbacks to KVM x86 core.

## Control flow
On vCPU PMU initialization, `amd_pmu_init()` seeds all possible AMD GP counters. After CPUID changes, `amd_pmu_refresh()` determines whether the guest has base PMU, `PERFCTR_CORE`, or `PERFMON_V2`, derives the counter count, and sets reserved masks. During MSR emulation, KVM calls `is_valid_msr`, then get/set callbacks. Counter MSRs call `pmc_read_counter()` or `pmc_write_counter()`; event selectors are masked and reprogrammed only when they actually change. RDPMC checks the index against the guest-visible counter count.

For mediated PMU, load clears any host global status, installs guest `global_status` and `global_ctrl`, and put disables global control, saves guest global status, and clears hardware status bits.

## State and persistence behavior
State is held in `struct kvm_pmu` and `struct kvm_pmc`: guest PMU version, GP counter count, counter bitmasks, reserved bit masks, raw event mask, per-counter `eventsel`, `eventsel_hw`, and counter values. Mediated PMU state persists `global_status` and `global_ctrl` across vCPU load/put. No file-local long-lived state exists beyond the `amd_pmu_ops` table.

## Dependencies and integration points
The file depends on KVM PMU core (`pmu.h`), CPUID helpers, perf event programming, MSR definitions, and SVM vCPU context switching. Nested SVM includes AMD PMU MSRs in its MSRPM merge list so PMU MSR interception is consistent for L2. PerfMonV2 depends on CPUID leaf `0x80000022`.

## Risks and edge cases
- MSR-to-counter mapping must handle overlapping K7 and Family 15h ranges and event/control parity correctly.
- Reserved bits in event selectors and global control/status must match AMD architecture and guest CPUID, or userspace-visible MSR behavior regresses.
- Mediated PMU global status clearing can perturb host PMU if load/put ordering is wrong.
- Counter counts are capped by host capability, so CPUID exposure and KVM PMU caps must remain synchronized.

## Test signals
Useful tests include PMU selftests for RDPMC bounds, K7 and F15h MSR aliases, PerfMonV2 global MSRs, event selector reserved-bit masking, CPUID counter count changes, mediated PMU vCPU switch behavior, and nested PMU MSR interception. Hardware perf counters and guest `perf` runs are practical integration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/sev.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/sev.c

## Purpose
`sev.c` implements AMD SEV, SEV-ES, and SEV-SNP support for KVM SVM. It manages encrypted-guest feature enablement, ASID allocation/recycling, firmware command dispatch, launch/update/measurement flows, migration and mirrored encryption contexts, encrypted memory registration, SEV-ES GHCB exits, SNP guest requests, AP creation, RMP transitions, guest_memfd private memory integration, VMSA encryption/decryption, and hardware setup/teardown.

## Important APIs, types, and functions
- Feature and ASID management: `sev_hardware_setup()`, `sev_hardware_unsetup()`, `sev_set_cpu_caps()`, `sev_asid_new()`, `sev_alloc_asid()`, `sev_asid_free()`, `sev_flush_asids()`, and `__sev_recycle_asids()`.
- VM lifecycle: `sev_vm_init()`, `sev_vm_destroy()`, `sev_vcpu_create()`, `sev_free_vcpu()`, `sev_init_vmcb()`, `sev_es_init_vmcb()`, and `pre_sev_run()`.
- User ABI dispatch: `sev_mem_enc_ioctl()` dispatches `KVM_SEV_*` and `KVM_SEV_SNP_*` commands.
- SEV/SEV-ES launch: `sev_guest_init()`, `sev_guest_init2()`, `sev_launch_start()`, `sev_launch_update_data()`, `sev_launch_update_vmsa()`, `sev_launch_measure()`, `sev_launch_finish()`, `sev_launch_secret()`, and attestation/debug helpers.
- Migration/mirroring: send/receive helpers, `sev_vm_move_enc_context_from()`, `sev_vm_copy_enc_context_from()`, `sev_migrate_from()`, and VM-pair locking helpers.
- SNP launch and memory: `snp_context_create()`, `snp_launch_start()`, `snp_launch_update()`, `sev_gmem_post_populate()`, `snp_launch_update_vmsa()`, `snp_launch_finish()`, and `snp_decommission_context()`.
- GHCB/VMGEXIT: `sev_handle_vmgexit()`, `sev_handle_vmgexit_msr_protocol()`, `sev_es_validate_vmgexit()`, `sev_es_sync_from_ghcb()`, `sev_es_sync_to_ghcb()`, `setup_vmgexit_scratch()`, and `sev_es_unmap_ghcb()`.
- SNP runtime: `snp_begin_psc()`, `snp_begin_psc_msr()`, `snp_complete_*()`, `sev_snp_ap_creation()`, `sev_snp_init_protected_guest_state()`, `snp_handle_guest_req()`, and `snp_handle_ext_guest_req()`.
- RMP/gmem: `kvm_rmp_make_shared()`, `snp_page_reclaim()`, `sev_handle_rmp_fault()`, `sev_gmem_prepare()`, `sev_gmem_invalidate()`, and `sev_gmem_max_mapping_level()`.
- Debug/VMSA: `sev_decrypt_vmsa()` and `sev_free_decrypted_vmsa()`.

## Control flow
Hardware setup validates NPT, NRIPS, decode assists, flush-by-ASID, PSP/SEV initialization, ASID ranges, SEV-ES requirements, SNP platform state, policy bits, ciphertext hiding ASID partitioning, and supported VMSA features. VM creation records the intended protected VM type; `KVM_SEV_INIT*` later allocates an ASID, charges the misc cgroup, initializes firmware, allocates SNP guest request buffers when needed, and inhibits APICv.

For classic SEV, userspace launches through `LAUNCH_START`, pins and encrypts memory through `LAUNCH_UPDATE_DATA`, optionally encrypts VMSAs for SEV-ES, measures, injects secrets, and finishes. SEV-ES VMSA sync copies KVM register/FPU state into a separate VMSA page, then firmware encrypts it and KVM marks guest state protected.

For SNP, launch start creates a firmware guest context and binds the ASID. Launch update populates guest_memfd private pages under `slots_lock`, validates RMP state, copies source data when needed, transitions PFNs private, and issues `SNP_LAUNCH_UPDATE`. Launch finish measures VMSAs, optionally passes ID/auth blocks, finalizes firmware state, and allows private pre-faulting.

At run time, `pre_sev_run()` installs the guest ASID, tracks CPUs that have run the guest for later cache writeback, and flushes ASID TLBs when a CPU/VMCB pairing changes. SEV-ES/SNP exits use either GHCB MSR protocol or a mapped GHCB page. KVM validates required GHCB fields for each exit code, synchronizes register state, handles MMIO, string IO, AP reset hold, AP jump table, SNP page-state changes, SNP guest requests, AP creation, or falls back to normal SVM exit handlers.

Teardown unregisters encrypted regions, flushes or writes back encrypted caches, decommissions firmware contexts, returns RMP entries to shared state, frees ASIDs, and handles mirror VMs without double-freeing owner state.

## State and persistence behavior
`struct kvm_sev_info` holds persistent VM encryption state: active/ES/SNP flags, ASID, firmware handle or SNP context, policy, PSP fd, GHCB version, VMSA features, locked-page accounting, misc cgroup, encrypted-region list, mirror-owner/list metadata, CPU-run cpumask, SNP guest request buffers, AP jump table, SNP cert-exit enablement, and migration-in-progress flag. Each `vcpu_svm` holds SEV-ES state such as VMSA pointer, GHCB map, scratch-area buffer, valid bitmap snapshot, AP reset hold type, SNP guest VMSA GPA, PSC progress, and whether the first SIPI was received.

Global state includes feature enable booleans, ASID ranges and bitmaps, reclaim bitmap, encryption bit/mask, supported SNP policy bits, supported VMSA feature bits, and locks for ASID bitmap and DEACTIVATE/DF_FLUSH ordering. User memory pinning is tracked per VM to enforce memlock limits and release pages on unregister/destroy. SNP RMP state persists in firmware/hardware and must be explicitly reclaimed or made shared.

## Dependencies and integration points
This file is a nexus for KVM x86 core, SVM VMCB code, PSP/SEV firmware commands, Linux mm/gup, misc cgroups, guest_memfd, RMP/SNP platform helpers, GHCB protocol definitions, CPUID/capability setup, APICv inhibit, KVM userspace exits, MMU invalidation and page fault handling, host CPU cache flush mechanisms, and tracepoints. It also integrates with migration through KVM fd validation and with userspace policy through `KVM_EXIT_HYPERCALL`, `KVM_EXIT_SNP_REQ_CERTS`, and `KVM_EXIT_SYSTEM_EVENT`.

## Risks and edge cases
- ASID recycling requires correct DEACTIVATE/DF_FLUSH/WBINVD ordering; failures can leak ASIDs or leave stale encrypted cache/TLB state.
- User memory pinning must enforce overflow, memlock, page dirtying, and cache coherency, especially on non-coherent SME systems.
- Firmware command errors must distinguish guest-visible firmware status from host infrastructure failures.
- SNP RMP transitions are security-critical; failed reclaim or shared/private updates intentionally leak pages rather than reusing protected memory unsafely.
- GHCB validation is the trust boundary for SEV-ES guests; missing validity checks can consume attacker-controlled stale state.
- AP creation rejects 2M-aligned VMSA GPAs to avoid an SNP erratum involving hugepage/RMP collisions.
- Mirrored encryption contexts and intra-host migration require careful lock ordering, refcounting, cgroup transfer, and vCPU state transfer.
- Debug decrypt paths must obey SEV/SNP policy bits and reclaim SNP firmware pages after use.

## Test signals
Test coverage should include SEV/SEV-ES/SNP initialization and failure paths, ASID exhaustion/recycling, memlock enforcement, launch update/measure/finish, VMSA encryption, SNP guest_memfd population, RMP fault PSMASH behavior, page-state-change exits, GHCB MSR and page protocols, SNP guest requests with and without certificate userspace exits, AP creation/destroy flows, migration/mirror ioctls, debug decrypt policy enforcement, and teardown leak/error paths. Runtime signals include SEV firmware return codes, `trace_kvm_vmgexit_*`, `trace_kvm_rmp_fault`, cache flush behavior, and KVM exits delivered to userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/svm/sev.c -->
