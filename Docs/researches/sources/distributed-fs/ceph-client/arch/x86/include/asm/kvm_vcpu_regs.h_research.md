# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_vcpu_regs.h

## Purpose
Provides canonical numeric indexes for x86 KVM vCPU general-purpose registers, used by `kvm_host.h` and register cache bitmaps.

## Important APIs, Types, And Functions
Defines `__VCPU_REGS_RAX` through `__VCPU_REGS_RDI` for all x86 builds and `__VCPU_REGS_R8` through `__VCPU_REGS_R15` when `CONFIG_X86_64` is enabled. There are no functions.

## Control Flow
The header participates in compile-time layout only. `enum kvm_reg` in `kvm_host.h` aliases these values and appends RIP plus extra register slots.

## State And Persistence
No standalone state. The indexes address `struct kvm_vcpu_arch.regs[]`, `regs_avail`, and `regs_dirty`.

## Dependencies And Integration Points
Integrated with KVM register caching, emulator register access, VMX/SVM save/restore code, and userspace register APIs that depend on stable x86 register ordering.

## Risks And Edge Cases
Renumbering entries would corrupt register-cache interpretation. The 64-bit-only registers must remain conditional or 32-bit builds will allocate and reference invalid slots.

## Test Signals
Compile both 32-bit and 64-bit x86 KVM. Register get/set selftests and emulator tests detect ordering mistakes.
