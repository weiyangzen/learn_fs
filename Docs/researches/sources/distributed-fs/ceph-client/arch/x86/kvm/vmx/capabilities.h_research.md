# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/capabilities.h

## Purpose
`vmx/capabilities.h` centralizes Intel VMX capability state and inline feature predicates for the VMX backend. It turns raw VMX MSR-derived configuration (`vmcs_config`) and EPT/VPID capability bits (`vmx_capability`) into readable gates used across VMX setup, nested VMX, VMCS access, APIC virtualization, tracing, memory management, and feature exposure.

## Important APIs, Types, And Functions
`struct nested_vmx_msrs` stores the "true" nested VMX control MSR masks, fixed CR0/CR4 masks, VMCS enum data, VMFUNC controls, EPT caps, VPID caps, basic/misc data, and related fields exposed to L1 guests. `struct vmcs_config` stores host-selected VM execution, entry, exit, and misc controls plus nested capability MSRs. `struct vmx_capability` stores EPT and VPID capability words. The file declares `vmcs_config` and `vmx_capability` as `__ro_after_init`, alongside module-tunable booleans such as `enable_vpid`, `enable_ept`, `enable_unrestricted_guest`, `enable_ept_ad_bits`, `enable_cet`, `enable_pml`, and `pt_mode`.

The many `cpu_has_*()` helpers gate individual VMX features: pin controls such as virtual NMIs, preemption timer, and posted interrupts; primary/secondary/tertiary execution controls such as MSR bitmaps, EPT, VPID, RDTSCP, APIC virtualization, PLE, VMFUNC, shadow VMCS, SGX ENCLS exiting, XSAVES, waitpkg, TSC scaling, bus-lock detection, IPI virtualization, and notify VM exits; VM-entry/exit controls for EFER, perf global control, CET, BNDCFGS; and EPT/VPID invalidation extents and page-size support. `cpu_need_tpr_shadow()` adds the vCPU-local dependency that in-kernel LAPIC must be active. `ept_caps_to_lpage_level()` converts EPT large-page caps to KVM page levels. `vmx_pebs_supported()` combines CPU PEBS support, PMU EPT capability, and mediated PMU exclusion.

## Control Flow
The header is all inline predicate logic. Most helpers directly test one bit in initialized global capability state, while compound helpers enforce multi-bit contracts, for example APICv requires APIC-register virtualization, virtual-interrupt delivery, and posted interrupts. Feature setup code in `vmx.c` fills `vmcs_config` and then later uses these helpers to enable or disable KVM capabilities, operation hooks, CPUID exposure, and nested VMX MSR masks.

## State And Persistence
Persistent state is the post-initialization global VMX capability snapshot. The globals are read-mostly or `__ro_after_init`, so runtime code assumes they are stable after hardware setup. `pt_mode` remains the selected Intel Processor Trace mode. No per-vCPU state is stored here except through helper parameters such as `cpu_need_tpr_shadow(vcpu)`.

## Dependencies And Integration Points
The header depends on `<asm/vmx.h>` control bit definitions and KVM x86 headers for LAPIC, CPUID, PMU, paging levels, and CPU feature tests. It is widely consumed by `vmx.c`, `nested.c`, `vmcs12.c`, SGX handling, TDX setup, VMX ops helpers, and VMX-on-Hyper-V sanitization. Nested VMX support depends on `nested_vmx_msrs` to present a coherent virtual VMX capability set to L1.

## Risks And Edge Cases
Incorrect predicates can expose unsupported hardware behavior to guests or disable valid acceleration paths. Compound helpers must stay aligned with Intel SDM requirements; e.g. APICv and shadow-VMCS support depend on multiple controls, not one raw bit. `vmx_umip_emulated()` deliberately treats lack of hardware UMIP plus descriptor-table exiting as an emulated capability. `vmx_pebs_supported()` must not enable PEBS when mediated PMU is active. Any initialization path that mutates `vmcs_config` after consumers cache decisions would be risky.

## Test Signals
Signals include module initialization on CPUs with varied VMX MSR capabilities, nested VMX selftests that read VMX MSRs and attempt controls, APICv/posted interrupt tests, EPT and VPID invalidation tests, Intel PT and PEBS capability exposure tests, SGX/ENCLS exiting tests, TSC scaling and bus-lock detection tests, and negative tests where module parameters disable EPT, VPID, unrestricted guest, PML, or CET.
