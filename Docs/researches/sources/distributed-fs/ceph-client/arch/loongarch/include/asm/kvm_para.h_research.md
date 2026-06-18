# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_para.h

## Purpose

`kvm_para.h` defines guest paravirtual hypercall interface. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 189 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: KVM_HCALL_* encodings, kvm_steal_time, kvm_hypercall0-5, kvm_para_available, kvm_arch_para_features/hints. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_KVM_PARA_H`, `HYPERVISOR_KVM`, `HYPERVISOR_VENDOR_SHIFT`, `HYPERCALL_ENCODE`, `KVM_HCALL_CODE_SERVICE`, `KVM_HCALL_CODE_SWDBG`, `KVM_HCALL_CODE_USER_SERVICE`, `KVM_HCALL_SERVICE`, `KVM_HCALL_FUNC_IPI`, `KVM_HCALL_FUNC_NOTIFY`, `KVM_HCALL_SWDBG`, `KVM_HCALL_USER_SERVICE`, representative callable declarations or inline helpers `kvm_hypercall0`, `kvm_hypercall1`, `kvm_hypercall2`, `kvm_hypercall3`, `kvm_hypercall4`, `kvm_hypercall5`, `kvm_para_available`, `kvm_arch_para_features`, `kvm_para_available`, `kvm_arch_para_features`, `kvm_arch_para_hints`, `kvm_check_and_clear_guest_paused`, and representative local types `kvm_steal_time`. Direct includes seen in the header are `uapi/asm/kvm_para.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header guest kernels use `hvcl` hypercalls for KVM services and steal-time accounting. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: argument register conventions and clobbers are ABI-sensitive. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
