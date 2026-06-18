# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmx_onhyperv.c

Purpose: implements the small runtime portion of KVM's VMX-on-Hyper-V enlightened VMCS support. Its main job is to advertise eVMCS usage through a static branch and sanitize VMX execution controls so KVM does not attempt to use VMCS fields that Hyper-V's eVMCSv1 does not support.

Important APIs and functions: `DEFINE_STATIC_KEY_FALSE(__kvm_is_using_evmcs)` provides the backing jump-label state consumed by `kvm_is_using_evmcs()` in the header. The local `evmcs_check_vmcs_conf(field, ctrl)` macro computes unsupported bits in a `struct vmcs_config` control field against `EVMCS1_SUPPORTED_*` masks, emits a once-only warning, and clears unsupported bits. `evmcs_sanitize_exec_ctrls(struct vmcs_config *vmcs_conf)` applies that check to primary, pin-based, secondary, tertiary, VM-entry, and VM-exit controls.

Control flow and behavior: VMX capability discovery builds a `vmcs_config`, and when KVM runs nested on Hyper-V with eVMCS enabled, `vmx_hardware_setup()` calls `evmcs_sanitize_exec_ctrls()`. Each control field is masked against the latest eVMCSv1 support definitions. If Hyper-V exposes a VMX feature in capability MSRs that KVM can see but eVMCS lacks a corresponding field, KVM warns once and disables that feature in its effective VMCS configuration.

State and persistence: the only persistent local state is the `__kvm_is_using_evmcs` static key, which changes the fast path of VMCS accessors while the module is loaded. `evmcs_sanitize_exec_ctrls()` mutates the caller's in-memory VMCS capability configuration; it does not store data independently and has no disk persistence.

Dependencies and integration points: depends on `capabilities.h` for `struct vmcs_config` and VMX control definitions, and `vmx_onhyperv.h`/`hyperv_evmcs.h` for eVMCS support masks. It integrates with VMX hardware setup in `vmx.c`, the `vmcs_read*()`/`vmcs_write*()` dispatch path in `vmx_ops.h`, and Hyper-V enlightenments exposed through `asm/mshyperv.h`.

Risks and correctness concerns: the support masks must remain synchronized with Hyper-V eVMCS field definitions. Overly permissive masks can make KVM write fields Hyper-V ignores or rejects; overly restrictive masks disable valid acceleration. The warning path intentionally treats unexpected unsupported bits as a KVM update signal, so new VMX controls require eVMCS support review.

Test signals: boot KVM-on-Hyper-V with eVMCS enabled and verify no unexpected `unsupported with eVMCS` warnings for known-good hosts. Nested virtualization selftests should cover EPT, APICv, TSC scaling, preemption timer, VM-entry/exit MSR controls, and Hyper-V nested flush paths with and without `CONFIG_HYPERV`.
