# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/vmx.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/vmx.h

Purpose: Intel VMX nested virtualization helper definitions for KVM selftests. It defines VM-execution/control bits, VMCS field encodings, VMX instruction wrappers, VMX page allocations, VMX capability structs, and setup helpers for VMX/EPT/APIC-virtualization tests.

Important APIs/types/functions: VMX control masks (`CPU_BASED_*`, `SECONDARY_EXEC_*`, `PIN_BASED_*`, `VM_EXIT_*`, `VM_ENTRY_*`), `enum vmcs_field`, `struct vmx_msr_entry`, VMX instruction helpers (`vmxon`, `vmxoff`, `vmclear`, `vmptrld`, `vmptrst`, `vmptrstz`, `vmlaunch`, `vmresume`, `vmcall`, `vmread`, `vmreadz`, `vmwrite`, `vmcs_revision`), `struct vmx_pages`, `union vmx_basic`, `union vmx_ctrl_msr`, `vcpu_alloc_vmx`, `prepare_for_vmx_operation`, `prepare_vmcs`, `load_vmcs`, `ept_1g_pages_supported`, `kvm_cpu_has_ept`, `vm_enable_ept`, and `prepare_virtualize_apic_accesses`.

Control flow and state: nested VMX tests allocate VMXON/VMCS/MSR bitmap/APIC/EPT pages, enable VMX operation, load a VMCS, write control/guest/host fields, launch or resume L2, and inspect VM-exit fields. If `enable_evmcs` is set, VMCS read/write/launch/resume delegate to `evmcs.h`.

Dependencies and integration: depends on `<asm/vmx.h>`, `x86/processor.h`, `x86/apic.h`, and `x86/evmcs.h`. It integrates with x86 nested VMX, EPT, APIC virtualization, Hyper-V eVMCS, and VM-entry failure tests.

Risks: VMCS field encodings and control bit masks are architecture ABI. Assembly wrappers clobber many registers and deliberately do not establish guest GPR state. eVMCS conditional behavior means tests must understand whether raw VMCS or enlightened VMCS is active.

Test signals: nested VMX tests validate VMXON/VMCS setup, VM-entry/exit, VMREAD/VMWRITE, EPT setup, APIC access virtualization, and eVMCS delegation.
