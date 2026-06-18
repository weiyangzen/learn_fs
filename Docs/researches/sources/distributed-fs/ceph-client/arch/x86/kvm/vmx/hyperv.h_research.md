# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv.h

## Purpose
`vmx/hyperv.h` declares VMX Hyper-V enlightened VMCS interfaces and provides inline helpers for eVMCS pointer state. It is the compile-time boundary between common nested VMX code and optional `CONFIG_KVM_HYPERV` support.

## Important APIs, Types, And Functions
`EVMPTR_INVALID` marks no valid eVMCS pointer and `EVMPTR_MAP_PENDING` marks a restored or deferred state where the GPA is known to require remapping before use. `enum nested_evmptrld_status` reports whether eVMCS loading is disabled, succeeded, failed architecturally, or failed due to a host mapping error.

With `CONFIG_KVM_HYPERV`, `evmptr_is_valid()` rejects invalid and map-pending sentinels, while `evmptr_is_set()` rejects only invalid. `nested_vmx_is_evmptr12_valid()` and `nested_vmx_is_evmptr12_set()` apply those tests to `vmx->nested.hv_evmcs_vmptr`. `nested_vmx_evmcs()` returns the mapped `struct hv_enlightened_vmcs *`. `guest_cpu_cap_has_evmcs()` exposes eVMCS to a vCPU only when Hyper-V CPUID is enabled and userspace explicitly enabled enlightened VMCS. The header declares `nested_get_evmptr()`, `nested_get_evmcs_version()`, `nested_enable_evmcs()`, `nested_evmcs_filter_control_msr()`, `nested_evmcs_check_controls()`, `nested_evmcs_l2_tlb_flush_enabled()`, and `vmx_hv_inject_synthetic_vmexit_post_tlb_flush()`.

When Hyper-V support is not compiled, the inline helpers compile to false or NULL and no function declarations are provided for the implementation-only operations.

## Control Flow
This header does not run complex control flow; it controls feature reachability. Nested VMX paths first check whether guest eVMCS capability is enabled, then use pointer-state helpers to decide whether an existing mapping can be used, needs mapping, or should be treated as absent. The non-Hyper-V stubs allow the same broader VMX code to compile out eVMCS paths.

## State And Persistence
The state represented here lives in `struct vcpu_vmx.nested`: the eVMCS GPA sentinel/value, host map, mapped pointer, and `enlightened_vmcs_enabled`. `EVMPTR_MAP_PENDING` is important for persistence across migration or state restore because it distinguishes "feature enabled but mapping not restored yet" from "no eVMCS".

## Dependencies And Integration Points
The header depends on KVM host types, `vmcs12.h`, and `vmx.h` for `struct vcpu_vmx`. It is included by nested VMX, VMX MSR handling, and Hyper-V eVMCS implementation code. It integrates with `arch/x86/kvm/hyperv.c` for CPUID/version exposure and with `nested.c` for `EVMPTRLD`-like mapping and release.

## Risks And Edge Cases
Confusing "set" and "valid" pointer semantics can break migration and lazy mapping: `EVMPTR_MAP_PENDING` is set but not valid. `guest_cpu_cap_has_evmcs()` requires both Hyper-V enabled in CPUID and userspace opt-in; bypassing either check would expose eVMCS unexpectedly. The !`CONFIG_KVM_HYPERV` stubs intentionally return false, so code that expects declarations must remain compiled under the same config guard.

## Test Signals
Test signals include builds with and without `CONFIG_KVM_HYPERV`, eVMCS enable/disable through userspace, nested VMX migration that restores `EVMPTR_MAP_PENDING`, nested VMCLEAR/VM-entry paths for valid and invalid eVMCS pointers, and CPUID combinations where Hyper-V is disabled even though VMX exists.
