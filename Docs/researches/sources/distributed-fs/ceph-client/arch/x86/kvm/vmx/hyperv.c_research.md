# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv.c

## Purpose
`vmx/hyperv.c` implements VMX-specific Hyper-V enlightened VMCS support for nested virtualization. It reads the guest Hyper-V VP assist page's current eVMCS pointer, reports supported eVMCS versions, filters virtual VMX control MSRs to the subset representable by eVMCS v1, validates nested VMCS controls under eVMCS, enables eVMCS per vCPU, and supports Hyper-V direct TLB-flush enlightenment for L2.

## Important APIs, Types, And Functions
`nested_get_evmptr()` returns the current nested eVMCS GPA from `hv_vcpu->vp_assist_page.current_nested_vmcs`, but only after ensuring the assist page can be read and enlightened VM-entry is enabled. `nested_get_evmcs_version()` returns a min/max version range encoded in a 16-bit value, currently versions 1 through `KVM_EVMCS_VERSION`, when VMX is available and the vCPU has eVMCS enabled if a vCPU is supplied.

Local enums define an eVMCS revision (`EVMCSv1_LEGACY`) and control classes (`EVMCS_EXIT_CTRLS`, `EVMCS_ENTRY_CTRLS`, `EVMCS_EXEC_CTRL`, secondary, tertiary, pin, and VMFUNC). `evmcs_supported_ctrls` maps those classes to the masks from `hyperv_evmcs.h`; secondary controls deliberately clear `SECONDARY_EXEC_TSC_SCALING` for exposed nested eVMCS controls. `nested_evmcs_filter_control_msr()` masks VMX MSR low/high words so Hyper-V guests do not try to use VMCS fields absent from eVMCS. It also hides perf global control unless the Hyper-V nested CPUID bit `HV_X64_NESTED_EVMCS1_PERF_GLOBAL_CTRL` is present. `nested_evmcs_check_controls()` rejects unsupported nested VMCS controls with `-EINVAL` and KVM nested consistency-check annotations. `nested_enable_evmcs()` sets `vmx->nested.enlightened_vmcs_enabled` and optionally returns the supported version range. `nested_evmcs_l2_tlb_flush_enabled()` checks the mapped eVMCS enlightenment bit and the VP assist page's direct-hypercall feature. `vmx_hv_inject_synthetic_vmexit_post_tlb_flush()` causes a synthetic nested VM exit after flush.

## Control Flow
The eVMCS activation flow starts in KVM's Hyper-V enable path, which calls `nested_enable_evmcs()`. CPUID/MSR paths call `nested_get_evmcs_version()` and `nested_evmcs_filter_control_msr()` to advertise only valid controls. During nested VM-entry, `nested.c` maps the GPA from `nested_get_evmptr()`, copies eVMCS content into `vmcs12`, and invokes `nested_evmcs_check_controls()`. On L2 TLB flush paths, nested VMX checks `nested_evmcs_l2_tlb_flush_enabled()` and may inject the synthetic post-flush VM exit.

## State And Persistence
This file mutates only `vcpu_vmx.nested.enlightened_vmcs_enabled`; the eVMCS pointer, mapped page, and VP assist state are stored elsewhere in `vcpu_vmx.nested` and `kvm_vcpu_hv`. The static supported-control table is immutable. The VP assist page content is guest/Hyper-V shared state and can change across entries or after migration, so callers must revalidate mapping and version.

## Dependencies And Integration Points
The implementation depends on KVM Hyper-V helpers, CPUID cache state, nested VMX, VMCS definitions, eVMCS masks from `hyperv_evmcs.h`, and trace/consistency-check infrastructure. Integration points include `x86.c`'s Hyper-V eVMCS enable ioctl/MSR path, `arch/x86/kvm/hyperv.c` CPUID generation, `vmx.c` feature MSR reads, and `nested.c` eVMCS mapping, control checks, direct flush handling, and synthetic VM exits.

## Risks And Edge Cases
The filter must match the actual eVMCS field map; advertising unsupported controls can make Hyper-V write fields KVM cannot translate. Hiding perf global control without the companion CPUID bit is a Windows compatibility quirk and should not be removed casually. `nested_get_evmptr()` returns invalid when the assist page cannot be read or enlightened entry is disabled, which disables eVMCS rather than failing all nested VMX. Version encoding is min/max in one word, so consumers must not treat it as a single revision. TLB-flush enlightenment depends on both eVMCS control and VP assist direct-hypercall state, including after migration.

## Test Signals
Useful tests include Hyper-V CPUID eVMCS version exposure, enabling eVMCS through KVM nested ops, reading VMX control MSRs with and without eVMCS and perf-global-control CPUID bit, nested VM-entry rejection of unsupported eVMCS controls, valid L2 launch through eVMCS, migration with remapped eVMCS, direct TLB-flush enlightenment and synthetic VM-exit delivery, and cases where the VP assist page is missing or `enlighten_vmentry` is clear.
