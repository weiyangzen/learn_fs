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
