# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/evmcs.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/evmcs.h

Purpose: Hyper-V enlightened VMCS support layer for x86 nested VMX selftests. It defines the packed `hv_enlightened_vmcs` layout, clean-field bits, global eVMCS state, and inline replacements for VMCS pointer/read/write/launch/resume operations when eVMCS is enabled.

Important APIs/types/functions: `EVMCS_VERSION`, `enable_evmcs`, `struct hv_enlightened_vmcs`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_*`, `HV_VMX_SYNTHETIC_EXIT_REASON_TRAP_AFTER_FLUSH`, `current_evmcs`, `vcpu_enable_evmcs`, `evmcs_enable`, `evmcs_vmptrld`, `load_evmcs`, `evmcs_vmptrst`, `evmcs_vmread`, `evmcs_vmwrite`, `evmcs_vmlaunch`, and `evmcs_vmresume`.

Control flow and state: tests allocate Hyper-V assist pages, call `load_evmcs`, then VMX helpers in `vmx.h` delegate `vmread`, `vmwrite`, launch, and resume to this layer when `enable_evmcs` is true. `evmcs_vmwrite` updates the matching field and clears the correct clean-field group so Hyper-V/KVM knows what changed. Launch/resume assembly stores host RSP/RIP into eVMCS and returns a status flag after VM-entry failure or VM-exit.

Dependencies and integration: includes `hyperv.h` and `vmx.h`, and depends on VMCS field encodings from `x86/vmx.h`. It integrates with nested VMX tests running with Hyper-V enlightenments.

Risks: the packed layout and field mapping must match Hyper-V's eVMCS version exactly. Missing a VMCS field in read/write switches returns failure and can break nested tests. Clean-field bookkeeping is subtle; wrong groups can make KVM use stale state.

Test signals: Hyper-V eVMCS nested tests validate field translation, clean-field invalidation, VP assist page state, and successful nested launch/resume.
