<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/vmx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/vmx.c

## Purpose
`vmx.c` provides nested Intel VMX support helpers for KVM selftests. It allocates VMX control pages, enables EPT/TDP mappings, enters VMX root operation, loads VMCS state, initializes control/host/guest VMCS fields, checks EPT capability, and prepares APIC-access virtualization memory.

## Important APIs, Types, and Functions
Important APIs include `vcpu_enable_evmcs()`, `vm_enable_ept()`, `vcpu_alloc_vmx()`, `prepare_for_vmx_operation()`, `load_vmcs()`, `ept_1g_pages_supported()`, `prepare_vmcs()`, `kvm_cpu_has_ept()`, and `prepare_virtualize_apic_accesses()`. Globals include `enable_evmcs`, `current_evmcs`, and `current_vp_assist`.

## Control Flow
VMX allocation reserves guest pages for VMXON, VMCS, MSR bitmap, shadow VMCS, VMREAD bitmap, VMWRITE bitmap, and optional EPTP root. VMX preparation adjusts CR0/CR4 according to fixed MSRs, enables CR4.VMXE, locks/enables feature control when possible, writes VMCS revisions, and executes `vmxon`, `vmclear`, and `vmptrld`. VMCS preparation initializes controls, optionally enables EPT with write-back memory type and A/D bits, records host state from current registers/MSRs, and initializes guest state mostly as a clone with caller-provided RIP/RSP.

## State and Persistence
State lives in allocated VMX pages, VMCS fields, VMX root mode, global enlightened-VMCS pointers, and stage-2 EPT page tables. It persists until VM teardown or explicit VMX operation changes.

## Dependencies and Integration Points
The file depends on `vmx.h`, `processor.h`, `kvm_util.h`, `test_util.h`, x86 VMX MSRs, Hyper-V EVMCS support, and TDP mapping helpers. It integrates with nested VMX tests, Hyper-V enlightened VMCS tests, and x86 memstress nested execution.

## Risks and Test Signals
Risks include illegal CR0/CR4 fixed-bit handling, feature-control writes that still leave VMXON unavailable, invalid EPTP construction, missing secondary controls, mismatched host/guest segment state, and unsupported 5-level EPT. Test signals are VMX instruction return values, `TEST_ASSERT()` and `GUEST_ASSERT()` checks, expected VM exits from nested guests, and feature probes via `kvm_cpu_has_ept()`/`ept_1g_pages_supported()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/vmx.c -->
