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
