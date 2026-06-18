# sources/distributed-fs/ceph-client/tools/arch/x86/include/uapi/asm/kvm.h

## Purpose
Defines the x86-specific KVM userspace ABI: register state, interrupt controller state, CPUID/MSR structures, debug state, nested virtualization state, Xen/Hyper-V attributes, SEV/SNP commands, TDX commands, quirks, and VM type IDs.

## APIs, Types, and Functions
Important exports include `struct kvm_regs`, `kvm_sregs`, `kvm_fpu`, `kvm_msrs`, `kvm_cpuid2`, `kvm_vcpu_events`, `kvm_xsave`, `kvm_xcrs`, `kvm_sync_regs`, `kvm_nested_state`, `kvm_pmu_event_filter`, `kvm_xen_hvm_attr`, `kvm_xen_vcpu_attr`, SEV command structs, and TDX structs. Macros define IRQ chip IDs, exception vectors, MSR filter limits, register ID builders, sync flags, x86 quirks, nested state flags, Xen attribute IDs, PMU masked events, and VM types.

## Control Flow, State, and Persistence
There are no functions, but the structures are persistent ioctl payloads exchanged between VMMs and KVM. Flexible-array structures carry variable-length MSR, CPUID, PMU, nested VMCS/VMCB, XSAVE, and TDX CPUID data. Flag macros determine which fields are valid on set/get operations.

## Dependencies and Integration
Includes Linux UAPI helpers for constants, bit masks, types, ioctl numbers, and flexible arrays. Integrated with `/dev/kvm` ioctls, QEMU-like VMMs, selftests, and architecture-specific KVM code.

## Risks and Test Signals
Risks include ABI-breaking layout changes, wrong padding/alignment, unsafe interpretation of guest-supplied `kvm_sync_regs`, variable-length buffer sizing errors, and inconsistent CPUID state for TDX guests. Test signals are KVM selftests for get/set regs, CPUID, MSR filters, nested state migration, Xen attributes, SEV/SNP launch flows, TDX initialization, and UAPI header ABI checks.
