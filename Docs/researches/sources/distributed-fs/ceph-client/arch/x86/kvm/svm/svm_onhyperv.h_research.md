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
