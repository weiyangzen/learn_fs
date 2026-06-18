# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/kvm.h

## Purpose
Defines the MIPS userspace KVM ABI for tools.

## Important APIs, Types, and Functions
Important types are `struct kvm_regs`, empty `kvm_fpu`, `kvm_debug_exit_arch`, `kvm_guest_debug_arch`, `kvm_sync_regs`, `kvm_sregs`, and `kvm_mips_interrupt`. Register ID macros cover GP registers, CP0 namespace, KVM-specific Count controls, and FPU/MSA register subsets.

## Control Flow, State, and Persistence
The header encodes ioctl payload layouts and one-reg IDs only. KVM persists guest registers/timer state; userspace uses `COUNT_CTL`, `COUNT_RESUME`, and `COUNT_HZ` to freeze/resume CP0_Count consistently.

## Dependencies and Integration Points
Depends on `linux/types.h` and generic KVM register-size bits. Integrates with MIPS KVM userspace, migration, debug exits, and interrupt injection.

## Risks and Test Signals
Risks include register ID layout mistakes, 32-bit CPU sign-extension semantics, and timer-freeze behavior being misused during migration. Test signals are `KVM_GET/SET_ONE_REG` round trips, Count freeze/resume migration tests, and interrupt injection validation.
