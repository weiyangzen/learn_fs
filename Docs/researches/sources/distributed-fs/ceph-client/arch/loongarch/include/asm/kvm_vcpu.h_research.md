# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_vcpu.h

## Purpose

`kvm_vcpu.h` declares vCPU exit handling, emulation and interrupt helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 140 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: larch_inst, exit_handle_fn, kvm_check_requests, kvm_handle_* exits, kvm_queue_irq, kvm_complete_iocsr_read, kvm_save/restore_timer, kvm_init/reset_vcpu. Symbol extraction from the file shows representative defines `__ASM_LOONGARCH_KVM_VCPU_H__`, `CPU_SIP0`, `CPU_SIP1`, `CPU_PMU`, `CPU_TIMER`, `CPU_IPI`, `CPU_AVEC`, `CPU_IP0`, `CPU_IP1`, `CPU_IP2`, `CPU_IP3`, `CPU_IP4`, representative callable declarations or inline helpers `kvm_emu_mmio_read`, `kvm_emu_mmio_write`, `kvm_complete_mmio_read`, `kvm_complete_iocsr_read`, `kvm_complete_user_service`, `kvm_emu_idle`, `kvm_pending_timer`, `kvm_handle_fault`, `kvm_deliver_intr`, `kvm_deliver_exception`, `kvm_own_fpu`, `kvm_lose_fpu`, and representative local types `union`, `int`, `kvm_vcpu`. Direct includes seen in the header are `asm/loongarch.h`, `linux/kvm_host.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header connects KVM guest exits to instruction decoding, CSR/IOCSR, MMU, IRQ and timer emulation. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: exit dispatch ordering and PC advancement are high-risk under nested faults or emulation failures. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
