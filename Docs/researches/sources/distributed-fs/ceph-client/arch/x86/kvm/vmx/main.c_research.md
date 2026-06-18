# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/main.c

## Purpose
`vmx/main.c` is the Intel KVM backend module entry point and operation table definition. When TDX is enabled, it provides a VT dispatch layer that routes each KVM x86 operation to either classic VMX or TDX based on VM/vCPU type. When TDX is not compiled, the same table aliases directly to VMX functions.

## Important APIs, Types, And Functions
Under `CONFIG_KVM_INTEL_TDX`, the file defines many `vt_*` wrappers. VM and vCPU lifecycle wrappers include `vt_hardware_setup()`, `vt_hardware_unsetup()`, `vt_disable_virtualization_cpu()`, `vt_vm_init()`, `vt_vm_pre_destroy()`, `vt_vm_destroy()`, `vt_vcpu_precreate()`, `vt_vcpu_create()`, `vt_vcpu_free()`, `vt_vcpu_reset()`, `vt_vcpu_load()`, `vt_vcpu_put()`, `vt_vcpu_pre_run()`, and `vt_vcpu_run()`. Runtime wrappers cover exit handling, MSR access, intercept recalculation, instruction emulation checks, APIC and interrupt operations, segment/control/debug register access, descriptor tables, TLB flushes, NMI/IRQ/exception injection, MMU root loading, Hyper-V timer, machine-check setup, TSS and identity-map addresses, TSC offset/multiplier, memory-encryption ioctls, and guest-memory mapping level.

`VMX_REQUIRED_APICV_INHIBITS` enumerates APICv inhibit reasons required by VMX: disabled, absent, Hyper-V, blocked IRQ, physical ID aliasing, APIC ID modified, and APIC base modified. `vt_x86_ops` fills `struct kvm_x86_ops` with VMX/TDX dispatch functions and feature hooks. `vt_init_ops` fills `struct kvm_x86_init_ops` with hardware setup, PMU ops, and the runtime ops table. `vt_init()` calls `vmx_init()`, sizes the vCPU cache for the larger of VMX and TDX structs when needed, marks TDX VM type support, then calls `kvm_init()`. `vt_exit()` calls `kvm_exit()` and `vmx_exit()`.

## Control Flow
Module initialization starts in `vt_init()`: initialize VMX, adjust vCPU allocation metadata for TDX, expose TDX VM type if enabled, and register KVM only after hardware/backend setup is ready because `/dev/kvm` becomes visible. Hardware setup later calls either `vmx_hardware_setup()` alone or VMX followed by TDX hardware setup. Runtime KVM calls enter `vt_x86_ops`; each wrapper checks `is_td()` or `is_td_vcpu()` and selects TDX behavior, VMX behavior, a harmless no-op, or an error where the operation is invalid for TDs. On module exit, common KVM teardown precedes VMX teardown.

## State And Persistence
This file owns static operation table state in `vt_x86_ops` and `vt_init_ops`, both `__initdata`, and mutates global KVM capability state by setting `kvm_caps.supported_vm_types` when TDX is enabled. It does not own per-vCPU state; wrappers delegate to VMX or TDX implementations. For TD guests, many architectural reads return zero or operations become no-ops because guest state is protected or managed by the TDX module rather than directly visible to KVM.

## Dependencies And Integration Points
The file includes VMX, MMU, nested VMX, PMU, posted interrupt, and TDX headers. It is integrated with core KVM through `kvm_x86_ops` and `kvm_x86_init_ops`, module init/exit, Intel PMU ops, nested VMX ops, posted interrupt hooks, Hyper-V timer hooks, SMM hooks under `CONFIG_KVM_SMM`, and TDX memory-encryption ioctls. `tdx.c` can further patch `vt_x86_ops` for TDX-specific private-memory operations during TDX setup.

## Risks And Edge Cases
Dispatch correctness is the primary risk. Operations that are impossible or unsafe for TD guests must not fall through to VMX, because TD guest state and memory are protected. Conversely, returning zero/no-op for TDs must match core KVM expectations; a wrong default can hide bugs or cause guest-visible state loss. Initialization order is sensitive: `kvm_init()` must remain last because it exposes `/dev/kvm`. vCPU cache sizing must cover both `struct vcpu_vmx` and `struct vcpu_tdx`. APICv inhibit masks must stay synchronized with VMX APIC virtualization requirements. Several wrappers use `KVM_BUG_ON`/`WARN_ON_ONCE` for paths that should never target TDs, which are good test signals but also indicate invariants relied on by core KVM.

## Test Signals
Useful tests include VMX module load/unload, TDX-enabled and TDX-disabled builds, creation of normal VMX VMs and TD VMs, vCPU lifecycle and run loops for both types, MSR get/set dispatch tests, interrupt/NMI/APIC behavior for TD and non-TD VMs, SMM tests confirming TD paths are blocked, TLB flush and MMU root load tests, Hyper-V timer rejection for TDs, memory-encryption ioctl routing, `/dev/kvm` exposure after successful init only, and regression tests for vCPU allocation size/alignment when TDX support is enabled.
