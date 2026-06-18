# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx.h

## Purpose
Defines the public TDX data model and inline accessors used by VMX/KVM code. It wraps TDX support in `CONFIG_KVM_INTEL_TDX`, defines TD and vCPU state structs, declares hardware/runtime hooks, and generates typed TDVPS read/write helpers.

## Important APIs, Types, And Functions
`enum kvm_tdx_state` models TD module state: uninitialized, initialized, runnable. `struct kvm_tdx` embeds `struct kvm` and stores misc cgroup, HKID, TD state, attributes, XFAM, TSC data, `struct tdx_td`, `page_add_src`, and `wait_for_sept_zap`. `enum vcpu_tdx_state` and `struct vcpu_tdx` hold TD vCPU state, common VT state, exit metadata, `struct tdx_vp`, per-CPU list node, VP.ENTER return, and MAP_GPA progress. Inline helpers include `td_tdcs_exec_read64()` and macro-generated `td_vmcs_read/write/setbit/clearbit*`, `td_management_*`, and `td_state_non_arch_*`.

## Control Flow
The header exposes TDX lifecycle hooks to `x86_ops.h` and VMX code. Generated accessors build TDX field IDs from VMCS, management, or non-architectural state classes and call `tdh_vp_rd()` or `tdh_vp_wr()`. Compile-time checks prevent unsupported TD VMCS high-field and width mismatches.

## State And Persistence
This header defines the persistent allocation shape for TDX VMs and vCPUs. It also records the transient synchronization field `wait_for_sept_zap`, used to keep vCPUs out of TD entry while Secure EPT zapping retries. In disabled builds, stub `struct kvm_tdx` and `struct vcpu_tdx` preserve container expectations without enabling functionality.

## Dependencies And Integration Points
Includes TDX architectural constants and errno values. Enabled builds include `common.h` and depend on SEAMCALL types from architecture headers. The structs are used as larger VM/vCPU allocations selected during TDX hardware setup.

## Risks
Struct layout affects allocation size and container casts. Accessor macros BUG the VM on unexpected TDH_VP_RD/WR failures, so field IDs and widths must be exact. Stub behavior must remain consistent enough for non-TDX builds to compile while preventing accidental TDX operation.

## Test Signals
Builds with and without `CONFIG_KVM_INTEL_TDX`, compile-time VMCS width checks, TDVPS access to posted interrupt and NMI fields, and KVM sanity checks for `kvm_tdx` allocation size validate this header.
