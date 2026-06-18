<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-ops.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-ops.h

## Purpose
KVM x86 operation list header used to generate the kvm_x86_ops structure, wrappers, and static calls for VMX/SVM backends. The header is 156 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: None visible in this header.

Notable declarations and inline helpers: None visible in this header.

## Control Flow
The file is repeatedly included with KVM_X86_OP macros defined differently; each line declares a required, optional, or optional-ret0 backend operation in stable order.

## State and Persistence
State is not stored here, but the operation table controls backend dispatch for vCPU creation, run, MMU, interrupts, MSR, nested virtualization, and feature hooks.

## Dependencies and Integration Points
Depends on KVM core macro inclusion discipline, VMX/SVM implementations, static_call generation, and operation table structure layout.

## Risks
Risks include changing order or optionality without matching backends, missing required ops, and silent ret0 defaults hiding backend feature gaps.

## Test Signals
Tests should compile VMX and SVM, run KVM unit tests, nested virtualization, migration/state save, APIC/MSR/MMU paths, and static_call dispatch validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-ops.h -->
