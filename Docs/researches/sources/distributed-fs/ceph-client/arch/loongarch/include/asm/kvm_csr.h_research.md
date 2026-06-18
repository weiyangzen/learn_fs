# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_csr.h

## Purpose

`kvm_csr.h` maps LoongArch guest CSR IDs to KVM software/hardware handling flags. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 217 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: KVM_CSR_* flag table macros, kvm_emu_iocsr, kvm_read/write/set/change_sw_gcsr, KVM_PMU_EVENT_ENABLED. Symbol extraction from the file shows representative defines `__ASM_LOONGARCH_KVM_CSR_H__`, `gcsr_read`, `gcsr_write`, `gcsr_xchg`, `read_gcsr_crmd`, `write_gcsr_crmd`, `read_gcsr_prmd`, `write_gcsr_prmd`, `read_gcsr_euen`, `write_gcsr_euen`, `read_gcsr_misc`, `write_gcsr_misc`, representative callable declarations or inline helpers `kvm_emu_iocsr`, `kvm_read_sw_gcsr`, `kvm_write_sw_gcsr`, `kvm_set_sw_gcsr`, `kvm_change_sw_gcsr`, and representative local types none visible in this header. Direct includes seen in the header are `asm/kvm_vcpu.h`, `asm/loongarch.h`, `linux/kvm_host.h`, `linux/uaccess.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by KVM exits, CSR emulation, PMU virtualization and guest state save/restore. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: CSR classification errors can expose host state or lose guest state. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
